"""
Task validation for OpenEnv coding tasks.

This module provides validation logic to check if coding task solutions are correct
and assign appropriate rewards based on correctness.
"""

import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class TaskValidator:
    """Validates coding task solutions and assigns rewards."""

    def __init__(self, base_reward: float = 1.0, partial_credit: float = 0.5):
        """
        Initialize the task validator.

        Args:
            base_reward: Reward for completely correct solution
            partial_credit: Reward for partially correct solution
        """
        self.base_reward = base_reward
        self.partial_credit = partial_credit

    def validate_output(
        self,
        actual_output: str,
        expected_outputs: Dict[Any, Any],
        task_id: str,
    ) -> float:
        """
        Validate task output and return reward.

        Args:
            actual_output: The actual output from code execution
            expected_outputs: Dictionary of expected test case results
            task_id: ID of the task being validated

        Returns:
            float: Reward value based on correctness
        """
        try:
            # Parse the actual output as JSON
            if not actual_output or actual_output.strip() == "(no output)":
                logger.warning(f"Task {task_id}: No output to validate")
                return 0.0

            # Try to parse as JSON
            try:
                actual_results = json.loads(actual_output.strip())
            except json.JSONDecodeError:
                # Try to extract JSON from output if it's embedded in other text
                import re

                json_match = re.search(r"\{.*\}", actual_output, re.DOTALL)
                if json_match:
                    actual_results = json.loads(json_match.group())
                else:
                    logger.warning(
                        f"Task {task_id}: Could not parse output as JSON: {actual_output[:100]}"
                    )
                    return 0.0

            # Compare with expected outputs
            if isinstance(actual_results, dict) and isinstance(expected_outputs, dict):
                return self._validate_dict_output(
                    actual_results, expected_outputs, task_id
                )
            elif isinstance(actual_results, list) and isinstance(
                expected_outputs, list
            ):
                return self._validate_list_output(
                    actual_results, expected_outputs, task_id
                )
            else:
                # Direct comparison for simple types
                if actual_results == expected_outputs:
                    logger.info(f"Task {task_id}: Perfect match!")
                    return self.base_reward
                else:
                    logger.warning(
                        f"Task {task_id}: Output mismatch. Expected {expected_outputs}, got {actual_results}"
                    )
                    return 0.0

        except Exception as e:
            logger.error(f"Task {task_id}: Error validating output: {e}")
            return 0.0

    def _validate_dict_output(
        self, actual: Dict, expected: Dict, task_id: str
    ) -> float:
        """Validate dictionary output with partial credit."""
        if not expected:
            return 0.0

        # Convert keys to strings for comparison (JSON serialization converts to strings)
        actual_str_keys = {str(k): v for k, v in actual.items()}
        expected_str_keys = {str(k): v for k, v in expected.items()}

        correct_count = 0
        total_count = len(expected_str_keys)

        for key, expected_value in expected_str_keys.items():
            if key in actual_str_keys:
                actual_value = actual_str_keys[key]
                if self._values_match(actual_value, expected_value):
                    correct_count += 1
                else:
                    logger.debug(
                        f"Task {task_id}: Mismatch for key {key}: expected {expected_value}, got {actual_value}"
                    )
            else:
                logger.debug(f"Task {task_id}: Missing key {key} in output")

        accuracy = correct_count / total_count if total_count > 0 else 0.0
        logger.info(
            f"Task {task_id}: {correct_count}/{total_count} test cases correct ({accuracy*100:.1f}%)"
        )

        if accuracy == 1.0:
            return self.base_reward
        elif accuracy >= 0.5:
            return self.partial_credit
        else:
            return 0.0

    def _validate_list_output(
        self, actual: list, expected: list, task_id: str
    ) -> float:
        """Validate list output with partial credit."""
        if not expected:
            return 0.0

        if len(actual) != len(expected):
            logger.warning(
                f"Task {task_id}: Length mismatch. Expected {len(expected)}, got {len(actual)}"
            )
            return 0.0

        correct_count = sum(
            1
            for a, e in zip(actual, expected)
            if self._values_match(a, e)
        )
        accuracy = correct_count / len(expected)

        logger.info(
            f"Task {task_id}: {correct_count}/{len(expected)} test cases correct ({accuracy*100:.1f}%)"
        )

        if accuracy == 1.0:
            return self.base_reward
        elif accuracy >= 0.5:
            return self.partial_credit
        else:
            return 0.0

    def _values_match(self, actual: Any, expected: Any) -> bool:
        """Check if two values match, handling type conversions."""
        # Handle boolean comparison (JSON may represent as true/false)
        if isinstance(expected, bool):
            if isinstance(actual, bool):
                return actual == expected
            if isinstance(actual, str):
                return actual.lower() == str(expected).lower()

        # Handle numeric comparison
        if isinstance(expected, (int, float)):
            try:
                return float(actual) == float(expected)
            except (ValueError, TypeError):
                return False

        # Direct comparison for other types
        return actual == expected
