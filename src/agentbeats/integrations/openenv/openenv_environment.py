"""
OpenEnv Environment Manager for AgentBeats.

Manages the lifecycle of OpenEnv Docker containers and provides
a unified interface for interacting with different OpenEnv environments.
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OpenEnvConfig:
    """Configuration for an OpenEnv environment."""
    env_name: str
    docker_image: str
    host: str = "localhost"
    port: Optional[int] = None
    auto_start: bool = True
    auto_cleanup: bool = True


class OpenEnvEnvironmentManager:
    """
    Manages OpenEnv environment lifecycle including Docker container management.

    This class handles:
    - Starting/stopping Docker containers for OpenEnv environments
    - Managing environment connections
    - Episode lifecycle (reset/step/state)
    - Resource cleanup
    """

    def __init__(self, config: OpenEnvConfig):
        """
        Initialize the environment manager.

        Args:
            config: Configuration for the OpenEnv environment
        """
        self.config = config
        self.client = None
        self._episode_active = False
        self._episode_id = None
        self._step_count = 0
        self._total_reward = 0.0

        logger.info(f"Initialized OpenEnvEnvironmentManager for {config.env_name}")

    def start(self) -> None:
        """
        Start the OpenEnv environment and Docker container.

        This method initializes the appropriate OpenEnv client based on the
        environment name and starts the Docker container if needed.
        """
        if self.client is not None:
            logger.warning("Environment already started")
            return

        try:
            # Import OpenEnv clients dynamically based on environment name
            if self.config.env_name == "coding_env":
                from envs.coding_env import CodingEnv
                self.client = CodingEnv.from_docker_image(
                    self.config.docker_image,
                    host=self.config.host,
                    port=self.config.port
                )
            elif self.config.env_name == "openspiel_env":
                from envs.openspiel_env import OpenSpielEnv
                self.client = OpenSpielEnv.from_docker_image(
                    self.config.docker_image,
                    host=self.config.host,
                    port=self.config.port
                )
            elif self.config.env_name == "git_env":
                from envs.git_env import GitEnv
                self.client = GitEnv.from_docker_image(
                    self.config.docker_image,
                    host=self.config.host,
                    port=self.config.port
                )
            else:
                raise ValueError(f"Unsupported environment: {self.config.env_name}")

            logger.info(f"Started {self.config.env_name} environment")

        except Exception as e:
            logger.error(f"Failed to start environment: {e}")
            raise

    def reset(self) -> Dict[str, Any]:
        """
        Reset the environment to start a new episode.

        Returns:
            Dict containing the initial observation and metadata
        """
        if self.client is None:
            raise RuntimeError("Environment not started. Call start() first.")

        try:
            result = self.client.reset()

            self._episode_active = True
            self._episode_id = result.state.episode_id if hasattr(result, 'state') else None
            self._step_count = 0
            self._total_reward = 0.0

            logger.info(f"Reset environment, episode_id: {self._episode_id}")

            return {
                "observation": result.observation,
                "state": result.state if hasattr(result, 'state') else None,
                "episode_id": self._episode_id,
            }

        except Exception as e:
            logger.error(f"Failed to reset environment: {e}")
            raise

    def step(self, action: Any) -> Dict[str, Any]:
        """
        Take a step in the environment with the given action.

        Args:
            action: The action to take (type depends on environment)

        Returns:
            Dict containing observation, reward, done flag, and metadata
        """
        if not self._episode_active:
            raise RuntimeError("No active episode. Call reset() first.")

        try:
            result = self.client.step(action)

            self._step_count += 1
            self._total_reward += result.reward

            logger.debug(f"Step {self._step_count}: reward={result.reward}, done={result.done}")

            if result.done:
                self._episode_active = False
                logger.info(f"Episode completed. Total reward: {self._total_reward}")

            return {
                "observation": result.observation,
                "reward": result.reward,
                "done": result.done,
                "truncated": getattr(result, 'truncated', False),
                "info": getattr(result, 'info', {}),
                "step_count": self._step_count,
                "total_reward": self._total_reward,
            }

        except Exception as e:
            logger.error(f"Failed to step environment: {e}")
            raise

    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of the environment.

        Returns:
            Dict containing current episode metadata
        """
        if self.client is None:
            raise RuntimeError("Environment not started. Call start() first.")

        try:
            state = self.client.state()

            return {
                "episode_id": state.episode_id if hasattr(state, 'episode_id') else self._episode_id,
                "step_count": state.step_count if hasattr(state, 'step_count') else self._step_count,
                "active": self._episode_active,
                "total_reward": self._total_reward,
            }

        except Exception as e:
            logger.error(f"Failed to get state: {e}")
            raise

    def close(self) -> None:
        """
        Close the environment and cleanup resources.

        This method stops the Docker container and releases resources.
        """
        if self.client is None:
            return

        try:
            self.client.close()
            logger.info(f"Closed {self.config.env_name} environment")

        except Exception as e:
            logger.error(f"Error closing environment: {e}")
            raise

        finally:
            self.client = None
            self._episode_active = False

    @property
    def is_active(self) -> bool:
        """Check if the environment is currently active."""
        return self.client is not None

    @property
    def episode_active(self) -> bool:
        """Check if an episode is currently active."""
        return self._episode_active

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
