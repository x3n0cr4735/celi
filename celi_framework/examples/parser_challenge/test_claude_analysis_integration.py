#!/usr/bin/env python3
"""
Test script to demonstrate how Claude's analysis is passed to Gemini
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from celi_framework.examples.parser_challenge.tool_implementations import ParserChallengeToolImplementations

def test_claude_analysis_integration():
    """Test that Claude's analysis can be passed through to Gemini"""
    
    # Initialize tools
    tools = ParserChallengeToolImplementations(
        document_type="LN6280P",
        bank_name="RegionalBank",
        fix_model="gemini-2.5-flash"
    )
    
    # Example of Claude's analysis that would be captured from the job description workflow
    claude_analysis = """
After analyzing the format differences between Jack Henry (JH) and RegionalBank:

1. **Customer Name Prefix Change**:
   - JH uses prefix '3' for customer names
   - RegionalBank uses prefix '4' for customer names
   
2. **Date Field Label Changes**:
   - JH: "Statement Date" → RegionalBank: "Billing Date"
   - JH: "Payment Due Date" → RegionalBank: "Due Date"
   
3. **Amount Field Label Changes**:
   - JH: "Total Amount Due" → RegionalBank: "Payment Amount Due" (with ** emphasis)
   - JH: "Current Balance" → RegionalBank: "Outstanding Balance"
   - JH: "Regular Payment Amount" → RegionalBank: "Monthly Payment"
   
4. **New Fields**:
   - RegionalBank adds "Phone Number" field after Due Date
   
5. **Bank Address Structure**:
   - JH: Empty dict {} for bank address
   - RegionalBank: Proper address dict with street/city/state/zip fields (all null)
   
6. **Bottom Section Label Change**:
   - JH: "Total Amount Due" → RegionalBank: "Payment Amount Due" in borrower section

These changes require updating the parser's regex patterns and field extraction logic while maintaining backward compatibility with JH format.
"""
    
    # Load Claude's adapted parser (simulating what would be passed)
    parser_code = tools.read_parser("LN6280P", "RegionalBank")
    
    # Now test with Claude's analysis included
    print("Testing parser with Claude's analysis passed to Gemini...")
    results = tools.run_comprehensive_tests_with_llm_fixes(
        parser_code=parser_code,
        max_iterations=3,
        claude_analysis=claude_analysis
    )
    
    print(results)

if __name__ == "__main__":
    test_claude_analysis_integration()