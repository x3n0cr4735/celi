#!/usr/bin/env python3
"""
Example script to run the parser challenge with CELI.

This demonstrates how to configure and run the parser challenge for different
document types and banks.
"""

# Load environment variables FIRST before any other imports
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(env_path)

import sys
import subprocess

# Example configurations for different scenarios
EXAMPLES = {
    # LN6280P challenges with different difficulty levels
    "ln6280p_regional": {
        "document_type": "LN6280P",
        "bank_name": "RegionalBank",
        "description": "Adapt LN6280P parser for RegionalBank (easy - minor format variations)"
    },
    "ln6280p_community": {
        "document_type": "LN6280P",
        "bank_name": "CommunityCredit",
        "description": "Adapt LN6280P parser for CommunityCredit (intermediate - moderate variations)"
    },
    "ln6280p_metro": {
        "document_type": "LN6280P",
        "bank_name": "MetroBank",
        "description": "Adapt LN6280P parser for MetroBank (advanced - significant variations)"
    },
    
    # Placeholder for future document types
    "cd2161p_newbank": {
        "document_type": "CD2161P", 
        "bank_name": "NewBank",
        "description": "Adapt CD2161P (Certificate of Deposit) parser for NewBank"
    },
    "dd2890p_newbank": {
        "document_type": "DD2890P",
        "bank_name": "NewBank", 
        "description": "Adapt DD2890P (Sweep Funds Transfer) parser for NewBank"
    }
}

def run_example(example_name: str, api_key: str = None, simulate: bool = False, model: str = None):
    """Run a parser challenge example."""
    
    if example_name not in EXAMPLES:
        print(f"Unknown example: {example_name}")
        print(f"Available examples: {', '.join(EXAMPLES.keys())}")
        return
    
    config = EXAMPLES[example_name]
    print(f"\nRunning: {config['description']}")
    print(f"Document Type: {config['document_type']}")
    print(f"Bank Name: {config['bank_name']}\n")
    
    # Build the command
    import json
    tool_config = json.dumps({
        "document_type": config['document_type'],
        "bank_name": config['bank_name']
    })
    cmd = [
        sys.executable, "-m", "celi_framework.main",
        "--job-description=celi_framework.examples.parser_challenge.job_description.job_description",
        f"--tool-config={tool_config}"
    ]
    
    # Add model specification (default to Claude Sonnet 4)
    if model:
        cmd.append(f"--primary-model-name={model}")
    else:
        # Use Claude Sonnet 4 as default
        cmd.append("--primary-model-name=claude-sonnet-4-20250514")
    
    # Add higher token limit for large parser code
    cmd.append("--max-tokens=20000")
    
    if simulate:
        cmd.append("--simulate-live")
        print("Running in simulation mode (using cached LLM responses)\n")
    elif api_key:
        cmd.append(f"--anthropic-api-key={api_key}")
    else:
        print("ERROR: Either provide --api-key or use --simulate flag")
        return
    
    # Run the command
    subprocess.run(cmd)

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run parser challenge examples with CELI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with OpenAI API key
  python run_example.py ln6280p_newbank --api-key YOUR_API_KEY
  
  # Run in simulation mode (no API key needed)
  python run_example.py ln6280p_newbank --simulate
  
Available examples:
""" + "\n".join(f"  {name}: {conf['description']}" for name, conf in EXAMPLES.items())
    )
    
    parser.add_argument(
        "example",
        choices=list(EXAMPLES.keys()),
        help="Which example to run"
    )
    parser.add_argument(
        "--api-key",
        help="Anthropic API key (required unless using --simulate)"
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run in simulation mode using cached responses"
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-20250514",
        help="LLM model to use (default: claude-sonnet-4-20250514)"
    )
    
    args = parser.parse_args()
    
    run_example(args.example, args.api_key, args.simulate, args.model)

if __name__ == "__main__":
    main()