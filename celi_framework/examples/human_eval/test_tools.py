import logging
import os
from functools import lru_cache
from os.path import dirname

import pandas as pd

from celi_framework.examples.human_eval.tools import HumanEvalTools

logger = logging.getLogger(__name__)


@lru_cache()
def get_tests():
    test_file = os.path.join(dirname(__file__), "test.csv")
    return pd.read_csv(test_file)


def test_get_prompt():
    tools = HumanEvalTools()
    prompt = tools.get_prompt("HumanEval/0")
    assert (
        prompt
        == '''from typing import List


def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """ Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    """
'''
    )


def test_run_tests():
    """Run all the tests in HumanEval."""
    tests = get_tests()
    tools = HumanEvalTools()
    for ix in range(tests.shape[0]):
        example = tests.iloc[ix, :]
        code = example["prompt"] + "\n" + example["canonical_solution"]
        assert tools._run_official_tests(example["task_id"], code) is None


def test_run_tests_invalid_code():
    tests = get_tests()
    tools = HumanEvalTools()
    example = tests.iloc[0, :]
    code = example["prompt"] + "\n    SYNTAX ERROR"
    ret = tools._run_official_tests(example["task_id"], code)
    assert (
        "There was an error in your function definition:\ninvalid syntax (<string>, line 13)"
        in ret
    )


def test_run_tests_incorrect_solution():
    tests = get_tests()
    tools = HumanEvalTools()
    example = tests.iloc[0, :]
    code = example["prompt"]
    ret = tools._run_official_tests(example["task_id"], code)
    assert "assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3) == True" in ret


def test_run_tests_exception_in_func():
    tests = get_tests()
    tools = HumanEvalTools()
    example = tests.iloc[0, :]
    code = example["prompt"] + "\n    raise Exception('This is an exception')\n"
    ret = tools._run_official_tests(example["task_id"], code)
    assert "An exception was thrown" in ret


def test_run_tests_assertion_in_func():
    tests = get_tests()
    tools = HumanEvalTools()
    example = tests.iloc[0, :]
    code = example["prompt"] + "\n    raise AssertionError('This is an exception')\n"
    ret = tools._run_official_tests(example["task_id"], code)
    assert "An assert failed in the function" in ret


def test_timeout():
    tests = get_tests()
    tools = HumanEvalTools()
    example = tests.iloc[0, :]
    code = example["prompt"] + "\n    while True:\n        pass\n"
    ret = tools._run_official_tests(example["task_id"], code)
    assert "Function execution timed out" in ret


def test_failure():
    func = 'from typing import List\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n    """ Check if in given list of numbers, are any two numbers closer to each other than\n    given threshold.\n    """\n    for i in range(len(numbers)):\n        for j in range(i + 1, len(numbers)):\n            if abs(numbers[i] - numbers[j]) < threshold:\n                return True\n    return False'
    task_id = "HumanEval/0"
    test_func = 'def check(candidate):\n    # Test case 1: Numbers far apart\n    assert candidate([1.0, 2.0, 3.0], 0.5) == False, "Test case 1 failed"\n    \n    # Test case 2: Numbers closer than threshold\n    assert candidate([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3) == True, "Test case 2 failed"\n    \n    # Test case 3: Empty list\n    assert candidate([], 0.5) == False, "Test case 3 failed"\n    \n    # Test case 4: All elements the same\n    assert candidate([2.0, 2.0, 2.0], 0.1) == True, "Test case 4 failed"\n    \n    # Test case 5: Negative numbers\n    assert candidate([-1.0, -1.5, -2.0], 0.4) == True, "Test case 5 failed"\n    \n    # Test case 6: Numbers close to threshold\n    assert candidate([0.1, 0.2, 0.4], 0.1) == False, "Test case 6 failed"'
    tools = HumanEvalTools()
    ret = tools.run_tests(task_id, func, test_func)
    assert "Test case 5 failed" in ret
    assert "assert candidate([-1.0, -1.5, -2.0], 0.4) == True" in ret
