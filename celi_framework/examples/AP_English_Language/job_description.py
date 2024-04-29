"""
This module serves as a generic template. It is designed to be adaptable for
a broad range of reports and is not specific to any particular field.
The tasks, function calls, and methodologies described herein are intended to provide a foundational
structure for document analysis and drafting, which can be customized to meet the needs of various
reporting requirements.
"""

from celi_framework.core.job_description import JobDescription, Task
from celi_framework.examples.AP_English_Language.tools import APEnglishLanguageToolImplementations
from celi_framework.core.mt_factory import MasterTemplateFactory
from celi_framework.utils.utils import load_json

# TODO: Get the "AP Way" of doing free response questions for AP English Language
#  Refactor the tasks below that are taking as example
#  need to also pull in examples, and set this up as one-shot using prior one-shot prompt engineering work"
# TODO: Note that this is in the general comments: A section is considered complete once the 'Final Response Review' task has been accomplished. Do not skip the 'Final Response Review' task.
task_library = [
    Task(
        task_name="Retrieve prompt for question",
        details={
            "description": "Find and retrieve the text for the prompt of the current test question.",
            "tool_call": "Perform a function call to retrieve the question's prompt.",
            "example_call": "{{'question_number': ['q1']}}",
            "instructions": [
            ],
        },
    ),
    Task(
        task_name="Analyze and Understand the Example Response",
        details={
            "description": "Analyze an example prompt and response to develop a preliminary understanding of the expected response structure, argument style, and evidence use.",
            "instructions": [
                "Examine the example prompt and response to grasp the expected structure, argumentation style, and use of evidence.",
                "Determine the scope of the question to ensure comprehensive coverage of all required aspects without digressing into irrelevant areas.",
                "Identify and abstract the key strategies and methodologies from the example response that effectively address the prompt."
            ],
            "additional_notes": [
                "Prepare to develop a response strategy based on these insights."
            ],
            "tool_call": "Use a function call to retrieve the example prompt and response pair for analysis.",
            "example_call": "{{'question_number': ['q1']}}",
        },
    ),
    Task(
        task_name="Develop response strategy",
        details={
            "description": "Formulate a detailed response strategy by integrating the insights gained from the analysis of the example prompt and response.",
            "instructions": [
                "Based on the analyzed strategies and methodologies, draft a preliminary strategy that outlines how these will be applied to effectively address the current question."
            ],
            "additional_notes": [
                "This strategy should guide the detailed outline creation and ensure that the response is tailored to meet the specific requirements of the current question."
            ],
        },
    ),
    Task(
        task_name="Draft a Numbered Response Outline",
        details={
            "description": "Based on the formulated strategy, draft a detailed and numbered outline for the current test question that mirrors the logical flow, clarity, and analytical depth required.",
            "instructions": [
                "Construct a numbered outline that includes an introduction with a thesis statement, a body section with evidence from provided sources, and a coherent conclusion."
            ],
            "example": {
                "Example Outline Format": "1. Introduction with thesis statement\n2. Body section with evidence points\n3. Conclusion"
            },
            "additional_notes": [
                "This outline serves as the blueprint for constructing a well-argued and substantiated response, maintaining originality in content and perspective."
            ],
            "tool_call": "Initiate drafting in the document editor with outline format enabled.",
            "example_call": "{{'question_number': ['q1']}}",
        },
    ),
    Task(
        task_name="Iteratively Draft Each Section of the Response",
        details={
            "description": "Using the previously formulated strategy and outline, iteratively draft each section of the test response, ensuring each part reflects the logical flow, clarity, and analytical depth required.",
            "instructions": [
                "Begin with drafting the introduction section that includes a thesis statement, outlining the main argument.",
                "Proceed to draft each body section sequentially, ensuring each part discusses evidence from the provided sources relevant to the thesis, as detailed in the outline.",
                "Conclude by drafting the conclusion section, summarizing the arguments and reinforcing the thesis.",
                "Ensure each drafted section transitions smoothly into the next, maintaining a coherent flow throughout the document."
            ],
            "example": {
                "Example Outline Format": "1. Introduction with thesis statement\n2. Body section 1 with evidence point\n3. Body section 2 with another evidence point\n4. Conclusion",
                "Example Drafted Section": "Introduction: [Draft text of introduction here, emphasizing the thesis and setting the tone for the subsequent sections.]"
            },
            "additional_notes": [
                "This task requires you to maintain the integrity of the original outline while adapting the content to the specifics of the test question.",
                "Focus on clarity and depth of analysis, ensuring each section is well-supported by evidence and aligns with the overall argument.",
                "Review each section upon completion to ensure it integrates seamlessly into the overall response structure."
            ],
            "tool_call": "Retrieve the instructions for the current question to refresh your memory.",
            "example_call": "{{'question_number': ['q1']}}",
        },
    ),
    Task(
        task_name="Synthesize Sections into a Final Draft",
        details={
            "description": "Use the drafted sections to create a cohesive final draft that flows well and aligns with the expected structure and length of a model response.",
            "instructions": [
                "Combine the individually drafted sections (introduction, body sections, and conclusion) into a single cohesive document.",
                "Ensure that the transition between sections is smooth, maintaining a logical and seamless narrative flow throughout the document.",
                "Review the combined draft to ensure that it adheres to the structural expectations set by the model response, both in terms of length and overall organization.",
                "Adjust the draft as necessary to ensure that the entire document is coherent, with each part contributing effectively towards supporting the thesis statement."
            ],
            "example": {
                "Model Response Example": "Refer to the structure and length of the model response as a benchmark for the final draft."
            },
            "additional_notes": [
                "Pay close attention to maintaining a balanced argument throughout the response, ensuring that no one section dominates at the expense of others unless strategically intended.",
                "Focus on refining the language and style to enhance readability and persuasive impact."
            ],
            "tool_call": "Use a function call to retrieve the example response to compare the final draft against the model for structure and length.",
            "example_call": "{{'question_number': ['model_q1']}}",
        }
    ),
Task(
    task_name="Final Response Review",
    details={
        "description": "Review the entire document to ensure that it meets the established criteria based on the insights and structure developed in previous tasks and compare it to a similar prompt, answer pair to ensure structural and thematic consistency.",
        "instructions": [
            "Use the 'retrieve_instructions' function to fetch a prompt and answer pair for a similar question to ensure alignment with standard response formats and expectations.",
            "Review each section of the document to ensure that it follows the logical flow and depth as outlined, comparing it with the retrieved example where necessary.",
            "Check that the thesis is clearly stated in the introduction and effectively supported throughout the body sections.",
            "Verify that the conclusion effectively summarizes the arguments and reiterates the thesis.",
            "Ensure that each section transitions smoothly into the next, maintaining a coherent narrative flow.",
            "Assess the use of evidence throughout the document to ensure it is pertinent and effectively integrated into the argument."
        ],
        "additional_notes": [
            "Ensure each section of the response maintains originality while effectively addressing the specifics of the test question.",
            "Pay special attention to the synthesis of information from provided sources, ensuring accurate representation and logical argumentation.",
            "Review the formatting and grammar to ensure the document is well-presented and free of errors."
        ],
        "success_criteria": {
            "FAIL": [
                "Sections fail to coherently support the thesis or argument flow is disrupted.",
                "Evidence used does not align with or effectively support the thesis.",
                "Significant grammatical, formatting, or citation errors that detract from the document's clarity or credibility."
            ],
            "PASS": [
                "Document presents a well-argued, substantiated response with a clear thesis and logical evidence flow.",
                "All sections are coherent and transitions are smooth, maintaining a consistent narrative.",
                "Document is free from significant grammatical or formatting errors and follows the required citation format."
            ]
        },
        "tool_call": "Use a function to retrieve the instructions for this question",
        "example_call": "{{'question_number': ['q1']}}",
        "output_format": {
            "Section Review": "Detailed feedback for each section",
            "Draft Quality": "Assessment of argumentation and evidence integration",
            "Final Verdict": "PASS or FAIL based on the established criteria",
            "Additional Comments": "Feedback on specific areas for improvement or commendation"
        }
    }
),
    Task(
        task_name="Move on to next question",
        details={
            "description": "Pop context to finish this question and move on to next question.",
            "tool_call": "Use the pop_context function.",
            "example_call": "{{'current_question_number': ['next_question_number']}}",
        },
    ),
]

general_comments = """
============
General comments:
Start with the first test question. Only do the next uncompleted task (only one task at a time).
Explicitly print out the current question number.
Explicitly print out whether the last task completed successfully or not.
Explicitly print out the task you are completing currently.
Explicitly print out what task you will complete next.
Explicitly provide a detailed and appropriate response for every task.
The most important thing for you to understand: The primary goal of the tasks is to answer the test question that you have been presented.
A section is considered complete once the 'Final Response Review' task has been accomplished. Do not skip the 'Final Response Review' task.

If a function call returns an error then try again with parameters, or make a different function call.
If task has not completed successfully, try again with an altered response.
If you notice a task (or series of tasks) being repeated erroneously, devise a plan to move on to the next uncompleted task.
If you encounter empty messages repeatedly in the chat history, reorient yourself by revisiting the last task completed. Check that the sequence of past tasks progresses in logical order. If not, assess and adjust accordingly.

Do not ever return a tool or function call with the name 'multi_tool_use.parallel'
=============
"""

initial_user_message = """
Please see system message for instructions. Take note of which test question is currently being worked on and which tasks have been completed. Complete the next uncompleted task.
If you do not see any tasks completed for the current test question, begin with Task #1.

If all tasks for the current test question have been completed, proceed to the next document section.
If the new section draft is complete, ensure to 'Prepare for Next Document Section' as described in the tasks.
"""

pre_algo_instruct = """
I am going to give you step by step instructions on how to draft a free response to a test question.
Below you will find a json object that contains the index of test questions that need to be responded to.
The keys of the json are the questions numbers (q1, q2, q3) of the free response section of a test. The values are the respective topics.
"""

post_algo_instruct = """
We will look at a completed example free response test section that is similar to the test to be worked on.
Its full content can be queried with a function (example_question_text_getter) and used as an example (in json format).
The keys of the json are the question numbers (q1, q2, q3) of the free response test section and the values contain the questions and answers.
Question n of the examples lines up with question n in the test section being worked on.
What I want you to do is to go question by question in the test section, and do the following, in sequential order:
"""

job_description = JobDescription(
    role="You are a professional test taker AI agent. You have the ability to call outside functions.",
    context="Free response test sections to be responded to:",
    task_list=task_library,
    tool_implementations_class=APEnglishLanguageToolImplementations,
    pre_context_instruct=pre_algo_instruct,
    post_context_instruct=post_algo_instruct,
    general_comments=general_comments,
    initial_user_message=initial_user_message,
)