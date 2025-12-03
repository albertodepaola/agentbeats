"""
OpenEnv Adapter for AgentBeats.

This module provides a bridge between AgentBeats agents and OpenEnv environments,
allowing agents to be evaluated on standardized RL environments.
"""

import logging
from typing import Any, Dict, List, Optional

from .openenv_environment import OpenEnvConfig, OpenEnvEnvironmentManager
from .openenv_tools import create_openenv_tools

logger = logging.getLogger(__name__)


class OpenEnvAdapter:
    """
    Adapter that connects AgentBeats agents with OpenEnv environments.

    This class provides:
    - Automatic tool generation from environment actions
    - Environment lifecycle management
    - Episode management and tracking
    - Integration with AgentBeats agent system
    """

    def __init__(
        self,
        env_name: str,
        docker_image: str,
        host: str = "localhost",
        port: Optional[int] = None,
        auto_start: bool = True,
    ):
        """
        Initialize the OpenEnv adapter.

        Args:
            env_name: Name of the OpenEnv environment (e.g., "coding_env")
            docker_image: Docker image name for the environment
            host: Host to run the environment on
            port: Port for the environment (optional, will be auto-assigned if None)
            auto_start: Whether to automatically start the environment
        """
        self.env_name = env_name

        # Create environment configuration
        config = OpenEnvConfig(
            env_name=env_name,
            docker_image=docker_image,
            host=host,
            port=port,
            auto_start=auto_start,
        )

        # Create environment manager
        self.env_manager = OpenEnvEnvironmentManager(config)

        # Tools will be created when environment starts
        self.tools = None

        # Start environment if auto_start is enabled
        if auto_start:
            self.start()

        logger.info(f"OpenEnvAdapter initialized for {env_name}")

    def start(self) -> None:
        """Start the OpenEnv environment and create tools."""
        if not self.env_manager.is_active:
            self.env_manager.start()

        # Create tools for this environment
        if self.tools is None:
            self.tools = create_openenv_tools(self.env_manager)

        logger.info(f"OpenEnvAdapter started with {len(self.tools)} tools")

    def get_tools(self) -> List:
        """
        Get the tools for this environment.

        Returns:
            List of tool functions that can be used by AgentBeats agents

        Raises:
            RuntimeError: If environment is not started
        """
        if self.tools is None:
            raise RuntimeError("Environment not started. Call start() first.")

        return self.tools

    def reset(self) -> Dict[str, Any]:
        """
        Reset the environment to start a new episode.

        Returns:
            Dict containing initial observation and metadata
        """
        return self.env_manager.reset()

    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of the environment.

        Returns:
            Dict containing episode metadata
        """
        return self.env_manager.get_state()

    def close(self) -> None:
        """Close the environment and cleanup resources."""
        self.env_manager.close()
        self.tools = None
        logger.info("OpenEnvAdapter closed")

    @property
    def is_active(self) -> bool:
        """Check if the adapter is active."""
        return self.env_manager.is_active

    @property
    def episode_active(self) -> bool:
        """Check if an episode is active."""
        return self.env_manager.episode_active

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False

    @classmethod
    def create_for_coding_env(
        cls,
        docker_image: str = "coding-env:latest",
        host: str = "localhost",
        port: Optional[int] = None,
    ) -> "OpenEnvAdapter":
        """
        Create an adapter for the CodingEnv environment.

        Args:
            docker_image: Docker image for coding environment
            host: Host to run on
            port: Port to use (optional)

        Returns:
            OpenEnvAdapter configured for CodingEnv
        """
        return cls(
            env_name="coding_env",
            docker_image=docker_image,
            host=host,
            port=port,
        )

    @classmethod
    def create_for_openspiel_env(
        cls,
        game_name: str = "tic_tac_toe",
        docker_image: str = "openspiel-env:latest",
        host: str = "localhost",
        port: Optional[int] = None,
    ) -> "OpenEnvAdapter":
        """
        Create an adapter for the OpenSpiel environment.

        Args:
            game_name: Name of the game to play
            docker_image: Docker image for OpenSpiel environment
            host: Host to run on
            port: Port to use (optional)

        Returns:
            OpenEnvAdapter configured for OpenSpiel
        """
        return cls(
            env_name="openspiel_env",
            docker_image=docker_image,
            host=host,
            port=port,
        )

    @classmethod
    def create_for_git_env(
        cls,
        docker_image: str = "git-env:latest",
        host: str = "localhost",
        port: Optional[int] = None,
    ) -> "OpenEnvAdapter":
        """
        Create an adapter for the Git environment.

        Args:
            docker_image: Docker image for Git environment
            host: Host to run on
            port: Port to use (optional)

        Returns:
            OpenEnvAdapter configured for GitEnv
        """
        return cls(
            env_name="git_env",
            docker_image=docker_image,
            host=host,
            port=port,
        )
