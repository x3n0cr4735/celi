"""
This module serves as a specialized template for the development of a scholarly review paper on Large Multimodal Agents.
The approach outlined here integrates advanced research methodologies with specific tasks designed to enhance the document's quality and coherence.
This job description provides the foundational structure for navigating through the document's sections systematically, complemented by custom instructions per section.
"""
import os
from dotenv import load_dotenv

from celi_framework.core.job_description import JobDescription, Task
from celi_framework.examples.literature_review.tools import LitReviewToolImplementations
from celi_framework.utils.utils import read_txt

load_dotenv()

ROOT_DIR = os.getenv("ROOT_DIR")


task_library = [
    Task(
        task_name="Pull Draft Progress",
        details={
            "description": "Retrieve the current draft status to assess progress and continuity.",
            "function_call": "pull_draft_progress",
            "example_call": "{{'section': 'Current Section'}}",
            "instructions": [
                "Review the current draft to understand what has been completed and what remains.",
                "Ensure continuity and coherence with the previously drafted content.",
            ],
        },
    ),
    Task(
        task_name="Pull Special Instructions",
        details={
            "description": "Retrieve special instructions for the current section to ensure specific requirements are met.",
            "function_call": "pull_special_instructions",
            "example_call": "{{'section': 'Current Section'}}",
            "instructions": [
                "Use the retrieved instructions to tailor the content according to specific guidelines unique to each section.",
            ],
        },
    ),
    Task(
        task_name="Scope Definition",
        details={
            "description": "Define the scope of work for the current drafting session based on the draft progress and special instructions.",
            "instructions": [
                "Outline what will be accomplished during the current session, ensuring alignment with the overall document goals.",
            ],
        },
    ),
    Task(
        task_name="Find Source Materials",
        details={
            "description": "Locate and list all relevant source materials for the section being drafted.",
            "function_call": "find_source_materials",
            "example_call": "{{'section': 'Current Section'}}",
            "instructions": [
                "Gather all necessary references and data sources that will support the content of the section.",
            ],
        },
    ),
    Task(
        task_name="Find Essential Source Materials",
        details={
            "description": "Identify and prioritize critical source materials that are essential for the content of the section.",
            "prerequisite_tasks": ["Find Source Materials"],
            "instructions": [
                "Highlight key sources that provide the most significant insights or data for the section.",
            ],
        },
    ),
    Task(
        task_name="Draft",
        details={
                "description": "Draft the section using the information gathered from the source materials and aligned with the special instructions.",
                "prerequisite_tasks": ["Find Essential Source Materials"],
                "instructions": [
                    "Integrate all collected materials to produce a coherent and scholarly section of the review paper.",
                    "Be mindful of integrating both textual and multimodal data where applicable, ensuring that all references are correctly cited.",
                    "In case of discrepancies or data inconsistencies, consult additional sources or seek clarification from a supervisor."
                ],
            },
        ),
    Task(
        task_name="Review",
        details={
            "description": "Review the newly drafted section to ensure it meets the scholarly standards and adheres to the document's guidelines.",
            "prerequisite_tasks": ["Draft"],
            "instructions": [
                "Critically assess the draft for accuracy, coherence, and alignment with the broader goals of the review paper.",
            ],
        },
    ),
    Task(
        task_name="Redraft",
        details={
            "description": "Make necessary revisions to the draft based on feedback from the review.",
            "prerequisite_tasks": ["Review"],
            "instructions": [
                "Incorporate feedback to enhance the clarity, depth, and scholarly impact of the section.",
            ],
        },
    ),
    Task(
        task_name="Save Draft",
        details={
            "description": "Save the revised draft of the section after all modifications have been made.",
            "prerequisite_tasks": ["Redraft"],
            "function_call": "save_draft",
            "example_call": "{{'section': 'Current Section', 'content': 'Revised Content'}}",
            "instructions": [
                "Ensure the draft is securely saved and accessible for future referencing or continuation of work.",
            ],
        },
    ),
]

general_comments = """
============
General comments:
Start with the first section. Only do the next uncompleted task (only one task at a time).
Explicitly print out the current section identifier.
Explicitly print out whether the last task completed successfully or not.
Explicitly print out the task you are completing currently.
Explicitly print out what task you will complete next.
Explicitly provide a detailed and appropriate response for every task.
The most important thing for you to understand: The primary goal of the tasks is to draft a new section of the document.
A section is considered complete once the 'Save Draft' task has been accomplished. Do not skip the 'Save Draft' task.

If a function call returns an error then try again with parameters, or make a different function call.
If task has not completed successfully, try again with an altered response.
If you notice a task (or series of tasks) being repeated erroneously, devise a plan to move on to the next uncompleted task.
If you encounter empty messages repeatedly in the chat history, reorient yourself by revisiting the last task completed. Check that the sequence of past tasks progresses in logical order. If not, assess and adjust accordingly.

Do not ever return a tool or function call with the name 'multi_tool_use.parallel'
=============
"""

initial_user_message = """
Please see system message for instructions. Take note of which document section is currently being worked on and which tasks have been completed. Complete the next uncompleted task.
If you do not see any tasks completed for the current section, begin with Task #1.

If all tasks for the current section have been completed, proceed to the next document section.
If the new section draft is complete, ensure to 'Prepare for Next Document Section' as described in the tasks.
"""

pre_algo_instruct = """
I am going to give you step by step instructions on how to draft a new literature review document, section by section.
Below you will find a json object that contains the index of sections that need to be drafted.
The keys of the json are the section numbers of the document. The values include the heading title.
"""

guidelines = read_txt(f"{ROOT_DIR}/celi_framework/examples/literature_review/guidelines.txt")
template = read_txt(f"{ROOT_DIR}/celi_framework/examples/literature_review/template.txt")

post_algo_instruct = f"""
Please review the following guidelines and section templates. 
The guidelines articulate what is required in general for the review and document.
The template articulates the expected output for each section drafted for the document.

What I want you to do is to go section by section in the Document to be drafted, and do the following, in sequential order:
"""

role = """
You are a skilled and experienced research assistant tasked with aiding the development and refinement of an agent 
review paper. Your role involves meticulously analyzing, drafting, and revising sections of the paper, ensuring each 
part aligns with specified guidelines and integrates all necessary data and insights.
"""

job_description = JobDescription(
    role=role,
    context="Document to be drafted:",
    task_list=task_library,
    tool_implementations_class=LitReviewToolImplementations,
    pre_context_instruct=pre_algo_instruct,
    post_context_instruct=post_algo_instruct,
    general_comments=general_comments,
    initial_user_message=initial_user_message,
)