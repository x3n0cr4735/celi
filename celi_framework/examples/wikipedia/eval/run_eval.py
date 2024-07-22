import asyncio
import copy
import json
import logging
import os
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
        draft_doc = "\n".join(f"{k}\n{v}" for k, v in sorted(draft_doc_sections.items(), key=lambda x: int(x[0])))
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

    prompt = f"""Your job is to compare a generated document versus a human-created reference.  Give a score of 0-100 
    based on how well the LLM created document matches the original.  0 indicates the document is useless, and 100 
    indicates that you'd prefer the generated document to the reference.  Begin your response by providing a reason and 
    then have the final line print out the integer score between 0 adn 100.
    
    <ExampleOutput>
    The document covers all the basic information adn is structured similarly, but lacks the compelling narrative
    of the original 
    
    SCORE: 75
    </ExampleOutput>
    
    <GeneratedDocument>{generated_doc}</GeneratedDocument> 
    <ReferenceDocument>{ground_truth_doc}</ReferenceDocument>
    """

    result = await quick_ask_async(prompt, "gpt-4o")

    eval_score_list = [int(line[6:]) for line in result.split('\n') if line.startswith("SCORE: ")]
    assert len(eval_score_list) == 1, f"Eval didn't return valid output: {result}"
    eval_score = eval_score_list[0]
    return {"eval_score": eval_score, 'eval_rationale': result}


if __name__ == "__main__":
    setup_logging()
    celi_config = get_celi_config()

    test_sets = read_json_from_file(Path(__file__).parent / "test_sets.json")
    results = [
        {"test_set": test_set_name, **asyncio.run(run_test(celi_config, example, target), debug=True)}
        for test_set_name, test_set in test_sets.items()
        for example in test_set
        for target in test_set
        if example != target
    ]
    ret = pd.DataFrame.from_records(results)
    print(ret)
    average_eval_scores = ret.groupby('test_set')['eval_score'].mean()
    print(average_eval_scores)
    print(f"Average eval score: {round(ret['eval_score'].mean(),2)}")

