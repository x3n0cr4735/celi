import logging
import os
import traceback
from dataclasses import dataclass
from os.path import dirname
from typing import Dict

import pandas as pd

from celi_framework.core.job_description import ToolImplementations
from celi_framework.utils.utils import format_toc

logger = logging.getLogger(__name__)


@dataclass
class HumanEvalTools(ToolImplementations):

    def __post_init__(self):
        test_file = os.path.join(dirname(__file__), 'test.csv')
        self.tests = pd.read_csv(test_file, index_col="task_id")

    # Retrieves the top level schema for the doc.  Ignore subsections as they change page to page.
    def get_schema(self) -> Dict[str, str]:
        return {k:v for k,v in zip(self.tests.index, self.tests['entry_point'])}

    def get_prompt(self, task_id: str) -> str:
        """Returns the prompt for the given task.

        Args:
            task_id (str): The task id for which to get the prompt.  An example taskId is: "HumanEval/10"

        Returns:
            str - The prompt for this question.
        """
        return self.tests.loc[task_id, "prompt"]

    def run_tests(self, task_id: str, func: str):
        """Runs the tests on a HumanEval example.

        Args:
            task_id (str): The task id for which to run tests.
            func (str): Code for the implemented function
        """
        local_namespace = {}

        # Define the function
        logger.debug(f"Evaluating {task_id}:\n{func}")
        try:
            exec(func, local_namespace, local_namespace)
        except Exception as e:
            return f"There was an error in your function:\n{e}"

        # # Define the check function in the same namespace
        # exec(example["test"][0], {}, local_namespace)

        # Now run the checks
        test_func = self.tests.loc[task_id, "test"]
        entry_point = self.tests.loc[task_id, "entry_point"]
        logger.debug(f"locals are {local_namespace.keys()}")
        try:
            exec(f'{test_func}\ncheck({entry_point})', local_namespace, local_namespace)
        except AssertionError as e:
            tb = traceback.extract_tb(e.__traceback__)
            last_tb = tb[-1]
            if last_tb.name == 'check':
                line = test_func.split('\n')[last_tb.lineno]
                return f"The function failed a check:\n{line}"
            else:
                return f"An assert failed in the function.\n{e}\n{tb}"
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            return f"An exception was thrown:\n{e}\n{tb}"
