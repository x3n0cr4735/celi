"""
This module serves as a generic template. It is designed to be adaptable for
a broad range of reports and is not specific to any particular field.
The tasks, function calls, and methodologies described herein are intended to provide a foundational
structure for document analysis and drafting, which can be customized to meet the needs of various
reporting requirements.
"""

from celi_framework.core.job_description import JobDescription, Task

from tools import GREToolImplementations
from celi_framework.core.mt_factory import MasterTemplateFactory
from celi_framework.utils.utils import load_json

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
        task_name="Analyze and Understand the Example Prompt & Response",
        details={
            "description": "This task involves a critical analysis of an example response to a prompt similar to the one retrieved in the previous step. The objective is to dissect and understand the structural components, argumentation style, and evidence utilization within the example. This analysis is essential for developing a strategy that aligns with high-scoring responses.",
            "tool_call": "Use a function call to retrieve the example prompt and response pair for detailed analysis.",
            "example_call": "{{'question_number': ['q1']}}",
            "instructions": [
                "Retrieve an example prompt and response pair using the provided function call, ensuring it correlates with the question number of the current task.",
                "Examine the structure of the response, noting the introduction, body, and conclusion arrangement.",
                "Identify key argumentation techniques used in the response, noting how evidence is integrated to support claims.",
                "Abstract strategies that are effective in addressing the prompt, including rhetorical devices, logical reasoning, and evidence presentation."
            ],
            "additional_notes": [
                "Highlight any innovative or particularly effective methods used in the example that could be adapted for your response.",
                "Consider the context in which the example was effective—cultural, educational, or disciplinary perspectives might influence how the response is crafted."
            ],
            "tool_call": "Use a function call to retrieve the example prompt and response pair for analysis.",
            "example_call": "{{'question_number': ['q1']}}",
        }
    ),
    Task(
        task_name="Develop Response Strategy",
        details={
            "description": "Based on insights gained from the analysis of the example response, this task focuses on formulating a comprehensive strategy to address the current test question effectively. The strategy should integrate the key structural components, argumentative techniques, and evidence-handling methods identified previously to ensure a coherent and persuasive response.",
            "instructions": [
                "Synthesize the findings from the previous analysis task into a cohesive strategy document.",
                "Outline how each identified successful technique will be adapted to fit the specific requirements and context of the current prompt.",
                "Develop a structured plan that specifies the introduction, development of arguments, integration of evidence, and conclusion.",
                "Ensure the strategy is flexible enough to accommodate potential variations in the prompt's requirements or unexpected insights gained during the drafting process."
            ],
            "additional_notes": [
                "The strategy should be documented clearly and concisely to serve as a guideline during the response drafting stage.",
                "Consider peer review or feedback mechanisms if possible, to validate and refine the strategy before proceeding to draft."
            ],
            "tool_call": "Initiate drafting in the document editor with outline format enabled.",
            "example_call": "{{'question_number': ['q1']}}",
        }
    ),
    Task(
        task_name="Draft a Numbered Response Outline",
        details={
            "description": "Utilizing the developed response strategy, this task involves drafting a detailed and numbered outline that maps out the structure of the intended response. This outline should mirror the logical flow, clarity, and analytical depth required by the prompt, serving as a foundational blueprint for the subsequent detailed drafting.",
            "instructions": [
                "Start with an introduction that sets the context and states the thesis clearly.",
                "List the main points that will form the body of the response, detailing the argument and evidence planned for each section.",
                "Conclude with a summary that reinforces the thesis and encapsulates the main arguments made in the body.",
                "Ensure each section is numbered and clearly delineated to facilitate easy navigation and organization during the drafting process."
            ],
            "example": {
                "Example Outline Format": "1. Introduction with thesis statement\n2. Body section 1 with evidence point\n3. Body section 2 with another evidence point\n4. Conclusion"
            },
            "additional_notes": [
                "This outline should not only serve as a guide for drafting but also as a checklist to ensure all critical points are covered.",
                "Revise the outline as necessary to reflect any new insights or adjustments in the response strategy."
            ]
        }
    ),
    Task(
        task_name="Iteratively Draft Each Section of the Response",
        details={
            "description": "This task involves the detailed drafting of each section of the response as outlined previously. The focus is on ensuring that each section is well-articulated, logically coherent, and supports the overarching thesis of the response. Iterative drafting allows for refinement and ensures alignment with the response strategy and outline.",
            "instructions": [
                "Begin by drafting the introduction, setting the tone and context for the response, and clearly stating the thesis.",
                "Proceed to draft each body section, elaborating on the main points with appropriate evidence and analysis as planned in the outline.",
                "Ensure each body section is interconnected, smoothly transitioning to maintain a cohesive argument throughout.",
                "Conclude with a strong summary that reiterates the thesis and synthesizes the main arguments discussed.",
                "Review and revise each section iteratively to improve clarity, flow, and impact, making adjustments as necessary based on the evolving understanding of the topic.",
                # "---> THIS TASK NEEDS TO BE EXECUTED AS SUB-TASKS. DRAFT THE INTRODUCTION, CONCLUSION, AND EACH BODY SECTION ONE RESPONSE AT A TIME <----",
                "---> THIS TASK NEEDS TO BE EXECUTED AS SUB-TASKS. DRAFT EACH SECTION AND SUB-SECTION ONE RESPONSE AT A TIME. SPLIT THEM UP. DO NOT DO AT THE SAME TIME. <----",
            ],
            "example": {
                "Example Drafted Section": "Introduction: [Draft text of introduction here, emphasizing the thesis and setting the tone for the subsequent sections.]"
            },
            "additional_notes": [
                "This drafting process should be iterative; don't hesitate to revisit earlier sections as you gain more insight or as the argument develops.",
                "Consider peer feedback on drafted sections to enhance clarity and effectiveness."
            ]
        }
    ),
    Task(
        task_name="Synthesize Sections into a Draft",
        details={
            "description": "After drafting individual sections, this task involves combining them into a single, cohesive final draft. The objective is to ensure that the document flows logically from introduction to conclusion, maintaining a unified argument that effectively addresses the prompt. This synthesis is crucial for ensuring that the response reads as a well-organized, integrated whole rather than as disjointed parts.",
            "instructions": [
                "Combine the drafted sections starting with the introduction, followed by the body sections, and ending with the conclusion.",
                "Ensure that transitions between sections are smooth and logical, enhancing the overall flow and readability of the document.",
                "Check that the final draft maintains a consistent style, tone, and voice throughout, which are important for presenting a professional and coherent argument.",
                "Review the entire document to ensure that it aligns with the response strategy and meets the structural and content expectations outlined previously."
            ],
            "example": {
                "Model Response Example": "Refer to the structure and length of the example response (essay) as a benchmark for the final draft."
            },
            "additional_notes": [
                "Consider the overall narrative arc of the response to ensure it effectively builds towards a convincing conclusion.",
                "Revisit the introduction after completing the body and conclusion to ensure it accurately reflects the depth and scope of the argument discussed.",
            ]
        }
    ),
Task(
        task_name="Save draft",
        details={
            "description": "Dave the draft.",
            "instructions": "Save content from the draft of each section into one json",
            "tool_call": "Use the save_draft tool.",
            "example_call": "{'draft_dict': {'Introduction': 'INTRO CONTENT', 'Section 1 (Title)': 'BODY SECTION 1 CONTENT', .... , 'Conclusion': 'CONCLUSION CONTENT'}}",
        },
    ),
Task(
    task_name="Review Draft",
    details={
        "description": "This final review task is crucial for ensuring that the complete document meets the established criteria, drawing on insights and structures developed in previous tasks. It involves a detailed comparison with a similar prompt-answer pair to check for structural and thematic consistency, ensuring the response aligns with standard response formats and expectations.",
        "instructions": [
            "Use the 'retrieve_instructions' function to fetch a prompt and answer pair for a similar question, ensuring alignment with standard response formats and expectations.",
            "Review each section of the document to confirm it follows the logical flow and depth outlined, comparing it with the retrieved example where necessary.",
            "Check that the thesis is clearly stated in the introduction and is effectively supported throughout the body sections.",
            "Verify that the conclusion effectively summarizes the arguments and reinforces the thesis.",
            "Ensure that each section transitions smoothly into the next, maintaining a coherent narrative flow.",
            "Assess the use of evidence to ensure it is pertinent and effectively integrated into the argument."
        ],
        "additional_notes": [
            "Maintain originality in each section while addressing the specifics of the test question effectively.",
            "Pay special attention to the synthesis of information from provided sources, ensuring accurate representation and logical argumentation.",
            "Review formatting and grammar to ensure the document is well-presented and free of errors.",
            """
            Here is typical feedback that you have received for prior drafts. Make sure you are addressing the previous concerns:
            Based on the GRE® Scoring Guide provided, the essay you've written would likely receive a Score 5 (out of 6). Here's the rationale for this assessment:
            
            Clear and Well-Considered Position: The essay presents a clear and articulated position that cooperation rather than competition is essential for nurturing future leaders capable of tackling modern societal complexities. This aligns well with the task's requirements.
            Development with Logically Sound Reasons and Examples: The position is developed using logically sound reasons and well-chosen examples, such as the collaboration on the international space station to illustrate effective teamwork leading to significant achievements. However, the depth of analysis and the variety of examples might benefit from further expansion to fully realize a score of 6.
            Focus and Organization: The essay maintains a general focus and organization. It logically structures the argument from introduction through to conclusion, though there could be smoother transitions and a more nuanced exploration of competing viewpoints to enhance the logical flow and depth of analysis.
            Clarity and Appropriateness of Language: The essay uses clear and appropriate language, employing a decent range of vocabulary and sentence structures. It conveys ideas effectively, although to achieve a score of 6, the essay could benefit from even more varied sentence structures and more precise vocabulary to enhance clarity and impact.
            Conventions of Standard Written English: The essay demonstrates a good command of standard written English, with only minor errors. The grammatical structure is solid, supporting the overall clarity and readability of the essay.
            A section is considered complete once there are no more revisions required. If there are revisions recommended then go back to Task Synthesize Sections into a Draft.
            
            Justification for Not Awarding a Score of 6:
            While the essay is robust, to achieve a score of 6, it would require a slightly more insightful and nuanced analysis, particularly in exploring the limitations of cooperation or how it interacts with competition in more depth.
            A score of 6 would also typically involve demonstrating superior skill in the use of language, including more sophisticated syntax and richer vocabulary.
            
            """,
            "BE VERY CRITICIAL. TRY TO POKE HOLES AS MUCH AS YOU CAN. THE DRAFT NEEDS TO BE AT PHD DISSERTATION LEVEL SOPHISTICATION"
        ],
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
    task_name="Recommend Revisions with Review Output",
    details={
        "description": "This task involves identifying necessary revisions based on detailed feedback and assessments provided in the 'Draft Review' task. The goal is to pinpoint areas where the document can be improved to meet established criteria, thus enhancing clarity, coherence, and argumentative strength based on the review outputs.",
        "instructions": [
            "Review the feedback provided in the 'Section Review', 'Draft Quality', and 'Final Verdict' components from the Draft Review.",
            "Identify key areas requiring improvement—these may include areas where argumentation needs to be strengthened, the thesis needs to be clearer, transitions between sections need to be smoother, or grammatical and formatting errors need to be corrected.",
            "Recommend specific revisions for each section of the document, focusing on the areas highlighted in the feedback.",
            "Suggest re-evaluation of the evidence used in the response to ensure it aligns well with the thesis and supports the overall argument effectively.",
            "Propose how to ensure that all recommended revisions will maintain the logical flow and coherence of the response, thus enhancing its overall persuasive impact."
        ],
        "additional_notes": [
            "Document the recommended changes to track revisions made during this phase, facilitating subsequent reviews if necessary.",
            "Advise on seeking additional feedback after proposing revisions to confirm that all issues have been adequately addressed and the response is optimized."
        ],
        "output_format": {
            "Revised Sections": "Detailed documentation of recommended changes for each section",
            "Improvements Proposed": "List of improvements suggested based on the feedback",
            "Re-Review Suggested": "Indicate whether an additional review is suggested after the recommended revisions"
        }
    }
),

    # TODO: Can we do one section at a time
Task(
        task_name="Redraft",
        details={
            "description": "Redraft with recommended revisions.",
            "instructions": [
                "Revise each of the sections and subsections drafted separately in 'Iteratively Draft Each Section of the Response'.",
                "---> THIS TASK NEEDS TO BE EXECUTED AS SUB-TASKS. DRAFT EACH SECTION AND SUB-SECTION SEPERATELY IN SEQUENTIAL PROMPT/COMPLETIONS (ONE RESPONSE AT A TIME) <----",
            ]
        },
    ),
Task(
        task_name="Save draft",
        details={
            "description": "Save the draft.",
            "instructions": "Save content from the draft of each section into one json",
            "tool_call": "Use the save_draft tool.",
            "example_call": "{'draft_dict': {'Introduction': 'INTRO CONTENT', 'Section 1 (Title)': 'BODY SECTION 1 CONTENT', .... , 'Conclusion': 'CONCLUSION CONTENT'}}",
        },
    ),

# TODO: To Add a step to review both saved drafts (pre/post revisions) and to choose the better one <<<<<<<<<<
Task(
        task_name="Score the final essay",
        details={
            "description": "Use the rubric provided in the instructions to score the final response from 1 to 6. Afterwards include the final score at the top of the essay.",
            "instructions": [
                "Use the 'get_rubric' function to fetch the rubric used to score the essay"
                "Use the returned rubric to score the essay from 1-6."
                "Be sure to take the entire essay into account when scoring the essay"
            ],
            "tool_call": "Use a function to retrieve the rubric to score this question",
    }
    ),

Task(
        task_name="Finish Essay and move on to next question",
        details={
            "description": "Pop context to finish this question and move on to next question if there are any questions left.",
            "instructions": "A section is considered complete once there are no more revisions required. If there are revisions recommended then go back to Task Synthesize Sections into a Draft - IN THIS CASE, DO NOT CALL pop_context.",
            "tool_call": "Use the pop_context function.",
            "example_call": "{{'current_question_number': ['next_question_number']}}",
        },
    ),
]

# TODO: Have a way to do automatic tagging of "last section" i.e. "A section is considered complete once the ... is complete"
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
A section is considered complete once there are no more revisions required. If there are revisions recommended then go back to Task Synthesize Sections into a Draft.

If a function call returns an error then try again with parameters, or make a different function call.
If task has not completed successfully, try again with an altered response.
If you notice a task (or series of tasks) being repeated erroneously, devise a plan to move on to the next uncompleted task.
If you encounter empty messages repeatedly in the chat history, reorient yourself by revisiting the last task completed. Check that the sequence of past tasks progresses in logical order. If not, assess and adjust accordingly.

Do not ever return a tool or function call with the name 'multi_tool_use.parallel'
=============
"""

initial_user_message = """
Please see system message for instructions. 
Take note of which test question is currently being worked on and which tasks have been completed. Complete the next uncompleted task.
If you do not see any tasks completed for the current test question, begin with Task #1.

Answer the question while being cognizant of the criteria for a score of 6.

A section is considered complete once there are no more revisions required. If there are revisions recommended then go back to Task 'Synthesize Sections into a Draft'.
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
    tool_implementations_class=GREToolImplementations,
    pre_context_instruct=pre_algo_instruct,
    post_context_instruct=post_algo_instruct,
    general_comments=general_comments,
    initial_user_message=initial_user_message,
)