"""
Enhanced hybrid iterative job description that captures and passes Claude's analysis to Gemini
"""

def job_description(tools):
    """
    Enhanced hybrid iterative approach that ensures Claude's analysis is passed to Gemini.
    This version captures Claude's initial analysis and includes it in all Gemini fix attempts.
    """
    
    # Storage for Claude's analysis
    claude_analysis_storage = {"analysis": None}
    
    def enhanced_analyze_formats(tools):
        """Task 1 with analysis capture"""
        result = tools.analyze_formats()
        
        # Capture the analysis text that Claude generates
        # This would be the detailed comparison of differences
        if hasattr(tools, '_last_analysis'):
            claude_analysis_storage["analysis"] = tools._last_analysis
        
        return result
    
    def enhanced_implementation_and_validation(tools):
        """Task 4 with Claude's analysis passed to Gemini"""
        # Get Claude's analysis from storage
        claude_analysis = claude_analysis_storage.get("analysis", None)
        
        # If we have claude_analysis, create a wrapper for run_comprehensive_tests_with_llm_fixes
        if claude_analysis and hasattr(tools, 'run_comprehensive_tests_with_llm_fixes'):
            original_method = tools.run_comprehensive_tests_with_llm_fixes
            
            def wrapped_method(parser_code, max_iterations=3):
                return original_method(parser_code, max_iterations, claude_analysis=claude_analysis)
            
            # Temporarily replace the method
            tools.run_comprehensive_tests_with_llm_fixes = wrapped_method
        
        # Run the standard implementation
        return tools.implementation_and_validation()
    
    return {
        "name": "Parser Adaptation with Hybrid Iterative LLM Approach (Enhanced)",
        "description": """Adapt a banking document parser to handle format variations from a new client.
        
This enhanced version:
1. Uses Claude to analyze formats and create the initial adaptation
2. Captures Claude's analysis of format differences
3. Passes Claude's analysis to Gemini for context in all fix attempts
4. Leverages Gemini to fix any edge cases Claude misses
5. Supports up to 3 iterations of refinement per fix attempt
6. Achieves 100% test coverage through intelligent collaboration

The key enhancement is that Gemini receives Claude's initial analysis, ensuring continuity of understanding across both models.""",
        
        "sections": {
            "parser_tasks": {
                "tasks": [
                    {
                        "name": "analyze_formats",
                        "description": "Analyze both the Jack Henry (JH) and RegionalBank formats to understand the key differences",
                        "instructions": """
1. Use read_parser to load the gold standard LN6280P parser.
2. Use read_input and read_expected_output to load the files for both 'JH' and 'RegionalBank'.
3. Compare the inputs and expected outputs to create a detailed list of the differences.
4. Document each difference clearly with examples from the actual data.
5. Store this analysis - it will be passed to Gemini later for context.

Your analysis should cover:
- Customer name prefix differences
- Date field label changes
- Amount field label changes  
- New fields added
- Structural differences in output JSON
- Any other patterns that differ between formats"""
                    },
                    {
                        "name": "propose_code_changes",
                        "description": "Based on your analysis, develop a plan of the necessary code modifications",
                        "instructions": """
1. Based on the format differences you identified, formulate specific code changes needed.
2. List the functions and regex patterns that need modification.
3. For each change, explain why it's needed and how it addresses the format differences.
4. Emphasize the additive enhancement approach - adding new patterns without removing existing ones."""
                    },
                    {
                        "name": "verify_plan_with_baseline",
                        "description": "Run the original parser on the new format to verify that your proposed changes are necessary",
                        "instructions": """
1. Use debug_parser_output to run the original gold parser on the RegionalBank input.
2. Analyze the failures to confirm they match your identified differences.
3. This validates that your analysis and proposed changes are correct."""
                    },
                    {
                        "name": "implementation_and_validation",
                        "description": "Implement the planned changes and validate against all test cases, with intelligent escalation",
                        "instructions": """
1. Implement the changes you planned in Task 2.
2. Use the additive enhancement approach - add new patterns alongside existing ones.
3. Run run_comprehensive_tests to validate against all 5 test cases.
4. If tests fail after your attempts, use run_comprehensive_tests_with_llm_fixes.
   - This will automatically call Gemini with:
     * Your analysis from Task 1
     * The current parser code
     * Detailed test failure information
     * All test cases (passing and failing)
     * Complete iteration history
   - Gemini will have full context including your initial analysis
5. The system supports up to 3 iterations of fixes."""
                    },
                    {
                        "name": "final_verification_and_summary", 
                        "description": "Review the final test results and summarize the work",
                        "instructions": """
1. Review the final test results to confirm all 5 tests pass.
2. Verify backward compatibility is maintained.
3. Summarize what was accomplished, including:
   - Your initial analysis findings
   - Changes you implemented
   - Any fixes Gemini contributed
   - Final success metrics"""
                    }
                ]
            }
        },
        
        # Override specific task implementations
        "task_overrides": {
            "analyze_formats": enhanced_analyze_formats,
            "implementation_and_validation": enhanced_implementation_and_validation
        }
    }