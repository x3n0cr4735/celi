"""
Module: templates.task_builder.llms

This module serves as a crucial component within the interactive task builder framework, specifically designed to enumerate the functions available for Large Language Models (LLMs) to use in interactive document drafting and analysis processes. Unlike the `utils.llms` module, which includes both utility functions for interacting with LLMs and the API calls themselves, `templates.task_builder.llms` exclusively provides a list of function calls that can be utilized by LLMs in the context of the task builder.

The module outlines a series of function entries, each detailing the name, description, and parameters of functions that LLMs can invoke to gather user input, assess file information, and sample document content. These function calls are integral to facilitating dynamic and user-responsive task generation, enabling the `InteractiveDocumentTemplate` to incorporate real-time data and inputs into the document drafting workflow.

Function Call Entries:
- The entries within this module represent callable actions that LLMs can perform as part of the interactive document drafting process. Each entry includes:
  - `name`: The identifier of the function, used for invoking the specific action within the LLM environment.
  - `description`: A brief overview of the function's purpose and its role in the interactive task generation process.
  - `parameters`: A detailed list of parameters that the function expects, each with its own description, helping to guide the LLM in performing the function call accurately.

Purpose:
The primary objective of this module is to act as a reference for the `InteractiveDocumentTemplate` class, aiding in the identification and invocation of functions that LLMs can execute to enhance the interactive drafting process. By providing a clear list of available function calls, it ensures that LLMs can effectively contribute to task generation, user interaction, and content analysis, making the document drafting process more adaptive and user-focused.

Note:
This module is specific to the interactive task builder's context and should be used in conjunction with the `InteractiveDocumentTemplate` class to dynamically generate tasks that respond to user inputs and document content, enhancing the document creation workflow.
"""

# TODO: We no longer need to list and describe available tools separately from llm_helper_funcs.
#  The descriptions are automatically pulled from the tool definition docstrings if you use ToolImplementations.

functions = [
    # Existing function entries...
    # Interactive Input Handler
    {
        "name": "interactive_input_handler",
        "description": "Interactively collects user input based on a provided question and simulates an LLM response.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The question to ask the user.",
                }
            },
            "required": ["question"],
        },
    },
    # OS File Info Handler
    {
        "name": "os_file_info_handler",
        "description": "Gathers information about files in a specified directory, including file formats, count, and total size.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "The directory to assess for file information.",
                }
            },
            "required": ["directory"],
        },
    },
    # Document Sampler Handler
    {
        "name": "document_sampler_handler",
        "description": "Samples text data from a specified number of documents within a directory, supporting formats like PDF.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "The directory from which to sample documents.",
                },
                "sample_count": {
                    "type": "string",
                    "description": "The number of documents to sample for text data.",
                },
            },
            "required": ["directory", "sample_count"],
        },
    },
]
