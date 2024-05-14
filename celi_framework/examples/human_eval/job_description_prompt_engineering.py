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
        task_name="Write specs",
        details={
            "description": """
        Write detailed specifications for the implementation of a function based on a given description. 
        Your specifications should guide a developer to understand exactly what needs to be coded, 
        ensuring they grasp both the functional requirements and the nuances of the problem. 

        The specification should include the following elements:

        1. **Function Signature**: Define the input and output types of the function. 

        2. **Purpose**: Describe what the function aims to achieve. Include any specific goals or problems it addresses.

        3. **Input Details**: Elaborate on the nature of the inputs, including the data type and any constraints or specific conditions that the inputs must meet.

        4. **Output Details**: Define what outputs are expected, the conditions they should meet, and the data type of these outputs.

        5. **Behavioral Specifications**: Describe how the function should behave in different scenarios, including edge cases.

        **Example Specification for `is_palindrome_permutation`**:
        **Function Signature**: 
        ```python
        def is_palindrome_permutation(s: str) -> bool
        ```

        **Purpose**: 
        Determine if any permutation of the characters in a given string can form a palindrome.

        **Input Details**: 
        - `s`: str - a string which can contain any ASCII characters.

        **Output Details**: 
        - Returns `True` if at least one permutation of the string can form a palindrome, otherwise `False`.

        **Behavioral Specifications**: 
        - The function should handle any string of ASCII characters, including empty strings.
        - Function should be case insensitive.
        
        DO NOT DO EXAMPLES YET. THAT IS FOR THE NEXT TASK.
        
        """
        },
    ),
    Task(
        task_name="Restate the problem / Example and Edge Case Development",
        details={
            "description": """
            Develop comprehensive example and edge cases that illustrate how the function `is_palindrome_permutation` should operate. This task is crucial for ensuring that the function is robust, handles all specified behaviors, and adheres to the requirements outlined in the function's specifications.
            HOWEVER, first you must step back and ask yourself if you really understand what the code challenge is asking. RESTATE THE CODING CHALLENGE PROMPT. THEN MOVE ON TO THE REST OF THIS TASK.

            **Objective**:
            - Create a set of example cases that demonstrate typical functionality as well as edge cases that test the function’s limits or special behavior.

            **Instructions**:
            1. **Generate Example Cases**: Create at least five varied example inputs that cover different scenarios, including simple cases and more complex strings. Ensure these examples comprehensively demonstrate the function's capability to evaluate whether any permutation of a string can form a palindrome.

            2. **Detail Edge Cases**: Specifically design edge cases that test the function's behavior with the smallest possible inputs, unusual patterns, or where edge behaviors might typically occur, such as empty strings or strings with a single character.

            3. **Explain Each Case**: For each example and edge case, provide a detailed explanation of why it is included, what it tests, and the expected output. This explanation should help clarify the function’s logic and its handling of different types of inputs.

            4. **Document Expected Outputs**: For each input case, clearly state the expected output and provide a rationale based on the function’s logic. This step is crucial for later validation during testing.

            # Example Assertions with Explanations
            assert candidate('Tact Coa') == True  # True: Can be permuted into "taco cat" or "atco cta", both palindromes.
            assert candidate('hello') == False  # False: No permutation forms a palindrome.
            assert candidate('A Santa at NASA') == True  # True: Can be permuted into "A Santa at NASA", a palindrome.
            assert candidate('No lemon, no melon') == True  # True: Can be permuted into "No lemon, no melon", a palindrome.
            assert candidate('1a2a1') == True  # True: Can be permuted into "a112a" or "1aa21", a palindrome.
            assert candidate('! 2020 !') == True  # True: Can be permuted to form "!02020!", a palindrome.
            assert candidate('abcd') == False  # False: No permutation can form a palindrome due to unique characters.
            
            # Edge Case Assertions with Explanations
            assert candidate('') == True  # True: An empty string is trivially a palindrome.
            assert candidate('a') == True  # True: A single character is trivially a palindrome.
            assert candidate('bb') == True  # True: The string "bb" is already a palindrome and trivially rearranged.
            assert candidate('abc') == False  # False: No permutation of 'abc' can form a palindrome due to all unique characters.
            assert candidate('Racecar') == True  # True: "Racecar" can be permuted to "racecaR", which is a palindrome ignoring case.
            assert candidate('1221') == True  # True: "1221" is already a palindrome and can be rearranged in multiple ways.
            assert candidate('123') == False  # False: With all unique digits, no permutation of '123' forms a palindrome.

            This comprehensive development of example and edge cases will ensure the function is thoroughly tested against a variety of inputs, enhancing reliability and robustness.
            """
        },
    ),
    Task(
        task_name="Develop Solution Logic",
        details={
            "description": """
        Before coding, systematically outline your solution strategy. This task involves a detailed breakdown of the problem to ensure you conceptualize the data handling and flow efficiently and prepare for straightforward implementation.

        1. **Review Requirements**: Thoroughly understand the function's purpose and the specifications it must meet. Consider what the function aims to achieve and any specific conditions it must satisfy.

        2. **Component Identification**: Identify essential components required for the solution, including necessary data structures for processing and elements for logical operations.

        3. **Infer Patterns from Examples**:
           - **Generate Examples**: Create at least five varied example inputs and determine their expected outputs.
           - **Analyze Outputs**: Examine the outputs to discern any underlying patterns or rules that could influence the function's logic.
           - **Formulate Strategy**: Develop a strategy based on observed patterns. This strategy should guide the function's logic to meet the specified requirements efficiently.

        4. **Logic Outline**: 
           - Clearly define the main steps of your solution, ensuring each part is justified with reference to the requirements and identified patterns.
           - Be pedagogical in your explanations, ensuring each logical decision is clearly articulated and logically sound.

        5. **Write Pseudocode**: Draft pseudocode that represents your solution logic in a straightforward and logical sequence. Ensure this pseudocode is simple and clear, making the actual coding process efficient and direct.

        6. **Edge Case Consideration**: Integrate edge cases into your testing strategy without complicating the core logic. Ensure that handling for these cases follows naturally from the main logic.

        7. **Testing Strategy**: Develop a comprehensive testing plan that includes both typical scenarios and edge cases. Make sure your tests validate the function against all specified behaviors and conditions.

        **Example Application**:
        For a function designed to determine if any permutation of a string can form a palindrome:
        - **Generate Example Cases**: Create inputs like 'A Santa at NASA', 'hello', etc., and predict outcomes.
        - **Pseudocode**:
            ```python
            def is_palindrome_permutation(s):
                if not s: return True
                from collections import Counter
                counts = Counter(s.lower().replace(" ", ""))
                return sum(v % 2 for v in counts.values()) <= 1
            ```
        - **Testing Strategy**:
            - Verify the function correctly identifies palindromic potential in inputs.
            - Ensure it handles empty strings and strings with a single type of character, as these are trivially palindromes.

        This framework ensures that your approach to coding is not only methodically sound but also efficiently meets the specified requirements with the simplest and most effective solution.
        """
        },
    ),
    Task(
        task_name="Write code and run tests",
        details={
            "description": """Decide how to implement the function and call run_tests to check your implementation.
            Use the "example cases" in the spec to test. If the tests don't pass, review the error and correct it.  
            Keep going as long as you are making progress (see "Note" however).
            Include the full prompt (with imports) in your call to run function.
            Append your implementation to the end of the prompt.
            Note: If the test are run but they fail due to the code needing improvements, retry this step until it 
            succeeds or you have retried it **5 times** (count the retries!), after which you can produce the final output.
            """,
        },
    ),
    # Task(
    #     task_name="Write code and run tests",
    #     details={
    #         "description": """Decide how to implement the function and call run_tests to check your implementation.
    #     If the tests don't pass, review the error, correct.  Keep going as long as you are making progress.
    #     Include the full prompt (with imports) in your call to run function.
    #     Append your implementation to the end of the prompt.
    #     Note: If the test are run but they fail due to the code needing improvements, retry this step until it
    #     succeeds or you have retried it 5 times.
    #     """,
    #     },
    # ),
    # Task(
    #     task_name="Write code and run tests",
    #     details={
    #         "description": """Decide how to implement the function and proceed to call run_tests to check your implementation.
    #     If the tests don't pass, review the error, make corrections, and retry. Continue this process as long as you are making progress.
    #     If you are unable to pass all tests after several attempts, consider moving on to the next step.
    #     Always include the full prompt (with imports) when you call the run function, and append your implementation at the end of the prompt.
    #     Note 1: Document each trial, noting down the attempt number and any significant changes made or insights gained during the process.
    #     Note 2: If you are stuck and cannot proceed with verifying the test results, try modifying the arguments used in the run_tests function.
    #     Review the arguments for correctness and ensure they are well-formed.
    #     Note 3: If an attempt fails, reflect on the process and determine if a different strategy might be more effective. Allow up to 10 attempts;
    #     if the issue persists, assess whether further attempts are likely to succeed.
    #     Note 4: Enhance error diagnostics by incorporating detailed print statements and assertions to track the function's behavior and internal state at critical points.
    #     Begin with basic logging and increase detail only as needed to avoid overwhelming output. Adjust the logging based on the complexity and frequency of issues encountered.
    #     This method will aid in isolating the cause of failures by providing insight into data flow and transformations.
    #     Note 5: After multiple attempts, take time to review all modifications and results. This reflection will help identify any recurring patterns or errors in your approach,
    #     enabling you to refine your strategy for future tasks.
    #     """,
    #     },
    # ),
    # TODO -> Send problem challenges to separate separate thread that then saves them back to the draft json if they are solved correctly
    Task(
        task_name="Produce the final output.",
        details={
            "description": """Your final output should be the body of the function indented by 4 spaces.  Do not
            include the function header.  Write the final output using the `save_final_output` tool.  Include the tests your wrote also.
            Signal that you have completed the example; you have the ability to call the pop_context function to do so."""
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
    include_schema_in_system_message=False,
)
