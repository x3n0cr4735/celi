from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass
from queue import Queue
from typing import Type, Optional

from llm_core.parsers import BaseParser

from celi_framework.core.job_description import JobDescription, ToolImplementations
from celi_framework.core.monitor import MonitoringAgent
from celi_framework.core.mt_factory import MasterTemplateFactory
from celi_framework.core.processor import ProcessRunner
from celi_framework.utils.codex import MongoDBUtilitySingleton
from celi_framework.utils.llmcore_utils import new_parser_factory
from celi_framework.utils.log import app_logger


@dataclass
class Directories:
    output_dir: str
    evaluations_dir: str

    @staticmethod
    def create(output_dir: str) -> Directories:
        return Directories(
            output_dir=output_dir,
            evaluations_dir=f"{output_dir}/evaluations",
        )


@dataclass
class MongoDBConfig:
    db_url: str
    db_name: str
    external_db: bool


@dataclass
class CELIConfig:
    mongo_config: Optional[MongoDBConfig]
    directories: Directories
    job_description: JobDescription
    tool_implementations: Optional[ToolImplementations]
    parser_cls: Type[BaseParser]
    parser_model_name: str
    llm_cache: bool
    use_monitor: bool
    primary_model_name: str


def run_celi(celi_config: CELIConfig):
    app_logger.debug("Beginning document generation")
    update_queue = Queue()

    mt = MasterTemplateFactory(
        job_desc=celi_config.job_description,
        schema=celi_config.tool_implementations.get_schema(),
    )

    codex = MongoDBUtilitySingleton(**asdict(celi_config.mongo_config))

    process_runner = ProcessRunner(
        master_template=mt,
        codex=codex,
        tool_implementations=celi_config.tool_implementations,
        llm_cache=celi_config.llm_cache,
        primary_model_name=celi_config.primary_model_name,
    )

    monitoring_agent = None
    if celi_config.use_monitor:
        # Start MonitoringAgent in its own thread
        parser_factory = new_parser_factory(
            celi_config.parser_cls,
            celi_config.parser_model_name,
            cache=celi_config.llm_cache,
            codex=codex,
        )
        monitoring_agent = MonitoringAgent(
            codex=codex,
            update_queue=update_queue,
            parser_factory=parser_factory,
            evaluations_dir=celi_config.directories.evaluations_dir,
        )
    asyncio.run(_await_agents(process_runner, monitoring_agent))


async def _await_agents(
    process_runner: ProcessRunner, monitoring_agent: MonitoringAgent
):
    tasks = [process_runner.run()]
    if monitoring_agent:
        tasks.append(monitoring_agent.start())
    await asyncio.gather(*tasks)
