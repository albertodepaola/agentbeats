"""
OpenEnv Evaluator for AgentBeats.

This module provides an evaluation harness for running AgentBeats agents
on OpenEnv environments and collecting performance metrics.
"""

import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

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
        with open(filepath, "w") as f:
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
                print(
                    f"  Episode {i}: {status} Reward={ep.total_reward:.2f}, "
                    f"Steps={ep.step_count}, Duration={ep.duration_seconds:.1f}s"
                )
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

    async def run_episode_async(
        self,
        episode_num: int,
        agent_executor: Any,
    ) -> EpisodeResult:
        """
        Run a single evaluation episode asynchronously.

        Args:
            episode_num: Episode number (for logging)
            agent_executor: AgentBeats executor instance with invoke_agent method

        Returns:
            EpisodeResult containing episode metrics
        """
        logger.info(f"Starting episode {episode_num}/{self.num_episodes}")
        start_time = time.time()

        try:
            # Reset environment
            reset_result = self.adapter.reset()
            episode_id = reset_result.get("episode_id", f"episode_{episode_num}")

            # Get task for this episode
            from .sample_tasks import get_task, format_task_prompt, get_expected_outputs
            from .task_validator import TaskValidator

            # Use episode number to select task (cyclic)
            task = get_task(index=episode_num - 1)
            initial_message = format_task_prompt(task, episode_num)
            expected_outputs = get_expected_outputs(task)

            logger.info(f"Episode {episode_num} task: {task['id']}")
            logger.info(f"Expected outputs: {expected_outputs}")
            logger.info(f"Prompt length: {len(initial_message)} characters")
            logger.debug(f"Full prompt:\n{initial_message}")

            # Create a minimal context object that provides get_user_input()
            # This is all that invoke_agent() actually needs
            class SimpleContext:
                def __init__(self, message: str):
                    self._message = message
                    self.current_task = None

                def get_user_input(self, delimiter: str = '\n') -> str:
                    return self._message

            mock_context = SimpleContext(initial_message)

            # Run agent - agent should call execute_code() to solve the task
            logger.info(f"Invoking agent to solve task: {task['id']}")
            agent_response = await agent_executor.invoke_agent(mock_context)

            # Capture the agent's conversation history
            agent_chat_history = agent_executor.chat_history if hasattr(agent_executor, 'chat_history') else []
            logger.info(f"Agent response: {agent_response}")
            logger.info(f"Agent chat history length: {len(agent_chat_history)} messages")
            logger.debug(f"Full chat history: {agent_chat_history}")

            # Get final state after agent execution
            final_state = self.adapter.get_state()
            env_reward = final_state.get("total_reward", 0.0)
            step_count = final_state.get("step_count", 0)

            # Validate task completion and assign reward
            validator = TaskValidator(base_reward=1.0, partial_credit=0.5)

            # Extract the actual output from the agent's last tool call
            actual_output = None
            for msg in reversed(agent_chat_history):
                if msg.get("type") == "function_call_output":
                    output_text = msg.get("output", "")
                    # Extract output from the response
                    if "Output:\n" in output_text:
                        actual_output = output_text.split("Output:\n")[1].split("\n")[0]
                        break

            logger.info(f"Extracted actual output: {actual_output}")

            if actual_output:
                task_reward = validator.validate_output(
                    actual_output=actual_output,
                    expected_outputs=expected_outputs,
                    task_id=task["id"]
                )
            else:
                logger.warning(f"Task {task['id']}: No output found in agent responses")
                task_reward = 0.0

            # Use task reward instead of environment reward for success determination
            total_reward = task_reward
            logger.info(f"Environment reward: {env_reward}, Task validation reward: {task_reward}")

            # Determine success (task completed correctly)
            success = task_reward >= validator.base_reward

            duration = time.time() - start_time

            result = EpisodeResult(
                episode_id=episode_id,
                total_reward=total_reward,
                step_count=step_count,
                success=success,
                duration_seconds=duration,
                error=None,
                metadata={
                    "episode_num": episode_num,
                    "task_id": task["id"],
                    "task_prompt": task["prompt"],
                    "task_difficulty": task.get("difficulty", "unknown"),
                    "agent_response": agent_response,
                    "agent_chat_history": agent_chat_history,
                    "final_state": final_state,
                },
            )

            logger.info(
                f"Episode {episode_num} completed: "
                f"task={task['id']}, reward={total_reward:.2f}, "
                f"steps={step_count}, success={success}, duration={duration:.1f}s"
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Episode {episode_num} failed: {e}")
            import traceback
            traceback.print_exc()

            return EpisodeResult(
                episode_id=f"episode_{episode_num}",
                total_reward=0.0,
                step_count=0,
                success=False,
                duration_seconds=duration,
                error=str(e),
            )

    def run_episode(
        self,
        episode_num: int,
        agent_executor: Any,
    ) -> EpisodeResult:
        """
        Synchronous wrapper for run_episode_async.

        Args:
            episode_num: Episode number (for logging)
            agent_executor: AgentBeats executor instance

        Returns:
            EpisodeResult containing episode metrics
        """
        import asyncio

        # Get or create event loop
        try:
            loop = asyncio.get_running_loop()
            # If we're already in an event loop, we need to create a task
            # This shouldn't happen in normal usage, but handle it gracefully
            future = asyncio.ensure_future(
                self.run_episode_async(episode_num, agent_executor)
            )
            return loop.run_until_complete(future)
        except RuntimeError:
            # No running loop, create one
            return asyncio.run(
                self.run_episode_async(episode_num, agent_executor)
            )

    def run(self, agent_card_json: Dict[str, Any], model_type: str, model_name: str,
            tool_list: List[Any], mcp_url_list: List[str]) -> EvaluationResults:
        """
        Run the full evaluation.

        Args:
            agent_card_json: Agent card configuration
            model_type: Model type (e.g., "google", "openai")
            model_name: Model name (e.g., "gemini-2.5-flash")
            tool_list: List of tool functions
            mcp_url_list: List of MCP server URLs

        Returns:
            EvaluationResults containing aggregated metrics
        """
        logger.info(f"Starting evaluation: {self.num_episodes} episodes")
        eval_start_time = time.time()

        self.episode_results = []

        for episode_num in range(1, self.num_episodes + 1):
            # Create a fresh executor for each episode to avoid state issues
            from agentbeats.agent_executor import AgentBeatsExecutor

            executor = AgentBeatsExecutor(
                agent_card_json=agent_card_json,
                model_type=model_type,
                model_name=model_name,
                mcp_url_list=mcp_url_list,
                tool_list=tool_list.copy(),  # Copy to avoid mutation
            )

            result = self.run_episode(episode_num, executor)
            self.episode_results.append(result)

        total_duration = time.time() - eval_start_time

        # Aggregate results
        results = self._aggregate_results(total_duration)

        # Save results if output directory specified
        if self.output_dir:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = (
                f"eval_{self.adapter.env_name}_{self.agent_name}_{timestamp}.json"
            )
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
