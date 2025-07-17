#!/usr/bin/env python3
"""Quick test to verify job descriptions don't have schema errors."""

import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

def test_job_description(job_file):
    """Test if a job description loads without schema errors."""
    print(f"\nTesting {job_file}...")
    try:
        if job_file == "job_description_simple.py":
            from job_description_simple import job_description
        elif job_file == "job_description_hybrid.py":
            from job_description_hybrid import job_description
        elif job_file == "job_description_hybrid_iterative.py":
            from job_description_hybrid_iterative import job_description
        else:
            print(f"Unknown job file: {job_file}")
            return
            
        # Try to create tool instance
        tools = job_description.tool_implementations_class()
        
        # Try to get schema
        schema = tools.get_schema()
        print(f"✓ Schema loaded successfully: {schema}")
        
        # Check task count
        print(f"✓ Tasks defined: {len(job_description.task_list)}")
        
        # Try to access tool methods
        methods = [m for m in dir(tools) if not m.startswith('_') and callable(getattr(tools, m))]
        print(f"✓ Tool methods available: {len(methods)}")
        
        print(f"✓ {job_file} is valid!")
        
    except Exception as e:
        print(f"✗ Error loading {job_file}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test all job descriptions
    test_job_description("job_description_simple.py")
    test_job_description("job_description_hybrid.py")
    test_job_description("job_description_hybrid_iterative.py")