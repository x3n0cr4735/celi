"""
This Python script establishes a multithreaded environment for document processing and monitoring within a given system. It is designed to efficiently manage and monitor the processing of documents by utilizing a combination of custom classes, threading, and resource management techniques. The script integrates several components, including:

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

import argparse
import inspect
import json
import logging.config
import os
from typing import Type

from dotenv import load_dotenv

from celi_framework.core.runner import CELIConfig, run_celi
from celi_framework.logging_setup import setup_logging
from celi_framework.utils.cli import bool_opt
from celi_framework.utils.utils import get_obj_by_name, read_json_from_file

logger = logging.getLogger(__name__)


def get_config():
    load_dotenv("./.env")

    parser = setup_standard_args()
    parser.add_argument(
        "--tool-config-json",
        type=str,
        default=os.getenv("TOOL_CONFIG_JSON"),
        help="Path to a JSON file which will be used to configure the tools.  See --tool-config for more information."
        "This option allows the JSON to be specified in a file instead of the command line.  If --tool-config is"
        "also specified, this option will be ignored.",
    )
    parser.add_argument(
        "--tool-config",
        type=str,
        default=os.getenv("TOOL_CONFIG"),
        help="This should be a JSON string which will be used to configure the tools.  The JSON will be converted into "
        "an object, which will be passed as keyword arguments to the tool implementation.  The specific values "
        "required (if any) will depend on the tool implementations.  For the HumanEval tools, a single argument can be "
        """passed that indicates only one example should be run.  --tool-config='{"single_example":"HumanEval/3"}' """
        "This option overrides --tool-config-json if both are set.",
    )
    args = parser.parse_args()
    celi_config = parse_standard_args(args)

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
    elif args.tool_config:
        tool_config = json.loads(args.tool_config)
    else:
        tool_config = {}

    celi_config.tool_implementations = (
        celi_config.job_description.tool_implementations_class(**tool_config)
    )

    return celi_config


def parse_standard_args(args):
    if args.openai_api_key:
        os.environ["OPENAI_API_KEY"] = args.openai_api_key

    return CELIConfig(  # noqa: F821
        job_description=get_obj_by_name(args.job_description),
        tool_implementations=None,
        llm_cache=not args.no_cache,
        simulate_live=args.simulate_live,
        primary_model_name=args.primary_model_name,
        model_url=args.model_api_url,
        max_tokens=args.max_tokens,
    )


def setup_standard_args():
    parser = argparse.ArgumentParser(
        description="All of the options below can also be set as environment variables"
        "(using the capitalized names), or in a local .env file."
    )

    parser.add_argument(
        "--openai-api-key",
        type=str,
        default=None,
        help="Your OpenAI API key.  For security reasons, it is preferrable to set this as an environment variable "
        "rather than passing it on the command line.  If you are serving your own models using --model-api-url, this will be the API key"
        "passed in the calls to those models.  The specific value required will depend on the server.",
    )
    parser.add_argument(
        "--primary-model-name",
        type=str,
        default=os.getenv("PRIMARY_LLM", "gpt-4-0125-preview"),
        help="Name of the primary LLM to use.  This will be passed in the OpenAI LLM calls.  If you are using OpenAI, "
        "you can use any of the OpenAI model names found at https://platform.openai.com/docs/models.  If you are"
        "serving your own models (using --model-api-url), you can use any name that the server supports.  ",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=os.getenv("MAX_TOKENS", 4096),
        help="The maximum number of tokens to be included in any one request.  This is a comprehensive number, it "
        "includes the tokens in the system message, chat history, and output response.  Setting this to a larger"
        "number than the default 4096 increases cost but allows for longer prompts and responses.  You may need to"
        "set this shorter if you are using a non-OpenAI model with a shorter context length.",
    )
    parser.add_argument(
        "--model-api-url",
        type=str,
        default=os.getenv("MODEL_API_URL", None),
        help="Sets the URL to use when making OpenAI LLM calls.  Leave this blank to use the normal OpenAI models.  If"
        "you are serving models locally using a server that implements the OpenAI API, you can set this to the "
        "URL for that server.  Several serving platforms support the OpenAI interface, including vLLM, NIMs, Ollama.",
    )
    parser.add_argument(
        "--job-description",
        type=str,
        default=os.getenv(
            "JOB_DESCRIPTION",
            "celi_framework.examples.human_eval.job_description.job_description",
        ),
        help="CELI requires a job description to know what task to run.  This parameter specifies the Python class name"
        " for the class containing the job description.  It must have JobDescription as a base class.  Several "
        "example job descriptions are provided within the celi_framework.examples module.",
    )
    bool_opt(
        parser,
        "--simulate-live",
        "SIMULATE_LIVE",
        "Set to true to add a delay to the LLM cache.  This simulates what a live run would look like even when cached LLM results are used",
    )
    bool_opt(parser, "--no-cache", "NO_CACHE", "Set to True to turn off LLM caching")
    return parser


def instantiate_with_argparse_args(args: argparse.Namespace, cls: Type):
    """Instantiates the given class, passing any args that match class members as keyword args."""
    init_signature = inspect.signature(cls.__init__)
    arg_names = [
        param_name
        for param_name in init_signature.parameters.keys()
        if param_name != "self"
    ]
    cls_args = {k: v for k, v in vars(args).items() if k in arg_names}
    return cls(**cls_args)


if __name__ == "__main__":
    setup_logging()
    logger.debug("Starting CELI")
    config = get_config()
    run_celi(config)
