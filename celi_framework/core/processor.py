import asyncio
import logging
from typing import Dict, Optional

from celi_framework.core.celi_update_callback import CELIUpdateCallback
from celi_framework.core.job_description import (
    ToolImplementations,
    generate_tool_descriptions,
)
from celi_framework.core.mt_factory import MasterTemplateFactory
from celi_framework.core.section_processor import SectionProcessor
from celi_framework.utils.llms import ToolDescription
from celi_framework.utils.log import app_logger
from celi_framework.utils.token_counters import TokenCounter

logger = logging.getLogger(__name__)


class ProcessRunner:
    """
    The ProcessRunner manages the overall CELI job.  It's primary job is to manage all fo the different sections that
    need to be completed. Each section is completed independently by a SectionProcessor.

    The ProcessRunner handles waiting on the sections, which are usually run in parallel.  It also coordinates any human
    input coming in and callbacks going out.
    """

    def __init__(
        self,
        master_template: MasterTemplateFactory,
        tool_implementations: ToolImplementations,
        llm_cache: bool,
        primary_model_name: str,
        max_tokens: int,
        force_tool_every_n: int,
        callback: Optional[CELIUpdateCallback] = None,
        model_url: Optional[str] = None,
        token_counter: Optional[TokenCounter] = None,
        sequential: bool = False,
    ):
        self.primary_model_name = primary_model_name
        self.model_url = model_url
        self.max_tokens = max_tokens
        self.force_tool_every_n = force_tool_every_n
        self.token_counter = token_counter
        self.callback = callback
        self.sequential = sequential
        logger.info(f"Using {primary_model_name} as the primary LLM")

        self.master_template = master_template
        self.builtin_tool_descriptions = [
            ToolDescription(
                name="complete_section",
                description="Indicates that this section has been completed.  This function should not be called unless"
                " save_draft_section or some similar function has been called to store the section's output.  Calling "
                " this will trigger a review of the results and possibly a retry of the whole section.",
                parameters={
                    "type": "object",
                    "properties": {
                        "current_section_number": {
                            "type": "string",
                            "description": "The section being completed.",
                        }
                    },
                    "required": ["current_section_number"],
                },
            )
        ]
        self.llm_cache = llm_cache

        self.system_message = self.master_template.create_system_message()
        app_logger.info(
            f"System message created:\n{self.system_message}",
            extra={"color": "cyan"},
        )

        self.sections_to_be_completed = list(self.master_template.schema.keys())

        self.tool_implementations = tool_implementations
        self.tool_descriptions = generate_tool_descriptions(
            self.master_template.job_desc.tool_implementations_class
        )

    def get_schema(self) -> Dict[str, str]:
        return self.tool_implementations.get_schema()

    async def run(self):
        """
        Runs all sections of the document.
        """
        try:
            logger.info(
                f"Starting new run on {len(self.sections_to_be_completed)} sections."
            )
            self.section_processors = [
                SectionProcessor(
                    current_section=_,
                    system_message=self.system_message,
                    initial_user_message=self.master_template.job_desc.initial_user_message,
                    tool_descriptions=self.tool_descriptions
                    + self.builtin_tool_descriptions,
                    tool_implementations=self.tool_implementations,
                    primary_model_name=self.primary_model_name,
                    llm_cache=self.llm_cache,
                    monitor_instructions=self.master_template.job_desc.monitor_instructions,
                    callback=self.callback,
                    model_url=self.model_url,
                    max_tokens=self.max_tokens,
                    token_counter=self.token_counter,
                    force_tool_every_n=self.force_tool_every_n,
                )
                for _ in self.sections_to_be_completed
            ]
            if self.sequential:
                for section_processor in self.section_processors:
                    await section_processor.run()
                self.notify_completion()
            else:
                self.tasks = {
                    section_processor.current_section: asyncio.create_task(
                        section_processor.run()
                    )
                    for section_processor in self.section_processors
                }
                logger.debug(f"Processing all sections in parallel.")
                await self.wait_on_tasks()
        except Exception as e:
            logger.exception("Error in process runner.")
            raise e

    async def wait_on_tasks(self):
        await asyncio.gather(*self.tasks.values())
        self.notify_completion()

    def notify_completion(self):
        app_logger.info(
            f"All sections have been completed. {self.token_counter.current_token_count} live tokens and "
            f"{self.token_counter.cached_token_count} cached tokens.",
            extra={"color": "cyan"},
        )
        if self.callback:
            self.callback.on_all_sections_complete()

    async def add_human_input_on_section(self, section_id: str, input: str):
        new_task = [
            _ for _ in self.section_processors if _.current_section == section_id
        ][0].add_human_input(input)
        if new_task:
            self.tasks[section_id] = asyncio.create_task(new_task)
        await self.wait_on_tasks()
