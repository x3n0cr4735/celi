from __future__ import annotations

import datetime
import inspect
import json
import logging
import os
import re
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type

import Levenshtein
from pydantic import BaseModel, field_serializer

from celi_framework.core.celi_update_callback import CELIUpdateCallback
from celi_framework.utils.llms import ToolDescription
from celi_framework.utils.utils import (
    encode_class_type,
    read_json_from_file,
    write_string_to_file,
)

logger = logging.getLogger(__name__)


class Task(BaseModel):
    task_name: str
    details: Dict[str, str | List[str] | Dict[str, Any]]

    def with_references_resolved(self, task_numbering: Dict[str, str]) -> Task:
        """Update references in each field and generates a new Task with references replaced."""

        updated_fields = {
            field: self._update_references(getattr(self, field), task_numbering)
            for field in self.model_fields
        }
        return type(self)(**updated_fields)  # type: ignore

    def _update_references(self, item: Any, task_numbering: Dict[str, str]):
        """
        Recursively updates references within an item (which could be a string, list, or dictionary)
        to reflect the dynamically assigned task numbers. This method ensures all references in task
        details, including nested structures, are correctly updated.

        Args:
            item: The content item (str, list, dict) potentially containing task references.
            task_numbering (dict): A mapping from original task names to their dynamically assigned numbers.

        Returns:
            The item with all references updated to reflect their corresponding task numbers.
        """
        if isinstance(item, str):
            # Direct replacement in strings
            for original, new_number in task_numbering.items():
                placeholder = f"{{{{TaskRef:{original}}}}}"
                item = item.replace(placeholder, new_number)
            return item
        elif isinstance(item, list):
            # Process each element in the list
            return [
                self._update_references(sub_item, task_numbering) for sub_item in item
            ]
        elif isinstance(item, dict):
            # Process each value in the dictionary
            return {
                key: self._update_references(value, task_numbering)
                for key, value in item.items()
            }
        else:
            # Non-string, non-list, non-dict items are returned unchanged
            return item


class ToolImplementations(ABC):
    """Each public function in the class becomes a tool that the LLM can use.

    There is one required function, `def get_schema(self) -> Dict[str, str]`.  This function returns a dictionary
    describing the document sections.  The processor will work through the sections, completing the defined tasks for
    each section.  Each dictionary can have any string values, but it is intended to be a section number followed by
    a section name.

    In addition to the `get_schema` function, the ToolImplementations class can have whatever other functions it needs
    to enable celi_framework.  Each function should be documented with type hints and a doc string.  The top section of
    the docstring will be included as the description of the overall function.  If the function takes arguments, there
    should be a section called "Args:" that contains a list of the arguments to the function and descriptions of each.
    An example docstring is given below:

        '''
        Extracts text from specified sections of documents.
        It handles different document types and logs any errors or warnings encountered.
        Returns concatenated text from the specified sections of the documents.
        If there is no content for the section, <empty section> will be returned.

        If the response contains "Error:", then there was a problem with the function call.

        Args:
            sections_dict_str (str): A JSON string mapping document names to their respective section numbers.  The json string will have the documents and sections in a dictionary.  The sections values should correspond to an entry in the table of contents for the specified document.

        '''
    """

    @abstractmethod
    def get_schema(self) -> Dict[str, str]:
        """This function returns a dictionary describing the document sections.  The processor will work through the
        sections, completing the defined tasks for each section.  Each dictionary can have any string values,
        but it is intended to be a section number followed by a section name."""
        pass


class BaseDocToolImplementations(ToolImplementations, ABC):
    """A base class for ToolImplementations that draft documents.  Adds a standard `update_draft_doc` tool."""

    def __init__(
        self,
        drafts_dir: str = "target/celi_output/drafts",
        callback: Optional[CELIUpdateCallback] = None,
    ):
        os.makedirs(drafts_dir, exist_ok=True)
        self.callback = callback
        self.draft_doc = (
            f"{drafts_dir}/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        )
        logger.info(f"Writing output to {self.draft_doc}")

    def save_draft_section(self, doc_section: str, draft: str):
        """Saves a draft of the current section.

        This must be called with the final output before calling pop_context and moving on to the next section.

        Args:
            doc_section: The section name to save
            draft: The draft text
        """
        matched_section = self.match_doc_section(doc_section)
        logger.info(
            f"Completed section {doc_section} ({matched_section}).  Draft output is:\n{draft}",
            extra={"color": "orange"},
        )
        if self.callback:
            self.callback.on_output(matched_section, draft)

        logger.info(f"Adding section {doc_section} to {self.draft_doc}")
        try:
            current = read_json_from_file(self.draft_doc)
        except FileNotFoundError:
            current = {}
        current[doc_section] = draft
        write_string_to_file(json.dumps(current, indent=2), self.draft_doc)

    def match_doc_section(self, doc_section):
        # Try to extract a number first
        number = BaseDocToolImplementations._extract_number(doc_section)
        if number is not None:
            return str(number)

        # If no number found, get the closest match from the dictionary
        return BaseDocToolImplementations._find_closest_match(
            doc_section, self.get_schema()
        )

    @staticmethod
    def _extract_number(doc_section):
        # Find all numbers in the string
        numbers = re.findall(r"\d+", doc_section)
        if numbers:
            return int(numbers[0])  # Return the first number found as an integer
        return None

    @staticmethod
    def _find_closest_match(section, schema_dict):
        closest_key = None
        closest_distance = float("inf")

        for key, value in schema_dict.items():
            distance = Levenshtein.distance(section, value)
            if distance < closest_distance:
                closest_distance = distance
                closest_key = key

        return closest_key


class JobDescription(BaseModel):
    """
    Specifies a configuration for MasterTemplateFactory

    This configuration file is a critical component of the automated document drafting framework, designed to work in tandem with the `MasterTemplateFactory` class. It outlines a series of structured tasks and instructions that guide the drafting process for various types of documents, emphasizing step-by-step clarity and comprehensive coverage of necessary content.

    Key Components:
    - `role`: Specifies the user's role in an interactive context, emphasizing active participation in defining the drafting objectives.
    - `context`: Establishes the theme of "Interactive Data Collection," indicating a focus on user engagement and data-driven task generation for document drafting.
    - `task_list`: A comprehensive collection of tasks, each defined with a unique task name, a brief description, specific instructions, and examples. These tasks form the backbone of the document drafting process, guiding users or AI agents through each step required to compile a thorough and accurate document.
    - `general_comments` and `user_message`: Provide overarching guidance and specific instructions to users or AI agents undertaking the drafting tasks. These sections ensure that the drafting process is approached systematically, with clear expectations for each task's completion.
    - `pre_algo_instruct` and `post_algo_instruct`: Introductory and concluding instructions that frame the drafting tasks within a broader context, helping to orient the user or AI agent to the document's overall structure and objectives.
    - `config`: A dictionary consolidating all elements of the configuration, including the role of the user or AI agent, the context for the drafting tasks, and the structure of the task list. Additional parameters like `include_prerequisites` and `final_output_task` further customize the drafting guidance provided by the `MasterTemplateFactory`.
    - 'include_schema_in_system_message': A bool (defaults to True) indicating whether the system message should include the schema.  This is useful if the different items in the schema relate to each other (like sections in a document), but not if they are independent (like different test cases in a benchmark)
    - 'monitor_instructions': Explicit items for the monitor to pay attention to.

    Usage:
    This configuration file is intended for use with the `MasterTemplateFactory` class to generate dynamic, structured instructions for drafting or analyzing documents. By defining tasks, prerequisites, and contextual guidance, it enables the automated creation of detailed documents across a variety of fields, including but not limited to technical documentation, and research reporting.

    Example Usage:
    The configuration is dynamically loaded by the `MasterTemplateFactory` to create a tailored set of instructions and tasks based on the specific requirements of the document being drafted. The factory class utilizes the `task_list` to generate a step-by-step guide for users or AI agents, incorporating `general_comments` and `user_message` to provide additional context and clarity.

    By structuring the document drafting process around this configuration, the `MasterTemplateFactory` ensures that each section of the document is developed with precision, adhering to the required standards and content specifications outlined in the `task_library`.
    """

    role: str
    context: str
    task_list: List[Task]
    tool_implementations_class: Type
    pre_context_instruct: Optional[str] = None
    post_context_instruct: Optional[str] = None
    general_comments: str = ""
    initial_user_message: str
    include_schema_in_system_message: bool = True
    monitor_instructions: str = ""

    @field_serializer("tool_implementations_class")
    def serialize_type(self, t: Type, _info):
        return encode_class_type(t)


def generate_tool_description(method: Callable) -> ToolDescription:
    """Generates a tool description from a member function object.

    Expects a docstring formatted like this one.  It uses that for method and parameter descriptions.
    Uses type hints for determine parameter types

    Args:
        method (Callable): A member function object to createc a ToolDescription for."""

    # Extracting the method's docstring and name
    method_name = method.__name__
    docstring = inspect.getdoc(method) or ""
    parts = docstring.split("Args:")
    description = parts[0].strip()
    args = "" if len(parts) == 1 else parts[1].strip()

    # Extracting parameters and their annotations, skipping 'self'
    sig = inspect.signature(method)
    parameters = {}
    # logger.debug(f"Inspecting {method}: {sig}")
    for param_name, param in sig.parameters.items():
        if param_name == "self":  # Skip 'self' parameter
            continue
        # logger.debug(f"Param {param}")

        if param.annotation == param.empty:
            param_type_dict = {"type": "string"}
        elif param.annotation == "str" or param.annotation.__name__ == "str":
            param_type_dict = {"type": "string"}
        elif param.annotation.__name__ == "List":
            param_type_dict = {"type": "array", "items": {"type": "string"}}
        else:
            param_type_dict = {"type": param.annotation.__name__}

        param_description = "No description provided."  # Default description
        # Extracting parameter description from docstring (if available)
        if param_name in args:
            # Looks for the parameter name and then takes from the next colon to the end of the line as the parameter description.
            param_description = (
                docstring.split(param_name)[1].split(":")[1].split("\n")[0].strip()
            )
        parameters[param_name] = {
            **param_type_dict,
            "description": param_description,
        }

    # Creating an instance of ToolDescription
    tool_description = ToolDescription(
        name=method_name,
        description=description,
        parameters={
            "type": "object",
            "properties": parameters,
            "required": list(parameters.keys()),
        },
    )
    return tool_description


def generate_tool_descriptions(cls: Type) -> List[ToolDescription]:
    descriptions = []
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith("_"):
            descriptions.append(generate_tool_description(attr))
    return descriptions
