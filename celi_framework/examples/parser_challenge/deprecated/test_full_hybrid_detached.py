#!/usr/bin/env python3
"""
Test script to run a full hybrid parser challenge in detached mode.

This runs the complete job description with Claude orchestrating and Gemini fixing tests.
"""

# Load environment variables FIRST before any other imports
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(env_path)

import os
import sys
import subprocess
import time

def main():
    """Run full hybrid test in detached mode."""
    print("Testing Full Hybrid Parser Challenge (Detached)")
    print("=" * 60)
    
    # Check for API keys
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not found!")
        print("Please run: export ANTHROPIC_API_KEY=your-key")
        sys.exit(1)
        
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not found!")
        print("Please run: export GOOGLE_API_KEY=your-key")
        sys.exit(1)
    
    print("✓ Both API keys found\n")
    
    # Run the detached hybrid job
    cmd = [
        sys.executable,
        "run_detached.py",
        "ln6280p_regional",
        "--api-key", os.getenv("ANTHROPIC_API_KEY"),
        "--hybrid"
    ]
    
    print("Starting hybrid parser challenge...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    # Run the command
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    
    if result.returncode == 0:
        print("\n✓ Hybrid job started successfully!")
        print("\nTo monitor progress:")
        print("  python check_status.py --tail 50")
        print("\nTo see full log:")
        print("  python check_status.py --log 0")
    else:
        print("\n✗ Failed to start hybrid job")
        sys.exit(1)

if __name__ == "__main__":
    main()