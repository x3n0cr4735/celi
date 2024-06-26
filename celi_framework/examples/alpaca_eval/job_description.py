"""
This module serves as a generic template. It is designed to be adaptable for
a broad range of reports and is not specific to any particular field.
The tasks, function calls, and methodologies described herein are intended to provide a foundational
structure for document analysis and drafting, which can be customized to meet the needs of various
reporting requirements.
"""

from celi_framework.core.job_description import JobDescription, Task

from .tools import AlpacaEvalToolImplementations
from celi_framework.core.mt_factory import MasterTemplateFactory
from celi_framework.utils.utils import load_json

output_format = """{
  "instruction": "Which year india won the first world cup in cricket?",
  "baseline_response": "India won the first world cricket cup in 1985",
  "output": "Your final response",
  "score": {
    "accuracy": 30,
    "relevance": 25,
    "completeness": 10,
    "conciseness": 10,
    "clarity_and_structure": 15,
    "creativity_or_analytical_depth": 4,
    "final_score": 94
  },
  "feedback": "The response did not answer the question accurately. The correct year is 1981, not 1982. Please provide the correct information in the final response."
}"""

task_library = [
       Task(
        task_name="Retrieve prompt for question",
        details={
            "description": "Find and retrieve the text for the prompt of the current test question.",
            "tool_call": "Perform a function call to retrieve the question's prompt by calling retrieve_question_prompt function for each question in the schema.",
            "example_call": "{{'question_number': ['1']}}",
            "instructions": [ ],
        },
    ),
  
        Task(
        task_name="Generate prompt to assist for the current question",
        details={
            "description": "Generate the a prompt for the current question based on the retrieved prompt.",
            "tool_call": "Perform a function call to retrieve the question's prompt by calling generate_system_prompt function for each question  based on the retrieved prompt in the {{tasref :: Retrieve prompt for question}}",
            "example_call": "{{'current_question': ['the retrieved prompt']}}",
            "instructions": [  "Call this only for the actual question and not for the verification questions.",
            ],
        },
    ),
         Task(
        task_name="Generate Baseline Response by answering the Current Instruction by thinking step by step",
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
                "Revise and rewrite the response based on the evaluations and feedback from previous tasks",
                "Make the answer concise and clear. It should address only the question asked."]
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
                 
                 "Evaluate the Response for Accuracy and Completeness", 
                 "Check for Clarity and Conciseness', 'Validate Factual Information",
                 "Make sure to address each point of feedback and correction."
            
                "The score should between 0 and 100. Consider the accuracy, clarity, and completeness of the response when assigning a score.",
                "The final response should definitely contain the score and final score for all type of questions."
            ],
        },
    ),
    
    Task(
        task_name=f"Save the response for each question in json format{output_format}",
        details={
            "description": f"Save the response in the json format{output_format}",
            "instructions": ["Save response for each question one by one into json file by calling save_json function",
                               "Don't forget to save any question.",
                               "If new answer for the question is generated, save the new answer again.",
                               f"The final response should also contain the answer from the task {{tasref :: Generate Final Verified Response}} in the json format {output_format}",],
            "tool_call": "Use the save_json tool.",
            "example_call": f"{{{output_format},'question_number': '1'}}",

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

initial_User_Message = "Welcome to your task dashboard for the Alpaca_Eval dataset. Please review the question in the dataset and start with the first uncompleted task. Focus on generating accurate and comprehensive responses. Refer to any previous tasks if needed to maintain continuity and accuracy. Always complete all the rest of the tasks if you start any tasks inbetween. Do the tasks for each questions, only once. Unless you need to do corrections."

pre_algo_instruct = """Before we start answering questions from the Alpaca_Eval dataset, ensure you understand the context and requirements of each question. You will be provided with the question and expected to research and draft a response based on reliable sources. Pay close attention to the specifics of each question to tailor your responses appropriately."""

post_algo_instruct = "After drafting your response, review it against the example outputs provided for quality and comprehensiveness. Ensure your final response aligns with the expected format and detail as illustrated by successful examples. Reflect on any feedback or revisions suggested in the dataset guidelines to optimize your response before submission."
    
system_message = """
    As an AI trained to assist with the answering questions, your goal is to generate concise and precise answers to the provided instructions.
    This guide will help you step by step to formulate responses that are not only correct but also well-informed and contextually relevant. Don't miss any task. 
    Carefully consider all aspects of the question and ensure your responses are accurate and well-verified. Break down complex problems into simpler, manageable parts and think step by step. Ensure your final answers are concise, clear, and easy to understand.
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



######### CT tasks #########

    # Task(
    #     task_name="Generate Baseline Response by answering the Current Instruction by thinking step by step",
    #     details={
    #         "description": "Produce an initial draft response to the given instruction.",
    #         "instructions": [
    #             "Analyze the instruction carefully and draft a response that fully addresses the query or requirement."
    #         ],
    #     },
    # ),
  
  # Task(
    #     task_name="Plan Verifications",
    #     details={
    #         "description": "Develop a set of verification questions that test the factual accuracy and relevance of the baseline response.",
    #         "instructions": [
    #             "Develop a series of questions that can be used to verify the accuracy and relevance of the response.",
    #             "The verification questions can also ask for sources to explain the reasoning behind the response."
    #             "Review the response to ensure that it correctly interprets the instruction and provides all necessary information or answers all parts of the question."
    #         ],
    #     },
    # ),
    # Task(
    #     task_name="Execute Verifications",
    #     details={
    #         "description": "Address each verification question independently to validate the baseline response.",
    #         "instructions": [
    #             "Examine the response to ensure that it is straightforward, avoiding any vague or redundant content."
    #         ],
    #     },
    # ),
    # Task(
    #     task_name="Generate Final Verified Response",
    #     details={
    #         "description": "Integrate the insights from the verification process to revise and finalize the response.",
    #         "instructions": [
    #             "Revise and rewrite the response based on the evaluations and feedback from previous tasks"]
    #     },
    # ),
    
    
    ######## CL template
    
    #     # Task(
    #     # task_name="Generate Baseline Response",
    #     # details={
    #     # "description": "Produce an initial draft response to the given instruction.",
    #     # "instructions": [
    #     # "Analyze the instruction carefully and draft a response that fully addresses the current question using the system prompt.",
    #     # "Think step by step to ensure a comprehensive answer."
    #     # ],
    #     # },
    #     # ),
    #     Task(
    #     task_name="Plan Verifications",
    #     details={
    #     "description": "Develop a set of verification questions to fact-check the baseline response for the current instruction.",
    #     "instructions": [
    #     "Review the baseline response and identify key facts or claims.",
    #     "For each important fact or claim, create a specific verification question.",
    #     "Ensure the verification questions are independent and don't rely on information from other parts of the response.",
    #     "Focus on questions that can help identify potential hallucinations or inaccuracies.",
    #     "These are verification questions and not additional questions for the baseline response of the current main question."

    #     ],
    #     },
    #     ),
    #     Task(
    #     task_name="Execute Verifications",
    #     details={
    #     "description": "Address each verification question independently to validate the baseline response",
    #     "instructions": [
    #      "Address each verification question independently to validate the baseline response."
    #     "Provide concise, factual answers to each verification question.",
    #     "If uncertain about an answer, indicate this rather than guessing."
    #     "Strictly Don't call generate_system_prompt function for these verification questions."
    #     ],
    #     },
    #     ),
    #     Task(
    #     task_name="Generate Final Verified Response",
    #     details={
    #     "description": "Integrate the insights from the verification process to revise and finalize the response.",
    #     "instructions": [
    #     "Compare the verification answers with the baseline response.",
    #     "Identify any inconsistencies or inaccuracies in the baseline response.",
    #     "Revise the response to correct any errors and incorporate verified information.",
    #     "Ensure the final response is coherent, accurate, and addresses the original instruction."
    #     ],
    #     },
    #     ),