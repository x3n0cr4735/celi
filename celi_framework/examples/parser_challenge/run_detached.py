#!/usr/bin/env python3
"""
Run parser challenge in detached mode with logging.
"""

# Load environment variables FIRST before any other imports
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(env_path)

import os
import sys
import subprocess
import json
from datetime import datetime

# Create logs directory
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

def run_detached(example_name: str, api_key: str, model: str = "claude-sonnet-4-20250514", hybrid: bool = False):
    """Run parser challenge in detached mode with logging."""
    
    # Create timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    hybrid_suffix = "_hybrid" if hybrid else ""
    log_file = LOGS_DIR / f"parser_challenge_{example_name}{hybrid_suffix}_{timestamp}.log"
    pid_file = LOGS_DIR / f"parser_challenge_{example_name}{hybrid_suffix}_{timestamp}.pid"
    
    # Example configurations
    EXAMPLES = {
        "ln6280p_regional": {
            "document_type": "LN6280P",
            "bank_name": "RegionalBank"
        },
        "ln6280p_community": {
            "document_type": "LN6280P",
            "bank_name": "CommunityCredit"
        },
        "ln6280p_metro": {
            "document_type": "LN6280P",
            "bank_name": "MetroBank"
        }
    }
    
    if example_name not in EXAMPLES:
        print(f"Unknown example: {example_name}")
        print(f"Available: {', '.join(EXAMPLES.keys())}")
        return None
    
    config = EXAMPLES[example_name]
    
    # Build command
    tool_config = json.dumps({
        "document_type": config['document_type'],
        "bank_name": config['bank_name']
    })
    
    # Choose job description based on hybrid flag
    if hybrid:
        job_desc = "celi_framework.examples.parser_challenge.job_description_hybrid_iterative.job_description"
        # Update tool config to include fix_model
        config_dict = json.loads(tool_config)
        config_dict["fix_model"] = "gemini-2.5-pro"
        tool_config = json.dumps(config_dict)
    else:
        job_desc = "celi_framework.examples.parser_challenge.job_description.job_description"
    
    cmd = [
        sys.executable, "-m", "celi_framework.main",
        f"--job-description={job_desc}",
        f"--tool-config={tool_config}",
        f"--anthropic-api-key={api_key}",
        f"--primary-model-name={model}",
        "--max-tokens=20000"
    ]
    
    # Run in background with nohup and redirect output to log
    full_cmd = ["nohup"] + cmd
    
    mode = "hybrid mode" if hybrid else "standard mode"
    print(f"Starting parser challenge for {config['bank_name']} in {mode}...")
    print(f"Log file: {log_file}")
    print(f"PID file: {pid_file}")
    
    # Start the process
    with open(log_file, 'w') as log, open(pid_file, 'w') as pid:
        process = subprocess.Popen(
            full_cmd,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            cwd=Path(__file__).parent.parent.parent.parent  # CELI root
        )
        pid.write(str(process.pid))
    
    print(f"Process started with PID: {process.pid}")
    print(f"Run 'python check_status.py' to check progress")
    
    return {
        "pid": process.pid,
        "log_file": str(log_file),
        "pid_file": str(pid_file),
        "timestamp": timestamp
    }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Run parser challenge in detached mode")
    parser.add_argument(
        "example",
        choices=["ln6280p_regional", "ln6280p_community", "ln6280p_metro"],
        help="Which example to run"
    )
    parser.add_argument(
        "--api-key",
        required=True,
        help="Anthropic API key"
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-20250514",
        help="Model to use"
    )
    parser.add_argument(
        "--hybrid",
        action="store_true",
        help="Use hybrid approach with Gemini for fixing failed tests"
    )
    
    args = parser.parse_args()
    
    # Activate virtual environment if available
    venv_activate = Path(__file__).parent.parent.parent.parent / ".venv" / "bin" / "activate_this.py"
    if venv_activate.exists():
        exec(open(venv_activate).read(), {'__file__': str(venv_activate)})
    
    result = run_detached(args.example, args.api_key, args.model, hybrid=args.hybrid)
    if result:
        print("\nProcess info saved to logs directory")

if __name__ == "__main__":
    main()