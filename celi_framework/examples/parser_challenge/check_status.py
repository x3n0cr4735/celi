#!/usr/bin/env python3
"""
Check status of detached parser challenge runs.
"""

# Load environment variables FIRST before any other imports
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(env_path)

import os
import sys
import subprocess
from datetime import datetime

LOGS_DIR = Path(__file__).parent / "logs"

def check_process_status(pid: int) -> bool:
    """Check if a process is still running."""
    try:
        # Check if process exists (doesn't actually kill it with signal 0)
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def tail_log(log_file: Path, lines: int = 50):
    """Show the last N lines of a log file."""
    if not log_file.exists():
        return "Log file not found"
    
    try:
        result = subprocess.run(
            ["tail", f"-{lines}", str(log_file)],
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        # Fallback to Python implementation
        with open(log_file, 'r') as f:
            content = f.readlines()
            return ''.join(content[-lines:])

def list_recent_runs():
    """List all recent parser challenge runs."""
    if not LOGS_DIR.exists():
        print("No logs directory found")
        return []
    
    runs = []
    for pid_file in sorted(LOGS_DIR.glob("*.pid"), reverse=True):
        log_file = pid_file.with_suffix('.log')
        
        # Parse info from filename
        parts = pid_file.stem.split('_')
        if len(parts) >= 4:
            example = '_'.join(parts[2:-2])
            timestamp = '_'.join(parts[-2:])
            
            # Read PID
            try:
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # Check if still running
                is_running = check_process_status(pid)
                
                # Get log file size
                log_size = log_file.stat().st_size if log_file.exists() else 0
                
                runs.append({
                    'example': example,
                    'timestamp': timestamp,
                    'pid': pid,
                    'running': is_running,
                    'log_file': log_file,
                    'log_size': log_size
                })
            except Exception as e:
                print(f"Error reading {pid_file}: {e}")
    
    return runs

def format_size(size: int) -> str:
    """Format file size in human readable form."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Check status of parser challenge runs")
    parser.add_argument(
        "--tail",
        type=int,
        metavar="N",
        help="Show last N lines of the most recent log (default: 50)"
    )
    parser.add_argument(
        "--log",
        type=int,
        metavar="INDEX",
        help="Show specific log by index (0 = most recent)"
    )
    parser.add_argument(
        "--kill",
        type=int,
        metavar="PID",
        help="Kill a running process by PID"
    )
    
    args = parser.parse_args()
    
    # Get list of runs
    runs = list_recent_runs()
    
    if not runs:
        print("No parser challenge runs found")
        return
    
    # Kill process if requested
    if args.kill:
        try:
            os.kill(args.kill, 15)  # SIGTERM
            print(f"Sent SIGTERM to process {args.kill}")
        except OSError as e:
            print(f"Error killing process {args.kill}: {e}")
        return
    
    # Show tail of specific log
    if args.tail is not None or args.log is not None:
        if args.log is not None:
            if 0 <= args.log < len(runs):
                run = runs[args.log]
            else:
                print(f"Invalid log index. Valid range: 0-{len(runs)-1}")
                return
        else:
            run = runs[0]  # Most recent
        
        lines = args.tail if args.tail else 50
        print(f"\n=== Last {lines} lines of {run['log_file'].name} ===\n")
        print(tail_log(run['log_file'], lines))
        
        if run['running']:
            print(f"\n[Process {run['pid']} is still running]")
        else:
            print(f"\n[Process {run['pid']} has completed]")
        return
    
    # Default: Show status of all runs
    print("Parser Challenge Runs:")
    print("-" * 80)
    print(f"{'#':<3} {'Example':<20} {'Timestamp':<15} {'PID':<8} {'Status':<10} {'Log Size':<10}")
    print("-" * 80)
    
    for i, run in enumerate(runs):
        status = "RUNNING" if run['running'] else "COMPLETE"
        print(f"{i:<3} {run['example']:<20} {run['timestamp']:<15} {run['pid']:<8} {status:<10} {format_size(run['log_size']):<10}")
    
    print("-" * 80)
    print(f"\nTotal runs: {len(runs)} ({sum(1 for r in runs if r['running'])} running)")
    print("\nUsage:")
    print("  python check_status.py --tail 100     # Show last 100 lines of most recent log")
    print("  python check_status.py --log 1        # Show log for run #1")
    print("  python check_status.py --kill PID     # Kill a running process")

if __name__ == "__main__":
    main()