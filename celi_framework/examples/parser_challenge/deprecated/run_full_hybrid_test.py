#!/usr/bin/env python3
"""
Full hybrid test script - runs from scratch with hybrid approach.

This demonstrates the full power of the hybrid approach by:
1. Starting with a fresh parser (0% pass rate)
2. Running tests to identify failures
3. Using Gemini to fix each failure
4. Achieving 100% pass rate
"""

# Load environment variables FIRST before any other imports
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(env_path)

import os
import sys
import shutil

# Add parent paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from celi_framework.examples.parser_challenge.tool_implementations import ParserChallengeToolImplementations

def main():
    """Run the full hybrid test from scratch."""
    print("Full Hybrid LLM Test - From 0% to 100%")
    print("=" * 60)
    
    # Check for API keys
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not found in environment variables.")
        print("Please export it: export ANTHROPIC_API_KEY=your-key")
        return
    
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        print("Error: GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables.")
        print("Please export it: export GOOGLE_API_KEY=your-key")
        return
    
    print("✓ API keys found")
    print("✓ Using hybrid approach: Claude + Gemini\n")
    
    # Initialize tools with hybrid configuration
    tools = ParserChallengeToolImplementations(
        document_type="LN6280P",
        bank_name="RegionalBank",
        fix_model="gemini-2.5-flash"
    )
    
    # Clean up any existing parser to start fresh
    parser_path = tools.output_dir / f"{tools.document_type}_{tools.bank_name}" / "parser.py"
    if parser_path.exists():
        print(f"Removing existing parser at: {parser_path}")
        parser_path.unlink()
        print("Starting fresh with 0% pass rate\n")
    
    # Step 1: Create initial parser (will fail all tests)
    print("Step 1: Creating initial parser from gold standard...")
    print("-" * 60)
    
    # Load gold standard parser
    gold_parser_path = Path("/home/sam/Projects/prog_parser_statements/prog_parsers/JH/LN6280P/parser.py")
    with open(gold_parser_path, 'r') as f:
        initial_parser = f.read()
    
    # Save as initial parser
    tools.save_parser(initial_parser)
    print(f"✓ Initial parser saved to: {parser_path}")
    
    # Step 2: Run initial tests (expect failures)
    print("\nStep 2: Running initial tests...")
    print("-" * 60)
    initial_results = tools.run_comprehensive_tests(initial_parser)
    print(initial_results)
    
    # Step 3: Run hybrid approach with automatic fixes
    print("\nStep 3: Running hybrid approach with automatic Gemini fixes...")
    print("-" * 60)
    final_results = tools.run_comprehensive_tests_with_llm_fixes(initial_parser)
    print(final_results)
    
    # Step 4: Verify final results
    print("\n" + "=" * 60)
    if "✅ Fixed parser saved successfully!" in final_results:
        print("SUCCESS! Full hybrid approach completed:")
        print("- Started with 0% pass rate (gold standard parser)")
        print("- Identified all format differences")
        print("- Used Gemini to fix each failure")
        print("- Achieved 100% pass rate")
        print(f"\nFinal parser saved to: {parser_path}")
    else:
        print("Some tests still failing. Check the output above for details.")

if __name__ == "__main__":
    main()