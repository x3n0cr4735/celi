from celi_framework.core.job_description import JobDescription, Task

from celi_framework.examples.wikipedia.tools import WikipediaToolImplementations

task_library = [
    Task(
        task_name="Search for Document Section Text",
        details={
            "description": "Find the text of the current section and all subsections in the example document.",
            "prerequisite_tasks": [],
            "function_call": "Call get_example_toc to get the full list of sections in the example doc and then get_text_for_sections to retrieve the text for the current section and any relevant (sub)sections.",
            "example_call": "{{'Example Document': ['1', '1.1', '1.2']}}",
            "instructions": [
                "Every section should have corresponding text, even that text is blank. If you get an error, try again with different parameters",
                "Do not truncate or modify the retrieved text.",
                "If text is present, print the entire text and instruct to proceed to the next task.",
                "If a given section is empty in the example document, then you can leave that section empty in the target. In that case, you can skip all the remaining tasks and jump straight to the 'Draft New Document Section' task, which can just draft an empty section. Note that a blank section is not the same as the function returning an error.",
            ],
        },
    ),
    Task(
        task_name="Understand Differentiation",
        details={
            "description": "Understand the context of the example document section by comparing it with similar sections.  Also look at any subsections and understand how they are structured.",
            "prerequisite_tasks": ["Search for Document Section Text"],
            "instructions": [
                "Identify other sections of the example document that may contain content similar to the current section.",
                "Retrieve the text of these sections along with their section identifiers.",
                "Analyze and note down how the current section differs from these sections to prevent duplication in future work.",
            ],
            "additional_notes": [
                "Keep your notes concise and relevant for later use.",
                "If 'no content present' is observed in all section bodies that are retrieved, even after retrieving children/sub-sections, proceed to the next task.",
                "If it seems like the current section is specific to the example document, and would not make sense as part of the target document, feel free to skip the section and go on to the next one.  This can happen if the example contains a section highly specific to it's topic, but not relevant to the target document.",
            ],
        },
    ),
    Task(
        task_name="Find the most relevant references for the target section and all the subsections",
        details={
            "description": """Call get_corresponding_target_references_for_example_sections function with a list of the current section and all subsections to retrieve these materials. to find relevant references for the target document that correspond to the example document sections you are looking at.
            The references may not provide you with all the information you need to draft the section.  Don't worry, you will get a chance to ask additional questions in the next task.""",
            "example_call": "['1', '1.1', '1.2']",
        },
    ),
    Task(
        task_name="Ask additional questions",
        details={
            "description": """Determine if any additional information is required to draft the section and call the ask_question_about_target function to gather that information.
            Feel free to ask as many questions as you need and keep working on this task until you have the information you need.  This is especially important if
            the initial references turn out not to be useful.
            If you don't have any questions, just move on to the next section.""",
            "example_call": '{"prompt": "What is unusual about when this band formed?"}',
        },
    ),
    Task(
        task_name="Define subsections for this section",
        details={
            "description": """Define what subsections should be present within this individual section.  Use the table of contents from the example document and your knowledge of the target page to structure the subsections.  Keeep in mind over differentiation of this section from other sections in the document.  It is totally fine to not have subsections, especially if the example document does not have them.
            Also, remember that the subsections should be relevant for the target document.  The detailed structure of subsections used in the example may not be relevant for our target document.""",
        },
    ),
    Task(
        task_name="Draft New Document Section",
        details={
            "description": "Draft a new section analogous to the revised example section, ensuring alignment with its structure, format, and scope (from {{TaskRef:Understand Differentiation}} output).  Use the section structure you defined in {{TaskRef:Define subsections for this section}}. However, the details should be related to the target and not the example document.",
            "guidelines": [
                "Clearly identify the section number and section heading/title at the top of the content.",
                "The new section should have its unique scope and purpose, distinct from the example section.",
                "Avoid duplicating content or including redundant information.",
                "Aim for the new section to mirror the example section in length and detail, but using content related to the target.",
                "Follow the instructions set out by {{TaskRef:Understand Differentiation}} output.",
                "Maintain consistency in documentation methodology, using the revised example as a template.",
                "Ensure content is exclusively about the target, and not the example topic.",
            ],
            "specific_instructions": [
                "Do not copy text verbatim. Include only text within the scope of the current section, as highlighted in the output of {{TaskRef:Understand Differentiation}}.",
                "Include cross-references to other sections as seen in the example if applicable.",
            ],
        },
    ),
    # Task(
    #     task_name="Final Section Review",
    #     details={
    #         "description": "Review the final text for this section and provide a PASS/FAIL decision based on the success criteria.",
    #         "prerequisite_tasks": ["Draft New Document Section"],
    #         "instructions": [
    #             "Evaluate the success of the new section draft",
    #             "Document the review outcome",
    #             "Print the final review output.",
    #         ],
    #         "success_flag_criteria": {
    #             "FAIL": [
    #                 "The section includes information beyond what's relevant as indicated by {{TaskRef:Understand Differentiation}}.",
    #                 "Any mention of specific drugs or combination therapies not relevant to the new study context.",
    #                 "Information in the new section is redundant with the sections analyzed in {{TaskRef:Understand Differentiation}}.",
    #                 "The draft does not reflect the structure, format, or detail level of the revised example section (output of {{TaskRef:Handle Treatment Details}}).",
    #                 "Missing or incorrectly referenced tables or figures from the new reference materials.",
    #                 "Significant deviation from the new reference materials, suggesting misalignment with the study's current focus.",
    #                 "Inconsistent use of verb tenses where required.",
    #             ],
    #             "PASS": [
    #                 "The section appropriately includes information within the scope defined by {{TaskRef:Understand Differentiation}}.",
    #                 "The draft logically follows what the section heading describes.",
    #                 "The draft focuses exclusively on the new study context.",
    #                 "The draft meets criteria for completeness, accuracy, and is aligned with the revised example and the new reference materials.",
    #             ],
    #         },
    #         "additional_instructions": "Offer feedback on the process of differentiating from other sections, the use of source materials, and the rationale for selected source mappings.",
    #         "output_format": {
    #             "Section Review": "[SECTION NUMBER] - [SECTION HEADING]",
    #             "Draft Review": "[content here]",
    #             "Comments": "[comments here]",
    #             "Success Flag": "[FAIL/PASS]",
    #             "Source Mapping Review": "[REVIEW OF UTILIZED SOURCES]",
    #             "Tables": "[LIST OF REFERENCED TABLES]",
    #             "Figures": "[LIST OF REFERENCED FIGURES]",
    #             "Cross-References": "[REFERENCES TO OTHER DOCUMENT SECTIONS (FROM EXAMPLE DOCUMENT)]",
    #             "Scope of Section Review": "[REFLECTION ON FOLLOWING THE SCOPE GUIDELINES SET OUT IN {{TaskRef:Understand Differentiation}} OUTPUT]",
    #         },
    #     },
    # ),
    Task(
        task_name="Prepare for Next Document Section",
        details={
            "description": "SIgnal that you have completed the draft by calling the pop_context function and prepare to start drafting the next section of the document.",
            "function_call": "Use the pop_context function with the argument value = current section identifier.",
            "example_call": "{{'current_section_identifier': ['1.2']}}",
            "instructions": [
                "Announce completion: 'Proceed to the next section of the document, [current section identifier] has been completed.'"
            ],
        },
    ),
]

general_comments = """
============
GENERAL COMMENTS:
START WITH THE FIRST SECTION. ONLY DO THE NEXT UNCOMPLETED TASK (ONLY ONE TASK AT A TIME).
EXPLICITLY print out the current section identifier.
EXPLICITLY print out wheter the last task completed successfully or not.
EXPLICITLY print out the task you are completing currently.
EXPLICITLY print out what task you will complete next.
EXPLICITLY provide a detailed and appropriate response for EVERY TASK.
THE MOST IMPORTANT THING FOR YOU TO UNDERSTAND: THE PRIMARY GOAL OF THE TASKS IS TO DRAFT A NEW SECTION OF THE DOCUMENT
A SECTION IS CONSIDERED COMPLETE ONCE THE LAST TASK HAS BEEN ACCOMPLISHED.

IF A FUNCTION CALL RETURNS AN ERROR THEN TRY AGAIN WITH PARAMETERS, OR MAKE DIFFERENT FUNCTION CALL.
IF TASK HAS NOT COMPLETED SUCCESSFULLY, TRY AGAIN WITH AN ALTERED RESPONSE.
DO NOT REPEAT YOUR PREVIOUS MESSAGE.  
IF YOU NOTICE A TASK (OR SERIES OF TASKS) BEING REPEATED ERRONEOUSLY, devise a plan to move on to the next uncompleted task.
IF YOU ENCOUNTER REPEATED MESSAGES IN THE CHAT HISTORY, reorient yourself by revisiting the last task completed. Check that the sequence of past tasks progresses in logical order. If not, assess and adjust accordingly.
If you are on the same task for a long time, and you are not making progress, just go to the next task and do the best you can.
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
I am going to give you step by step instructions on how to draft a new wiki page section by section.
Below you will find a json object that contains the index of sections that need to be drafted.
The keys of the json are the section numbers of the document. The values include the heading title.

The subsections in the target document will be different and should be based on the information in the target document.
"""

post_algo_instruct = """
We will look at an Example Document that is similar to the document to be drafted.
Its full content can be queried with a function (get_text_for_sections) and used as an example (in json format).
The keys of the json are the section numbers of the document and the values contain the sections' bodies.
What I want you to do is to go section by section in the Document to be drafted, and do the following, in sequential order:
"""

job_description = JobDescription(
    role="You are a wiki writing AI agent. You have the ability to call outside functions.",
    context="Document to be drafted:",
    task_list=task_library,
    tool_implementations_class=WikipediaToolImplementations,
    pre_context_instruct=pre_algo_instruct,
    post_context_instruct=post_algo_instruct,
    general_comments=general_comments,
    initial_user_message=initial_user_message,
)
