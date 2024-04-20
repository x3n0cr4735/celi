"""
This Python script establishes a multi-threaded environment for document processing and monitoring within a given system. It is designed to efficiently manage and monitor the processing of documents by utilizing a combination of custom classes, threading, and resource management techniques. The script integrates several components, including:

- `ProcessRunner`: A class responsible for managing the processing pipeline of documents. It uses MongoDB for storage and retrieval of documents and employs a queue for managing updates.
- `MonitoringAgent`: A class tasked with monitoring the progress and status of document processing, ensuring that system performance is maintained and any issues are promptly addressed.
- `MongoDBUtilitySingleton`: A singleton class that provides a centralized connection to MongoDB, ensuring efficient data handling and retrieval.
- `Queue`: A thread-safe queue used for communication between the process runner and monitoring agent, facilitating efficient data exchange and task management.

Key features include:
- Threading: Utilizes Python's `threading` module to run document processing and monitoring tasks concurrently, improving system throughput and responsiveness.
- Memory Profiling: Employs the `memory_profiler` module to monitor and optimize memory usage, ensuring the application runs efficiently even under heavy load.
- Environment Configuration: Leverages `dotenv` for managing environment variables, allowing for flexible configuration of critical paths and parameters without hardcoding.

The script is structured to initiate and manage parallel threads dedicated to document processing and system monitoring, demonstrating an effective pattern for building scalable and responsive Python applications. By separating concerns into distinct threads and utilizing a shared queue for communication, it achieves a high degree of concurrency and efficiency in processing tasks.
"""

if __name__ == "__main__":
    # This has to be run before any loggers are created.
    from celi_framework.logging_setup import setup_logging

    setup_logging()

import argparse
from dataclasses import asdict
import inspect
import logging
import logging.config
import os
from typing import Type

from dotenv import load_dotenv

from celi_framework.core.runner import CELIConfig, Directories, MongoDBConfig, run_celi
from celi_framework.utils.codex import MongoDBUtilitySingleton
from celi_framework.utils.llmcore_utils import new_parser_factory
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
        "--external-db",
        "EXTERNAL_DB",
        "Set to True if using an existing mongo server.",
    )
    parser.add_argument(
        "--job-description",
        type=str,
        default=os.getenv(
            "JOB_DESCRIPTION",
            "celi_framework.examples.wikipedia.job_description.job_description",
        ),
        help="Fully qualified name of a JobDescription instance with information on the task to perform",
    )
    parser.add_argument(
        "--tool-config-json",
        type=str,
        default=os.getenv("TOOL_CONFIG_JSON"),
        help="Path to a JSON file which will be used to instantiate the tool implementation.",
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
        "--no-monitor",
        "NO_MONITOR",
        "Set to True to turn off the monitoring thread",
    )

    args = parser.parse_args()

    directories = Directories.create(args.output_dir)
    mongo_config = instantiate_with_argparse_args(args, MongoDBConfig)

    job_description = get_obj_by_name(args.job_description)

    # If the tool_config_json file doesn't exist, try to find it relative to the root of the installed package.
    # This allows examples packaged with celi to work correctly.
    if args.tool_config_json:
        if os.path.exists(args.tool_config_json):
            tool_config_json = args.tool_config_json
        else:
            # Find the root of the installed package
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            tool_config_json = os.path.join(root_dir, args.tool_config_json)
            if not os.path.exists(tool_config_json):
                raise FileNotFoundError(
                    f"Could not find {args.tool_config_json} or {tool_config_json}"
                )
        tool_config = read_json_from_file(tool_config_json)
    else:
        tool_config = {}

    tool_implementations = job_description.tool_implementations_class(**tool_config)

    llm_cache = not args.no_cache
    use_monitor = not args.no_monitor

    # Instantiate the class, passing parser_model as a parameter
    parser_cls = get_obj_by_name(args.parser_model_class)

    return CELIConfig(  # noqa: F821
        mongo_config=mongo_config,
        directories=directories,
        job_description=job_description,
        tool_implementations=tool_implementations,
        parser_cls=parser_cls,
        parser_model_name=args.parser_model_name,
        llm_cache=llm_cache,
        use_monitor=use_monitor,
    )


def instantiate_with_argparse_args(args: argparse.Namespace, cls: Type):
    """Instantiates the given class, passing any args that match class members as keyword args."""
    init_signature = inspect.signature(cls.__init__)
    arg_names = [
        param_name
        for param_name in init_signature.parameters.keys()
        if param_name != "self"
    ]
    # cls.__annotations__
    cls_args = {k: v for k, v in vars(args).items() if k in arg_names}
    return cls(**cls_args)


if __name__ == "__main__":
    logger.debug("Starting CELI")
    config = get_config()
    run_celi(config)
