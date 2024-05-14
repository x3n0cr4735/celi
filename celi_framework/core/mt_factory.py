"""
Module: templates.master_instructions_notes.factory

This module is integral to the creation of structured instructions and tasks for a variety of document
drafting processes. The MasterTemplateFactory class at its core is designed to support a wide range of
applications, from study reports to any structured document requiring detailed,
step-by-step instructions for creation or analysis.

By leveraging a rich library of tasks, the MasterTemplateFactory enables the generation of comprehensive
guides that facilitate the automated drafting or analysis of documents. These guides are pivotal in ensuring
efficiency, consistency, and adherence to specific guidelines or standards across diverse domains.

Classes:
    MasterTemplateFactory: A versatile class that generates structured instructions and tasks, adaptable
    to various drafting and analytical needs.

This module represents a flexible tool for automating and enhancing the document creation process,
capable of catering to a broad spectrum of document types and requirements.
"""

from typing import Dict

from celi_framework.core.job_description import JobDescription, Task
from celi_framework.utils.utils import generate_hash_id


class MasterTemplateFactory:
    """
    A versatile factory class for generating structured instructions and tasks applicable to various
    document drafting or analytical processes. It abstracts the complexity of document planning into
    actionable, step-by-step guides, making it a valuable asset for automating document creation across
    different fields.

    Attributes:
        config (dict): Configuration details including user roles, drafting contexts, and specific task lists.
        schema (dict): The schema or structural blueprint of the document to be created or analyzed.
        role (str): The intended role of the user or system utilizing the generated instructions,
                    allowing for tailored guidance.
        context (str): The overarching context or scope of the document-related tasks, ensuring
                       relevance and focus.
        task_list (dict): A detailed compilation of tasks, each with specific descriptions and operational instructions.
        final_output_task (str): The designated concluding task of the process, marking the endpoint of the instruction set.
        general_comments (str): Supplementary comments or notes providing additional insights or clarifications.
        user_message (str): A customizable message to convey specific instructions or information to the user or system.
        include_prerequisites (bool): A flag indicating whether prerequisite tasks should be included in the instructions.
        id (str): A unique identifier for the generated template, facilitating traceability and version control.

    Methods:
        __init__(config, schema): Prepares the factory with necessary configurations and the document schema for instruction generation.
        get_algorithm_setup_section(): Constructs the introductory section of the algorithm, establishing the groundwork for subsequent tasks.
        get_tasks_section(include_prerequisites): Assembles the tasks section, detailing each task's execution pathway, optionally including prerequisites.
        create_system_message(): Synthesizes the setup instructions, task details, and general comments into a unified system message for users or systems.

    The MasterTemplateFactory is designed to bridge the gap between conceptual document planning and practical execution,
    offering a systematic approach to document creation and analysis that enhances productivity, consistency, and quality
    across a wide array of applications.
    """

    def __init__(self, job_desc: JobDescription, schema: Dict[str, str]):
        """
        Initializes the MasterTemplateFactory with the provided configuration and schema, setting up the necessary
        attributes for generating structured document instructions. This method prepares the factory to create
        actionable, step-by-step guides tailored to specific document creation or analysis needs across various domains.

        Args:
            config (dict): A dictionary containing configuration details that guide the instruction generation process.
                           This includes information such as the role of the user, the context of the tasks, specific
                           task lists to be included, and any general comments or user messages to be incorporated.
            schema (dict): A dictionary representing the structural blueprint of the document to be created or analyzed.
                           The schema defines the organization, sections, and expected content, providing a framework
                           for the task generation process.

        The initialization process ensures that the factory is equipped with all the information needed to generate
        precise and relevant instructions, facilitating efficient and effective document drafting or analysis workflows.
        """

        self.job_desc = job_desc
        self.schema = schema
        # Generate a unique template ID based on the hash of the config string
        hash_obj = str(job_desc) + str(schema)
        self.id = generate_hash_id(hash_obj)

    def get_algorithm_setup_section(self):
        """
        Generates the initial setup section of the instruction set, providing foundational context and guidelines
        for the document drafting or analysis process. This section outlines the role of the user, the overall
        objective, and the structural approach to be taken, setting the stage for the detailed tasks that follow.

        Returns:
            str: A string containing the setup instructions, including an introduction to the document creation
                 or analysis process, the user's role, and the context within which the tasks are to be performed.
                 This setup section is designed to orient users or systems towards the goals and expectations
                 of the process, ensuring a clear understanding of the task ahead.

        This method plays a crucial role in ensuring that the instructions begin with a clear and comprehensive
        overview, laying a solid foundation for the successful execution of subsequent tasks.
        """
        schema = (
            f"{self.schema}\n\n"
            if self.job_desc.include_schema_in_system_message
            else ""
        )

        return (
            f"{self.job_desc.role}\n\n"
            f"{self.job_desc.pre_context_instruct}\n\n"
            f"{self.job_desc.context}\n"
            f"{schema}"
            f"{self.job_desc.post_context_instruct}\n\n"
        )

    def get_numbered_tasks(self):
        """
        Returns a version of this class's task list including dynamically assigned numbers and updated references
        to other tasks within the task details to reflect these numbers.
        """
        # Generate a mapping of task names to their dynamically assigned numbers
        # This is done by enumerating over the keys (task names) in the task list and formatting each task number as "Task {i+1}"
        task_numbering = {
            task.task_name: f"Task {i + 1}"
            for i, task in enumerate(self.job_desc.task_list)
        }

        # Initialize an empty dictionary to hold the updated task list
        numbered_task_list = {
            task_numbering[task.task_name]: task.with_references_resolved(
                task_numbering
            )
            for task in self.job_desc.task_list
        }
        return numbered_task_list

    def create_system_message(self):
        """
        Generates a comprehensive system message that includes all tasks with updated references. The system message
        is composed of the algorithm setup section, the tasks section, and the general comments. Each part is separated
        by two newline characters for readability.

        Returns:
            str: A string that comprises the algorithm setup section, the tasks section, and the general comments,
                 with each part separated by two newline characters.
        """

        # Call the method to dynamically number and update tasks in the task list
        numbered_task_list = self.get_numbered_tasks()

        # Initialize a list to hold the parts of the system message
        system_message_parts = [
            # The first part is the algorithm setup section
            self.get_algorithm_setup_section(),
            # The second part is the tasks section, which is created by joining each task's name and formatted details
            # with newline characters, and then joining all tasks with two newline characters
            "\n\n".join(
                [
                    f"{name}\n{self._format_task_details(task)}"
                    for name, task in numbered_task_list.items()
                ]
            ),
            # The third part is the general comments, which is retrieved from the configuration
            self.job_desc.general_comments,
        ]

        # Join the parts of the system message with two newline characters, excluding any parts that are empty,
        # and return the resulting string
        return "\n\n".join(part for part in system_message_parts if part)

    def _format_task_details(self, task: Task):
        """
        Formats the details of a task for inclusion in the system message. If the value of a detail is a list, each item
        in the list is preceded by a dash and a space. The key of each detail is capitalized.

        Args:
            details (dict): A dictionary of details belonging to a task.

        Returns:
            str: A string that comprises the formatted details of a task, with each detail separated by a newline character.
        """

        # Initialize an empty list to hold the formatted details
        formatted_details = []

        # Iterate over each detail in the provided dictionary
        for key in task.model_fields:
            value = getattr(task, key)
            # Ignore empty values.
            if value:
                # Check the type of the detail's value
                if isinstance(value, list):
                    # If the value is a list, format each item in the list with a preceding dash and a space,
                    # then join the items into a single string separated by newline characters
                    formatted_value = "\n".join(f"- {item}" for item in value)
                    # Append the formatted detail to the list of formatted details, with the detail's key capitalized and followed by a colon
                    formatted_details.append(f"{key.capitalize()}:\n{formatted_value}")
                else:
                    # If the value is not a list, append the formatted detail to the list of formatted details,
                    # with the detail's key capitalized and followed by a colon, and the value as is
                    formatted_details.append(f"{key.capitalize()}: {value}")

        # Join the list of formatted details into a single string separated by newline characters and return it
        return "\n".join(formatted_details)

    def print_system_message(self):
        print(self.create_system_message())

    def print_initial_user_message(self):
        # Print user instructions based on the task progression
        print(self.job_desc.initial_user_message)
