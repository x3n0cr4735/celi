# Hybrid Iterative Parser Challenge - Code Review Summary

## Overview
This document summarizes the changes made to fix the asyncio issue preventing Gemini escalation in the hybrid iterative parser challenge.

## Files Modified

### 1. `/celi_framework/examples/parser_challenge/tool_implementations.py`
**Changes**: Fixed asyncio conflict in `_call_llm_for_fix()` method (lines 602-647)

**Original Code**:
```python
try:
    fixed_code = quick_ask(
        prompt=prompt,
        model_name=model,
        temperature=0.2,
        max_tokens=20000,
        verbose=True
    )
except Exception as e:
    return f"Error calling {model}: {str(e)}"
```

**Fixed Code**:
```python
try:
    # Check if we're already in an event loop
    try:
        loop = asyncio.get_running_loop()
        # We're in an event loop, need to use a different approach
        import concurrent.futures
        
        # Run in a separate thread to avoid event loop conflict
        def run_in_thread():
            # Create a new event loop for this thread
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(quick_ask_async(
                    prompt=prompt,
                    model_name=model,
                    temperature=0.2,
                    max_tokens=20000,
                    verbose=True
                ))
            finally:
                new_loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            fixed_code = future.result(timeout=300)  # 5 minute timeout
            
    except RuntimeError:
        # No event loop running, we can use asyncio.run
        fixed_code = asyncio.run(quick_ask_async(
            prompt=prompt,
            model_name=model,
            temperature=0.2,
            max_tokens=20000,
            verbose=True
        ))
except Exception as e:
    return f"Error calling {model}: {str(e)}"
```

### 2. `/celi_framework/examples/parser_challenge/job_description_hybrid_iterative.py`
**Changes**: 
- Reduced from 6 tasks to 5 tasks
- Combined implementation and validation into single `implementation_and_validation` task
- Fixed tool name from `execute_parser_code` to `debug_parser_output`

## Problem Summary

**Issue**: When `run_comprehensive_tests_with_llm_fixes` tried to call Gemini, it failed with:
```
Error calling gemini-2.5-flash: asyncio.run() cannot be called from a running event loop
```

**Root Cause**: 
- CELI framework runs in an async event loop
- `quick_ask()` uses `asyncio.run()` to create a new event loop
- Can't create a new event loop when one is already running

**Solution**:
- Detect if already in an event loop using `asyncio.get_running_loop()`
- If in event loop: Run the async call in a separate thread with its own event loop
- If not in event loop: Use standard `asyncio.run()`

## Testing Instructions

1. Activate virtual environment:
   ```bash
   source /home/sam/Projects/celi/.venv/bin/activate
   ```

2. Export API keys:
   ```bash
   export ANTHROPIC_API_KEY=<your-key>
   export GOOGLE_API_KEY=<your-key>
   ```

3. Run the test:
   ```bash
   cd /home/sam/Projects/celi/celi_framework/examples/parser_challenge
   python run_hybrid_iterative_test.py
   ```

## Expected Behavior

1. Claude will progress through 5 tasks
2. In Task 4, if tests fail after Claude's attempts, it should successfully call Gemini
3. Previously this would fail with asyncio error - now it should work

## Full File Collection

All relevant files have been collected in:
`/home/sam/Projects/celi/celi_framework/examples/parser_challenge/hybrid_iterative_files_20250625_111642.txt`

This file contains the complete source code of all files involved in the run.