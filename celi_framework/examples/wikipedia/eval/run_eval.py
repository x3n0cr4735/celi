import asyncio
import copy
import json
import logging
import os
import re
from pathlib import Path

import pandas as pd

from celi_framework.core.runner import CELIConfig, run_process_runner
from celi_framework.examples.wikipedia.loader import (
    format_content,
    load_content_from_wikipedia_url,
)
from celi_framework.examples.wikipedia.tools import WikipediaToolImplementations
from celi_framework.logging_setup import setup_logging
from celi_framework.main import get_celi_config
from celi_framework.utils.llms import quick_ask_async
from celi_framework.utils.utils import read_json_from_file

logger = logging.getLogger(__name__)


def page_name(url: str) -> str:
    return url.split("/")[-1]


async def run_test(celi_config: CELIConfig, example: str, target: str):
    logger.info(
        f"Running test with example: {page_name(example)} and target: {page_name(target)}"
    )
    dir = os.path.join("target/wikipedia_eval")
    os.makedirs(dir, exist_ok=True)
    result_file_name = f"{page_name(target)}_from_{page_name(example)}.json"
    eval_path = os.path.join(dir, result_file_name)
    if os.path.exists(eval_path):
        logger.info(f"Skipping test {result_file_name} as it already exists")
        return read_json_from_file(eval_path)
    else:
        config = copy.deepcopy(celi_config)
        from celi_framework.examples.wikipedia.job_description import job_description

        config.job_description = job_description
        config.tool_implementations = WikipediaToolImplementations(
            example, target, ignore_updates=True
        )
        await run_process_runner(config)
        logger.debug(f"Evaluating {result_file_name}")
        draft_doc_path = config.tool_implementations.draft_doc
        draft_doc_sections = read_json_from_file(draft_doc_path)
        draft_doc = "\n".join(
            f"{k}\n{v}"
            for k, v in sorted(draft_doc_sections.items(), key=lambda x: int(''.join(filter(str.isdigit, x[0]))))
        )
        result = await evaluate(draft_doc, target)
        logger.debug("Evaluation complete")
        result_out = {
            "example": page_name(example),
            "target": page_name(target),
            **result,
        }
        with open(eval_path.replace(".json", ".txt"), "wt") as f:
            logger.info(f"Writing draft and results to {eval_path}")
            f.write(draft_doc)
        with open(eval_path, "wt") as f:
            json.dump(result_out, f)
        return result_out


async def evaluate(generated_doc: str, target_url: str):
    target_dict, _ = load_content_from_wikipedia_url(
        target_url, include_references=False
    )
    ground_truth_doc = format_content(target_dict)

    prompt = f"""Your job is to compare a generated document versus a human-created reference.  Rate the document using
    an integer from 0-6 using the scale below.

    0 - Irrelevant: The AI document is completely off-topic or unusable.
    1 - Very Poor: Major errors or missing information make the document largely ineffective.
    2 - Insufficient: Significant elements are missing, and extensive revisions are needed.
    3 - Marginal: Meets the basic requirements but contains several deficiencies.
    4 - Satisfactory: Acceptable as a first draft but requires refinement.
    5 - Comparable: Matches the quality and completeness of the ground truth document.
    6 - Outstanding: Surpasses the ground truth in quality, detail, and presentation.
    Have the scores be discrete (no floats)

    Begin your response by providing a reason and then have the final line print out the integer score.
    
    <ExampleOutput>
    The document covers all the basic information adn is structured similarly, but lacks the compelling narrative
    of the original 
    
    SCORE: 3
    </ExampleOutput>
    
    <GeneratedDocument>{generated_doc}</GeneratedDocument> 
    <ReferenceDocument>{ground_truth_doc}</ReferenceDocument>
    """

    result = await quick_ask_async(prompt, "gpt-4o")

    eval_score_list = [
        int(re.sub(r"[^0-9]", "", line.split(" ")[-1]))
        for line in result.split("\n")
        if "SCORE:" in line
    ]
    assert len(eval_score_list) == 1, f"Eval didn't return valid output: {result}"
    eval_score = eval_score_list[0]
    return {"eval_score": eval_score, "eval_rationale": result}


if __name__ == "__main__":
    setup_logging()
    celi_config = get_celi_config()

    test_sets = read_json_from_file(Path(__file__).parent / "test_sets.json")
    results = [
        {
            "test_set": test_set_name,
            **asyncio.run(run_test(celi_config, example, target), debug=True),
        }
        for test_set_name, test_set in test_sets.items()
        for example in test_set
        for target in test_set
        if example != target
    ]
    ret = pd.DataFrame.from_records(results)
    print(ret)
    average_eval_scores = ret.groupby("test_set")["eval_score"].mean()
    print(average_eval_scores)
    print(f"Average eval score: {round(ret['eval_score'].mean(),2)}")
