#!/usr/bin/env python3
"""Test the hybrid Claude + Gemini approach with the existing parser."""

# Load environment variables FIRST before any other imports
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(env_path)

import os
import sys

# Add parent paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from celi_framework.examples.parser_challenge.tool_implementations import ParserChallengeToolImplementations

def main():
    """Test the hybrid approach."""
    print("Testing Hybrid LLM Approach for Parser Fixes\n")
    print("=" * 60)
    
    # Check for Gemini API key
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY not found in environment variables.")
        print("Please add GEMINI_API_KEY to your .env file.")
        return
    
    print("✓ Gemini API key found")
    print("✓ Using hybrid approach with configurable LLMs\n")
    
    # Initialize tools with configurable fix model
    tools = ParserChallengeToolImplementations(
        document_type="LN6280P",
        bank_name="RegionalBank",
        fix_model="gemini-2.5-flash"  # Can be changed to any supported model
    )
    
    # Load the existing parser that has 60% pass rate
    parser_path = Path("/home/sam/Projects/celi/celi_framework/examples/parser_challenge/output/LN6280P_RegionalBank/parser.py")
    
    if not parser_path.exists():
        print("Error: Parser not found. Please run the parser challenge first.")
        return
    
    print(f"Loading parser from: {parser_path}")
    with open(parser_path, 'r') as f:
        parser_code = f.read()
    
    print("\nRunning comprehensive tests with automatic Gemini fixes...")
    print("-" * 60)
    
    # Run the hybrid test + fix approach
    results = tools.run_comprehensive_tests_with_llm_fixes(parser_code)
    
    print(results)
    
    # Check if the fixed parser was saved
    if "✅ Fixed parser saved successfully!" in results:
        print("\n" + "=" * 60)
        print("SUCCESS! Gemini fixed the parser and all tests now pass!")
        print(f"Fixed parser saved to: {tools.output_dir / f'{tools.document_type}_{tools.bank_name}' / 'parser.py'}")
    else:
        print("\n" + "=" * 60)
        print("Some tests still failing. Manual intervention may be needed.")

if __name__ == "__main__":
    main()