"""
Tool generation for OpenEnv environments in AgentBeats.

This module creates AgentBeats-compatible tools from OpenEnv action types,
allowing agents to interact with OpenEnv environments using natural function calls.
"""

import logging
from typing import List, Any, Callable
import agentbeats
from dataclasses import fields

logger = logging.getLogger(__name__)


def create_coding_env_tools(env_manager) -> List[Callable]:
    """
    Create tools for the CodingEnv environment.

    Args:
        env_manager: OpenEnvEnvironmentManager instance

    Returns:
        List of tool functions decorated with @agentbeats.tool
    """

    @agentbeats.tool
    def execute_code(code: str) -> str:
        """
        Execute Python code in the coding environment.

        Use this tool to run Python code and get the output. The code will be executed
        in a sandboxed environment with access to standard libraries.

        Args:
            code: The Python code to execute as a string

        Returns:
            The execution result including stdout, stderr, and any return values
        """
        try:
            # Import the action type
            from envs.coding_env import CodeAction

            # Create action and step
            action = CodeAction(code=code)
            result = env_manager.step(action)

            # Format the response
            obs = result["observation"]
            response = f"Execution completed.\n"

            if hasattr(obs, 'output') and obs.output:
                response += f"Output:\n{obs.output}\n"

            if hasattr(obs, 'error') and obs.error:
                response += f"Error:\n{obs.error}\n"

            if hasattr(obs, 'success'):
                response += f"Success: {obs.success}\n"

            response += f"Reward: {result['reward']}\n"

            if result['done']:
                response += "Episode completed.\n"

            return response

        except Exception as e:
            return f"Error executing code: {str(e)}"

    @agentbeats.tool
    def reset_environment() -> str:
        """
        Reset the coding environment to start fresh.

        Use this tool to clear all previous code execution context and start a new episode.

        Returns:
            Confirmation message that the environment has been reset
        """
        try:
            result = env_manager.reset()
            obs = result["observation"]

            message = "Environment reset successfully.\n"
            if hasattr(obs, 'message'):
                message += f"{obs.message}\n"

            return message

        except Exception as e:
            return f"Error resetting environment: {str(e)}"

    @agentbeats.tool
    def get_environment_status() -> str:
        """
        Get the current status of the coding environment.

        Use this tool to check episode information, step count, and total reward.

        Returns:
            Status information about the current episode
        """
        try:
            state = env_manager.get_state()

            status = "Environment Status:\n"
            status += f"Episode ID: {state['episode_id']}\n"
            status += f"Step Count: {state['step_count']}\n"
            status += f"Total Reward: {state['total_reward']:.2f}\n"
            status += f"Episode Active: {state['active']}\n"

            return status

        except Exception as e:
            return f"Error getting status: {str(e)}"

    return [execute_code, reset_environment, get_environment_status]


def create_openspiel_env_tools(env_manager) -> List[Callable]:
    """
    Create tools for the OpenSpiel environment.

    Args:
        env_manager: OpenEnvEnvironmentManager instance

    Returns:
        List of tool functions decorated with @agentbeats.tool
    """

    @agentbeats.tool
    def make_move(action: int) -> str:
        """
        Make a move in the OpenSpiel game.

        Args:
            action: The action index to take in the game

        Returns:
            The result of the move including the new game state and reward
        """
        try:
            from envs.openspiel_env import OpenSpielAction

            action_obj = OpenSpielAction(action=action)
            result = env_manager.step(action_obj)

            obs = result["observation"]
            response = f"Move executed.\n"

            if hasattr(obs, 'observation'):
                response += f"Game State:\n{obs.observation}\n"

            if hasattr(obs, 'legal_actions'):
                response += f"Legal Actions: {obs.legal_actions}\n"

            response += f"Reward: {result['reward']}\n"

            if result['done']:
                response += "Game completed.\n"

            return response

        except Exception as e:
            return f"Error making move: {str(e)}"

    @agentbeats.tool
    def get_legal_actions() -> str:
        """
        Get the list of legal actions in the current game state.

        Returns:
            List of legal action indices that can be played
        """
        try:
            state = env_manager.get_state()
            # This would need to be implemented based on OpenSpiel's API
            return "Legal actions retrieval needs OpenSpiel state access"

        except Exception as e:
            return f"Error getting legal actions: {str(e)}"

    return [make_move, get_legal_actions, reset_environment, get_environment_status]


def create_git_env_tools(env_manager) -> List[Callable]:
    """
    Create tools for the Git environment.

    Args:
        env_manager: OpenEnvEnvironmentManager instance

    Returns:
        List of tool functions decorated with @agentbeats.tool
    """

    @agentbeats.tool
    def run_git_command(command: str) -> str:
        """
        Run a git command in the environment.

        Args:
            command: The git command to run (e.g., "git status", "git commit -m 'message'")

        Returns:
            The output of the git command
        """
        try:
            from envs.git_env import GitAction

            action = GitAction(command=command)
            result = env_manager.step(action)

            obs = result["observation"]
            response = f"Git command executed.\n"

            if hasattr(obs, 'output'):
                response += f"Output:\n{obs.output}\n"

            response += f"Reward: {result['reward']}\n"

            if result['done']:
                response += "Task completed.\n"

            return response

        except Exception as e:
            return f"Error running git command: {str(e)}"

    return [run_git_command, reset_environment, get_environment_status]


def create_openenv_tools(env_manager) -> List[Callable]:
    """
    Create tools for the specified OpenEnv environment.

    This function automatically selects the appropriate tool set based on
    the environment type.

    Args:
        env_manager: OpenEnvEnvironmentManager instance

    Returns:
        List of tool functions for the environment

    Raises:
        ValueError: If the environment type is not supported
    """
    env_name = env_manager.config.env_name

    tool_creators = {
        "coding_env": create_coding_env_tools,
        "openspiel_env": create_openspiel_env_tools,
        "git_env": create_git_env_tools,
    }

    if env_name not in tool_creators:
        raise ValueError(
            f"Unsupported environment: {env_name}. "
            f"Supported environments: {list(tool_creators.keys())}"
        )

    logger.info(f"Creating tools for {env_name}")
    tools = tool_creators[env_name](env_manager)
    logger.info(f"Created {len(tools)} tools for {env_name}")

    return tools
