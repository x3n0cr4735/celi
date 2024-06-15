# TODO -> Put stuff in utils/common where it makes sense
from celi_framework.logging_setup import setup_logging
setup_logging()

import sys
import os
from dotenv import load_dotenv
load_dotenv()
ROOT_DIR = os.getenv("ROOT_DIR")
sys.path.append(ROOT_DIR)

import argparse
import copy
import logging.config

from celi_framework.core.runner import CELIConfig, Directories, MongoDBConfig, run_celi
from celi_framework.main import instantiate_with_argparse_args
from celi_framework.utils.utils import get_obj_by_name
from celi_framework.utils.cli import str2bool
from tools import GREToolImplementations
from job_description import job_description
from run_gpt_alone import run_gpt



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

# TODO: You have a bunch of print statements in here. Change them to loggers
def runner():
    config = get_config()
    logger.info("Running narratives app <-----")
    config = copy.deepcopy(config)
    config.tool_implementations = GREToolImplementations()

    # Pass shutdown_flag to run_celi
    for i in range(3):
        run_celi(config)

    run_gpt()

if __name__ == "__main__":
    runner()  # Invoke celi runner functions after preprocessing completes
