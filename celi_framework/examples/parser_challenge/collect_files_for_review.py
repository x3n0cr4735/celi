#!/usr/bin/env python3
"""
Helper script to collect all relevant files for the hybrid iterative parser challenge
and output them to a single text file for review.
"""

import os
from pathlib import Path
from datetime import datetime

def read_file_safely(filepath):
    """Read a file and return its contents, or an error message if it fails."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"ERROR READING FILE: {str(e)}"

def format_file_section(filepath, content):
    """Format a file's content with proper headers and separators."""
    separator = "=" * 80
    relative_path = filepath
    if "/home/sam/Projects/" in str(filepath):
        relative_path = str(filepath).split("/home/sam/Projects/")[1]
    
    return f"""
{separator}
FILE: {relative_path}
{separator}

{content}

"""

def main():
    # Define all files to collect
    files_to_collect = [
        # Job Description
        "/home/sam/Projects/celi/celi_framework/examples/parser_challenge/job_description_hybrid_iterative.py",
        
        # Tool Implementations (MODIFIED)
        "/home/sam/Projects/celi/celi_framework/examples/parser_challenge/tool_implementations.py",
        
        # Test Harness
        "/home/sam/Projects/celi/celi_framework/examples/parser_challenge/test_harness.py",
        
        # Hybrid LLM Tools
        "/home/sam/Projects/celi/celi_framework/examples/parser_challenge/hybrid_llm_tools.py",
        
        # Runner Script
        "/home/sam/Projects/celi/celi_framework/examples/parser_challenge/run_hybrid_iterative_test.py",
        
        # NEW: Test script for Claude analysis integration
        "/home/sam/Projects/celi/celi_framework/examples/parser_challenge/test_claude_analysis_integration.py",
        
        # NEW: Enhanced job description with analysis capture (example)
        "/home/sam/Projects/celi/celi_framework/examples/parser_challenge/job_description_hybrid_iterative_with_analysis.py",
        
        # CELI Framework Core Files
        "/home/sam/Projects/celi/celi_framework/utils/llms.py",
        "/home/sam/Projects/celi/celi_framework/utils/anthropic_client.py",
        "/home/sam/Projects/celi/celi_framework/utils/converse_client.py",
        "/home/sam/Projects/celi/celi_framework/core/processor.py",
        "/home/sam/Projects/celi/celi_framework/core/section_processor.py",
        "/home/sam/Projects/celi/celi_framework/core/runner.py",
        "/home/sam/Projects/celi/celi_framework/core/job_description.py",
        "/home/sam/Projects/celi/celi_framework/main.py",
        
        # Requirements
        "/home/sam/Projects/celi/celi_framework/examples/parser_challenge/requirements.txt",
        "/home/sam/Projects/celi/pyproject.toml",
    ]
    
    # Output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"/home/sam/Projects/celi/celi_framework/examples/parser_challenge/hybrid_iterative_files_{timestamp}.txt"
    
    # Collect all files
    with open(output_file, 'w', encoding='utf-8') as out:
        # Write header
        out.write(f"""HYBRID ITERATIVE PARSER CHALLENGE - FILE COLLECTION
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This collection includes all files relevant to the hybrid iterative parser challenge run.

KEY CHANGES:
1. job_description_hybrid_iterative.py - Modified to use 5 tasks instead of 6
2. tool_implementations.py - Fixed asyncio issue in fix_parser_with_llm() method (lines 602-647)
3. tool_implementations.py - NEW: Added support for passing Claude's analysis to Gemini:
   - Added claude_analysis instance variable to store Claude's initial analysis
   - Added set_claude_analysis() method to store the analysis
   - Modified run_comprehensive_tests_with_llm_fixes() to accept claude_analysis parameter
   - Modified fix_parser_with_llm_comprehensive_iterative() to include Claude's analysis in prompt
   - Gemini now receives Claude's initial format analysis for better context

ENVIRONMENT REQUIREMENTS:
- ANTHROPIC_API_KEY must be set
- GOOGLE_API_KEY must be set
- Virtual environment: /home/sam/Projects/celi/.venv

""")
        
        # Add each file
        for filepath in files_to_collect:
            if os.path.exists(filepath):
                content = read_file_safely(filepath)
                out.write(format_file_section(filepath, content))
            else:
                out.write(format_file_section(filepath, "FILE NOT FOUND"))
        
        # Add summary of key sections to review
        out.write("""
================================================================================
KEY SECTIONS TO REVIEW
================================================================================

1. ASYNCIO FIX in tool_implementations.py (lines 605-655):
   - The fix_parser_with_llm() method now detects if running in an event loop
   - Uses ThreadPoolExecutor to run LLM calls in separate thread
   - This allows Gemini to be called when tests fail

2. CLAUDE ANALYSIS INTEGRATION (NEW):
   - tool_implementations.py line 28: Added self.claude_analysis instance variable
   - tool_implementations.py lines 36-45: Added set_claude_analysis() method
   - tool_implementations.py line 922: Modified fix_parser_with_llm_comprehensive_iterative signature
   - tool_implementations.py lines 958-965: Added Claude's analysis to Gemini's prompt
   - tool_implementations.py lines 1203-1218: Modified run_comprehensive_tests_with_llm_fixes
   - tool_implementations.py line 1313: Pass claude_analysis to fix method

3. JOB DESCRIPTION CHANGES in job_description_hybrid_iterative.py:
   - Task 4 now named "implementation_and_validation" 
   - Contains intelligent escalation logic with if/else conditions
   - Uses run_comprehensive_tests first, then run_comprehensive_tests_with_llm_fixes if needed

4. TASK STRUCTURE:
   - Task 1: analyze_formats
   - Task 2: propose_code_changes
   - Task 3: verify_plan_with_baseline (uses debug_parser_output)
   - Task 4: implementation_and_validation (with escalation)
   - Task 5: final_verification_and_summary

5. HOW CLAUDE'S ANALYSIS IS PASSED:
   - During Task 1, Claude analyzes format differences
   - The job description should call tools.set_claude_analysis(analysis_text)
   - When run_comprehensive_tests_with_llm_fixes is called, it includes this analysis
   - Gemini receives the analysis in its prompt under "CLAUDE'S INITIAL ANALYSIS" section

6. COMMAND TO RUN:
   source /home/sam/Projects/celi/.venv/bin/activate
   export ANTHROPIC_API_KEY=<key> && export GOOGLE_API_KEY=<key>
   python run_hybrid_iterative_test.py

""")
    
    print(f"Files collected and saved to: {output_file}")
    return output_file

if __name__ == "__main__":
    output_file = main()