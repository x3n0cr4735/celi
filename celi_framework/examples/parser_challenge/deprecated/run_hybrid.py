#!/usr/bin/env python3
"""
Quick script to run the hybrid parser challenge.

Usage:
    export ANTHROPIC_API_KEY=your-key && export GOOGLE_API_KEY=your-key && python run_hybrid.py
"""

# Load environment variables FIRST before any other imports
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(env_path)

import os
import sys

# Check for API keys
if not os.getenv("ANTHROPIC_API_KEY"):
    print("ERROR: ANTHROPIC_API_KEY not found in environment!")
    print("Please export it: export ANTHROPIC_API_KEY=your-key")
    sys.exit(1)

if not os.getenv("GOOGLE_API_KEY"):
    print("ERROR: GOOGLE_API_KEY not found in environment!")
    print("Please export it: export GOOGLE_API_KEY=your-key")
    sys.exit(1)

print("✓ API keys found")
print("\nRunning hybrid parser challenge for LN6280P RegionalBank...")
print("-" * 60)

# Run the test
from test_hybrid_approach import main
main()