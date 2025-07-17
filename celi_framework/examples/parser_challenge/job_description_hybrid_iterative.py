"""Job description for parser challenge with systematic Claude + Gemini hybrid approach."""

from celi_framework.core.job_description import JobDescription, Task
from celi_framework.examples.parser_challenge.tool_implementations import ParserChallengeToolImplementations

# Create the job description
job_description = JobDescription(
    role="""You are an expert parser developer specializing in banking document processing. 
You excel at pattern recognition, code analysis, and creating robust parsers.""",
    
    context="""Your goal is to adapt the LN6280P parser to handle format variations from a new client, RegionalBank. 
The original parser for Jack Henry (JH) is the starting point. You will focus exclusively on making 
the parser work for the new RegionalBank format.

You will follow a systematic, evidence-based development plan with 5 tasks that form ONE complete workflow:
1. Task 1: Analyze the formats to understand the key differences.
2. Task 2: Propose code changes based on your analysis before writing code.
3. Task 3: Verify your plan by running a baseline test.
4. Task 4: Implement changes and validate with intelligent escalation if needed.
5. Task 5: Review final results and summarize the work.

All 5 tasks must be completed before calling complete_section. This systematic approach ensures your changes are logical and robust.""",
    
    task_list=[
        Task(
            task_name="analyze_formats",
            details={
                "description": "Analyze both the Jack Henry (JH) and RegionalBank formats to understand the key differences",
                "instructions": """
1. Use read_parser to load the gold standard LN6280P parser.
2. Use read_input and read_expected_output to load the files for both 'JH' and 'RegionalBank'.
3. Compare the inputs and expected outputs to create a detailed list of the differences. 
   This analysis will be the foundation for your code changes."""
            }
        ),
        
        Task(
            task_name="propose_code_changes",
            details={
                "description": "Based on your analysis, develop a plan of the necessary code modifications",
                "instructions": """
1. Based on the format differences you observed in Task 1, formulate a hypothesis of what needs to change in the parser code.
2. List the specific functions and regex patterns that will require modification.
3. For each, describe the change you plan to make (e.g., "Update the find_customer_info function to detect the '4' prefix instead of '3'.")"""
            }
        ),
        
        Task(
            task_name="verify_plan_with_baseline",
            details={
                "description": "Run the original parser on the new format to verify that your proposed changes are necessary",
                "instructions": """
1. Now, use debug_parser_output to run the original gold parser on the RegionalBank input.
2. Analyze the failures from this baseline test by comparing the actual vs. expected output.
3. Confirm that the fields that fail are the same ones you identified for modification in your Task 2 plan."""
            }
        ),
        
        Task(
            task_name="implementation_and_validation",
            details={
                "description": "Implement the planned changes and validate against all test cases, with intelligent escalation",
                "instructions": """
1. Start by implementing the changes you planned in Task 2.
2. Run `run_comprehensive_tests` to validate your parser against all 5 test cases.
3. Analyze the results:
   - **If all tests pass**: Excellent! Your implementation is complete.
   - **If some tests fail**: Study the error messages and try to fix them yourself. You may iterate 1-2 times.
4. After your attempts, run `run_comprehensive_tests` again.
5. **If tests still fail after your attempts**: Use `run_comprehensive_tests_with_llm_fixes` to get expert assistance from Gemini. This tool will analyze the failures and provide targeted fixes."""
            }
        ),
        
        Task(
            task_name="final_verification_and_summary",
            details={
                "description": "Review the final test results and summarize the work",
                "instructions": """
1. Review the final test results to confirm all 5 tests have passed.
2. If successful, the parser will be automatically saved.
3. Summarize the changes that were made to adapt the parser for the RegionalBank format."""
            }
        )
    ],
    
    tool_implementations_class=ParserChallengeToolImplementations,
    
    pre_context_instruct="""You will follow a systematic approach: analyze, plan, verify, implement, and validate.
This ensures your changes are based on evidence and your implementation is robust.""",
    
    post_context_instruct="""Remember: Focus exclusively on making the parser work for RegionalBank. 
Since backward compatibility is not required, you can modify or replace patterns as needed.

IMPORTANT: Do NOT call complete_section until ALL 5 TASKS have been completed. 
The tasks form one complete workflow - analyze, propose, verify, implement/validate, and summarize.
Only after Task 5 (final_verification_and_summary) should you call complete_section with "parser_tasks".""",
    
    monitor_instructions="""Key requirements:
1. Systematic development - analyze, plan, verify, then implement
2. Exact JSON output match
3. RegionalBank format working correctly
4. Clear documentation of changes
5. All 5 test cases must pass
6. Smart escalation - try fixing yourself first, then leverage Gemini if needed""",
    
    initial_user_message="""Help me adapt the LN6280P parser to handle RegionalBank's format.
Follow the systematic approach: analyze the differences, propose changes, verify with baseline test,
then implement and validate. If you encounter difficult test failures, the system can leverage Gemini's expertise."""
)