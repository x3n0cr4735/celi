import datetime
import json
import logging
import multiprocessing
import os
import traceback
from dataclasses import dataclass
from os.path import dirname
from typing import Dict, Optional

import pandas as pd
from pydantic import BaseModel

from celi_framework.core.job_description import (
    ToolImplementations,
)
from celi_framework.utils.utils import read_json_from_file, write_string_to_file

logger = logging.getLogger(__name__)


class SafeExecException(Exception):
    pass


class HumanEvalInit(BaseModel):
    drafts_dir: str = "target/celi_output/drafts"
    single_example: Optional[str] = None  # "HumanEval/129"


@dataclass
class HumanEvalTools(ToolImplementations):
    drafts_dir: str = "target/celi_output/drafts"
    single_example: Optional[str] = None  # "HumanEval/129"

    def __post_init__(self):
        os.makedirs(self.drafts_dir, exist_ok=True)
        self.draft_doc = f"{self.drafts_dir}/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        logger.info(f"Writing output to {self.draft_doc}")

        test_file = os.path.join(dirname(__file__), "test.csv")
        self.tests = pd.read_csv(test_file, index_col="task_id")

        self.last_func = None
        self.last_test_func = None
        self.last_task_id = None

    def get_schema(self) -> Dict[str, str]:
        ret = {
            k: v
            for k, v in zip(self.tests.index, self.tests["entry_point"])
            if self.single_example is None or k == self.single_example
        }
        return ret

    def get_prompt(self, task_id: str) -> str:
        """Returns the prompt for the given task.

        Args:
            task_id (str): The task id, including the "HumanEval/" prefix.  For example, "HumanEval/10".

        Returns:
            str - The prompt for this question.  This will be a function signature and doc string.
        """
        return self.tests.loc[task_id, "prompt"]

    def save_final_output(self, task_id: str, func: str, test_func: str):
        """Writes the final output for the problem.

        Args:
            task_id (str): The HumanEval problem identifier
            func (str): The body of the function indented by 4 spaces (without the function signature).
            test_func (str): The full definition of the `check` function (including the `def check` line)

        This must be called before calling pop_context and moving on to the next problem.  The most recently submitted
        code will be used.
        """
        logger.info(
            f"Completed problem {task_id}.  Code is:\n{func}\nTests are:\n{test_func}",
            extra={"color": "orange"},
        )

        logger.info(f"Adding section {task_id} to {self.draft_doc}")
        try:
            current = read_json_from_file(self.draft_doc)
        except FileNotFoundError:
            current = {}
        current[task_id] = {
            "func": func,
            "tests": test_func,
        }
        write_string_to_file(json.dumps(current, indent=2), self.draft_doc)

    def _run_official_tests(self, task_id: str, func: str):
        """Runs the tests on a HumanEval example.

        Args:
            task_id (str): The task id for which to run tests.
            func (str): Code for the implemented function
        """
        # logger.debug(f"Running official test {task_id}")
        test_func = self.tests.loc[task_id, "test"]
        return self.run_tests(task_id, func, test_func)

    def run_tests(self, task_id: str, func: str, test_func: str):
        self.last_task_id = task_id
        self.last_func = func
        self.last_test_func = test_func

        result_queue = multiprocessing.Queue()
        p = multiprocessing.Process(
            target=self._run_tests_sandboxed,
            args=[task_id, func, test_func, result_queue],
        )
        p.start()

        try:
            # Wait for the process to finish, with a timeout of 3 seconds
            p.join(timeout=3)
            if p.is_alive():
                # If the process is still alive after 3 seconds, terminate it
                p.terminate()
                p.join()
                return "Function execution timed out"
            result = result_queue.get()
            return result
        finally:
            result_queue.close()

    def _run_tests_sandboxed(
        self,
        task_id: str,
        func: str,
        test_func: str,
        result_queue: multiprocessing.Queue,
    ):
        ret = self._execute_test(task_id, func, test_func)
        logger.info(f"Result is {ret}")
        result_queue.put(ret)

    def _execute_test(self, task_id: str, func: str, test_func: str):
        local_namespace = {}
        entry_point = self.tests.loc[task_id, "entry_point"]

        # Define the function
        logger.debug(f"Evaluating {task_id}:\n{func}\n{test_func}")

        def safe_exec(code: str, error_prefix: str):
            try:
                exec(code, local_namespace, local_namespace)
            except AssertionError as e:
                tb = traceback.extract_tb(e.__traceback__)
                last_tb = tb[-1]
                if last_tb.name == "check":
                    line = test_func.split("\n")[last_tb.lineno - 1]
                    raise SafeExecException(
                        f"The function failed a check:\n{e}\n{line}"
                    )
                else:
                    raise SafeExecException(
                        f"An assert failed in the function.\n{e}\n{tb}"
                    )
            except Exception as e:
                tb = traceback.extract_tb(e.__traceback__)
                raise SafeExecException(f"{error_prefix}:\n{e}\n{tb}")

        try:
            safe_exec(func, "There was an error in your function definition")

            if "check" in local_namespace:
                return "You defined a 'check' function in your function definition.  That isn't allowed.  Use a different name"
            if entry_point not in local_namespace:
                return f"Your function didn't have the right entry point name.  Expected {entry_point}, but got {local_namespace.keys()}"

            safe_exec(test_func, "There was an error in your test function definition")

            if "check" not in local_namespace:
                return "Your test code didn't define a 'check' function."

            # Now run the checks
            safe_exec(f"check({entry_point})", "An exception was thrown")
        except SafeExecException as e:
            return e.args[0]
