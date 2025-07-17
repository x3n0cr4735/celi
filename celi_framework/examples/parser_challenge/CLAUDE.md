# Parser Challenge Example for CELI

This example demonstrates how to use the CELI framework to automate the process of adapting banking document parsers to handle format variations from different banks.

## ⚠️ CRITICAL: ENVIRONMENT SETUP & API KEYS ⚠️

### 1. Activate the Virtual Environment FIRST
```bash
# From the CELI root directory (/home/sam/Projects/celi)
source .venv/bin/activate

# Verify activation - you should see (.venv) in your prompt
which python  # Should show /home/sam/Projects/celi/.venv/bin/python
```

### 2. Export API Keys in Your Commands
The Google Gemini library (and other LLM libraries) check for API keys in environment variables BEFORE our Python code can load from .env files. This means you MUST export keys in your shell command.

### ❌ WRONG (WILL FAIL):
```bash
python test_hybrid_approach.py  # FAILS - No API key in environment
python -m celi_framework.main job_description.py  # FAILS - No API key
```

### ✅ CORRECT:
```bash
# Always activate venv first!
source /home/sam/Projects/celi/.venv/bin/activate

# For hybrid approach (Claude + Gemini):
export ANTHROPIC_API_KEY=your-key && export GOOGLE_API_KEY=your-key && python test_hybrid_approach.py

# For main CELI runner:
export ANTHROPIC_API_KEY=your-key && python -m celi_framework.main job_description.py

# With detached runner:
export ANTHROPIC_API_KEY=your-key && export GOOGLE_API_KEY=your-key && python run_detached.py ln6280p_regional
```

## Requirements

- **Python Virtual Environment**: Use the CELI venv at `/home/sam/Projects/celi/.venv`
- **Claude Sonnet 4 Model**: This example requires the Claude Sonnet 4 model (`claude-sonnet-4-20250514`) for optimal performance
- **Anthropic API Key**: You need a valid Anthropic API key with access to Claude Sonnet 4
- **Google API Key** (for hybrid approach): You need a Google API key for Gemini models
- **uv**: This project uses `uv` for dependency management. Install it with: `pip install uv`

## Overview

The parser challenge involves taking existing Jack Henry (JH) banking document parsers that work perfectly for their standard format, and extending them to handle format variations from other banks. The key requirement is maintaining backward compatibility while adding support for new patterns.

## Key Design Principles

### Tool Simplicity
The tools in this example are intentionally simple - they focus on:
- **Reading files** into context for the LLM to analyze
- **Executing parser code** safely in isolated environments (similar to HumanEval)
- **Testing parsers** against multiple test cases automatically
- **Saving files** with results
- **Basic validation** (JSON validity, output comparison)

The actual intelligence and analysis comes from the LLM examining the file contents and making decisions based on what it sees.

### Code Execution Model
Similar to the HumanEval example, this framework supports:
- **Safe code execution** in temporary directories
- **Direct testing** of parser code without manual file management
- **Automated test runs** against both gold standard and new bank inputs
- **Immediate feedback** on test results

### Job Description Structure
The job description guides the LLM through a systematic process:
1. **Load and understand** the gold standard parser
2. **Compare formats** between banks by reading actual files
3. **Test baseline** to see what's not working
4. **Identify changes** based on the analysis
5. **Implement changes** using additive enhancement
6. **Test thoroughly** including backward compatibility
7. **Validate results** for exact matches

## Installation

1. Install dependencies using `uv`:
```bash
cd /home/sam/Projects/celi
uv pip install -e .

# Or install specific requirements for this example:
cd celi_framework/examples/parser_challenge
uv pip install -r requirements.txt

# For development with pyproject.toml:
uv pip install -e .
```

2. Ensure you have the latest Anthropic library:
```bash
uv pip install --upgrade anthropic
```

3. Set up environment variables:
```bash
export ANTHROPIC_API_KEY=<your-api-key>
export PRIMARY_LLM=claude-sonnet-4-20250514
```

## Running the Parser Challenge

### 🚀 Quick Start (Hybrid Iterative - RECOMMENDED)

```bash
# 1. Activate virtual environment
source /home/sam/Projects/celi/.venv/bin/activate

# 2. Navigate to parser challenge directory
cd /home/sam/Projects/celi/celi_framework/examples/parser_challenge

# 3. Run the hybrid iterative approach
export ANTHROPIC_API_KEY=your-key && export GOOGLE_API_KEY=your-key && python run_hybrid_iterative_test.py
```

### Full Test Suite

```bash
# Run complete evaluation of all parsers
source /home/sam/Projects/celi/.venv/bin/activate
cd /home/sam/Projects/celi/celi_framework/examples/parser_challenge

# Evaluate existing parsers
python eval.py

# Generate detailed report
python eval.py --report > evaluation_report.txt
```

### Direct CELI Framework Run

```bash
# Activate environment first!
source /home/sam/Projects/celi/.venv/bin/activate

# Claude-only approach
export ANTHROPIC_API_KEY=your-key && python -m celi_framework.main \
  --job-description=celi_framework.examples.parser_challenge.job_description.job_description \
  --tool-config='{"document_type":"LN6280P", "bank_name":"RegionalBank"}' \
  --primary-model-name=claude-sonnet-4-20250514

# Hybrid iterative approach (RECOMMENDED)
export ANTHROPIC_API_KEY=your-key && export GOOGLE_API_KEY=your-key && \
python -m celi_framework.main \
  --job-description=celi_framework.examples.parser_challenge.job_description_hybrid_iterative.job_description \
  --tool-config='{"document_type":"LN6280P", "bank_name":"RegionalBank", "fix_model":"gemini-2.5-flash"}' \
  --primary-model-name=claude-sonnet-4-20250514
```

### Detached/Background Runs

⚠️ **Note**: The detached runner requires the API key as a command line argument using `--api-key`

```bash
# Always from activated environment
source /home/sam/Projects/celi/.venv/bin/activate
cd /home/sam/Projects/celi/celi_framework/examples/parser_challenge

# Start a detached run (Claude only):
export ANTHROPIC_API_KEY=your-key && python run_detached.py ln6280p_regional --api-key "$ANTHROPIC_API_KEY"

# Start a detached run (Hybrid iterative) - MUST also export GOOGLE_API_KEY:
export ANTHROPIC_API_KEY=your-key && export GOOGLE_API_KEY=your-key && \
python run_detached.py ln6280p_regional --api-key "$ANTHROPIC_API_KEY" --hybrid

# Available examples:
# - ln6280p_regional   (Easy difficulty)
# - ln6280p_community  (Medium difficulty)
# - ln6280p_metro      (Hard difficulty)

# Monitor progress
python check_status.py

# View last 100 lines of most recent log
python check_status.py --tail 100

# View specific log (0 = most recent)
python check_status.py --log 0

# Kill a running process (if needed)
python check_status.py --kill 0  # Kill most recent
```

### Configuration Options

- `document_type`: The type of document to parse (e.g., "LN6280P", "CD2161P", "DD2890P")
- `bank_name`: The name of the new bank whose format needs to be supported

## Parser Requirements

The adapted parser must:
1. **Produce exact output matches** with expected JSON
2. **Maintain backward compatibility** with JH format
3. **Handle edge cases** including Unicode, complex names, special characters
4. **Use additive enhancement** - only add patterns, never remove
5. **Include clear comments** explaining all changes

## Current File Structure (After Cleanup)

### ✨ Active Files

```
parser_challenge/
├── 📝 Core Job Descriptions
│   ├── job_description_hybrid_iterative.py  # ⭐ RECOMMENDED - Best hybrid approach with iterative loops
│   └── job_description.py                   # Basic Claude-only approach
│
├── 🔧 Tool Implementation
│   ├── tool_implementations.py              # All parser tools (read, execute, test, save)
│   ├── test_harness.py                      # Comprehensive test runner with 5 test cases per bank
│   └── hybrid_llm_tools.py                  # Tools for calling Gemini/Claude directly
│
├── 🏃 Runners
│   ├── run_hybrid_iterative_test.py         # ⭐ RECOMMENDED - Run hybrid iterative approach
│   ├── run_detached.py                      # Run jobs in background with logging
│   ├── check_status.py                      # Monitor detached runs
│   └── eval.py                              # Evaluate all generated parsers
│
├── 📄 Documentation
│   ├── CLAUDE.md                            # This file
│   └── HYBRID_ITERATIVE_IMPROVEMENTS.md     # Technical improvements details
│
├── ⚙️ Configuration
│   ├── requirements.txt                     # Python dependencies
│   ├── pyproject.toml                       # Project configuration
│   └── __init__.py                          # Module initialization
│
└── 📁 Directories
    ├── deprecated/                          # Old/unused files (with README)
    ├── logs/                                # Execution logs from all runs
    └── output/                              # Generated parsers
        └── LN6280P_RegionalBank/
            └── parser.py                    # Example adapted parser
```

### 🗑️ Deprecated Files (Moved to `deprecated/`)

The following files have been moved to the `deprecated/` subdirectory and should not be used:

#### Test Files
- `test_hybrid_approach.py` - Superseded by `run_hybrid_iterative_test.py`
- `test_integrated_hybrid.py` - Development testing file
- `test_celi_hybrid.py` - Testing file
- `test_job_description.py` - Testing file
- `test_full_hybrid_detached.py` - Testing file

#### Old Runners
- `run_hybrid.py` - Use `run_hybrid_iterative_test.py` instead
- `run_full_hybrid_test.py` - Redundant with iterative version
- `run_example.py` - Generic runner, use specific runners

#### Old Job Descriptions
- `job_description_hybrid.py` - Had schema issues, replaced by iterative version
- `job_description_simple.py` - Simplified test version

#### Other
- `hybrid_strategy_examples.py` - Unused example strategies

See `deprecated/README.md` for more details about why each file was deprecated.

## Example Workflow

1. The LLM loads the gold standard parser and studies its patterns
2. It compares input files to identify format differences
3. It tests the gold parser on new input to see what fails
4. It identifies specific patterns that need to be added
5. It creates an adapted parser with new patterns
6. It tests the adapted parser on both new and original inputs
7. It iterates until achieving exact matches

## Hybrid LLM Approach

The parser challenge includes a powerful hybrid approach that leverages multiple LLMs:

### How It Works
1. **Claude** (PRIMARY_LLM) orchestrates the entire process and implements base enhancements
2. **Gemini** is called automatically to fix any failing tests with surgical precision
3. The system achieves 100% test pass rate through this collaboration

### Running the Hybrid Approach

#### Standalone Test:
```bash
# MUST EXPORT BOTH API KEYS!
export ANTHROPIC_API_KEY=your-key && export GOOGLE_API_KEY=your-key && python test_hybrid_approach.py
```

#### Full Job Description:
```bash
# MUST EXPORT BOTH API KEYS!
export ANTHROPIC_API_KEY=your-key && export GOOGLE_API_KEY=your-key && \
python -m celi_framework.main \
  --job-description=celi_framework.examples.parser_challenge.job_description_hybrid.job_description \
  --tool-config='{"document_type":"LN6280P", "bank_name":"RegionalBank"}'
```

### Hybrid Tools Available

The `hybrid_llm_tools.py` module provides:
- `ask_llm(prompt, model)` - Send prompts to specific models
- `ask_for_code(prompt)` - Optimized for code generation (defaults to Gemini)
- `ask_for_analysis(prompt)` - Optimized for analysis (defaults to Claude)
- `fix_code_with_llm(code, error)` - Fix code issues (defaults to Gemini)

## Best Practices

- **Let the LLM analyze**: The tools load content, the LLM does the analysis
- **Additive only**: Never remove existing patterns, only add new ones
- **Test incrementally**: Fix one issue at a time
- **Verify compatibility**: Always test on original input too
- **Document changes**: Clear comments for every modification
- **Use hybrid approach** for challenging parsers that need that extra precision

## Test Harness

The parser challenge includes a comprehensive test harness similar to HumanEval:

### Running Tests

After generating parsers, you can evaluate them:

```bash
# Evaluate all generated parsers
python eval.py

# Evaluate with detailed report
python eval.py --report

# Test a specific bank parser
python test_harness.py --bank RegionalBank
```

### Test Cases

Each bank challenge includes 5 test cases:
1. **Main Example**: The primary input/output pair
2. **Test Case 1 & 2**: Standard scenarios
3. **Stress Test 1**: Unicode and special characters
4. **Stress Test 2**: Edge cases and business entities

### Difficulty Levels

The three bank challenges have different difficulty levels:
- **RegionalBank** (Easy): Minor format variations
- **CommunityCredit** (Intermediate): Moderate variations requiring multiple pattern additions
- **MetroBank** (Advanced): Significant variations testing parser robustness

## How It All Works Together

### Data Flow

1. **Source Data** (`/home/sam/Projects/prog_parser_statements/`)
   - Gold standard parsers: `prog_parser_statements/prog_parsers/JH/{doc_type}/parser.py`
   - Test inputs: `prog_parser_statements/demos/{doc_type}/{bank_name}/input_output/`
   - Test cases: `prog_parser_statements/demos/{doc_type}/{bank_name}/test_cases/`

2. **CELI Framework Processing**
   - **Job Description**: Defines the task workflow (5 tasks for hybrid iterative)
   - **Tool Implementations**: Provides file I/O, parser execution, and testing capabilities
   - **LLM Orchestration**: Claude analyzes and implements changes iteratively
   - **Hybrid Fixing**: Gemini fixes edge cases that Claude misses

3. **Output** (`./output/{document_type}_{bank_name}/`)
   - Generated parser that handles both JH and new bank formats
   - Maintains backward compatibility
   - Passes all 5 test cases

### Key Components Explained

#### `tool_implementations.py`
- **read_parser()**: Loads gold standard parsers from prog_parser_statements
- **read_input()**: Loads bank-specific input files
- **read_expected_output()**: Loads expected JSON outputs
- **_execute_parser_code()**: Safely executes parser code in isolated environment (private method)
- **test_parser_code()**: Tests parser against both banks
- **run_comprehensive_tests()**: Runs all 5 test cases
- **run_comprehensive_tests_with_llm_fixes()**: Runs tests and auto-fixes failures with Gemini
- **save_parser()**: Saves the final adapted parser

#### `test_harness.py`
- Provides comprehensive testing infrastructure
- 5 test cases per bank: main example, 2 standard tests, 2 stress tests
- Validates JSON output and checks for exact matches
- Used by `run_comprehensive_tests()` tool

#### `hybrid_llm_tools.py`
- Direct access to Gemini and Claude models
- Used by the hybrid fixing mechanism
- Allows targeted code fixes for specific test failures

### Test Case Structure

Each bank has 5 test cases:
1. **main_example**: Primary input/output pair
2. **test_case_1**: Standard scenario
3. **test_case_2**: Another standard scenario  
4. **stress_test_1**: Unicode, special characters
5. **stress_test_2**: Business entities, edge cases

### Success Criteria

A parser is considered successful when:
- ✅ All 5 test cases pass for the new bank (e.g., RegionalBank)
- ✅ All 5 test cases still pass for JH (backward compatibility)
- ✅ Output JSON exactly matches expected output (no field differences)
- ✅ Parser handles Unicode and special characters correctly

## Integration with prog_parser_statements

This example is designed to work with the existing parser infrastructure in the `prog_parser_statements` project. It reads parsers, test data, and schemas from that project while saving adapted parsers to its own output directory.

The separation allows:
- Clean testing of CELI framework capabilities
- No modification of source parsers
- Easy comparison of adapted vs original parsers
- Isolated output for evaluation