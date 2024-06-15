# Run base GPT-4 with our prompts and see how it performs:
import asyncio
import logging

from dotenv import load_dotenv

from celi_framework.examples.human_eval.tools import HumanEvalTools
from celi_framework.logging_setup import setup_logging
from celi_framework.utils.llms import ask_split
from celi_framework.utils.utils import save_json

logger = logging.getLogger(__name__)

system_prompt = """
You are an expert at Python coding challenges.

You will be give a prompt which is a Python function signature and doc string.  Your job is to draft the function.

Think through the problem and develop an initial set of test cases that will be used to check the logic for your 
function.  Think through edge cases and different types of inputs that might be passed to the function.  Once you 
have the test cases, you can implement the function.

When you are done, indicate your final output with a blank line that says "FINAL OUTPUT:".  Your final output should
be just the function body, without the function signature, indented by 4 spaces.  No text should follow the function 
body.

For example.  If the prompt is;
def add(a: int, b: int) -> int:
    "Add two numbers"

Then your response would be:

Notes from you thinking out the solution step by step.
FINAL OUTPUT:
    return a+b
"""

setup_logging()
load_dotenv()
tools = HumanEvalTools()


async def run_gpt(id):
    ret = await ask_split(
        system_message=system_prompt,
        user_prompt=tools.tests.loc[id, "prompt"],
        model_name="gpt-4o",
    )
    response = ret.message.content
    delimiter = "FINAL OUTPUT:\n"
    parts = response.split(delimiter)
    if len(parts) < 2:
        logger.error(f"Missing final output delimiter in response: {response}")
        return None
    lines = parts[1].split("\n")
    if lines[0] == "```python":
        lines = lines[1:-1]
    joined = "\n".join(lines)

    return {"func": joined}


async def main():
    tasks = {_: run_gpt(_) for _ in tools.tests.index.values}
    results = await asyncio.gather(*tasks.values())
    result_dict = dict(zip(tasks.keys(), results))
    result_dict = {k: v for k, v in result_dict.items() if v is not None}
    save_json(result_dict, "gpt_only_example.json")


asyncio.run(main())
