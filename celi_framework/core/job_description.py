from __future__ import annotations
from abc import ABC, abstractmethod
import inspect
from typing import Any, Callable, Dict, List, Optional, Type

from celi_framework.utils.llms import ToolDescription

from pydantic import BaseModel, field_serializer
from celi_framework.utils.utils import encode_class_type


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

    There is one required function, `def get_schema(self) -> Dict[str, str]`.  This function returns a dictionary describing the document sections.  The processor will work through the sections, completing the defined tasks for each section.  Each dictionary can have any string values, but it is intended to be a section number followed by a section name.

    In addition to the `get_schema` function, the ToolImplementations class can have whatever other functions it needs to enable celi_framework.  Each function should be documented with type hints and a doc string.  The top section of the docstring will be included as the description of the overall function.  If the function takes arguments, there should be a section called "Args:" that contains a list of the arguments to the function and descriptions of each.  An example docstring is given below:

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
        "This function returns a dictionary describing the document sections.  The processor will work through the sections, completing the defined tasks for each section.  Each dictionary can have any string values, but it is intended to be a section number followed by a section name."
        pass


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
    for param_name, param in sig.parameters.items():
        if param_name == "self":  # Skip 'self' parameter
            continue

        if param.annotation == param.empty:
            param_type_dict = {"type": "string"}
        elif param.annotation.__name__ == "str":
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
