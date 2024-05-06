from celi_framework.core.job_description import JobDescription, Task
from celi_framework.examples.human_eval.tools import HumanEvalTools

task_library = [
    Task(
        task_name="Get the prompt for this task",
        details={
            "description": "Find the coding prompt for the current section by calling get_prompt",
        },
    ),
    Task(
        task_name="Write code and run tests",
        details={
            "description": """Decide how to implement the function and call run_tests to check your implementation.
            If the tests don't pass, review the error, correct.  Keep going as long as you are making progress, but if 
            you can't get all the tests to pass after a few tried, move on to the next step.  Include the full prompt
            (with imports) in your call to run function.  Append your implementation to the end of the prompt.""",
        },
    ),
    Task(
        task_name="Product the final output.",
        details={
            "description": """Your final output should be the body of the function indented by 4 spaces.  Do not
            include the function header.  Write the final output using the `save_draft_section` tool.  
            Signal that you have completed the example by calling the pop_context function."""
        },
    ),
]

general_comments = """
============
GENERAL COMMENTS:
START WITH THE FIRST SECTION. ONLY DO THE NEXT UNCOMPLETED TASK (ONLY ONE TASK AT A TIME).
EXPLICITLY print out the current section identifier.
EXPLICITLY print out whether the last task completed successfully or not.
EXPLICITLY print out the task you are completing currently.
EXPLICITLY print out what task you will complete next.
EXPLICITLY provide a detailed and appropriate response for EVERY TASK.

IF TASK HAS NOT COMPLETED SUCCESSFULLY, TRY AGAIN WITH AN ALTERED RESPONSE.
DO NOT REPEAT YOUR PREVIOUS MESSAGE.  
IF YOU NOTICE A TASK (OR SERIES OF TASKS) BEING REPEATED ERRONEOUSLY, devise a plan to move on to the next uncompleted task.
IF YOU ENCOUNTER REPEATED MESSAGES IN THE CHAT HISTORY, reorient yourself by revisiting the last task completed. Check that the sequence of past tasks progresses in logical order. If not, assess and adjust accordingly.
If you are on the same task for a long time, and you are not making progress, just go to the next task and do the best you can.
Do not ever return a tool or function call with the name 'multi_tool_use.parallel'

=============
"""


initial_user_message = """
Please see system message for instructions. Take note of which document section is currently being worked on and which 
tasks have been completed. Complete the next uncompleted task.
If you do not see any tasks completed for the current section, begin with Task #1.

If all tasks for the current section have been completed, proceed to the next document section.
If the new section draft is complete, ensure to 'Prepare for Next Document Section' as described in the tasks.
"""

pre_algo_instruct = """
I am going to give you step by step instructions on how to solve problems in the HumanEval data set.  For each problem
you are given a prompt which is a Python function signature and doc string.  Your job is to draft the function.  There
are a set of test cases that will check the behavior.  You can run the tests and check the results as many times as you
like.  When you are done with your result, your final output is the function body.
For example.  If the prompt is;
def add(a: int, b: int) -> int:
    "Add two numbers"
    
Then your response would be:
    return a+b


You will be given the examples one at a time.
"""

post_algo_instruct = """
"""

job_description = JobDescription(
    role="You are a python coding AI agent. You have the ability to call outside functions.",
    context="The test cases are:",
    task_list=task_library,
    tool_implementations_class=HumanEvalTools,
    pre_context_instruct=pre_algo_instruct,
    post_context_instruct=post_algo_instruct,
    general_comments=general_comments,
    initial_user_message=initial_user_message,
)
