#!/usr/bin/env python3
"""
Test the hybrid iterative approach.
"""

import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

import subprocess
import sys
from pathlib import Path
from datetime import datetime

def main():
    """Run the hybrid iterative parser challenge."""
    
    # Check for API keys
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not found in environment")
        print("Please run: export ANTHROPIC_API_KEY=your-key")
        return 1
        
    if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        print("Error: GOOGLE_API_KEY or GEMINI_API_KEY not found in environment")
        print("Please run: export GOOGLE_API_KEY=your-key")
        return 1
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"hybrid_iterative_test_{timestamp}.log"
    
    print(f"Starting hybrid iterative parser challenge...")
    print(f"Log file: {log_file}")
    print(f"Using job description: job_description_hybrid_iterative.py")
    
    # Build the command
    cmd = [
        sys.executable,
        "-m", "celi_framework.main",
        "--job-description=celi_framework.examples.parser_challenge.job_description_hybrid_iterative.job_description",
        "--tool-config={\"document_type\":\"LN6280P\", \"bank_name\":\"RegionalBank\", \"fix_model\":\"gemini-2.5-pro\"}",
        "--primary-model-name=claude-sonnet-4-20250514"
    ]
    
    # Run the command with output to both console and log file
    with open(log_file, 'w') as f:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Stream output
        for line in process.stdout:
            print(line, end='')
            f.write(line)
            f.flush()
        
        process.wait()
    
    print(f"\n{'='*60}")
    print(f"Hybrid iterative test completed!")
    print(f"Log saved to: {log_file}")
    print(f"Return code: {process.returncode}")
    
    # Check if parser was created
    parser_path = Path("output/LN6280P_RegionalBank/parser.py")
    if parser_path.exists():
        print(f"✅ Parser created at: {parser_path}")
    else:
        print(f"❌ Parser not found at: {parser_path}")
    
    return process.returncode

if __name__ == "__main__":
    sys.exit(main())