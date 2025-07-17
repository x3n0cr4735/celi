#!/usr/bin/env python3
"""Test running CELI with the hybrid job description."""

import sys
from pathlib import Path

# Add parent paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from celi_framework.core.runner import CELIConfig, run_celi
from celi_framework.examples.parser_challenge.job_description_hybrid import job_description
from celi_framework.examples.parser_challenge.tool_implementations import ParserChallengeToolImplementations

def main():
    """Run CELI with hybrid job description."""
    print("Testing CELI with Hybrid Job Description")
    print("=" * 60)
    
    # Initialize tool implementations
    tool_implementations = ParserChallengeToolImplementations(
        document_type="LN6280P",
        bank_name="RegionalBank",
        fix_model="gemini-2.5-flash"
    )
    
    # Create CELI configuration
    config = CELIConfig(
        job_description=job_description,
        tool_implementations=tool_implementations,
        llm_cache=True,
        primary_model_name="claude-3-5-sonnet-20240620",
        max_tokens=4096,
        model_url=None,
        simulate_live=False,
        token_budget=0,
        sequential=True,  # Run tasks sequentially for easier debugging
        force_tool_every_n=5
    )
    
    # Run CELI
    try:
        run_celi(config)
        print("\n✅ CELI completed successfully!")
    except Exception as e:
        print(f"\n❌ Error running CELI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()