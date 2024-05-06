import logging
import os
from functools import lru_cache
from os.path import dirname

import pandas as pd

from celi_framework.examples.human_eval.tools import HumanEvalTools

logger = logging.getLogger(__name__)


@lru_cache()
def get_tests():
    test_file = os.path.join(dirname(__file__), 'test.csv')
    return pd.read_csv(test_file)


def test_get_prompt():
    tools = HumanEvalTools()
    prompt = tools.get_prompt("HumanEval/0")
    assert prompt == '''from typing import List


def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """ Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    """
'''


def test_run_tests():
    """Run all the tests in HumanEval."""
    tests = get_tests()
    tools = HumanEvalTools()
    for ix in range(tests.shape[0]):
        example = tests.iloc[ix,:]
        code = example['prompt']+'\n'+example['canonical_solution']
        assert tools.run_tests(example['task_id'], code) is None


def test_run_tests_invalid_code():
    tests = get_tests()
    tools = HumanEvalTools()
    example = tests.iloc[0,:]
    code = example['prompt']+'\n    SYNTAX ERROR'
    ret = tools.run_tests(example['task_id'], code)
    assert ret == "There was an error in your function:\ninvalid syntax (<string>, line 13)"


def test_run_tests_incorrect_solution():
    tests = get_tests()
    tools = HumanEvalTools()
    example = tests.iloc[0,:]
    code = example['prompt']
    ret = tools.run_tests(example['task_id'], code)
    assert "assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.05) == False" in ret


def test_run_tests_exception_in_func():
    tests = get_tests()
    tools = HumanEvalTools()
    example = tests.iloc[0,:]
    code = example['prompt']+"\n    raise Exception('This is an exception')\n"
    ret = tools.run_tests(example['task_id'], code)
    assert "An exception was thrown" in ret


def test_run_tests_assertion_in_func():
    tests = get_tests()
    tools = HumanEvalTools()
    example = tests.iloc[0,:]
    code = example['prompt']+"\n    raise AssertionError('This is an exception')\n"
    ret = tools.run_tests(example['task_id'], code)
    assert "An assert failed in the function" in ret


def test_timeout():
    tests = get_tests()
    tools = HumanEvalTools()
    example = tests.iloc[0,:]
    code = example['prompt']+"\n    while True:\n        pass\n"
    ret = tools.run_tests(example['task_id'], code)
    assert "Function execution timed out" in ret
