"""
Sample coding tasks for OpenEnv evaluation.

This module provides a dataset of coding challenges for evaluating
agents on the OpenEnv CodingEnv environment.
"""

from typing import List, Dict, Any, Optional


CODING_TASKS = [
    # Concise tasks (≤100 chars) - these work with current coding-env:stable reward system
    {
        "id": "add_numbers",
        "prompt": "Write a one-line function `add(a,b)` that returns the sum of two numbers.",
        "test_cases": [
            {"input": (3, 5), "expected": 8},
            {"input": (10, 20), "expected": 30},
            {"input": (-5, 5), "expected": 0},
            {"input": (0, 0), "expected": 0},
        ],
        "difficulty": "easy",
        "solution_template": "def add(a,b):return a+b",
        "expected_length": "short",  # ≤100 chars
    },
    {
        "id": "multiply",
        "prompt": "Write a one-line function `mul(a,b)` that returns the product of two numbers.",
        "test_cases": [
            {"input": (3, 4), "expected": 12},
            {"input": (7, 8), "expected": 56},
            {"input": (0, 10), "expected": 0},
            {"input": (-2, 5), "expected": -10},
        ],
        "difficulty": "easy",
        "solution_template": "def mul(a,b):return a*b",
        "expected_length": "short",
    },
    {
        "id": "is_even",
        "prompt": "Write a one-line function `is_even(n)` that returns True if n is even, False otherwise.",
        "test_cases": [
            {"input": 4, "expected": True},
            {"input": 7, "expected": False},
            {"input": 0, "expected": True},
            {"input": -2, "expected": True},
        ],
        "difficulty": "easy",
        "solution_template": "def is_even(n):return n%2==0",
        "expected_length": "short",
    },
    {
        "id": "square",
        "prompt": "Write a one-line function `sq(n)` that returns the square of a number.",
        "test_cases": [
            {"input": 5, "expected": 25},
            {"input": 0, "expected": 0},
            {"input": -3, "expected": 9},
            {"input": 10, "expected": 100},
        ],
        "difficulty": "easy",
        "solution_template": "def sq(n):return n*n",
        "expected_length": "short",
    },
    {
        "id": "absolute",
        "prompt": "Write a one-line function `abs_val(n)` that returns the absolute value of n. Don't use abs().",
        "test_cases": [
            {"input": -5, "expected": 5},
            {"input": 5, "expected": 5},
            {"input": 0, "expected": 0},
            {"input": -100, "expected": 100},
        ],
        "difficulty": "easy",
        "solution_template": "def abs_val(n):return n if n>=0 else -n",
        "expected_length": "short",
    },
    {
        "id": "max_two",
        "prompt": "Write a one-line function `max2(a,b)` that returns the larger of two numbers. Don't use max().",
        "test_cases": [
            {"input": (5, 3), "expected": 5},
            {"input": (2, 8), "expected": 8},
            {"input": (7, 7), "expected": 7},
            {"input": (-1, -5), "expected": -1},
        ],
        "difficulty": "easy",
        "solution_template": "def max2(a,b):return a if a>b else b",
        "expected_length": "short",
    },
    {
        "id": "is_positive",
        "prompt": "Write a one-line function `is_pos(n)` that returns True if n is positive, False otherwise.",
        "test_cases": [
            {"input": 5, "expected": True},
            {"input": -3, "expected": False},
            {"input": 0, "expected": False},
            {"input": 100, "expected": True},
        ],
        "difficulty": "easy",
        "solution_template": "def is_pos(n):return n>0",
        "expected_length": "short",
    },
    {
        "id": "double",
        "prompt": "Write a one-line function `dbl(n)` that returns double the value of n.",
        "test_cases": [
            {"input": 5, "expected": 10},
            {"input": 0, "expected": 0},
            {"input": -3, "expected": -6},
            {"input": 7, "expected": 14},
        ],
        "difficulty": "easy",
        "solution_template": "def dbl(n):return n*2",
        "expected_length": "short",
    },
    # Full-length tasks (>100 chars) - will work when Docker image has task-aware rewards
    {
        "id": "fibonacci",
        "prompt": "Write a Python function called `fibonacci(n)` that returns the nth Fibonacci number. You can use either recursion or iteration.",
        "test_cases": [
            {"input": 0, "expected": 0},
            {"input": 1, "expected": 1},
            {"input": 5, "expected": 5},
            {"input": 10, "expected": 55},
        ],
        "difficulty": "easy",
        "solution_template": """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)""",
        "expected_length": "long",
    },
    {
        "id": "reverse_string",
        "prompt": "Write a function called `reverse_string(s)` that takes a string and returns it reversed.",
        "test_cases": [
            {"input": "hello", "expected": "olleh"},
            {"input": "Python", "expected": "nohtyP"},
            {"input": "", "expected": ""},
            {"input": "a", "expected": "a"},
        ],
        "difficulty": "easy",
        "solution_template": """def reverse_string(s):
    return s[::-1]""",
        "expected_length": "long",
    },
    {
        "id": "is_palindrome",
        "prompt": "Write a function called `is_palindrome(s)` that returns True if the string is a palindrome (reads the same forwards and backwards), False otherwise. Ignore case and spaces.",
        "test_cases": [
            {"input": "racecar", "expected": True},
            {"input": "hello", "expected": False},
            {"input": "A man a plan a canal Panama", "expected": True},
            {"input": "python", "expected": False},
        ],
        "difficulty": "easy",
        "solution_template": """def is_palindrome(s):
    s = s.lower().replace(' ', '')
    return s == s[::-1]""",
        "expected_length": "long",
    },
    {
        "id": "sum_list",
        "prompt": "Write a function called `sum_list(numbers)` that takes a list of numbers and returns their sum. Do not use the built-in sum() function.",
        "test_cases": [
            {"input": [1, 2, 3, 4, 5], "expected": 15},
            {"input": [10, 20, 30], "expected": 60},
            {"input": [], "expected": 0},
            {"input": [-1, 1, -2, 2], "expected": 0},
        ],
        "difficulty": "easy",
        "solution_template": """def sum_list(numbers):
    total = 0
    for num in numbers:
        total += num
    return total""",
        "expected_length": "long",
    },
    {
        "id": "find_maximum",
        "prompt": "Write a function called `find_maximum(numbers)` that takes a non-empty list of numbers and returns the maximum value. Do not use the built-in max() function.",
        "test_cases": [
            {"input": [1, 5, 3, 9, 2], "expected": 9},
            {"input": [10], "expected": 10},
            {"input": [-5, -1, -10], "expected": -1},
            {"input": [7, 7, 7], "expected": 7},
        ],
        "difficulty": "easy",
        "solution_template": """def find_maximum(numbers):
    maximum = numbers[0]
    for num in numbers:
        if num > maximum:
            maximum = num
    return maximum""",
        "expected_length": "long",
    },
    {
        "id": "count_vowels",
        "prompt": "Write a function called `count_vowels(s)` that takes a string and returns the number of vowels (a, e, i, o, u) in it. Ignore case.",
        "test_cases": [
            {"input": "hello", "expected": 2},
            {"input": "Python Programming", "expected": 4},
            {"input": "aeiou", "expected": 5},
            {"input": "xyz", "expected": 0},
        ],
        "difficulty": "easy",
        "solution_template": """def count_vowels(s):
    vowels = 'aeiouAEIOU'
    count = 0
    for char in s:
        if char in vowels:
            count += 1
    return count""",
        "expected_length": "long",
    },
    {
        "id": "factorial",
        "prompt": "Write a function called `factorial(n)` that returns the factorial of n (n!). The factorial of n is the product of all positive integers less than or equal to n. For example, 5! = 5 × 4 × 3 × 2 × 1 = 120.",
        "test_cases": [
            {"input": 0, "expected": 1},
            {"input": 1, "expected": 1},
            {"input": 5, "expected": 120},
            {"input": 7, "expected": 5040},
        ],
        "difficulty": "easy",
        "solution_template": """def factorial(n):
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result""",
        "expected_length": "long",
    },
    {
        "id": "is_prime",
        "prompt": "Write a function called `is_prime(n)` that returns True if n is a prime number, False otherwise. A prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself.",
        "test_cases": [
            {"input": 2, "expected": True},
            {"input": 17, "expected": True},
            {"input": 4, "expected": False},
            {"input": 1, "expected": False},
            {"input": 29, "expected": True},
        ],
        "difficulty": "medium",
        "solution_template": """def is_prime(n):
    if n <= 1:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True""",
        "expected_length": "long",
    },
    {
        "id": "binary_search",
        "prompt": "Implement a binary search function `binary_search(arr, target)` that returns the index of target in a sorted array arr, or -1 if target is not found.",
        "test_cases": [
            {"input": ([1, 2, 3, 4, 5], 3), "expected": 2},
            {"input": ([1, 2, 3, 4, 5], 6), "expected": -1},
            {"input": ([10, 20, 30, 40, 50], 10), "expected": 0},
            {"input": ([1, 3, 5, 7, 9], 7), "expected": 3},
        ],
        "difficulty": "medium",
        "solution_template": """def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1""",
        "expected_length": "long",
    },
    {
        "id": "merge_sorted_lists",
        "prompt": "Write a function called `merge_sorted_lists(list1, list2)` that takes two sorted lists and returns a new sorted list containing all elements from both lists.",
        "test_cases": [
            {"input": ([1, 3, 5], [2, 4, 6]), "expected": [1, 2, 3, 4, 5, 6]},
            {"input": ([1, 2, 3], [4, 5, 6]), "expected": [1, 2, 3, 4, 5, 6]},
            {"input": ([], [1, 2, 3]), "expected": [1, 2, 3]},
            {"input": ([1, 5, 9], [2, 3, 7]), "expected": [1, 2, 3, 5, 7, 9]},
        ],
        "difficulty": "medium",
        "solution_template": """def merge_sorted_lists(list1, list2):
    result = []
    i, j = 0, 0
    while i < len(list1) and j < len(list2):
        if list1[i] < list2[j]:
            result.append(list1[i])
            i += 1
        else:
            result.append(list2[j])
            j += 1
    result.extend(list1[i:])
    result.extend(list2[j:])
    return result""",
        "expected_length": "long",
    },
]


def get_task(task_id: Optional[str] = None, index: Optional[int] = None) -> Dict[str, Any]:
    """
    Get a task by ID or index.

    Args:
        task_id: The ID of the task to retrieve (e.g., "fibonacci")
        index: The index of the task to retrieve (cycles through tasks if >= len(CODING_TASKS))

    Returns:
        A task dictionary containing id, prompt, test_cases, difficulty, and solution_template

    Examples:
        >>> task = get_task(task_id="fibonacci")
        >>> task["id"]
        'fibonacci'

        >>> task = get_task(index=0)
        >>> task["id"]
        'add_numbers'

        >>> task = get_task(index=15)  # Cycles through tasks
        >>> task["id"] in [t["id"] for t in CODING_TASKS]
        True
    """
    if task_id:
        task = next((t for t in CODING_TASKS if t["id"] == task_id), None)
        if task is None:
            raise ValueError(f"Task with id '{task_id}' not found")
        return task

    if index is not None:
        return CODING_TASKS[index % len(CODING_TASKS)]

    # Default to first task
    return CODING_TASKS[0]


def format_task_prompt(task: Dict[str, Any], episode_num: int) -> str:
    """
    Format a task into a prompt for the agent.

    Args:
        task: Task dictionary containing prompt and test_cases
        episode_num: The episode number (for display purposes)

    Returns:
        A formatted prompt string ready to be passed to the agent

    Example:
        >>> task = get_task(task_id="fibonacci")
        >>> prompt = format_task_prompt(task, 1)
        >>> "Episode 1 Coding Challenge" in prompt
        True
    """
    # Format test cases
    test_cases_lines = []
    for tc in task["test_cases"]:
        input_val = tc["input"]
        expected_val = tc["expected"]
        test_cases_lines.append(f"  - Input: {input_val} → Expected: {expected_val}")
    test_cases_str = "\n".join(test_cases_lines)

    # Check if this is a short task
    is_short = task.get("expected_length") == "short"

    brevity_note = ""
    if is_short:
        brevity_note = "\n⚠️ IMPORTANT: Write CONCISE code if possible (≤100 chars)\n"

    return f"""Episode {episode_num} Coding Challenge:

{task["prompt"]}

Test Cases:
{test_cases_str}
{brevity_note}
Instructions:
1. Write complete, working Python code that defines the required function
2. Use the execute_code() tool to test your solution
3. Make sure your function works with all the provided test cases
4. You can call execute_code() multiple times to debug and refine your solution

Begin solving the task now!"""


def get_all_task_ids() -> List[str]:
    """
    Get a list of all task IDs.

    Returns:
        List of task ID strings
    """
    return [task["id"] for task in CODING_TASKS]


def get_task_count() -> int:
    """
    Get the total number of tasks in the dataset.

    Returns:
        Number of tasks
    """
    return len(CODING_TASKS)


def get_expected_outputs(task: Dict[str, Any]) -> Dict[Any, Any]:
    """
    Extract expected outputs from a task for validation.

    Args:
        task: Task dictionary containing test_cases

    Returns:
        Dictionary mapping inputs to expected outputs

    Example:
        >>> task = get_task(task_id="fibonacci")
        >>> expected = get_expected_outputs(task)
        >>> expected[0]
        0
        >>> expected[10]
        55
    """
    expected_outputs = {}
    for tc in task["test_cases"]:
        input_val = tc["input"]
        # For tuple inputs (like binary_search), use the first element as key
        # since the code should return a dict with first arg as keys
        if isinstance(input_val, tuple):
            # For functions with multiple args, we expect the code to handle them specially
            # For now, just use the tuple as a string key
            key = str(input_val)
        else:
            key = input_val
        expected_outputs[key] = tc["expected"]
    return expected_outputs
