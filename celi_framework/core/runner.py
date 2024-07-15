from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional

from celi_framework.core.job_description import JobDescription, ToolImplementations
from celi_framework.core.mt_factory import MasterTemplateFactory
from celi_framework.core.processor import ProcessRunner
from celi_framework.utils.llm_cache import enable_llm_caching, get_celi_llm_cache
from celi_framework.utils.log import app_logger
from celi_framework.utils.token_counters import TokenCounter


@dataclass
class CELIConfig:
    job_description: JobDescription
    tool_implementations: Optional[ToolImplementations]
    llm_cache: bool
    primary_model_name: str
    max_tokens: int
    model_url: Optional[str]
    simulate_live: bool = False
    token_budget: int = 0


def run_celi(celi_config: CELIConfig):
    """
    Runs the CELI process using the provided configuration.

    Args:
        celi_config (CELIConfig): The configuration object for the CELI process.

    Returns:
        None

    Raises:
        None

    Notes:
        - This function runs the CELI process asynchronously using the event loop.
        - It cancels all pending tasks and waits for them to complete before closing the event loop.
    """
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_process_runner(celi_config))
    finally:
        pending_tasks = asyncio.all_tasks(loop)
        if pending_tasks:
            app_logger.debug(
                f"Pending tasks: {pending_tasks}",
            )
        for task in pending_tasks:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*pending_tasks, return_exceptions=True))
        loop.close()
    # Used to debug threading issues.
    # for thread in threading.enumerate():
    #     app_logger.debug(f"Thread {thread.name}: Daemon={thread.daemon}")
    #     stack = "".join(traceback.format_stack(sys._current_frames()[thread.ident]))
    #     app_logger.debug(f"Stack trace for thread {thread.name}:\n{stack}")


async def run_process_runner(celi_config):
    """
    A function that runs the CELI process with the given configuration.

    Parameters:
        celi_config: The configuration object containing job description, tool implementations, llm cache, primary model name, model url, max tokens, and token budget.

    Returns:
        None
    """
    app_logger.debug("Beginning CELI")
    try:
        mt = MasterTemplateFactory(
            job_desc=celi_config.job_description,
            schema=celi_config.tool_implementations.get_schema(),
        )

        process_runner = ProcessRunner(
            master_template=mt,
            tool_implementations=celi_config.tool_implementations,
            llm_cache=celi_config.llm_cache,
            primary_model_name=celi_config.primary_model_name,
            model_url=celi_config.model_url,
            max_tokens=celi_config.max_tokens,
            token_counter=TokenCounter(celi_config.token_budget),
        )

        if celi_config.llm_cache:
            enable_llm_caching(celi_config.simulate_live)

        await process_runner.run()
    finally:
        if get_celi_llm_cache():
            await get_celi_llm_cache().close()
