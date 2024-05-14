"""This Python module, celi_framework.processor, is part of a larger system designed to automate the drafting of
documents using language models. The module contains the ProcessRunner class, which is responsible for managing and
orchestrating the drafting process.

The ProcessRunner class interacts with various utility functions and MongoDB for data storage and retrieval,
optimizing the process through adaptive learning and feedback mechanisms. It also leverages a MasterTemplateFactory
for dynamic task management, ensuring a structured approach to document creation based on a predefined configuration
and schema.

The module must be run from main.py in the root directory. It imports various utility functions and classes from
multiple modules, including llm_helper_funcs, llmcore_utils, TokenSplitter, token_counters, and exceptions. These
imported functions and classes provide essential functionalities for parsing messages, managing tokens,
handling exceptions, and splitting tokens, among others.

The module also defines several constants related to token pricing and maximum spend.
These constants are used to manage the costs associated with using language models for content generation.

The ProcessRunner class is initialized with a master template, codex, id prefix, new JSON document, document directory,
drafts directory, update queue, and a configuration. It also accepts an optional list of sections to skip.

The class includes numerous methods for managing the drafting process, such as generating task instructions,
saving templates, restarting the process, saving prompts and completions, dispatching function calls, running the
main execution loop, processing iterations, retrieving responses, handling responses, updating prompt completions,
checking token limits, handling draft settings, handling table settings, handling context popping, logging errors,
and stopping the process.

Each method in the ProcessRunner class plays a specific role in the drafting process, from initiating and managing
the main execution loop to handling responses from the language model and updating the ongoing conversation context.
The class ensures that each interaction with the language model contributes towards the completion of the document,
while also managing token usage to prevent excessive costs."""

import asyncio
import logging
from typing import List

from celi_framework.core.job_description import (
    ToolImplementations,
    generate_tool_descriptions,
)
from celi_framework.core.mt_factory import MasterTemplateFactory
from celi_framework.core.section_processor import SectionProcessor
from celi_framework.utils.codex import MongoDBUtilitySingleton
from celi_framework.utils.llms import ToolDescription
from celi_framework.utils.log import app_logger
from celi_framework.utils.utils import (
    create_new_timestamp,
)

logger = logging.getLogger(__name__)


class ProcessRunner:
    """
    The ProcessRunner class orchestrates document drafting by managing a sequence of tasks that interact with language
    models for content generation and refinement. It leverages a MasterTemplateFactory for dynamic task management based
    on a predefined configuration and schema, ensuring a structured approach to document creation.

    This class is central to automating the drafting process, utilizing natural language processing to generate,
    analyze, and refine text based on source material and expert guidance. It interacts closely with utility functions
    and MongoDB for data storage and retrieval, optimizing the process through adaptive learning and feedback mechanisms.

    Args:
        master_template (MasterTemplateFactory): Factory instance to manage task templates.
        codex (MongoDBUtilitySingleton): Persistent storage - holds the LLM cache and CELI output
        tool_implementations (ToolImplementations): Tools that CELI can call
        llm_cache (bool): Whether to cache LLM requests
        skip_section_list (List[str]): Optional list of sections to skip in the processing

    The ProcessRunner class encapsulates the complexity of automating document drafting, providing a structured and adaptive framework for content generation, analysis, and refinement. It represents a key component in leveraging AI and NLP technologies for enhancing the efficiency and quality of documentation.
    """

    def __init__(
        self,
        master_template: MasterTemplateFactory,
        codex: MongoDBUtilitySingleton,
        tool_implementations: ToolImplementations,
        llm_cache: bool,
        skip_section_list=None,
    ):
        if skip_section_list is None:
            skip_section_list = []
        self.master_template = master_template  # config and schema need to be defined # TODO -> Read latest version from codex?
        # TODO -> Have it be so that there is a manual template creation process which would be what's above (but with arg for manual create passed in),
        #  then rest of time have it just read from Mongo/codex
        self.builtin_tool_descriptions = [
            ToolDescription(
                name="pop_context",
                description="This used to signal to the outer layer that a pop is requested by the LLMs. Returns the "
                "next test case taskID.\n\nThis function should not be called unless the save_draft_section"
                "function has been called and you are ready to move to the next test case.\nIt will empty "
                "out the current chat history.",
                parameters={
                    "type": "object",
                    "properties": {
                        "current_section_number": {
                            "type": "string",
                            "description": "Current taskID.",
                        }
                    },
                    "required": ["current_section_number"],
                },
            )
        ]
        self.codex = codex
        self.llm_cache = llm_cache

        self.system_message = self.master_template.create_system_message()
        app_logger.info(
            f"System message created:\n{self.system_message}",
            extra={"color": "cyan"},
        )
        self.save_template()

        section_list = list(self.master_template.schema.keys())
        self.sections_to_be_completed = self.removed_skipped_sections(
            section_list, skip_section_list
        )

        self.tool_implementations = tool_implementations
        self.tool_descriptions = generate_tool_descriptions(
            self.master_template.job_desc.tool_implementations_class
        )

    async def run(self):
        """
        Runs all sections of the document.
        """
        section_processors = [
            SectionProcessor(
                current_section=_,
                system_message=self.system_message,
                initial_user_message=self.master_template.job_desc.initial_user_message,
                tool_descriptions=self.tool_descriptions
                + self.builtin_tool_descriptions,
                tool_implementations=self.tool_implementations,
                codex=self.codex,
                llm_cache=self.llm_cache,
            )
            for _ in self.sections_to_be_completed
        ]
        tasks = [section_processor.run() for section_processor in section_processors]
        await asyncio.gather(*tasks)
        app_logger.info("All sections have been completed.", extra={"color": "cyan"})

    def removed_skipped_sections(
        self, all_sections: List[str], skip_section_list: List[str]
    ):
        """
        Filters out sections from the drafting process based on a provided list of sections to skip.

        Args:
            all_sections (list of str): The full list of section identifiers
            skip_section_list (list of str): A list of section identifiers to be skipped in the drafting process.

        Returns:
            The section list with skipped sections removed.
        """

        ret = [section for section in all_sections if section not in skip_section_list]
        app_logger.info(
            f"Sections (num) remaining after processing skip list: {len(ret)}"
        )
        return ret

    def save_template(self):
        """
        Saves the current task template to MongoDB, incorporating versioning for record-keeping.

        This method serializes the current state of the MasterTemplateFactory instance, including the
        configuration and schema, and saves it to a designated MongoDB collection. This allows for the
        auditing of templates used in the drafting process and supports the retrieval of specific templates
        for review or reuse in future drafting sessions.

        Returns:
            None
        """
        # Generate a unique id for the template by appending the current timestamp (in milliseconds) to the template id
        unique_id = str(self.master_template.id + create_new_timestamp(ms=True))

        # Create a dictionary to represent the template, including all relevant attributes and configurations
        template = {
            "_id": unique_id,  # Unique id for the template
            "id": self.master_template.id,  # Template id
            "process_id": f"{self.codex._id}",  # Process id from the codex
            "job_description": self.master_template.job_desc.model_dump(),  # User message from the template configuration
            "schema": self.master_template.schema,  # Schema of the template
        }

        # Save the template to MongoDB using the codex's save_document_with_versioning method
        # The template is saved to the "templates" collection
        self.codex.save_document_with_versioning(template, collection_name="templates")

        # Log a message to indicate that the template has been saved to the codex
        app_logger.info("Stored controller template to codex", {"color": "cyan"})
