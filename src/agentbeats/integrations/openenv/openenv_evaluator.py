"""
OpenEnv Evaluator for AgentBeats.

This module provides an evaluation harness for running AgentBeats agents
on OpenEnv environments and collecting performance metrics.
"""

import logging
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime

from .openenv_adapter import OpenEnvAdapter

logger = logging.getLogger(__name__)


@dataclass
class EpisodeResult:
    """Results from a single episode."""
    episode_id: str
    total_reward: float
    step_count: int
    success: bool
    duration_seconds: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class EvaluationResults:
    """Aggregated results from multiple episodes."""
    env_name: str
    agent_name: str
    num_episodes: int
    episodes: List[EpisodeResult]
    avg_reward: float
    avg_steps: float
    success_rate: float
    total_duration_seconds: float
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            **asdict(self),
            "episodes": [ep.to_dict() for ep in self.episodes],
        }

    def save_to_file(self, filepath: Path) -> None:
        """Save results to a JSON file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Saved evaluation results to {filepath}")

    def print_summary(self) -> None:
        """Print a summary of the evaluation results."""
        print("\n" + "=" * 60)
        print(f"Evaluation Results: {self.agent_name} on {self.env_name}")
        print("=" * 60)
        print(f"Episodes: {self.num_episodes}")
        print(f"Average Reward: {self.avg_reward:.2f}")
        print(f"Average Steps: {self.avg_steps:.1f}")
        print(f"Success Rate: {self.success_rate * 100:.1f}%")
        print(f"Total Duration: {self.total_duration_seconds:.1f}s")
        print("=" * 60)

        if self.episodes:
            print("\nPer-Episode Results:")
            print("-" * 60)
            for i, ep in enumerate(self.episodes, 1):
                status = "✓" if ep.success else "✗"
                print(f"  Episode {i}: {status} Reward={ep.total_reward:.2f}, "
                      f"Steps={ep.step_count}, Duration={ep.duration_seconds:.1f}s")
                if ep.error:
                    print(f"    Error: {ep.error}")
            print("=" * 60 + "\n")


class OpenEnvEvaluator:
    """
    Evaluator for running AgentBeats agents on OpenEnv environments.

    This class handles:
    - Running multiple evaluation episodes
    - Collecting metrics and performance data
    - Aggregating results
    - Saving trajectory logs
    """

    def __init__(
        self,
        adapter: OpenEnvAdapter,
        agent_name: str = "Unknown Agent",
        num_episodes: int = 10,
        max_steps_per_episode: Optional[int] = None,
        output_dir: Optional[Path] = None,
    ):
        """
        Initialize the evaluator.

        Args:
            adapter: OpenEnvAdapter instance
            agent_name: Name of the agent being evaluated
            num_episodes: Number of episodes to run
            max_steps_per_episode: Maximum steps per episode (None for no limit)
            output_dir: Directory to save results (None for no saving)
        """
        self.adapter = adapter
        self.agent_name = agent_name
        self.num_episodes = num_episodes
        self.max_steps_per_episode = max_steps_per_episode
        self.output_dir = Path(output_dir) if output_dir else None

        self.episode_results: List[EpisodeResult] = []

        logger.info(
            f"Initialized OpenEnvEvaluator: {agent_name} on {adapter.env_name}, "
            f"{num_episodes} episodes"
        )

    def run_episode(
        self,
        episode_num: int,
        agent_runner: Any,
    ) -> EpisodeResult:
        """
        Run a single evaluation episode.

        Args:
            episode_num: Episode number (for logging)
            agent_runner: AgentBeats agent runner instance

        Returns:
            EpisodeResult containing episode metrics
        """
        logger.info(f"Starting episode {episode_num}/{self.num_episodes}")
        start_time = time.time()

        try:
            # Reset environment
            reset_result = self.adapter.reset()
            episode_id = reset_result.get("episode_id", f"episode_{episode_num}")

            # Get initial observation
            initial_obs = reset_result.get("observation")

            # Create initial message for agent
            if hasattr(initial_obs, 'message'):
                initial_message = initial_obs.message
            else:
                initial_message = f"Environment reset. Starting episode {episode_num}."

            # Run agent
            # Note: This is a simplified version. In practice, you'd want to:
            # 1. Send initial message to agent
            # 2. Agent uses tools (which call env_manager.step())
            # 3. Continue until episode is done or max steps reached

            step_count = 0
            done = False
            error_msg = None

            # Get final state
            final_state = self.adapter.get_state()
            total_reward = final_state.get("total_reward", 0.0)
            step_count = final_state.get("step_count", 0)

            # Determine success (environment-specific logic)
            success = total_reward > 0  # Simple heuristic

            duration = time.time() - start_time

            result = EpisodeResult(
                episode_id=episode_id,
                total_reward=total_reward,
                step_count=step_count,
                success=success,
                duration_seconds=duration,
                error=error_msg,
                metadata={
                    "episode_num": episode_num,
                    "final_state": final_state,
                },
            )

            logger.info(
                f"Episode {episode_num} completed: "
                f"reward={total_reward:.2f}, steps={step_count}, "
                f"success={success}, duration={duration:.1f}s"
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Episode {episode_num} failed: {e}")

            return EpisodeResult(
                episode_id=f"episode_{episode_num}",
                total_reward=0.0,
                step_count=0,
                success=False,
                duration_seconds=duration,
                error=str(e),
            )

    def run(self, agent_runner: Optional[Any] = None) -> EvaluationResults:
        """
        Run the full evaluation.

        Args:
            agent_runner: AgentBeats agent runner instance (optional for now)

        Returns:
            EvaluationResults containing aggregated metrics
        """
        logger.info(f"Starting evaluation: {self.num_episodes} episodes")
        eval_start_time = time.time()

        self.episode_results = []

        for episode_num in range(1, self.num_episodes + 1):
            result = self.run_episode(episode_num, agent_runner)
            self.episode_results.append(result)

        total_duration = time.time() - eval_start_time

        # Aggregate results
        results = self._aggregate_results(total_duration)

        # Save results if output directory specified
        if self.output_dir:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"eval_{self.adapter.env_name}_{self.agent_name}_{timestamp}.json"
            results.save_to_file(self.output_dir / filename)

        # Print summary
        results.print_summary()

        logger.info("Evaluation completed")

        return results

    def _aggregate_results(self, total_duration: float) -> EvaluationResults:
        """
        Aggregate results from all episodes.

        Args:
            total_duration: Total evaluation duration in seconds

        Returns:
            EvaluationResults with aggregated metrics
        """
        if not self.episode_results:
            return EvaluationResults(
                env_name=self.adapter.env_name,
                agent_name=self.agent_name,
                num_episodes=0,
                episodes=[],
                avg_reward=0.0,
                avg_steps=0.0,
                success_rate=0.0,
                total_duration_seconds=total_duration,
                timestamp=datetime.now().isoformat(),
            )

        # Calculate aggregates
        total_reward = sum(ep.total_reward for ep in self.episode_results)
        total_steps = sum(ep.step_count for ep in self.episode_results)
        num_successes = sum(1 for ep in self.episode_results if ep.success)

        avg_reward = total_reward / len(self.episode_results)
        avg_steps = total_steps / len(self.episode_results)
        success_rate = num_successes / len(self.episode_results)

        return EvaluationResults(
            env_name=self.adapter.env_name,
            agent_name=self.agent_name,
            num_episodes=len(self.episode_results),
            episodes=self.episode_results,
            avg_reward=avg_reward,
            avg_steps=avg_steps,
            success_rate=success_rate,
            total_duration_seconds=total_duration,
            timestamp=datetime.now().isoformat(),
        )

    @classmethod
    def create_for_coding_env(
        cls,
        agent_name: str = "Coding Agent",
        num_episodes: int = 10,
        docker_image: str = "coding-env:latest",
        output_dir: Optional[Path] = None,
    ) -> "OpenEnvEvaluator":
        """
        Create an evaluator for the CodingEnv environment.

        Args:
            agent_name: Name of the agent
            num_episodes: Number of episodes to run
            docker_image: Docker image for coding environment
            output_dir: Directory to save results

        Returns:
            OpenEnvEvaluator configured for CodingEnv
        """
        adapter = OpenEnvAdapter.create_for_coding_env(docker_image=docker_image)

        return cls(
            adapter=adapter,
            agent_name=agent_name,
            num_episodes=num_episodes,
            output_dir=output_dir,
        )
