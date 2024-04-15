"""
This Python module, celi_framework.processor, is part of a larger system designed to automate the drafting of documents using language models.
The module contains the ProcessRunner class, which is responsible for managing and orchestrating the drafting process.

The ProcessRunner class interacts with various utility functions and MongoDB for data storage and retrieval,
optimizing the process through adaptive learning and feedback mechanisms. It also leverages a MasterTemplateFactory for dynamic task management,
ensuring a structured approach to document creation based on a predefined configuration and schema.

The module must be run from main.py in the root directory. It imports various utility functions and classes from multiple modules,
including llm_helper_funcs, llmcore_utils, TokenSplitter, token_counters, and exceptions. These imported functions and classes provide essential functionalities for parsing messages, managing tokens, handling exceptions, and splitting tokens, among others.

The module also defines several constants related to token pricing and maximum spend.
These constants are used to manage the costs associated with using language models for content generation.

The ProcessRunner class is initialized with a master template, codex, id prefix, new JSON document, document directory,
drafts directory, update queue, and a configuration. It also accepts an optional list of sections to skip.

The class includes numerous methods for managing the drafting process, such as generating task instructions, saving templates,
restarting the process, saving prompts and completions, dispatching function calls, running the main execution loop, processing iterations, retrieving responses, handling responses, updating prompt completions, checking token limits, handling draft settings, handling table settings, handling context popping, logging errors, and stopping the process.

Each method in the ProcessRunner class plays a specific role in the drafting process,
from initiating and managing the main execution loop to handling responses from the language model and updating the ongoing conversation context.
The class ensures that each interaction with the language model contributes towards the completion of the document,
while also managing token usage to prevent excessive costs.
"""

import copy
from dataclasses import asdict
import datetime
import json
import os
from queue import Queue
from typing import Dict, List, Tuple

from llm_core.splitters import TokenSplitter

from celi_framework.core.job_description import (
    ToolImplementations,
    generate_tool_descriptions,
)
from celi_framework.core.mt_factory import MasterTemplateFactory
from openai.types.chat.chat_completion import Choice
from celi_framework.utils.codex import MongoDBUtilitySingleton
from celi_framework.utils.llmcore_utils import (
    FinalOutput,
    IsPromptError,
    ParserFactory,
    parse,
)
from celi_framework.utils.llms import ToolDescription, ask_split
from celi_framework.utils.log import app_logger
from celi_framework.utils.token_counters import (
    get_master_counter_instance,
    token_counter_og,
)
from celi_framework.utils.utils import (
    create_new_timestamp,
    generate_hash_id,
    generate_prompt_and_completion_id,
    generate_task_specific_id,
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

    Attributes:
        master_template_factory (MasterTemplateFactory): Factory instance to manage task templates.
        keep_running (bool): Flag indicating if the process loop should continue running.
        json_doc_new (dict): Template for new document content (Table of Contents).
        doc_dir (str): Directory path for storing generated documents.
        drafts_dir (str): Directory path for storing draft versions.
        update_queue (Queue): Queue for processing updates and feedback from monitoring agents.
        system_message (str): Instructional message for guiding the drafting process.
        user_message (str): Placeholder for user-specific messages or instructions.
        ongoing_chat (str): Accumulative chat history for context preservation.
        token_counter (TokenCounter): Utility for tracking token usage against predefined limits.
        new_drafts_dir (str): Directory for new drafts within the drafting session.
        new_dir_templates (str): Directory for storing session-specific templates.

    Methods:
        process_skip_section_list(skip_section_list): Processes and skips specified sections from drafting.
        generate_task_instructions(): Generates dynamic task instructions based on the current template and section.
        save_template(): Saves the current task template to MongoDB with versioning for record-keeping and auditing.
        restart(): Resets and restarts the drafting process, typically invoked after modifications to the template or in response to feedback.
        save_prompt_and_completion(response): Parses and saves the interaction with the language model to MongoDB, handling versioning and error logging.
        function_calls(name, arguments): Dispatches function calls to utility functions based on the name and provided arguments.
        run(): Initiates and manages the main execution loop for processing drafting tasks.
        process_iteration(): Manages a single iteration within the execution loop, handling task execution, response processing, and system updates.
        get_response(): Retrieves responses from the language model based on current prompts and context.
        handle_response(response): Processes language model responses, directing flow based on content type and action required.
        handle_no_message_returned(): Handles scenarios where no message is returned from the language model.
        handle_message_returned(message): Processes and logs messages returned from the language model.
        handle_function_call(response): Executes function calls specified in language model responses.
        update_prompt_completion(prompt_completion): Updates the ongoing chat with the latest prompt completion content.
        check_token_limits(): Monitors and enforces token usage limits to prevent excessive costs.
        check_chat_token_count(): Ensures the ongoing chat does not exceed token count limits, adjusting context as necessary.
        handle_draft_setting(function_return): Processes and saves draft content based on function return values.
        handle_table_setting(function_return): Handles the incorporation of table content into the draft based on function returns.
        handle_pop_context(function_return): Manages context updates and section progression based on pop context function returns.
        log_error_and_save_as_text(error, content, content_type): Logs errors and saves associated content for debugging.
        stop(): Gracefully terminates the drafting process.

    The ProcessRunner class encapsulates the complexity of automating document drafting, providing a structured and adaptive framework for content generation, analysis, and refinement. It represents a key component in leveraging AI and NLP technologies for enhancing the efficiency and quality of documentation.
    """

    def __init__(
        self,
        master_template: MasterTemplateFactory,
        codex: MongoDBUtilitySingleton,
        parser_factory: ParserFactory,
        tool_implementations: ToolImplementations,
        drafts_dir: str,
        update_queue: Queue,
        llm_cache: bool,
        skip_section_list: List[str] = [],
    ):  # skip_section_list=SECTIONS_COMPLETED):
        # Initialize MasterTemplateFactory # TODO -> Have this passed in, instead of initializing like this
        self.master_template = master_template  # config and schema need to be defined # TODO -> Read latest version from codex?
        # TODO -> Have it be so that there is a manual template creation process which would be what's above (but with arg for manual create passed in),
        #  then rest of time have it just read from Mongo/codex
        self.builtin_tool_descriptions = [
            ToolDescription(
                name="pop_context",
                description='This used to signal to the outer layer that a pop is requested by the LLMs. Returns the next section number.\n\nThis function should not be called unless the "Final Document Review" has been completed and you are ready to move to the next section.\nIt will empty out the current chat history.',
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
        self.update_queue = update_queue
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

        self.save_template()

    def process_iteration2(self):
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
            self.update_draft_doc(self.ongoing_chat)
            self.handle_pop_context()

    def format_chat_messages(self, msgs: List[ChatMessageable]):
        return "\n\n".join(self.format_message_content(m) for m in msgs)

    def format_message_content(self, m: ChatMessageable):
        if isinstance(m, dict):
            return f"{m['role'].capitalize()}:\n{m['content']}"
        return f"{m[0].capitalize()}:\n{m[1]}"

    def update_draft_doc(self, msgs):
        parsed_draft = parse(
            self.parser_factory,
            target_cls=FinalOutput,
            msg=self.format_chat_messages(msgs[-8:]),
        )
        app_logger.info(
            f"Completed section {parsed_draft.doc_section}.  Draft output is:\n{parsed_draft.draft}",
            extra={"color": "orange"},
        )
        self.update_draft_doc_file(parsed_draft)

        _id = generate_hash_id(msgs)
        id = _id
        draft_dict = {
            "_id": _id,  # Assuming _id is defined elsewhere and unique to each draft
            "id": id,  # Assuming id is defined elsewhere and unique to each draft
            "draft_output": asdict(parsed_draft),
        }
        self.codex.save_document_with_versioning(draft_dict, collection_name="drafts")

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

    def save_prompt_and_completion(self, response):
        """
        Parses the language model's response and saves the interaction details to MongoDB. This method
        handles the creation of a comprehensive document that includes the interaction's context, the
        response, any identified function calls, and metadata such as timestamps and unique identifiers.
        The document is versioned and saved for record-keeping, auditing, and potential future analysis.

        This method also categorizes the response based on its content (e.g., draft content, function calls)
        and handles errors or exceptions during parsing. It ensures that all significant interactions are
        logged and stored in a structured format.

        Args:
            response (obj): The response object from the language model, encapsulating content, metadata,
                            and any special instructions or function calls included in the response.

        Returns:
            str: The unique ID of the document saved in MongoDB, representing the specific interaction.

        Raises:
            ParsingException: If any errors occur during the parsing of the language model's response,
                              indicating issues with understanding or processing the response content.

        The method meticulously processes the response, checking for and executing function calls as necessary,
        and prepares a document that captures the essence of the interaction. This document is then saved to
        MongoDB, with a unique identifier returned for reference. Errors during parsing or saving trigger exceptions,
        ensuring robust error handling and data integrity.
        """

        # Initialize variables with default values.
        timestamp = create_new_timestamp(
            ms=True
        )  # Create a new timestamp for this operation.
        task_list, task_desc = ["None"], "Tool Call"  # Default task information.
        function_name, arguments = "None", "None"  # Default function call information.
        response_msg = "None"  # Default value for response message.
        prompt_exception = False

        # try:
        # Determine the type of response and extract relevant information.
        if response.finish_reason == "tool_calls":
            # Extract tool details if the finish reason is tool calls.
            task_list = [
                f"{_.function.name} with {json.dumps(_.function.arguments)}"
                for _ in response.message.tool_calls
            ]
        elif response.message.content:
            # Parse the direct message content for task details.
            response_msg = response.message.content
            # logger.info(f"Response message:\n{response_msg}", extra={"color": "green"})

            # try:
            # logger.info(
            #     "Attempting to parse content",
            #     extra={"color": "orange"},
            # )
            # parsed_msg = parse(self.parser_factory, Message, response_msg)
            # # TODO -> Should we switch to parsed_msg.last_current_task_description_list (LIST)

            # # Check if the task description matches the final output task, indicating a draft output.
            # draft_output = self.master_template.job_desc.final_output_task in task_desc
            # except Exception as e:
            #     # Log and append context length issues encountered during parsing of prompt completion.
            #     logger.exception(e, extra={"color": "red"})
            #     error_message = f"{e}"
            #     logger.error(error_message, extra={"color": "red"})
            #     self.prompt_completion += f"\n{error_message}"
            #     # prompt_exception = True

        # except Exception as e:
        #     # Log and append any errors encountered during parsing.
        #     error_message = f"Error processing response: {e}"
        #     logger.error(error_message, extra={"color": "red"})
        #     self.prompt_completion += f"\n{error_message}"
        #     raise ParsingException(f"Failed to parse response: {e}")

        try:
            # New chunking and error detection logic
            # logger.info(
            #     f"Self.prompt_completion = {self.prompt_completion}",
            #     extra={"color": "green"},
            # )
            token_count = token_counter_og(string=str(self.prompt_completion))
            app_logger.info(f"Self.completion token count = {token_count}")

            # Initialize the TokenSplitter with the appropriate model and chunk size
            splitter = TokenSplitter(
                # model="mistral-7b-instruct-v0.1.Q5_K_M.gguf", DD This cause an error unknown encoding: mistral-7b-instruct-v0.1.Q5_K_M.gguf
                chunk_size=4000,
                chunk_overlap=50,
            )

            # Iterate through chunks generated by TokenSplitter
            for chunk in splitter.chunkify(self.prompt_completion):
                app_logger.info("Processing chunk...", extra={"color": "green"})

                # Parse the current chunk for errors or exceptions
                # parsed_prompt = parse_completion_for_error_with_llamacpp_parser(chunk)
                parsed_prompt = parse(
                    self.parser_factory, target_cls=IsPromptError, msg=chunk
                )
                app_logger.info(
                    f"parse_completion_for_error:\n{parsed_prompt}",
                    extra={"color": "orange"},
                )

                # Check if the parsed result indicates an error or exception
                if (
                    parsed_prompt.is_there_a_function_exception
                    or parsed_prompt.is_there_a_function_error
                ):
                    prompt_exception = True
                    app_logger.error(
                        "Error or exception detected in prompt completion.",
                        extra={"color": "red"},
                    )
                    self.prompt_completion += (
                        "\nError or exception detected in prompt completion."
                    )
                    break
        except Exception as e:
            app_logger.exception(e)
            app_logger.error(f"Error Parsing is not working:\n{e}")

        # Generate unique IDs for the MongoDB document based on the task information.
        unique_id, prompt_id, id = self.generate_document_ids(timestamp, task_list)

        draft_output = self.pop_context_flag

        # Prepare the MongoDB document with all extracted and parsed information.
        document = self.prepare_document(
            unique_id,
            prompt_id,
            id,
            task_list,
            task_desc,
            draft_output,
            response.finish_reason,
            response_msg,
            function_name,
            arguments,
            prompt_exception,
            timestamp,
        )

        try:
            # Attempt to save the prepared document to MongoDB with versioning.
            self.codex.save_document_with_versioning(
                document, collection_name="process_executions"
            )
            app_logger.info("Document saved with versioning.", extra={"color": "cyan"})
        except Exception as e:
            # Log and append any errors encountered during saving to MongoDB.
            error_message = f"Failed to save document to MongoDB: {e}"
            app_logger.error(error_message, extra={"color": "red"})
            self.prompt_completion += f"\n{error_message}"

        if draft_output:
            # Prepare and save the draft document if a draft output is indicated.
            draft = self.prepare_draft_dict(response_msg, document)
            self.codex.save_document_with_versioning(draft, collection_name="drafts")
            app_logger.info("Draft saved with versioning.", extra={"color": "green"})

        # Return the unique ID of the main document saved or updated.
        return document["_id"]

    def generate_document_ids(self, timestamp, task_list):
        """
        Generates a set of unique identifiers for a new document based on the current timestamp and task list.
        These identifiers are used to uniquely tag and track the document within the MongoDB database,
        ensuring accurate versioning and retrieval.

        The method produces three types of IDs:
        1. A unique document ID that represents the specific interaction instance.
        2. A prompt ID that identifies the set of prompts leading up to the current interaction.
        3. A task-specific ID that links the document to a specific task within the process,
           facilitating task-level tracking and analysis.

        Args:
            timestamp (str): A string representation of the current timestamp, used for generating time-based unique IDs.
            task_list (list): A list of tasks that have been processed or are in processing, contributing to the context of the document.

        Returns:
            tuple: Contains three strings representing the unique document ID, prompt ID, and task-specific ID, respectively.

        This method plays a critical role in the documentation and tracking system of the `ProcessRunner`,
        ensuring that each piece of content generated and each interaction with the language model can be
        uniquely identified and accessed.
        """

        unique_id = generate_prompt_and_completion_id(
            system_message=self.system_message,
            ongoing_chat=self.ongoing_chat,
            prompt_completion=self.prompt_completion,
            timestamp=timestamp,
        )
        prompt_id = generate_prompt_and_completion_id(
            system_message=self.system_message,
            ongoing_chat=self.ongoing_chat,
        )

        id = generate_task_specific_id(
            document_type="document",  # TODO: Unhard code this
            section_number=self.completed_section,
            task=task_list[-1] if task_list else None,
        )
        return unique_id, prompt_id, id

    def prepare_document(
        self,
        unique_id,
        prompt_id,
        id,
        task_list,
        task_desc,
        draft_output,
        finish_reason,
        response_msg,
        function_name,
        arguments,
        prompt_exception,
        timestamp,
    ):
        """
        Prepares a document for storage in MongoDB by organizing response data, interaction context,
        and metadata into a structured format. This method consolidates the various pieces of information
        related to a single interaction with the language model, including the response, any executed
        function calls, and the overall context of the conversation.

        Args:
            unique_id (str): A unique identifier for the document, representing the specific interaction.
            prompt_id (str): An identifier for the set of prompts leading up to the interaction.
            id (str): A task-specific identifier linking the document to a particular task within the process.
            task_list (list): The list of tasks involved in or relevant to the current interaction.
            task_desc (str): A description of the current task or tasks being addressed.
            draft_output (bool): Indicates whether the interaction resulted in draft content for the document.
            finish_reason (str): The reason provided by the language model for completing the response.
            response_msg (str): The content of the response from the language model.
            function_name (str): The name of any function called during the interaction, if applicable.
            arguments (str): A string representation of arguments passed to the called function, if any.
            prompt_exception (bool): Indicates whether an exception occurred during prompt processing.
            timestamp (str): The timestamp when the interaction occurred, used for versioning and tracking.

        Returns:
            dict: A dictionary representing the structured document ready for storage in MongoDB, including all relevant interaction details and metadata.

        This method is crucial for ensuring that data from each interaction is accurately captured and stored in a manner that supports both immediate process needs and long-term analysis. The structured format facilitates querying, analysis, and retrieval of interactions based on various criteria.
        """

        document = {
            "_id": unique_id,
            "id": id,
            "id_is": "task specific id",
            "id_is_hash_of": "master_template + section_number + task",
            "prompt_id": prompt_id,
            "process_id": f"{self.codex._id}",
            "template_id": self.master_template.id,
            "finish_reason": finish_reason,
            "document_section": self.current_section,
            "task": task_list,
            "task_desc": task_desc,
            "draft_output": draft_output,
            "system_message": self.system_message,
            "ongoing_chat": self.ongoing_chat,
            "prompt_completion": self.prompt_completion,
            "prompt_exception": prompt_exception,
            "response_msg": response_msg,
            "function_name": function_name,
            "function_arguments": arguments,
            "timestamp": timestamp,
        }
        return document

    def prepare_draft_dict(self, response_msg, document):
        """
        Prepares and structures the draft content based on the language model's response and additional document metadata.
        This method formats the draft content, including any tables, figures, and references extracted from the response,
        into a dictionary suitable for storage in MongoDB. It leverages parsing utilities to extract structured information
        from the response message and associates this information with relevant document metadata.

        Args:
            response_msg (str): The content of the response from the language model, which includes draft text and potentially tables, figures, or references.
            document (dict): A dictionary containing metadata about the interaction, including unique identifiers and task descriptions.

        Returns:
            dict: A dictionary representing the structured draft content, ready for storage in MongoDB. This includes extracted sections, tables, figures, references, and any comments or annotations identified in the response.

        The returned dictionary includes keys for section content, comments, success flags indicating parsing success,
        source material mappings, scope descriptions, and identifiers for tables, figures, and cross-references.
        This structured approach facilitates later retrieval and analysis of draft content, supporting the iterative
        refinement and compilation of the document.
        """

        parsed_draft = parse(
            self.parser_factory, target_cls=FinalOutput, msg=response_msg
        )
        app_logger.info("THIS IS IMPORTANT!!!!!", extra={"color": "orange"})
        app_logger.info(
            f"parse_final_output_with_llamacpp_parser:\n{parsed_draft}",
            extra={"color": "orange"},
        )
        _id = generate_hash_id(response_msg)
        id = document["id"]

        self.update_draft_doc_file(parsed_draft)

        draft_dict = {
            "_id": _id,  # Assuming _id is defined elsewhere and unique to each draft
            "id": id,  # Assuming id is defined elsewhere and unique to each draft
            "draft_output": asdict(parsed_draft),
        }

        return draft_dict

    def update_draft_doc_file(self, output: FinalOutput):
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
            self.process_iteration2()

    def process_iteration(self):
        """
        Manages a single iteration within the execution loop, orchestrating the processing of a task or interaction.
        This method encapsulates the steps involved in generating a response from the language model, processing
        that response, and preparing for subsequent actions based on the outcome.

        The method performs the following key operations in sequence:
        1. Retrieves a response from the language model based on the current context and instructions.
        2. Processes the received response to understand and act upon any directives, content, or function calls it contains.
        3. Updates the ongoing conversation context with the new information obtained from the response.
        4. Checks for and handles any token usage limits to ensure compliance with operational constraints.
        5. Saves the processed interaction to MongoDB, capturing the dialogue, decisions, and any generated content for record-keeping.

        Each iteration represents a step forward in the drafting process, potentially advancing the document's content,
        adjusting the drafting strategy based on feedback, or handling administrative tasks like context management
        and token accounting.

        Returns:
            None. The primary effect of this method is the advancement of the drafting process through side effects
            on class attributes and external data stores (e.g., MongoDB).

        This method is crucial for maintaining the flow of the drafting process, ensuring that each interaction with
        the language model is purposeful and that its outcomes are effectively integrated into the ongoing work. It
        leverages other methods within the class to perform specific tasks, such as `get_response`, `handle_response`,
        and `update_prompt_completion`.
        """

        # Log the start of a new iteration
        app_logger.info("Started a new iteration", extra={"color": "orange"})
        self.pop_context_flag = False

        # Retrieve a response from the language model based on the current context and instructions
        response = self.get_response()
        app_logger.info(
            f"Received response with finish reason {response.finish_reason}",
            extra={"color": "orange"},
        )

        # Process the received response to understand and act upon any directives, content, or function calls it contains
        prompt_completion = self.handle_response(response)
        app_logger.info(
            f"Handled response:\n{prompt_completion}", extra={"color": "green"}
        )

        # Update the ongoing conversation context with the new information obtained from the response
        self.update_ongoing_chat(prompt_completion)
        app_logger.info(
            "Updated ongoing chat with new response", extra={"color": "orange"}
        )

        # Check for and handle any token usage limits to ensure compliance with operational constraints
        self.check_token_limits()
        app_logger.info("Checked token limits", extra={"color": "orange"})

        # Count the tokens in the ongoing chat to ensure it does not exceed the limit
        self.check_chat_token_count()
        app_logger.info("Counted chat tokens", extra={"color": "orange"})

        # Save the processed interaction to MongoDB, capturing the dialogue, decisions, and any generated content for record-keeping
        doc_id = self.save_prompt_and_completion(response)
        app_logger.info("Saved data to MongoDB", extra={"color": "orange"})

        # Put the document ID in the update queue for monitoring
        self.update_queue.put(("doc_save", doc_id))
        app_logger.info(
            f"Enqueued Doc ID {doc_id} for monitoring", extra={"color": "cyan"}
        )

        if self.pop_context_flag:
            self.handle_pop_context()

    def get_response(self) -> Choice:
        """
        Retrieves a response from the language model by submitting the current prompts and context. This method forms
        the bridge between the drafting process and the language model, sending the constructed prompts to the model
        and awaiting its response. The response is expected to further the drafting process, whether by generating text,
        providing instructions, or executing a function call.

        The method constructs a request that includes the ongoing conversation context and any specific instructions
        encoded in the system and user messages. It then submits this request to the language model and waits for a
        response, handling any errors or timeouts that may occur during the request.

        Returns:
            An object representing the language model's response. This object typically includes the generated text
            response, metadata such as the reason for completion, and any function calls or instructions embedded within
            the response text.

        This response is crucial for advancing the drafting process, as it may contain the next piece of content to
        be added to the document, instructions for the next steps, or commands to modify the drafting context. The
        `get_response` method ensures that each interaction with the language model is captured and acted upon
        according to the system's logic.
        """

        # Call LLM with system message and ongoing chat
        return ask_split(
            codex=self.codex if self.llm_cache else None,
            user_prompt=self.ongoing_chat,  # type: ignore
            system_message=self.system_message,
            verbose=True,
            timeout=None,
            tool_descriptions=self.tool_implementations.tool_descriptions,
        )

    def handle_response(self, response: Choice):
        """
        Processes the response received from the language model, determining the appropriate course of action
        based on the content and directives within the response. This method interprets the response to decide
        whether to update the draft content, execute a function call, or adjust the conversation context.

        The response from the language model can contain various types of information, including text content
        for the draft, instructions for next steps, or commands for specific function calls. This method
        categorizes the response appropriately and initiates the corresponding actions, such as updating
        the draft content or handling embedded function calls.

        Args:
            response: An object representing the language model's response, which includes the response content,
                      metadata such as the finish reason, and any embedded instructions or commands.

        Returns:
            str: A string representing the processed content to be appended to the ongoing conversation context.
                 This could include new draft content, a summary of executed actions, or an indication of any
                 required user input or decision-making.

        The `handle_response` method is central to the operational logic of the `ProcessRunner`, ensuring that
        each response from the language model is effectively integrated into the drafting process. It leverages
        other methods within the class, such as `handle_no_message_returned`, `handle_message_returned`, and
        `handle_function_call`, to address specific types of responses and actions required.
        """
        if response.finish_reason == "tool_calls":
            prompt_completion = self.handle_function_call(response)
        elif response.message.content:
            # TODO -> We could add and drop prompt_completions to queue strategically
            #  to keep only completions which are relevant to the tasks at hand
            prompt_completion = self.handle_message_returned(response.message.content)
        else:
            prompt_completion = self.handle_no_message_returned()

        return prompt_completion

    def handle_no_message_returned(self):
        """
        Handles scenarios where the language model's response contains no message content. This situation can occur
        when the model's output does not directly contribute to the drafting process or when an expected output is
        missing due to model limitations or contextual constraints.

        This method is invoked as a fallback mechanism to maintain the flow of the drafting process, ensuring that
        even in the absence of direct content from the language model, the process can proceed with minimal disruption.
        It may generate a placeholder message or prompt for further input, aiming to elicit more actionable guidance
        or content on subsequent interactions.

        Returns:
            str: A placeholder message or instruction generated in response to the absence of a message from the
                 language model. This output is designed to keep the conversation going and guide the user or system
                 towards providing additional context or modifying the request to obtain a more useful response.

        The method ensures continuity in the drafting process, preventing stalls due to incomplete or missing responses
        and encouraging adjustments to the interaction strategy to better leverage the language model's capabilities.
        """

        app_logger.warning(
            "No message was returned and no function was called.",
            extra={"color": "red"},
        )
        return (
            "\n\nNo message was returned from you (the writer) and no function was called.\n"
            "As a writer, explain in detail what you want to do next."
        )

    def handle_message_returned(self, message):
        """
        Processes and integrates the message content returned from the language model into the drafting process.
        This method is called when the language model provides actionable content or instructions within its response.

        The returned message is evaluated for its relevance and utility in advancing the document's content or
        addressing specific drafting tasks. Based on this evaluation, the method may update the draft content,
        adjust the conversation context, or prompt further actions to refine or expand upon the provided content.

        Args:
            message (str): The content of the message returned by the language model, containing text, instructions,
                           or commands to be integrated into the drafting process.

        Returns:
            str: The processed content, ready to be appended to the ongoing conversation context or used to update
                 the draft document. This includes any modifications or annotations added to the original message
                 to enhance its clarity or utility.

        By effectively interpreting and utilizing the content provided by the language model, this method plays a
        key role in maintaining the momentum of the drafting process and ensuring that each response contributes
        towards the completion of the document.
        """
        return f"\nPrior message from you (the writer): \n{message}"

    def handle_function_call(self, response):
        """
        Executes specific function calls embedded within the language model's response. This method is critical
        for handling responses that contain instructions for actions beyond simple text generation, such as
        retrieving additional data, performing analysis, or modifying the draft content in a particular manner.

        Function calls are identified within the response based on predefined patterns or markers. Once detected,
        this method dispatches the function call to the appropriate utility function within the system, passing
        along any arguments specified in the response.

        Args:
            response: The response object from the language model, potentially containing one or more function
                      calls along with the necessary arguments for execution.

        Returns:
            str: A summary or result of the executed function call, encapsulating any direct outputs, status
                 messages, or indications of actions taken as a result of the function call. This information
                 is used to update the ongoing conversation context or draft content.

        This method ensures that the drafting process can dynamically adapt to the needs of the document, leveraging
        the full range of capabilities offered by the language model and auxiliary utility functions to achieve
        comprehensive and nuanced content development.
        """

        prompt_completion = (
            self.handle_message_returned(response.message.content)
            if response.message.content
            else ""
        )
        tool_results = self.make_tool_calls(response)
        prompt_completion += "\n\n".join(_["content"] for _ in tool_results)
        return prompt_completion

    def make_tool_calls(self, response: Choice):
        def make_tool_call(tool_call):
            name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if name == "pop_context":
                # pop_context is a built-in function and not in the tool_implementations.
                self.pop_context_flag = True
                function_return = arguments["current_section_number"]
            else:
                unknown_func = False
                try:
                    method_to_call = getattr(self.tool_implementations, name)
                except AttributeError:
                    unknown_func = True

                if unknown_func:
                    app_logger.error(
                        f"Unknown function name: {name}", extra={"color": "red"}
                    )
                    function_return = "Error: Called unknown function name: {name}"
                else:
                    function_return = method_to_call(**arguments)
            function_log = f"Call to function {name} with arguments {arguments} returned\n{function_return}"
            return {"role": "function", "name": name, "content": function_log}

        return [make_tool_call(_) for _ in response.message.tool_calls]

    def update_ongoing_chat(self, prompt_completion):
        """
        Updates the ongoing conversation context with the latest response or content generated by the language model.
        This method is essential for integrating new information into the drafting process, ensuring that each
        language model interaction contributes to the evolving document draft and maintains the continuity of the conversation.

        Args:
            prompt_completion (str): The content or instructions to be added to the ongoing conversation context.
                                      This can include text generated by the language model, summaries of executed
                                      actions, or other relevant information that supports the drafting process.

        Modifies:
            This method directly updates the `ongoing_chat` attribute by appending the new `prompt_completion` content,
            ensuring that the updated context is used in subsequent interactions with the language model.

        Returns:
            None. The primary effect of this method is the modification of the class's internal state, specifically
            the updating of the conversation context to include the latest interactions.

        The updated conversation context plays a critical role in informing future prompts and interactions with the
        language model, allowing for a dynamic and responsive drafting process that adapts to new information and
        instructions as the document develops.
        """

        self.prompt_completion = copy.deepcopy(prompt_completion)
        self.ongoing_chat += prompt_completion

    def check_token_limits(self):
        """
        Monitors and enforces the predefined token usage limits to manage costs associated with the language model's API calls.
        This method calculates the total cost of tokens consumed in requests and responses, comparing it against the
        maximum allowable spend (MAX_SPEND). If the total cost exceeds this limit, the method triggers a halt in the
        drafting process to prevent further charges.

        The token costs are determined by multiplying the number of tokens used in requests and responses by their respective
        prices (REQUEST_TOKEN_PRICE and RESPONSE_TOKEN_PRICE). This approach ensures transparent and controlled usage of the
        language model, aligning with budget constraints.

        Modifies:
            This method potentially modifies the `keep_running` attribute, setting it to False if the token usage exceeds
            the specified maximum spend, effectively stopping the process.

        Returns:
            None. The primary function of this method is to perform a check and potentially modify the process's
            execution state based on the outcome.

        This method is a critical component of the operational management within the `ProcessRunner`, ensuring that
        the drafting process remains cost-effective and within budgetary limits. It exemplifies prudent resource
        management, safeguarding against unexpected expenditures.
        """

        # Get the total number of request and response tokens used so far from the token counter
        request_tokens, response_tokens = self.token_counter.get_total_tokens()

        # Log the total number of request and response tokens
        app_logger.info(
            f"Total Request Tokens: {request_tokens}, Total Response Tokens: {response_tokens}",
            extra={"color": "dark_grey"},
        )

        # Calculate the total cost of the tokens used in requests and responses by multiplying the number of tokens by their respective prices
        total_cost = (
            REQUEST_TOKEN_PRICE * request_tokens
            + RESPONSE_TOKEN_PRICE * response_tokens
        )

        # Check if the total cost exceeds the maximum allowable spend
        if total_cost > MAX_SPEND:
            # If the total cost exceeds the maximum spend, log an error message
            app_logger.error("Max Spend Reached!", extra={"color": "red"})

            # Set the keep_running flag to False to stop the drafting process
            self.keep_running = False

            # Exit the program (this line may be removed later when we are confident about stopping and need to keep state)
            exit()  # TODO <- To be removed later when we are confident about stoping and need to keep state (?)

    def check_chat_token_count(self):
        """
        Evaluates the token count of the ongoing conversation context to ensure it remains within the limits
        acceptable by the language model's API. This method is crucial for maintaining the effectiveness and
        efficiency of interactions with the language model, as exceeding token count limits can lead to truncated
        responses or failed requests.

        If the token count exceeds a predefined threshold, this method initiates measures to reduce the context size,
        such as invoking the `pop_context` function to manage the conversation history or summarizing the context to
        maintain essential information while discarding older or less relevant content.

        Returns:
            None. The focus of this method is on evaluating and potentially modifying the `ongoing_chat` attribute
            to ensure compliance with token count constraints.

        Through active context management, this method supports the continuous and uninterrupted operation of the
        drafting process, ensuring that each interaction with the language model is optimized for relevance and
        compliance with technical constraints.
        """

        # Calculate the token count of the ongoing chat by calling the token_counter_og function
        chat_token_count = token_counter_og(self.ongoing_chat)

        # Log the token count of the ongoing chat
        app_logger.info(
            f"Token count of ongoing context: {chat_token_count}",
            extra={"color": "white"},
        )

        # Check if the token count of the ongoing chat exceeds the limit of 100000 tokens
        if chat_token_count > ONGOING_CHAT_TOKEN_LIMIT:
            # If the token count exceeds the limit, append a message to the ongoing chat to stop the current action
            # and call the pop_context function with the current section number as the argument
            self.ongoing_chat += (
                "\n\nStop what you are doing and call function pop_context "
                "with current section number as the value passed to the function."
            )

            # Log an error message indicating that a pop request had to be sent because the token count for the ongoing chat exceeded the limit
            app_logger.error(
                "Had to send pop request because tokens for ongoing chat = {chat_token_count}"
            )

    def handle_pop_context(self):
        """
        Adjusts the drafting context in response to a 'pop context' function call, which is used to manage the conversation
        history and focus on relevant content. This method may be triggered by specific directives in the language model's
        response or as part of context management strategies to optimize the interaction with the language model.

        Args:
            function_return: The outcome or data associated with the 'pop context' function call. While this method does
                                not typically process complex return values, the argument is included to maintain consistency
                                in function call handling.

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
            try:
                next_section = self.sections_to_be_completed[0]
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
