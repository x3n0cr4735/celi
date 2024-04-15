from celi_framework.logging_setup import setup_logging

setup_logging()

import json
import argparse
import copy
import logging
import logging.config
import os

from functools import lru_cache
from pathlib import Path
from typing import List

import pandas as pd
from dotenv import load_dotenv
from evaluate import load

from celi_framework.core.runner import CELIConfig, Directories, MongoDBConfig, run_celi
from celi_framework.examples.wikipedia.job_description import job_description
from celi_framework.examples.wikipedia.loader import (
    format_content,
    load_content_from_wikipedia_url,
)
from celi_framework.examples.wikipedia.tools import WikipediaToolImplementations
from celi_framework.main import instantiate_with_argparse_args
from celi_framework.utils.utils import get_obj_by_name, read_json_from_file, str2bool

logger = logging.getLogger(__name__)


def get_config():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run the document generator.")

    def bool_opt(opt: str, env_var: str, help: str):
        parser.add_argument(
            opt,
            action="store_true",
            default=str2bool(os.getenv(env_var, "False")),
            help=help,
        )

    parser.add_argument(
        "--output-dir",
        type=str,
        default=os.getenv("OUTPUT_DIR"),
        help="Output directory path",
    )
    parser.add_argument(
        "--db-url",
        type=str,
        default=os.getenv("DB_URL", "mongodb://localhost:27017/"),
        help="Mongo DB URL",
    )
    parser.add_argument(
        "--db-name", type=str, default="celi", help="Mongo database name"
    )
    bool_opt(
        "--external-db", "EXTERNAL_DB", "Set to True if using an existing mongo server."
    )
    parser.add_argument(
        "--parser-model-class",
        type=str,
        default=os.getenv("PARSER_MODEL_CLASS", "llm_core.parsers.LLaMACPPParser"),
    )
    parser.add_argument(
        "--parser-model-name",
        type=str,
        default=os.getenv("PARSER_MODEL_NAME", "mixtral-8x7b-v0.1.Q5_K_M.gguf"),
    )
    bool_opt("--no-cache", "NO_CACHE", "Set to True to turn off LLM caching")
    bool_opt(
        "--no-monitor", "NO_MONITOR", "Set to True to turn off the monitoring thread"
    )

    args = parser.parse_args()

    directories = Directories.create(args.output_dir)
    mongo_config = instantiate_with_argparse_args(args, MongoDBConfig)

    llm_cache = not args.no_cache
    use_monitor = not args.no_monitor

    # Instantiate the class, passing parser_model as a parameter
    parser_cls = get_obj_by_name(args.parser_model_class)

    return CELIConfig(  # noqa: F821
        mongo_config=mongo_config,
        directories=directories,
        job_description=job_description,
        tool_implementations=None,
        parser_cls=parser_cls,
        parser_model_name=args.parser_model_name,
        llm_cache=llm_cache,
        use_monitor=use_monitor,
    )


def page_name(url: str) -> str:
    return url.split("/")[-1]


def run_test(config: CELIConfig, example: str, target: str):
    logger.info(
        f"Running test with example: {page_name(example)} and target: {page_name(target)}"
    )
    dir = os.path.join(config.directories.output_dir + "/wikipedia_eval")
    os.makedirs(dir, exist_ok=True)
    result_file_name = f"{page_name(target)}_from_{page_name(example)}.json"
    eval_path = os.path.join(dir, result_file_name)
    if os.path.exists(eval_path):
        logger.info(f"Skipping test {result_file_name} as it already exists")
        return read_json_from_file(eval_path)
    else:
        config = copy.deepcopy(config)
        config.tool_implementations = WikipediaToolImplementations(
            example, target, ignore_updates=True
        )
        draft_doc_path = run_celi(config)
        draft_doc_sections = read_json_from_file(draft_doc_path)
        draft_doc = "\n".join(f"{k}\n{v}" for k, v in draft_doc_sections.items())
        result = evaluate(draft_doc, target)
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


def run_test_set(config: CELIConfig, test_set_name: str, test_set: List[str]):
    logger.info(f"Running test set: {test_set_name}")
    return [
        {"test_set": test_set_name, **run_test(config, example, target)}
        for example in test_set
        for target in test_set
        if example != target
    ]


def evaluate(generated_doc: str, target_url: str):
    bertscore = load_eval_model()
    target_dict, _ = load_content_from_wikipedia_url(
        target_url, include_references=False
    )
    ground_truth_doc = format_content(target_dict)

    results = bertscore.compute(
        predictions=[generated_doc],
        references=[ground_truth_doc],
        model_type="distilbert-base-uncased",
    )
    return results


@lru_cache()
def load_eval_model():
    return load("bertscore")


if __name__ == "__main__":
    config = get_config()

    test_sets = read_json_from_file(Path(__file__).parent / "test_sets.json")
    result = [
        _
        for test_set_name, test_set in test_sets.items()
        for _ in run_test_set(config, test_set_name, test_set)
    ]
    ret = pd.DataFrame.from_records(result)
    print(ret)
