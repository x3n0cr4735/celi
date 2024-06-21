"""
This module serves as a generic template. It is designed to be adaptable for
a broad range of reports and is not specific to any particular field.
The tasks, function calls, and methodologies described herein are intended to provide a foundational
structure for document analysis and drafting, which can be customized to meet the needs of various
reporting requirements.
"""

from celi_framework.core.job_description import JobDescription, Task

from tools import AlpacaEvalToolImplementations
from celi_framework.core.mt_factory import MasterTemplateFactory
from celi_framework.utils.utils import load_json

task_library = [
       Task(
        task_name="Retrieve prompt for question",
        details={
            "description": "Find and retrieve the text for the prompt of the current test question.",
            "tool_call": "Perform a function call to retrieve the question's prompt by calling retrieve_question_prompt function for each question in the schema",
            "example_call": "{{'question_number': ['1']}}",
            "instructions": [  
            ],
        },
    ),
    
    Task(
        task_name="Generate Baseline Response by answering the Current Instruction",
        details={
            "description": "Produce an initial draft response to the given instruction.",
            "instructions": [
                "Analyze the instruction carefully and draft a response that fully addresses the query or requirement."
            ],
        },
    ),
    Task(
        task_name="Plan Verifications",
        details={
            "description": "Develop a set of verification questions that test the factual accuracy and relevance of the baseline response.",
            "instructions": [
                "Develop a series of questions that can be used to verify the accuracy and relevance of the response.",
                "The verification questions can also ask for sources to explain the reasoning behind the response."
                "Review the response to ensure that it correctly interprets the instruction and provides all necessary information or answers all parts of the question."
            ],
        },
    ),
    Task(
        task_name="Execute Verifications",
        details={
            "description": "Address each verification question independently to validate the baseline response.",
            "instructions": [
                "Examine the response to ensure that it is straightforward, avoiding any vague or redundant content."
            ],
        },
    ),
    Task(
        task_name="Generate Final Verified Response",
        details={
            "description": "Integrate the insights from the verification process to revise and finalize the response.",
            "instructions": [
                "Revise and rewrite the response based on the evaluations and feedback from previous tasks: 'Evaluate the Response for Accuracy and Completeness', 'Check for Clarity and Conciseness', 'Validate Factual Information', making sure to address each point of feedback and correction."
            ],
        },
    ),
    Task(
        task_name="Score the Response",
        details={
            "description": "Use the rubric provided in the instructions to score the final response",
            "tool_call": "Get the rubric using the get_rubric function for the current question.",
            "example_call": "{{}}",
            "instructions": [
                "Use the rubric to score the final response",
                "The score should between 0 and 100. Consider the accuracy, clarity, and completeness of the response when assigning a score.",
                "The final response should definitely contain the score and final score for all type of questions."
            ],
        },
    ),
    Task(
        task_name="Save the repsone for each question in json format",
        details={
            "description": "Save the response in the json format.",
            "instructions": "Save response for each question one by one into json file by calling save_json function",
            "tool_call": "Use the save_json tool.",
            "example_call": "{{'response' :{'instruction': 'Which year india won the first world cup in cricket?', 'baseline_response': 'India won the first world cricket cup in 1985', 'final_response': 'India won the first world cricket cup in 1981.', 'Excepted_output': 'India won the first world cricket cup in 1981.',  'verification_answers': {'Question 1': 'Answer', 'Question 2': 'Answer', ...}, 'feedback': {'accuracy': 'The response is factually correct and provides an accurate answer to the given instruction.', 'relevance': 'The response directly addresses the instruction, with all parts of the response clearly related to the question.', 'completeness': 'The response thoroughly answers the instruction, leaving no aspect unaddressed.', 'clarity_and_structure': 'The response is clearly articulated and well-structured, making it easy to follow and understand.', 'creativity_or_analytical_depth': 'The response is basic, with no significant creativity or analytical depth.'}, 'score': {'accuracy': 30, 'relevance': 25, 'completeness': 20, 'clarity_and_structure': 15, 'creativity_or_analytical_depth': 4, 'final_score': 94}, 'question_number': '1'}}}",

                },
    ),
]



# TODO: Have a way to do automatic tagging of "last section" i.e. "A section is considered complete once the ... is complete"
# general_comments = """
# ============
# General comments:
# Start with the first test question. Only do the next uncompleted task (only one task at a time).
# Explicitly print out the current question number.
# Explicitly print out whether the last task completed successfully or not.
# Explicitly print out the task you are completing currently.
# Explicitly print out what task you will complete next.
# Explicitly provide a detailed and appropriate response for every task.
# The most important thing for you to understand: The primary goal of the tasks is to answer the test question that you have been presented.
# A section is considered complete once there are no more revisions required. If there are revisions recommended then go back to Task Synthesize Sections into a Draft.

# If a function call returns an error then try again with parameters, or make a different function call.
# If task has not completed successfully, try again with an altered response.
# If you notice a task (or series of tasks) being repeated erroneously, devise a plan to move on to the next uncompleted task.
# If you encounter empty messages repeatedly in the chat history, reorient yourself by revisiting the last task completed. Check that the sequence of past tasks progresses in logical order. If not, assess and adjust accordingly.

# Do not ever return a tool or function call with the name 'multi_tool_use.parallel'
# =============
# """

initial_User_Message = "Welcome to your task dashboard for the Alpaca_Eval dataset. Please review the question in the dataset and start with the first uncompleted task. Focus on generating accurate and comprehensive responses. Refer to any previous tasks if needed to maintain continuity and accuracy."

pre_algo_instruct = """Before we start answering questions from the Alpaca_Eval dataset, ensure you understand the context and requirements of each question. You will be provided with the question and expected to research and draft a response based on reliable sources. Pay close attention to the specifics of each question to tailor your responses appropriately.

    Analyze the Example Instruction and Output:
    Analyse the types of questions and formulate a strategy for the type of question.
    Examine how the response effectively addresses the instruction, noting the use of specific details and the structure of the answer.
    
    Example Instruction & Output:
      "1":{
    "instruction": "Marie is at the music store for a store day. She bought two $50 combos. Then, for $25 she bought two t-shirts for $5 each and five hoodies for $2 each. Then, she bought sneakers for $8 each. How much did she spend total?",
    "output": "Marie spent a total of $147."}
     """

post_algo_instruct = "After drafting your response, review it against the example outputs provided for quality and comprehensiveness. Ensure your final response aligns with the expected format and detail as illustrated by successful examples. Reflect on any feedback or revisions suggested in the dataset guidelines to optimize your response before submission."
    
system_message = """
    As an AI trained to assist with the answering questions, your goal is to generate concise and precise answers to the provided instructions.
    This guide will help you step by step to formulate responses that are not only correct but also well-informed and contextually relevant.
    """
job_description = JobDescription(
    role=system_message,
    context="Respond to questions from the Alpaca_Eval dataset by following the provided instructions and generating accurate and comprehensive responses. Use the tools and guidelines provided to ensure the quality and relevance of your answers.",
    task_list=task_library,
    tool_implementations_class=AlpacaEvalToolImplementations,
    pre_context_instruct=pre_algo_instruct,
    post_context_instruct=post_algo_instruct,
    #general_comments=general_comments,
    initial_user_message=initial_User_Message,
)