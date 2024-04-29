"""
This module serves as a generic template. It is designed to be adaptable for
a broad range of reports and is not specific to any particular field.
The tasks, function calls, and methodologies described herein are intended to provide a foundational
structure for document analysis and drafting, which can be customized to meet the needs of various
reporting requirements.
"""

from celi_framework.core.job_description import JobDescription, Task
from celi_framework.examples.AP_English_Language.tools import APEnglishLanguageToolImplementations

# TODO: Get the "GRE Way" of doing free response questions for the GRE
#  Refactor the tasks below that are taking as example
#  need to also pull in examples, and set this up as one-shot using prior one-shot prompt engineering work"
# TODO: Note that this is in the general comments: A section is considered complete once the 'Final Answer Review' task has been accomplished. Do not skip the 'Final Answer Review' task.
task_library = [
    Task(
        task_name="Search for Document Section Text",
        details={
            "description": "Find and retrieve the text for a specific section within the document.",
            "prerequisite_tasks": [],
            "function_call": "Perform a function call to retrieve the section's text.",
            "example_call": "{{'Document': ['Section Identifier']}}",
            "instructions": [
                "Ensure every section has corresponding text, noting empty sections without modification.",
                "If encountering an error, attempt again with different parameters.",
            ],
        },
    ),
    Task(
        task_name="Understand Differentiation",
        details={
            "description": "Analyze the context of the document's section by comparing it with similar sections.",
            "prerequisite_tasks": ["Search for Document Section Text"],
            "instructions": [
                "Identify similar sections within the document, retrieving their text for comparison.",
                "Document the differences to ensure uniqueness and prevent duplication.",
            ],
            "example": {
                "Example Section 1": "Example text...",
                "Example Section 2": "Another example text...",
            },
            "additional_notes": [
                "Keep notes concise and relevant for future use.",
            ],
        },
    ),
    Task(
        task_name="Redraft Section for Relevant Content",
        details={
            "description": "Review and adjust detailed content within the section for relevance and conciseness.",
            "prerequisite_tasks": ["Search for Document Section Text"],
            "instructions": [
                "If the section focuses solely on the primary topic, proceed directly to the next task.",
                "For sections including additional detailed content, summarize or omit as necessary while maintaining coherence.",
            ],
            "examples": {
                "to_exclude": [
                    "Example of detailed content to potentially exclude or summarize.",
                ],
                "not_to_exclude": [
                    "Example of essential content to retain.",
                ],
            },
        },
    ),
    Task(
        task_name="Identify Document Source",
        details={
            "description": "Determine the source materials for the document's section.",
            "function_call": "Call the source_materials_retrieval function.",
        },
    ),
    Task(
        task_name="Find Essential Source Materials",
        details={
            "description": "Prioritize the most critical source materials for drafting the document's section.",
            "prerequisite_tasks": ["Identify Document Source"],
            "task": "Organize these materials by relevance in a bulleted list.",
        },
    ),
    Task(
        task_name="Get Source Table of Contents",
        details={
            "description": "Retrieve the Table of Contents (TOC) for essential source documents for the current section.",
            "function_call": "Call get_source_tocs.",
            "example_call": "{{'current_section': 'Section Identifier'}}",
            "instructions": [
                "Retrieve TOCs without modification, focusing on relevance to the current section.",
            ],
        },
    ),
    Task(
        task_name="Map Example Document Sources to New Source ToCs",
        details={
            "description": "Align the example source document sections with the current document's sources.",
            "prerequisite_tasks": ["Identify Document Source"],
            "instructions": [
                "For each of the example document's source sections find the sections in the new document's sources "
                "that would have the most similar content thematically (not by document numbering).",
            ],
        },
    ),
    Task(
        task_name="Handle Document Subsections",
        details={
            "description": "Identify subsections of the new document source sections that may be relevant as sources "
                           "for the new document",
            "prerequisite_tasks": ["Map Example Document Sources to New Source ToCs"],
        },
    ),
    Task(
        task_name="New Reference Material Retrieval",
        details={
            "description": "Retrieve text for new source sections identified as critical.",
            "prerequisite_tasks": ["ap Example Document Sources to New Source ToCs"],
            "function_call": "section_text_getter",
            "example_call": "{{ 'New Document': ['Section Identifiers'], 'New Guidelines': ['Identifiers'] }}",
        },
    ),
    Task(
        task_name="Draft New Document Section",
        details={
            "description": "Draft a new section analogous to the revised example section content (from {{TaskRef:Redraft Section for Relevant Content}} output), ensuring alignment with its structure, format, and scope (from {{TaskRef:Understand Differentiation}} output).",
            "guidelines": [
                "The new section should have its unique scope and purpose, distinct from the example section.",
                "Closely align with the example section's approach for consistency.",
                "Avoid duplicating content or including redundant information.",
                "Aim for the new section to mirror the example section in length and detail.",
                "Follow the instructions set out by {{TaskRef:Understand Differentiation}} output.",
            ],
            "prerequisite_tasks": "All prior tasks.",
            "considerations": [
                "What differentiates this section from other similar sections? Refer to the output of {{TaskRef:Understand Differentiation}}.",
                "Concentrate on content relevant to the specific section within the broader document context.",
                "Maintain consistency in documentation methodology, using the revised example as a template.",
                "Ensure content is derived exclusively from the newly identified source materials.",
            ],
            "specific_instructions": [
                "Do not copy text verbatim. Include only text within the scope of the current section, as highlighted in the output of {{TaskRef:Understand Differentiation}}.",
                "Include cross-references to other sections as seen in the example if applicable.",
                "Incorporate references to tables and sections within the new reference documents as appropriate, providing context to the study's methodology and decision-making processes.",
            ],
            "note": "Focus on the specific section, considering its role within the parent sections and its relation to the revised example section. Utilize the guidance from {{TaskRef:Understand Differentiation}} for the scope of the section",
        },
    ),
    Task(
        task_name="Final Document Review",
        details={
            "description": "Review the final document and provide a PASS/FAIL decision based on the success criteria.",
            "prerequisite_tasks": ["Draft New Document Section"],
            "instructions": [
                "Evaluate the success of the new section draft",
                "Document the review outcome",
                "Print the final review output.",
            ],
            "success_flag_criteria": {
                "FAIL": [
                    "The section includes information beyond what's relevant as indicated by {{TaskRef:Understand Differentiation}}.",
                    "Information in the new section is redundant with other sections analyzed in {{TaskRef:Understand Differentiation}}.",
                    "The draft does not reflect the structure, format, or detail level of the revised example section (output of {{TaskRef:Redraft Section for Relevant Content}}).",
                    "Missing or incorrectly referenced tables or figures from the new reference materials.",
                    "Significant deviation from the new reference materials, suggesting misalignment with the report's current focus.",
                    "Inconsistent use of verb tenses where required.",
                ],
                "PASS": [
                    "The section appropriately includes information within the scope defined by {{TaskRef:Understand Differentiation}}.",
                    "The draft logically follows what the section heading describes.",
                    "The draft focuses exclusively on the new report's context.",
                    "The draft meets criteria for completeness, accuracy, and is aligned with the revised example and the new reference materials.",
                ],
            },
            "additional_instructions": "Offer feedback on the process of differentiating from other sections, the use of source materials, and the rationale for selected source mappings.",
            "output_format": {
                "Section Review": "[SECTION NUMBER] - [SECTION HEADING]",
                "Draft Review": "[content here]",
                "Comments": "[comments here]",
                "Success Flag": "[FAIL/PASS]",
                "Source Mapping Review": "[REVIEW OF UTILIZED SOURCES]",
                "Tables": "[LIST OF REFERENCED TABLES]",
                "Figures": "[LIST OF REFERENCED FIGURES]",
                "Cross-References": "[REFERENCES TO OTHER DOCUMENT SECTIONS (FROM SAMPLE DOCUMENT)]",
                "Scope of Section Review": "[REFLECTION ON FOLLOWING THE SCOPE GUIDELINES SET OUT IN {{TaskRef:Understand Differentiation}} OUTPUT]",
            },
        },
    ),
    Task(
        task_name="Prepare for Next Document Section",
        details={
            "description": "Conclude current tasks and prepare to draft the next document section.",
            "prerequisite_tasks": ["Final Document Review"],
            "function_call": "Use the pop_context function.",
            "example_call": "{{'current_section_identifier': ['Next Section Identifier']}}",
        },
    ),
]

general_comments = """
============
General comments:
Start with the first test question. 
Explicitly print out the current question number.
Explicitly print out the task you are completing currently.
Explicitly provide a detailed and appropriate response for the task.
The most important thing for you to understand: The primary goal of the tasks is to answer the test question that you have been presented.
A section is considered complete once the 'Final Answer Review' task has been accomplished. Do not skip the 'Final Answer Review' task.

If a function call returns an error then try again with parameters, or make a different function call.
If task has not completed successfully, try again with an altered response.
If you notice a task (or series of tasks) being repeated erroneously, devise a plan to move on to the next uncompleted task.
If you encounter empty messages repeatedly in the chat history, reorient yourself by revisiting the last task completed. Check that the sequence of past tasks progresses in logical order. If not, assess and adjust accordingly.

Do not ever return a tool or function call with the name 'multi_tool_use.parallel'
=============
"""

initial_user_message = """
Please see system message for instructions. 
If you do not see any tasks completed for the current test question, begin with Task #1.

If all tasks for the current test question have been completed, proceed to the next document section.
If the new section draft is complete, ensure to 'Prepare for Next Document Section' as described in the tasks.
"""

pre_algo_instruct = """
I am going to give you step by step instructions on how to draft a free response to a test question.
Below you will find a json object that contains the index of test questions that need to be responded to.
The keys of the json are the question numbers (q1) of the free response section of a test. The values are the respective topics.
"""

post_algo_instruct = """
We will look at a completed example free response test section that is similar to the test to be worked on.
Its full content can be queried with a function (example_question_text_getter) and used as an example (in json format).
The keys of the json are the question numbers (q1) of the free response test section and the values contain the questions and answers.
Question n of the examples lines up with question n in the test section being worked on.
What I want you to do is to go question by question in the test section, and do the following, in sequential order:
"""

job_description = JobDescription(
    role="You are a professional test taker AI agent. You have the ability to call outside functions.",
    context="Free response test sections to be responded to:",
    task_list=task_library,
    tool_implementations_class=GREToolImplementations,
    pre_context_instruct=pre_algo_instruct,
    post_context_instruct=post_algo_instruct,
    general_comments=general_comments,
    initial_user_message=initial_user_message,
)
