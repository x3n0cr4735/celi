# Deprecated Files

This directory contains files that have been deprecated and are no longer actively used in the parser_challenge example.

## Why these files were deprecated:

### Test Files
- `test_hybrid_approach.py` - Superseded by `run_hybrid_iterative_test.py`
- `test_integrated_hybrid.py` - Development testing file, no longer needed
- `test_celi_hybrid.py` - Testing file, functionality covered elsewhere
- `test_job_description.py` - Testing file, not needed for production
- `test_full_hybrid_detached.py` - Testing file, redundant

### Runners
- `run_hybrid.py` - Use `run_hybrid_iterative_test.py` instead
- `run_full_hybrid_test.py` - Redundant with iterative version
- `run_example.py` - Generic runner, use specific runners instead

### Job Descriptions
- `job_description_hybrid.py` - Had schema validation issues, replaced by `job_description_hybrid_iterative.py`
- `job_description_simple.py` - Simplified test version, use main job descriptions instead

### Other
- `hybrid_strategy_examples.py` - Example strategies that aren't being used

## Current recommended approach:
Use `job_description_hybrid_iterative.py` with `run_hybrid_iterative_test.py` for the best results.

These files are kept for reference but should not be used in new development.