from __future__ import annotations
from dataclasses import asdict, dataclass
from queue import Queue
import threading
from typing import Type
from llm_core.parsers import BaseParser
from celi_framework.core.job_description import JobDescription, ToolImplementations
from celi_framework.core.monitor import MonitoringAgent
from celi_framework.core.mt_factory import MasterTemplateFactory
from celi_framework.core.processor import ProcessRunner
from celi_framework.utils.codex import MongoDBUtilitySingleton
from celi_framework.utils.llmcore_utils import ParserFactory, new_parser_factory
from celi_framework.utils.log import app_logger


@dataclass
class Directories:
    output_dir: str
    drafts_dir: str
    evaluations_dir: str

    @staticmethod
    def create(output_dir: str) -> Directories:
        return Directories(
            output_dir=output_dir,
            drafts_dir=f"{output_dir}/drafts",
            evaluations_dir=f"{output_dir}/evaluations",
        )


@dataclass
class MongoDBConfig:
    db_url: str
    db_name: str
    external_db: bool


@dataclass
class CELIConfig:
    mongo_config: MongoDBConfig
    directories: Directories
    job_description: JobDescription
    tool_implementations: ToolImplementations
    parser_cls: Type[BaseParser]
    parser_model_name: str
    llm_cache: bool
    use_monitor: bool


def run_celi(celi_config: CELIConfig):
    app_logger.debug("Beginning document generation")
    update_queue = Queue()

    mt = MasterTemplateFactory(
        job_desc=celi_config.job_description,
        schema=celi_config.tool_implementations.get_schema(),
    )

    codex = MongoDBUtilitySingleton(**asdict(celi_config.mongo_config))
    parser_factory = new_parser_factory(
        celi_config.parser_cls,
        celi_config.parser_model_name,
        cache=celi_config.llm_cache,
        codex=codex,
    )

    process_runner = ProcessRunner(
        master_template=mt,
        codex=codex,
        parser_factory=parser_factory,
        tool_implementations=celi_config.tool_implementations,
        drafts_dir=celi_config.directories.drafts_dir,
        update_queue=update_queue,
        llm_cache=celi_config.llm_cache,
    )

    # Start ProcessRunner in its own thread
    process_runner_thread = threading.Thread(target=process_runner.run, daemon=True)
    process_runner_thread.start()
    threads = [process_runner_thread]

    if celi_config.use_monitor:
        # # Start MonitoringAgent in its own thread
        monitoring_agent = MonitoringAgent(
            codex=codex,
            update_queue=update_queue,
            parser_factory=parser_factory,
            evaluations_dir=celi_config.directories.evaluations_dir,
        )

        monitoring_agent_thread = threading.Thread(
            target=monitoring_agent.start, daemon=True
        )
        monitoring_agent_thread.start()
        threads.append(monitoring_agent_thread)

    # Wait for threads to finish
    [_.join() for _ in threads]
    app_logger.info("Threads completed. Exiting.")
    return process_runner.draft_doc
