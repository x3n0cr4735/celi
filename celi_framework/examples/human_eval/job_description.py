from celi_framework.core.job_description import JobDescription, Task
from celi_framework.examples.human_eval.tools import HumanEvalTools

task_library = [
    Task(
        task_name="Get the prompt",
        details={
            "description": "Find the coding prompt for the current section by calling get_prompt",
        },
    ),
    Task(
        task_name="Develop initial test cases",
        details={
            "description": """Think through the problem and develop an initial set of test cases that will be used to
            check the logic for your function.  The test cases must be implemented as a function called 
            'def check(candidate)' that takes the function as an argument.  Each test is an 'assert' statement that 
            calls the function with some inputs and verifies that that output is as expected.  For example, if the task its to create a function called
            'add_two_numbers", the test function might look like:
            def check(candidate):
                assert add_two_numbers(1, 2) == 3
                assert add_two_numbers(0, 0) == 0
                assert add_two_numbers(-1, 1) == 0
                assert add_two_numbers(1.5, 1) == 2.5
            
            When writing test cases, think through edge cases and different types of inputs that might be passed to the function.
            Some functions that may seen very simple have a trick to them.  
            When mapping from a real world description of a problem to the algorithm, make sure you have the situation modeled correctly.
            Be sure the function behaves correctly when numbers are integers or floats.
            Be sure to handle negative numbers appropriately.
            If you have a test case that is failing, write out the intermediate steps involved in that test case and see
            if that explains why your implementation is failing.
            If you need to debug, you can add print statements into the functions you pass to run_tests. 
            Think about issue like empty inputs and multiple delimiters.  
            
            Remember that check must take the a `candidate` argument that is the function to test.         
            """,
        },
    ),
    Task(
        task_name="Write and test code",
        details={
            "description": """
            In this task you iteratively refine your implementation and test cases.   
            Decide how to implement the function and call run_tests to check your implementation, passing in the code 
            and tests. Make sure to include all required imports.   If the tests don't pass, check both your implementation 
            and the test cases and decide which needs 
            to be adjusted (or both). Don't assume the test cases are correct, review the problem specification and 
            adjust if necessary.  Also, feel free to add more tests.  
            Keep going as long as you are making progress, but if 
            you can't get all the tests to pass after a few tries, just save your output and complete.""",
        },
    ),
    Task(
        task_name="Produce the final output.",
        details={
            "description": """Call save_final_output to save off your final answer.  This should include your 
            function implementation as well as your test function.  Always do this, even if you aren't completely
            happy with your answer. 
            Signal that you have completed the example by calling the complete_section function."""
        },
    ),
]

general_comments = """
============
GENERAL COMMENTS:
Work through the listed tasks one by one.  Explicitly note which task you are working on.
Do not return an empty response.
Do not return a tool or function call with the name 'multi_tool_use.parallel'
=============
"""


initial_user_message = """
Call get_prompt to get function signature.
"""

pre_algo_instruct = """
We are solving a problem in the HumanEval data set.  You are given a prompt which is a Python function signature and doc string.  
Your job is to draft the function.

For example.  If the prompt is;
def add(a: int, b: int) -> int:
    "Add two numbers"
    
Then your response would be:
    return a+b

The tasks you need to do to solve the problem are:

"""

post_algo_instruct = """
"""

job_description = JobDescription(
    role="You are a python coding AI agent.",
    context="",
    task_list=task_library,
    tool_implementations_class=HumanEvalTools,
    pre_context_instruct=pre_algo_instruct,
    post_context_instruct=post_algo_instruct,
    monitor_instructions="""save_final_output must be called before calling complete_section.  
    Also, run_tests should have been called on the implementation that was saved and it should have returned without 
    any failures.""",
    general_comments=general_comments,
    initial_user_message=initial_user_message,
    include_schema_in_system_message=False,
)
