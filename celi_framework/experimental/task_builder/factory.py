"""
The `templates.task_builder.factory` module is part of a larger framework designed to automate and simplify the process of document drafting and analysis. At the heart of this module is the `InteractiveDocumentTemplate` class, which extends the `MasterTemplateFactory` to provide a more interactive and user-centric approach to document creation. This module leverages a configurable task library to generate detailed, numbered tasks and a comprehensive system message that guides users through each step of the document drafting or analysis process.

The `InteractiveDocumentTemplate` class is specifically tailored to support a variety of document types and requirements, making it a versatile tool for projects ranging from writing to technical documentation. It ensures that users or AI agents can follow a clear, sequential path through the drafting process, enhancing understanding and efficiency.

Key Features:
- Inherits and extends the `MasterTemplateFactory` class to support interactive document drafting.
- Dynamically numbers tasks and enriches them with detailed descriptions for clarity.
- Generates a comprehensive system message that includes the user role, context, detailed tasks, general comments, and a user message.
- Utilizes a configuration and schema to tailor the drafting guide to specific document types and drafting goals.
"""

from celi_framework.core.mt_factory import MasterTemplateFactory
from celi_framework.experimental.task_builder.template import job_description


class InteractiveDocumentTemplate(MasterTemplateFactory):
    """
    The `InteractiveDocumentTemplate` class extends the `MasterTemplateFactory` to offer enhanced capabilities for generating interactive and structured instructions for document drafting and analysis. This class focuses on creating a user-friendly experience by systematically numbering tasks and compiling a comprehensive system message that includes all necessary details for each task. It's particularly suited for applications requiring a guided approach to document creation, ensuring that users or AI agents can follow a clear, sequential path through the drafting process.

    Attributes:
        Inherits all attributes from the `MasterTemplateFactory`, utilizing them to construct a detailed and interactive guide for document drafting.

    Methods:
        __init__(config, schema):
            Initializes the `InteractiveDocumentTemplate` with a given configuration and document schema. It leverages the superclass initialization to set up the foundational structure for task generation and then extends it with interactive functionalities.

        number_and_detail_tasks():
            Enhances the task list by assigning sequential numbers to each task and appending detailed descriptions. This method ensures that tasks are presented in a clear, ordered manner, facilitating easy navigation and comprehension for users.

        create_system_message():
            Overrides the parent class method to produce a detailed system message. This message incorporates the user role, context, and a list of numbered, detailed tasks, along with any general comments and user-specific messages. The generated system message serves as a comprehensive guide, encapsulating all the instructions, tasks, and additional notes necessary for completing the document drafting or analysis process.
    """

    def __init__(self, config, schema):
        """
        Initializes the InteractiveDocumentTemplate with configuration and schema,
        leveraging the base class initialization.
        """
        super().__init__(config, schema)
        # Additional initialization specific to the interactive template can be added here

    def number_and_detail_tasks(self):
        """
        Processes the task list to assign numbers and prepare detailed descriptions for each task.
        """
        numbered_tasks = {}
        for i, (task_name, task_details) in enumerate(self.task_list.items(), start=1):
            numbered_tasks[f"Task {i}: {task_name}"] = task_details["description"]
        self.task_list = numbered_tasks  # Update the task list with numbered tasks

    def create_system_message(self):
        """
        Overrides the parent method to generate a detailed system message that includes the user role,
        a high-level description, and the detailed, numbered tasks.
        """
        system_message_parts = [
            f"Role: {self.role}",
            f"Context: {self.context}\n",
            "Tasks to be completed:",
        ]

        # Append numbered tasks to the system message
        for task_name, task_description in self.task_list.items():
            system_message_parts.append(f"{task_name}: {task_description}")

        # Include general comments and user message if provided
        if self.general_comments:
            system_message_parts.append(f"\nGeneral Comments:\n{self.general_comments}")
        if self.user_message:
            system_message_parts.append(f"\nUser Message:\n{self.user_message}")

        return "\n".join(system_message_parts)


# Example Usage
if __name__ == "__main__":
    schema = {}  # Placeholder for document schema

    interactive_template = InteractiveDocumentTemplate(config, schema)
    interactive_template.number_and_detail_tasks()  # Process tasks to number them and prepare detailed descriptions
    system_message = interactive_template.create_system_message()
    print(system_message)
