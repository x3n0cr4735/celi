"""Job description for parser challenge with Gemini hybrid approach."""

from celi_framework.core.job_description import JobDescription, Task
from celi_framework.examples.parser_challenge.tool_implementations import ParserChallengeToolImplementations

# Create the job description
job_description = JobDescription(
    role="""You are an expert parser developer specializing in banking document processing. 
Your task is to adapt existing parsers to handle format variations from different banks 
while maintaining backward compatibility. You work with Claude for analysis and orchestration,
and can leverage Gemini 2.5 Pro for fixing complex code issues.""",
    
    context="""You are working on adapting the LN6280P parser to handle format variations 
from RegionalBank. The gold standard parser works perfectly for Jack Henry (JH) format 
but needs enhancement to handle RegionalBank's variations. The key requirement is 
maintaining backward compatibility - the enhanced parser must still work correctly 
with the original JH format.""",
    
    task_list=[
        Task(
            task_name="analyze_gold_parser",
            details={
                "description": "Load and analyze the gold standard parser",
                "instructions": """
1. Use read_parser to load the gold standard LN6280P parser for bank 'JH'
2. Understand its structure, patterns, and extraction methods
3. Note the key components: section detection, field extraction, transaction parsing"""
            }
        ),
        
        Task(
            task_name="compare_formats",
            details={
                "description": "Compare JH and RegionalBank input formats",
                "instructions": """
1. Use read_input to load example inputs for both 'JH' and 'RegionalBank'
2. Compare them side-by-side to identify differences
3. Note specific changes in: field labels, prefixes, formatting, structure"""
            }
        ),
        
        Task(
            task_name="analyze_expected_outputs",
            details={
                "description": "Compare expected outputs",
                "instructions": """
1. Use read_expected_output for both 'JH' and 'RegionalBank'
2. Identify any structural differences in the JSON
3. Note if RegionalBank expects additional fields (like phone number)"""
            }
        ),
        
        Task(
            task_name="test_baseline",
            details={
                "description": "Test gold parser on new input",
                "instructions": """
1. Use execute_parser_code to run the gold parser on RegionalBank input
2. Compare the output with expected output to see what's not working
3. Make a list of specific issues to fix"""
            }
        ),
        
        Task(
            task_name="identify_changes",
            details={
                "description": "Identify required parser changes",
                "instructions": """
Based on your analysis, list the specific changes needed:
1. New field label patterns to add
2. New prefix patterns to support
3. Additional extraction logic needed
4. Remember: use additive enhancement only - don't remove existing patterns"""
            }
        ),
        
        Task(
            task_name="implement_enhancements",
            details={
                "description": "Create enhanced parser",
                "instructions": """
1. Start with the gold parser code
2. Add new patterns for each identified difference
3. Use multiple regex patterns with fallback (try JH pattern first, then RegionalBank)
4. Add clear comments explaining each enhancement
5. Ensure all changes are additive - preserve existing functionality"""
            }
        ),
        
        Task(
            task_name="test_enhanced_parser",
            details={
                "description": "Test the enhanced parser",
                "instructions": """
1. Use execute_parser_code to test on RegionalBank input
2. Verify the output matches expected JSON exactly
3. Also test on JH input to ensure backward compatibility
4. If any issues, fix and retest"""
            }
        ),
        
        Task(
            task_name="comprehensive_validation_with_llm_fixes",
            details={
                "description": "Final validation with all test cases using LLM for fixes",
                "instructions": """
1. Run run_comprehensive_tests_with_llm_fixes with your enhanced parser code
2. This will:
   - Run all 5 test cases (main + 4 tests including stress tests)
   - If any fail, automatically call an LLM (Gemini by default) to fix the issues
   - Re-test the fixed code
   - Save the parser if all tests pass
3. Review the results and confirm success"""
            }
        )
    ],
    
    tool_implementations_class=ParserChallengeToolImplementations,
    
    pre_context_instruct="""Remember: The tools will load file contents for you to analyze. 
You should read and understand the actual content, identify patterns and differences yourself, 
and make informed decisions about what changes to implement. When tests fail, Gemini 2.5 Pro
will help fix the specific issues.""",
    
    post_context_instruct="""Focus on creating a robust parser through additive enhancement. 
The gold standard parser is already excellent - you just need to add patterns for the new bank's variations.
If tests fail, the system will automatically use Gemini to help fix them.""",
    
    monitor_instructions="""Ensure:
1. Exact output match with expected JSON
2. Backward compatibility maintained
3. Clear comments for all changes
4. No removal of existing patterns
5. Robust handling of edge cases
6. Leverage Gemini's coding expertise when needed""",
    
    initial_user_message="""Help me adapt the LN6280P parser to handle RegionalBank's format. 
The parser must produce output that exactly matches the expected JSON while maintaining compatibility 
with the original Jack Henry format. Use the hybrid approach with Gemini for fixing any test failures."""
)