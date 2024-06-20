"""
This module acts as a general template for report generation.
It is not specific to any particular type of report or study, but rather provides a set of tools and implementations
for handling and generating sections of a report from various source materials.
The functionality includes reading document schemas, retrieving and formatting text from specified sections,
and providing interfaces to external language model services for content drafting and table setting.

Usage of this module can be tailored to fit the needs of any structured reporting format across different domains,
emphasizing its versatility and adaptability.
"""

import json
import os
from typing import Dict

from attr import dataclass

from celi_framework.core.job_description import (
    BaseDocToolImplementations,
)
from celi_framework.experimental.templates import (
    make_draft_setting_output_prompt,
    make_table_setting_output_prompt,
)
from celi_framework.utils.llms import quick_ask
from celi_framework.utils.log import app_logger
from celi_framework.utils.token_counters import get_master_counter_instance
from celi_framework.utils.utils import (
    format_toc,
    get_section_context_as_text,
    read_json_from_file,
)


@dataclass
class Document:
    toc: Dict[str, str]
    content: Dict[str, str]


class ReportingToolImplementations(BaseDocToolImplementations):
    doc_dir: str

    def __init__(self, doc_dir: str):
        super().__init__()
        self.doc_dir = doc_dir

        def dir(s):
            return os.path.join(self.doc_dir, s)

        self.source_mappings = read_json_from_file(dir("mappings_gpt.json"))
        self.example_doc = Document(
            toc=read_json_from_file(dir("example_report_schema.json")),
            content=read_json_from_file(dir("example_report_filled.json")),
        )
        self.example_doc_sources = {
            "example_source_1": Document(
                toc=read_json_from_file(dir("example_source_1_schema.json")),
                content=read_json_from_file(dir("example_source_1_filled.json")),
            ),
            "example_source_2": Document(
                toc=read_json_from_file(dir("example_source_2_schema.json")),
                content=read_json_from_file(dir("example_source_2_filled.json")),
            ),
        }
        self.new_doc_sources = {
            "new_source_1": Document(
                toc=read_json_from_file(dir("new_source_1_schema.json")),
                content=read_json_from_file(dir("new_source_1_filled.json")),
            ),
            "new_source_2": Document(
                toc=read_json_from_file(dir("new_source_2_schema.json")),
                content=read_json_from_file(dir("new_source_2_filled.json")),
            ),
        }

    def get_schema(self) -> Dict[str, str]:
        return self.example_doc.toc

    def source_sections_getter(self, section_number: str):
        """
        Identify the documents and their sections that are source materials for the example document section.

        Args:
            section_number (str): The section number of the document for which you want to get the source material.
        """
        return self.source_mappings[section_number]

    def section_text_getter(
        self,
        sections_dict_str: str,
    ):
        """
        Extracts text from specified sections of documents.
        It handles different document types and logs any errors or warnings encountered.
        Returns concatenated text from the specified sections of the documents.
        If there is no content for the section, <empty section> will be returned.

        If the response contains "Error:", then there was a problem with the function call.

        Args:
            sections_dict_str (str): A JSON string mapping document names to their respective section numbers.  The json string will have the documents and sections in a dictionary.  The sections values should correspond to an entry in the table of contents for the specified document..
        """

        try:
            sections_dict = json.loads(sections_dict_str)
        except json.JSONDecodeError as e:
            app_logger.error(f"Invalid JSON format: {e}", extra={"color": "red"})
            return "Error: Provided sections_dict_str is not a valid JSON format."

        output_text = ""
        for document_name, section_numbers in sections_dict.items():
            app_logger.info(
                f"Processing document: {document_name} with Sections: {section_numbers}",
                extra={"color": "cyan"},
            )

            # Load the document based on the document name
            if document_name == "Example Document":
                document = self.example_doc
            elif document_name in self.example_doc_sources:
                document = self.example_doc_sources[document_name]
            else:
                err_msg = f"Error: No document named {document_name} was found to extract text from"
                app_logger.error(err_msg, extra={"color": "red"})
                output_text += f"{err_msg}\n\n"
                continue

            # Process each section for the current document
            for section_number in section_numbers:
                # Attempt to get the section text
                text = document.content.get(
                    section_number,
                    f"Error: {section_number} not found in {document_name}",
                ).strip()
                section_title = document.toc.get(
                    section_number, "No section title"
                ).strip()
                if not text or (text[:-1] == section_title):
                    text = "<empty section>"
                output_text += (
                    f"{document_name} Section {section_number}:\n"
                    f"{get_section_context_as_text(section_number, document.toc)}"
                    f"Content:\n{text}\n"
                )
        return output_text

    def get_source_tocs(self):
        """
        Retrieves and formats the table of contents for source documents.

        This function loads the flat schemas of the source documents, formats their
        table of contents, and combines them into a single string. The combined string is intended
        to be sent to a language model for further processing. The function also logs the output
        for debugging purposes.

        Returns:
            str: A string containing the formatted tables of contents for source documents,
                followed by an instruction to proceed to the next task.
        """
        reformatted = [
            f"{k} Table of Contexts:\n\n{format_toc(v.toc)}"
            for k, v in self.example_doc_sources.items()
        ]

        # Combine the schemas into a single string for the response
        send_to_llm = (
            "\n\n".join(reformatted)
            + "\n\nProceed to next task: Map example sources to new sources indexes"
        )
        app_logger.info(
            f"Getter outputs to LLM: {send_to_llm[0:100]}...", extra={"color": "cyan"}
        )
        return send_to_llm

    def draft_setter(self, section_content):
        """
        Processes the section content using a drafting template and sends it to an external service for response
        generation. It parses the JSON response and handles any potential decoding errors.

        Args:
            section_content (str): The content of the section to be processed.

        Returns:
            dict or str: The response from the service, either as a parsed JSON object or an error message.
        """

        app_logger.info(
            f"Content sent to secondary LLM to save content: {section_content}",
            extra={"color": "cyan"},
        )
        # Generate a prompt using the drafting template
        prompt = make_draft_setting_output_prompt(section_content)
        # Send the prompt to an external service (LLM)
        response_str = quick_ask(
            prompt,
            token_counter=get_master_counter_instance(),
            json_output=True,
            timeout=150,
            model_name="gpt-4-0125-preview",
        )
        try:
            # Attempt to parse the response string as JSON
            response = (
                json.loads(response_str)
                if isinstance(response_str, str)
                else response_str
            )
        except json.JSONDecodeError:
            # Handle JSON decoding errors
            response = f"Error parsing response for content {section_content}. Response: {response_str}"
            print(f"\nPrompt was: \n{prompt}")

        app_logger.info(f"Draft Setter outputs:\n{response}", extra={"color": "cyan"})
        app_logger.info(
            f"Draft Setter output type: {type(response)}", extra={"color": "cyan"}
        )

        return response

    def table_setter(self, table_content):
        """
        Processes the section content using a drafting template and sends it to an external service for response
        generation. It parses the JSON response and handles any potential decoding errors.

        Args:
            section_content (str): The content of the section to be processed.

        Returns:
            dict or str: The response from the service, either as a parsed JSON object or an error message.
        """

        # Generate a prompt using the drafting template
        prompt = make_table_setting_output_prompt(table_content)
        # Send the prompt to an external service (LLM)
        response_str = quick_ask(
            prompt,
            token_counter=get_master_counter_instance(),
            json_output=True,
            model_name="gpt-4-0125-preview",
        )
        try:
            # Attempt to parse the response string as JSON
            response = (
                json.loads(response_str)
                if isinstance(response_str, str)
                else response_str
            )
        except json.JSONDecodeError:
            # Handle JSON decoding errors
            response = f"Error parsing response for content {table_content}. Response: {response_str}"
            print(f"Prompt was: \n{prompt}")

        app_logger.info(f"Table Setter outputs:\n{response}", extra={"color": "white"})
        app_logger.info(
            f"Table Setter output type: {type(response)}", extra={"color": "white"}
        )
        return response
