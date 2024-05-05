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

import datetime
import json
import os
from typing import Dict, List, Tuple

from openai.types.chat.chat_completion import Choice

from celi_framework.core.job_description import (
    ToolImplementations,
    generate_tool_descriptions,
)
from celi_framework.core.mt_factory import MasterTemplateFactory
from celi_framework.utils.codex import MongoDBUtilitySingleton
from celi_framework.utils.llmcore_utils import (
    FinalOutput,
    ParserFactory,
    parse,
)
from celi_framework.utils.llms import ToolDescription, ask_split
from celi_framework.utils.log import app_logger
from celi_framework.utils.token_counters import (
    get_master_counter_instance,
)
from celi_framework.utils.utils import (
    create_new_timestamp,
    read_json_from_file,
    write_string_to_file,
)

REQUEST_TOKEN_PRICE = 0.00001
RESPONSE_TOKEN_PRICE = 0.00003
MAX_SPEND = 400.0
ONGOING_CHAT_TOKEN_LIMIT = 100000

ChatMessageable = Tuple[str, str] | Dict[str, str]


class ProcessRunner:
    """
    The ProcessRunner class orchestrates document drafting by managing a sequence of tasks that interact with language models for content generation and refinement. It leverages a MasterTemplateFactory for dynamic task management based on a predefined configuration and schema, ensuring a structured approach to document creation.

    This class is central to automating the drafting process, utilizing natural language processing to generate, analyze, and refine text based on source material and expert guidance. It interacts closely with utility functions and MongoDB for data storage and retrieval, optimizing the process through adaptive learning and feedback mechanisms.

    Args:
        master_template (MasterTemplateFactory): Factory instance to manage task templates.
        codex (MongoDBUtilitySingleton): Persistent storage - holds the LLM cache and CELI output
        parser_factory (ParserFactory): Which LLM to use for parsing output
        tool_implementations (ToolImplementations): Tools that CELI can call
        drafts_dir (str): Where to write the output
        llm_cache (bool): Whether to cache LLM requests
        skip_section_list (List[str]): Optional list of sections to skip in the processing

    The ProcessRunner class encapsulates the complexity of automating document drafting, providing a structured and adaptive framework for content generation, analysis, and refinement. It represents a key component in leveraging AI and NLP technologies for enhancing the efficiency and quality of documentation.
    """

    def __init__(
        self,
        master_template: MasterTemplateFactory,
        codex: MongoDBUtilitySingleton,
        parser_factory: ParserFactory,
        tool_implementations: ToolImplementations,
        drafts_dir: str,
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
                description='This used to signal to the outer layer that a pop is requested by the LLMs. Returns the '
                            'next section number.\n\nThis function should not be called unless the "Final Document '
                            'Review" has been completed and you are ready to move to the next section.\nIt will empty '
                            'out the current chat history.',
                parameters={
                    "type": "object",
                    "properties": {
                        "current_section_number": {
                            "type": "string",
                            "description": "No description provided.",
                        }
                    },
                    "required": ["current_section_number"],
                },
            )
        ]
        self.codex = codex
        self.llm_cache = llm_cache
        self.parser_factory = parser_factory
        self.tool_implementations = tool_implementations
        self.keep_running = True
        os.makedirs(drafts_dir, exist_ok=True)
        self.draft_doc = (
            f"{drafts_dir}/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        )
        self.completed_section = None
        self.sections_to_be_completed = list(
            self.master_template.schema.keys()
        )  # Assuming json_doc_new is a dict
        self.process_skip_section_list(skip_section_list)
        self.current_section = self.sections_to_be_completed[0]
        self.most_recent_task = "Pre-Tasks"
        self.system_message = self.master_template.create_system_message()
        app_logger.info(
            f"System message created:\n{self.system_message}", extra={"color": "cyan"}
        )
        self.ongoing_chat: List[Dict[str, str] | Tuple[str, str]] = [
            ("user", self.master_template.job_desc.initial_user_message)
        ]
        self.token_counter = get_master_counter_instance()
        self.tool_descriptions = generate_tool_descriptions(
            self.master_template.job_desc.tool_implementations_class
        )
        self.pop_context_flag = False
        self.save_template()

    def process_iteration(self):
        app_logger.info("Started a new iteration", extra={"color": "orange"})
        self.pop_context_flag = False
        chat_len = len(self.ongoing_chat)

        llm_response = ask_split(
            codex=self.codex if self.llm_cache else None,
            user_prompt=self.ongoing_chat,  # type: ignore
            system_message=self.system_message,
            verbose=True,
            timeout=None,
            tool_descriptions=self.tool_descriptions + self.builtin_tool_descriptions,
        )
        self.ongoing_chat += [("assistant", str(llm_response.message.content or ""))]

        if llm_response.finish_reason == "tool_calls":
            tool_result = self.make_tool_calls(llm_response)
            self.ongoing_chat += tool_result

        app_logger.info(
            "New chat iteration:\n"
            + self.format_chat_messages(self.ongoing_chat[chat_len:]),
            extra={"color": "green"},
        )

        if self.pop_context_flag:
            try:
                self.update_draft_doc(self.ongoing_chat)
            except Exception as e:
                app_logger.exception(
                    f"Error updating draft doc, retrying", extra={"color": "red"}
                )
                self.pop_context_flag = False

            if self.pop_context_flag:
                self.handle_pop_context()


    def format_chat_messages(self, msgs: List[ChatMessageable]):
        return "\n\n".join(self.format_message_content(m) for m in msgs)

    def format_message_content(self, m: ChatMessageable):
        if isinstance(m, dict):
            return f"{m['role'].capitalize()}:\n{m['content']}"
        return f"{m[0].capitalize()}:\n{m[1]}"

    def update_draft_doc(self, msgs):
        output = parse(
            self.parser_factory,
            target_cls=FinalOutput,
            msg=self.format_chat_messages(msgs[-8:]),
        )
        app_logger.info(
            f"Completed section {output.doc_section}.  Draft output is:\n{output.draft}",
            extra={"color": "orange"},
        )

        app_logger.info(f"Adding section {output.doc_section} to {self.draft_doc}")
        try:
            current = read_json_from_file(self.draft_doc)
        except FileNotFoundError:
            current = {}
        section_key = (
            output.doc_section
            if output.doc_section not in current
            else (output.doc_section + " (2)")
        )
        current[section_key] = output.draft
        write_string_to_file(json.dumps(current), self.draft_doc)


    def process_skip_section_list(self, skip_section_list):
        """
        Filters out sections from the drafting process based on a provided list of sections to skip.

        This method updates the internal list of sections that are pending completion by removing any
        sections specified in the skip_section_list. This is particularly useful for excluding sections
        that have already been completed or are not relevant to the current drafting context.

        Args:
            skip_section_list (list of str): A list of section identifiers to be skipped in the drafting process.

        Modifies:
            self.sections_to_be_completed: Updates the list by removing sections specified in skip_section_list.
        """

        # The method starts by iterating over each section in the skip_section_list
        for section in skip_section_list:
            # It checks if the current section is in the list of sections to be completed
            if section in self.sections_to_be_completed:
                # If the section is in the list, it removes the section from the list
                self.sections_to_be_completed.remove(section)
        # After all sections in the skip_section_list have been processed, it logs the remaining number of sections to be completed
        app_logger.info(
            f"Sections (num) remaining after processing skip list: {len(self.sections_to_be_completed)}"
        )

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

        # The method does not return anything
        return None

    def run(self):
        """
        Initiates and manages the main execution loop for drafting documents. This loop continues
        until the `keep_running` flag is set to False, indicating a request to terminate the process, either due to
        completion of all tasks or an external command to halt operations.

        Within each iteration of the loop, the method performs the following operations:
            - Generates task instructions based on the current state and configuration.
            - Retrieves a response from the language model using the current task instructions and context.
            - Processes the language model's response, including handling any specified function calls, updating
                the draft content, and managing the ongoing conversation context.
            - Checks for token usage limits to ensure compliance with predefined constraints.
            - Updates internal state and prepares for the next iteration or termination of the process.

        The method ensures that each task is processed in accordance with the system's operational logic,
        leveraging the language model's capabilities for content generation and refinement. It maintains
        responsive interaction with the language model, adapting to its feedback and instructions to
        dynamically guide the drafting process.

        No parameters are required for this method, as it operates based on the class's internal state
        and configuration. However, it relies on several other methods within the class to perform its
        operations, including `process_iteration`, `get_response`, and `handle_response`.

        Returns:
            None. The method's primary function is to execute the drafting process loop, updating internal
            state and interacting with external systems as necessary. Any outputs are managed through
            side-effects on the class's state or external data stores.

        This method represents the core operational loop of the `ProcessRunner` class, driving the
        automated drafting of document by coordinating tasks, responses, and updates in a continuous,
        controlled cycle.
        """

        while self.keep_running:
            self.process_iteration()

    def make_tool_calls(self, response: Choice):
        def make_tool_call(tool_call):
            name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if name == "pop_context":
                # pop_context is a built-in function and not in the tool_implementations.
                self.pop_context_flag = True
                function_return = arguments["current_section_number"]
            else:
                method_to_call = None
                try:
                    method_to_call = getattr(self.tool_implementations, name)
                except AttributeError:
                    pass

                if not method_to_call:
                    app_logger.error(
                        f"Unknown function name: {name}", extra={"color": "red"}
                    )
                    function_return = f"Error: Called unknown function name: {name}"
                else:
                    function_return = method_to_call(**arguments)
            function_log = f"Call to function {name} with arguments {arguments} returned\n{function_return}"
            return {"role": "function", "name": name, "content": function_log}

        return [make_tool_call(_) for _ in response.message.tool_calls]

    def handle_pop_context(self):
        """
        Adjusts the drafting context in response to a 'pop context' function call, which is used to manage the conversation
        history and focus on relevant content. This method may be triggered by specific directives in the language model's
        response or as part of context management strategies to optimize the interaction with the language model.

        Returns:
            str: A summary message reflecting the action taken to adjust the context. This may include confirmation that
                    older or less relevant conversation history has been truncated or summarized to maintain focus and efficiency.

        The 'handle_pop_context' method is crucial for maintaining the relevance and manageability of the ongoing conversation
        context, ensuring that interactions with the language model remain focused and productive. It supports the drafting
        process by dynamically adapting the context to fit current needs and constraints.
        """

        app_logger.info("Popping context")

        self.pop_context_flag = False
        # Remove the completed section from sections_to_be_completed if it exists
        assert self.current_section in self.sections_to_be_completed
        self.sections_to_be_completed.remove(self.current_section)
        if self.sections_to_be_completed:
            next_section = self.sections_to_be_completed[0]
            try:
                next_user_msg = (
                    f"Proceed to document section {next_section}, and do Task #1."
                )
                app_logger.info(next_user_msg, extra={"color": "cyan"})
            except Exception as e:
                next_user_msg = f"An error occurred in handle_pop_context: {e}.\nStart with the document section immediately after {self.current_section}. Do Task #1"
                app_logger.error(next_user_msg)
        else:
            next_user_msg = "All sections have been completed."
            app_logger.info(next_user_msg, extra={"color": "cyan"})
            self.keep_running = False
            return

        self.ongoing_chat = [
            ("user", self.master_template.job_desc.initial_user_message),
            ("user", next_user_msg),
        ]
        self.completed_section = self.current_section
        self.current_section = next_section

        app_logger.info(
            f"After pop ongoing chat:\n{self.format_chat_messages(self.ongoing_chat)}",
            extra={"color": "green"},
        )
