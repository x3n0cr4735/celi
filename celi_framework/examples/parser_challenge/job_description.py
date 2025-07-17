"""Job description for the parser challenge - adapting parsers for new bank formats."""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import from celi_framework
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from celi_framework.core.job_description import JobDescription, Task
from celi_framework.examples.parser_challenge.tool_implementations import ParserChallengeToolImplementations


def job_description(run_config) -> JobDescription:
    """
    Creates a job description for the parser challenge.
    
    This job description guides an AI agent through the process of:
    1. Reading and understanding existing parsers
    2. Analyzing format differences between banks
    3. Adapting parsers to handle new formats
    4. Testing and validating the results
    """
    
    document_type = run_config.get('document_type', 'LN6280P')
    bank_name = run_config.get('bank_name', 'NewBank')
    
    return JobDescription(
        role="""You are an expert parser developer specializing in banking document processing. 
You excel at:
- Pattern recognition and analysis
- Understanding code structure and logic
- Identifying format variations in documents
- Writing robust parsers that handle edge cases
- Maintaining backward compatibility""",
        
        context=f"""You are working on adapting the {document_type} parser to handle format variations 
from {bank_name}. The gold standard parser from Jack Henry (JH) works perfectly for their format. 
Your task is to extend it to handle the new bank's format variations.

Key principles to follow:
1. ADDITIVE ENHANCEMENT: Add new patterns without removing existing ones
2. ROBUSTNESS: Maintain Unicode support and edge case handling
3. EXACT MATCH: The output must exactly match the expected JSON
4. BACKWARD COMPATIBILITY: The adapted parser must still work with JH format""",
        
        task_list=[
            Task(
                task_name="load_gold_standard",
                details={
                    "description": f"Load and analyze the gold standard {document_type} parser",
                    "instructions": f"""
Use read_parser to load the gold standard parser for {document_type} from bank 'JH'.
Study its structure carefully:
- How does it identify document sections?
- What patterns does it use for each field?
- How does it handle Unicode and special characters?
- What makes it robust?"""
                }
            ),
            
            Task(
                task_name="load_inputs",
                details={
                    "description": "Load both input files to compare formats",
                    "instructions": f"""
Use read_input to load:
1. The gold standard input for {document_type} from bank 'JH'
2. The new bank input for {document_type} from bank '{bank_name}'

Compare them line by line and identify:
- Document title differences
- Field label variations
- Format differences (dates, phones, amounts)
- Structure differences"""
                }
            ),
            
            Task(
                task_name="load_expected_outputs",
                details={
                    "description": "Load expected outputs to understand requirements",
                    "instructions": f"""
Use read_expected_output to load:
1. The gold standard output for {document_type} from bank 'JH'
2. The expected output for {document_type} from bank '{bank_name}'

Verify they have the same JSON structure.
Note any special formatting requirements."""
                }
            ),
            
            Task(
                task_name="test_baseline",
                details={
                    "description": "Test gold parser on new bank input",
                    "instructions": f"""
1. Use execute_parser_code with the gold standard parser code and the new bank input
2. Check if there are any errors
3. If successful, compare the output with the expected output
4. If they don't match, analyze exactly which fields are wrong or missing"""
                }
            ),
            
            Task(
                task_name="identify_needed_changes",
                details={
                    "description": "Identify specific changes needed",
                    "instructions": """
Based on your analysis, list the specific changes needed:
1. New document title patterns to add
2. New field label patterns to add
3. New format patterns (phone, date, etc.)
4. Any other variations

Be very specific about what patterns to add."""
                }
            ),
            
            Task(
                task_name="create_adapted_parser",
                details={
                    "description": "Create the adapted parser",
                    "instructions": """
Starting with the gold standard parser code:
1. Add new patterns for document titles (use elif statements)
2. Add new patterns for field labels (add to existing pattern lists)
3. Add new format patterns where needed
4. Add clear comments explaining each change
5. DO NOT remove or replace existing patterns

The parser code should be complete and executable."""
                }
            ),
            
            Task(
                task_name="test_new_parser",
                details={
                    "description": "Test the adapted parser",
                    "instructions": f"""
1. Use execute_parser_code to run the adapted parser on the new bank input
2. Check if the output matches the expected output
3. If not matching, analyze the differences and fix the parser
4. Repeat until you get an exact match"""
                }
            ),
            
            Task(
                task_name="verify_compatibility",
                details={
                    "description": "Verify backward compatibility",
                    "instructions": f"""
Use test_parser_code to run comprehensive tests:
1. It will test on both gold standard JH input and new bank input
2. Review the results to ensure both tests pass
3. If any test fails, fix the parser and test again"""
                }
            ),
            
            Task(
                task_name="final_validation",
                details={
                    "description": "Final validation with all test cases",
                    "instructions": """
1. Run run_comprehensive_tests to test against all 5 test cases (main example + 4 test cases)
2. Review the results - all tests must pass
3. If all tests pass, save the final parser code using save_parser
4. Summarize the changes made and confirm success"""
                }
            )
        ],
        
        tool_implementations_class=ParserChallengeToolImplementations,
        
        pre_context_instruct="""Remember: The tools will load file contents for you to analyze. 
You should read and understand the actual content, identify patterns and differences yourself, 
and make informed decisions about what changes to implement.""",
        
        post_context_instruct="""Focus on creating a robust parser through additive enhancement. 
The gold standard parser is already excellent - you just need to add patterns for the new bank's variations.""",
        
        monitor_instructions="""Ensure:
1. Exact output match with expected JSON
2. Backward compatibility maintained
3. Clear comments for all changes
4. No removal of existing patterns
5. Robust handling of edge cases""",
        
        initial_user_message=f"""Help me adapt the {document_type} parser to handle {bank_name}'s format. 
The parser must produce output that exactly matches the expected JSON while maintaining compatibility 
with the original Jack Henry format."""
    )