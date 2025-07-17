"""Tool implementations for the parser challenge - focused on file I/O and execution."""

import json
import os
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from celi_framework.utils.log import app_logger


hard_coded_analysis = """
            ### **Key Format Differences:**

            1. **Customer Name Prefix**: 
            - JH: Uses `3 CUSTOMER NAME` 
            - RegionalBank: Uses `4 CUSTOMER NAME`

            2. **Date Field Labels**:
            - JH: `Statement Date` and `Payment Due Date`
            - RegionalBank: `Billing Date` and `Due Date`

            3. **Amount Field Labels**:
            - JH: `**Total Amount Due**`
            - RegionalBank: `**Payment Amount Due**`

            4. **Balance Field Labels**:
            - JH: `Current Balance`
            - RegionalBank: `Outstanding Balance`

            5. **Payment Field Labels**:
            - JH: `Regular Payment Amount` and `Total Amount Due`
            - RegionalBank: `Monthly Payment` and `Payment Amount Due`

            6. **Phone Number Field**:
            - JH: Not present
            - RegionalBank: Includes `Phone Number (555) 123-4567` which should be captured in bank.phone

            7. **Payment Stub Labels**:
            - JH: `Total Amount Due`
            - RegionalBank: `Payment Amount Due`

            The core structure and transaction history format remain identical between both formats. The main changes needed are updating the regex patterns to handle the different field labels and the customer name prefix change from '3' to '4'.

            """


class ParserChallengeToolImplementations:
    """Simple tools for reading files, running parsers, and saving output."""
    
    def __init__(self, document_type: str = 'LN6280P', bank_name: str = 'NewBank', fix_model: str = 'gemini-2.5-flash', **kwargs):
        self.document_type = document_type
        self.bank_name = bank_name
        self.base_path = Path("/home/sam/Projects/prog_parser_statements")
        self.output_dir = Path("/home/sam/Projects/celi/celi_framework/examples/parser_challenge/output")
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.fix_model = fix_model
        self.claude_analysis = hard_coded_analysis  # Store Claude's analysis for later use
        
    def get_schema(self):
        """Return the schema of document types to process."""
        return {
            "parser_tasks": [f"{self.document_type}_{self.bank_name}"]
        }
    
    def set_claude_analysis(self, analysis: str):
        """
        Store Claude's initial analysis of format differences.
        This will be passed to Gemini during the fix process.
        
        Args:
            analysis: Claude's analysis text describing the differences between formats
        """
        self.claude_analysis = analysis
        app_logger.info("Stored Claude's analysis for passing to Gemini")
    
    def read_parser(self, document_type: str, bank: str = "JH") -> str:
        """
        Read a parser file and return its contents.
        
        Args:
            document_type: The document type (e.g., 'LN6280P')
            bank: The bank name (default 'JH' for gold standard)
            
        Returns:
            The full parser code as a string
        """
        if bank == "JH":
            parser_path = self.base_path / "prog_parsers" / "JH" / document_type / "parser.py"
        else:
            parser_path = self.base_path / "prog_parsers" / "JH" / f"{document_type}_{bank}" / "parser.py"
        
        try:
            with open(parser_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"Parser not found at {parser_path}"
    
    def read_input(self, document_type: str, bank: str = "JH") -> str:
        """
        Read an input file for a document type and bank.
        
        Args:
            document_type: The document type (e.g., 'LN6280P')
            bank: The bank name (default 'JH' for gold standard)
            
        Returns:
            The input file contents
        """
        if bank == "JH":
            input_path = self.base_path / "data" / "JH" / document_type / "input_output" / f"{document_type.lower()}_input.txt"
        else:
            input_path = self.base_path / "demos" / document_type / bank / "input_output" / f"{document_type.lower()}_{bank.lower()}_input.txt"
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"Input file not found at {input_path}"
    
    def read_expected_output(self, document_type: str, bank: str = "JH") -> str:
        """
        Read an expected output JSON file for a document type and bank.
        
        Args:
            document_type: The document type (e.g., 'LN6280P')
            bank: The bank name (default 'JH' for gold standard)
            
        Returns:
            The expected output JSON as a string
        """
        if bank == "JH":
            output_path = self.base_path / "data" / "JH" / document_type / "input_output" / f"{document_type.lower()}_output.json"
        else:
            output_path = self.base_path / "demos" / document_type / bank / "input_output" / f"{document_type.lower()}_{bank.lower()}_output.json"
        
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"Output file not found at {output_path}"
    
    def run_parser(self, parser_path: str, input_text: str) -> str:
        """
        Run a parser on input text and return the output.
        
        Args:
            parser_path: Full path to the parser file
            input_text: The input text to parse
            
        Returns:
            The parser output (JSON string)
        """
        # Save input to temporary file
        temp_input = self.output_dir / "temp_input.txt"
        with open(temp_input, 'w', encoding='utf-8') as f:
            f.write(input_text)
        
        try:
            # Run the parser
            result = subprocess.run(
                [sys.executable, parser_path, str(temp_input)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return f"Parser error: {result.stderr}"
            
            return result.stdout
        except Exception as e:
            return f"Error running parser: {e}"
        finally:
            # Clean up temp file
            if temp_input.exists():
                temp_input.unlink()
    
    def _execute_parser_code(self, parser_code: str, input_text: str):
        """
        Internal method to execute parser code directly with input text.
        This is similar to the HumanEval execution model.
        
        Args:
            parser_code: The complete parser code to execute
            input_text: The input text to parse
            
        Returns:
            Tuple of (output, error) - output is the JSON result or empty string, 
            error contains any exception messages
        """
        # Create a temporary directory for safe execution
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write parser code to a file
            parser_file = temp_path / "parser.py"
            with open(parser_file, 'w', encoding='utf-8') as f:
                f.write(parser_code)
            
            # Write input to a file
            input_file = temp_path / "input.txt"
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(input_text)
            
            # Execute the parser in a subprocess for safety
            try:
                result = subprocess.run(
                    [sys.executable, str(parser_file), str(input_file)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=temp_dir
                )
                
                if result.returncode != 0:
                    return "", f"Parser execution failed:\n{result.stderr}"
                
                return result.stdout.strip(), ""
                
            except subprocess.TimeoutExpired:
                return "", "Parser execution timed out (10 seconds)"
            except Exception as e:
                return "", f"Execution error: {str(e)}\n{traceback.format_exc()}"
    
    def test_parser_code(self, parser_code: str) -> str:
        """
        Test parser code against multiple test cases.
        
        Args:
            parser_code: The parser code to test
            
        Returns:
            Test results summary
        """
        results = []
        
        # Test 1: Gold standard input
        gold_input = self.read_input(self.document_type, "JH")
        gold_expected = self.read_expected_output(self.document_type, "JH")
        
        output, error = self._execute_parser_code(parser_code, gold_input)
        if error:
            results.append(f"❌ Gold standard test failed: {error}")
        else:
            match = self.compare_outputs(output, gold_expected)
            if match == "MATCH":
                results.append("✅ Gold standard test: PASS")
            else:
                results.append(f"❌ Gold standard test: Output mismatch")
        
        # Test 2: New bank input
        new_input = self.read_input(self.document_type, self.bank_name)
        new_expected = self.read_expected_output(self.document_type, self.bank_name)
        
        output, error = self._execute_parser_code(parser_code, new_input)
        if error:
            results.append(f"❌ {self.bank_name} test failed: {error}")
        else:
            match = self.compare_outputs(output, new_expected)
            if match == "MATCH":
                results.append(f"✅ {self.bank_name} test: PASS")
            else:
                results.append(f"❌ {self.bank_name} test: Output mismatch")
        
        return "\n".join(results)
    
    def save_parser(self, parser_code: str) -> str:
        """
        Save a new parser to the output directory.
        
        Args:
            parser_code: The complete parser code
            
        Returns:
            The path where the parser was saved
        """
        # Create directory structure
        parser_dir = self.output_dir / f"{self.document_type}_{self.bank_name}"
        parser_dir.mkdir(exist_ok=True)
        
        parser_path = parser_dir / "parser.py"
        
        with open(parser_path, 'w', encoding='utf-8') as f:
            f.write(parser_code)
        
        app_logger.info(f"Saved parser to: {parser_path}")
        return str(parser_path)
    
    def validate_json(self, json_string: str) -> str:
        """
        Validate that a string is valid JSON.
        
        Args:
            json_string: String to validate as JSON
            
        Returns:
            "Valid JSON" or error message
        """
        try:
            json.loads(json_string)
            return "Valid JSON"
        except json.JSONDecodeError as e:
            return f"Invalid JSON: {e}"
    
    def compare_outputs(self, actual: str, expected: str) -> str:
        """
        Compare two JSON outputs and report if they match.
        
        Args:
            actual: The actual output JSON string
            expected: The expected output JSON string
            
        Returns:
            "MATCH" if identical, or a summary of differences
        """
        try:
            actual_obj = json.loads(actual)
            expected_obj = json.loads(expected)
            
            # Normalize by pretty-printing with sorted keys
            actual_normalized = json.dumps(actual_obj, indent=2, sort_keys=True)
            expected_normalized = json.dumps(expected_obj, indent=2, sort_keys=True)
            
            if actual_normalized == expected_normalized:
                return "MATCH"
            else:
                # Just report that they don't match - let the LLM analyze the differences
                return "NO MATCH - outputs differ"
        except json.JSONDecodeError as e:
            return f"JSON decode error: {e}"
    
    def debug_parser_output(self, parser_code: str, input_text: str) -> str:
        """
        Execute parser code and return both output and detailed error information for debugging.
        
        Args:
            parser_code: The parser code to debug
            input_text: The input text to parse
            
        Returns:
            Detailed output including stdout, stderr, and any exceptions
        """
        output, error = self._execute_parser_code(parser_code, input_text)
        
        result = []
        if output:
            result.append("=== PARSER OUTPUT ===")
            result.append(output)
            result.append("")
        
        if error:
            result.append("=== PARSER ERROR ===")
            result.append(error)
            result.append("")
        
        # Try to validate JSON if we got output
        if output and not error:
            validation = self.validate_json(output)
            result.append(f"=== JSON VALIDATION ===")
            result.append(validation)
        
        return "\n".join(result)
    
    def run_comprehensive_tests(self, parser_code: str, detailed_errors: bool = False) -> str:
        """
        Run comprehensive tests including all 5 test cases per bank.
        
        Args:
            parser_code: The parser code to test
            detailed_errors: If True, include detailed error information for debugging
            
        Returns:
            Detailed test results
        """
        # Import test harness
        sys.path.append(str(Path(__file__).parent))
        from test_harness import ParserTestHarness, TestResult
        
        # Save parser temporarily
        temp_parser_path = self.save_parser(parser_code)
        parser_path = Path(temp_parser_path)
        
        # Create test harness
        harness = ParserTestHarness(self.document_type)
        
        # Store detailed error info
        detailed_failures = []
        
        # Run tests for this bank
        try:
            bank_results = harness.test_bank_parser(parser_path, self.bank_name)
            
            # Format results
            result_lines = []
            result_lines.append(f"=== COMPREHENSIVE TEST RESULTS FOR {self.bank_name} ===")
            result_lines.append(f"Difficulty: {bank_results.difficulty}")
            result_lines.append(f"Overall Pass Rate: {bank_results.pass_rate:.1f}%")
            result_lines.append("")
            
            for test in bank_results.test_results:
                status = "✅ PASS" if test.passed else "❌ FAIL"
                result_lines.append(f"{test.test_name}: {status}")
                if test.execution_time:
                    result_lines.append(f"  Execution time: {test.execution_time:.2f}s")
                if not test.passed and test.error_message:
                    result_lines.append(f"  Error: {test.error_message.split(chr(10))[0]}")
                    
                    # Collect detailed error info for failed tests
                    if detailed_errors:
                        # Get test input and expected output
                        test_input_path = self.base_path / "demos" / self.document_type / self.bank_name / "test_cases" / f"{test.test_name}_input.txt"
                        test_output_path = self.base_path / "demos" / self.document_type / self.bank_name / "test_cases" / f"{test.test_name}_output.json"
                        
                        detailed_info = {
                            "test_name": test.test_name,
                            "error_message": test.error_message,
                            "input_file": str(test_input_path),
                            "expected_output_file": str(test_output_path)
                        }
                        
                        # Try to get actual vs expected comparison
                        if "!=" in test.error_message:
                            parts = test.error_message.split("!=")
                            if len(parts) == 2:
                                detailed_info["actual_value"] = parts[0].strip().split(": ")[-1].strip()
                                detailed_info["expected_value"] = parts[1].strip()
                        
                        detailed_failures.append(detailed_info)
                        
                result_lines.append("")
            
            if bank_results.overall_passed:
                result_lines.append("🎉 ALL TESTS PASSED! 🎉")
            else:
                result_lines.append(f"⚠️  {sum(1 for t in bank_results.test_results if not t.passed)} tests failed")
                
                if detailed_errors and detailed_failures:
                    result_lines.append("\n=== DETAILED ERROR INFORMATION ===")
                    for failure in detailed_failures:
                        result_lines.append(f"\nTest: {failure['test_name']}")
                        result_lines.append(f"Error: {failure['error_message']}")
                        if 'actual_value' in failure:
                            result_lines.append(f"Actual: {failure['actual_value']}")
                            result_lines.append(f"Expected: {failure['expected_value']}")
            
            return "\n".join(result_lines)
            
        except Exception as e:
            return f"Error running comprehensive tests: {e}\n{traceback.format_exc()}"
    
    def call_gemini_directly(self, prompt: str) -> str:
        """
        Call Gemini API directly using Google's generative AI library.
        
        Args:
            prompt: The prompt to send to Gemini
            
        Returns:
            The response from Gemini
        """
        import os
        import google.generativeai as genai
        
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "Error: GEMINI_API_KEY not found in environment"
        
        app_logger.info(f"Using Gemini API key: {api_key[:10]}...")
        genai.configure(api_key=api_key)
        
        # Create the model - using exact model name from user
        # Try gemini-2.5-flash
        model = genai.GenerativeModel('gemini-2.5-flash')
        app_logger.info("Created Gemini model instance")
        
        # Generate response
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=20000,
                )
            )
            return response.text
        except Exception as e:
            return f"Error calling Gemini: {str(e)}"
    
    def fix_parser_with_llm(self, parser_code: str, test_failures: str, detailed_test_info: list = None, model: str = "gemini-2.5-flash") -> str:
        """
        Use an LLM to fix failing tests in the parser.
        
        Args:
            parser_code: The current parser code
            test_failures: Description of which tests failed and why
            detailed_test_info: Optional list of dicts with detailed test failure info
            model: The model to use for fixing (defaults to gemini-2.5-flash)
            
        Returns:
            Fixed parser code
        """
        import difflib
        
        # Load the gold standard parser for reference
        gold_parser = self.read_parser(self.document_type, "JH")
        
        # Load example inputs and outputs for both banks
        jh_input = self.read_input(self.document_type, "JH")
        jh_output = self.read_expected_output(self.document_type, "JH")
        regional_input = self.read_input(self.document_type, self.bank_name)
        regional_output = self.read_expected_output(self.document_type, self.bank_name)
        
        # Prepare comprehensive prompt for Gemini
        prompt = f"""You are an expert Python parser developer. Fix the failing tests in this parser.

CONTEXT:
You are adapting a parser that works perfectly for Jack Henry (JH) bank format to also work with {self.bank_name} format.
The parser must maintain backward compatibility - it should still work with JH format after your changes.

GOLD STANDARD PARSER (works perfectly for JH format):
```python
{gold_parser}
```

EXAMPLE INPUTS AND OUTPUTS:

1. Jack Henry (JH) Format Input:
```
{jh_input}
```

Expected JH Output:
```json
{jh_output}
```

2. {self.bank_name} Format Input:
```
{regional_input}
```

Expected {self.bank_name} Output:
```json
{regional_output}
```

CURRENT PARSER CODE (your starting point):
```python
{parser_code}
```

TEST FAILURES:
{test_failures}
"""
        
        # Add detailed information if available
        if detailed_test_info:
            prompt += "\n\nDETAILED FAILURE ANALYSIS:\n"
            
            for test_info in detailed_test_info:
                prompt += f"\n{'='*60}\nTest: {test_info['test_name']}\n"
                prompt += f"Error Type: {test_info.get('error_type', 'Unknown')}\n"
                
                # If it's an execution error (parser crashed)
                if test_info.get('error_type') == 'execution_error':
                    prompt += f"Execution Error: {test_info['error_message']}\n"
                    if 'traceback' in test_info:
                        prompt += f"Traceback:\n{test_info['traceback']}\n"
                    if 'input_snippet' in test_info:
                        prompt += f"\nInput that caused the error (first 500 chars):\n```\n{test_info['input_snippet'][:500]}...\n```\n"
                
                # If it's an output mismatch (parser ran but produced wrong output)
                elif test_info.get('error_type') == 'output_mismatch':
                    prompt += f"Output Mismatch: {test_info['error_message']}\n"
                    
                    # Add diff if we have both outputs
                    if 'actual_output' in test_info and 'expected_output' in test_info:
                        try:
                            # Parse JSON for pretty comparison
                            actual_json = json.loads(test_info['actual_output'])
                            expected_json = json.loads(test_info['expected_output'])
                            
                            # Pretty print both for diff
                            actual_lines = json.dumps(actual_json, indent=2, sort_keys=True).splitlines(keepends=True)
                            expected_lines = json.dumps(expected_json, indent=2, sort_keys=True).splitlines(keepends=True)
                            
                            # Generate unified diff
                            diff = difflib.unified_diff(
                                expected_lines,
                                actual_lines,
                                fromfile='expected_output.json',
                                tofile='actual_output.json',
                                n=5  # Context lines
                            )
                            
                            prompt += "\nJSON Diff (expected vs actual):\n```diff\n"
                            diff_lines = list(diff)
                            # Limit diff output to avoid token explosion
                            if len(diff_lines) > 100:
                                prompt += ''.join(diff_lines[:100])
                                prompt += f"\n... ({len(diff_lines) - 100} more lines) ...\n"
                            else:
                                prompt += ''.join(diff_lines)
                            prompt += "\n```\n"
                            
                        except json.JSONDecodeError:
                            # If JSON parsing fails, show the raw error
                            prompt += f"JSON parsing failed. Raw output comparison:\n"
                            prompt += f"Expected (first 200 chars): {test_info['expected_output'][:200]}...\n"
                            prompt += f"Actual (first 200 chars): {test_info['actual_output'][:200]}...\n"
                    
                    # Add input snippet for context
                    if 'input_snippet' in test_info:
                        prompt += f"\nTest Input (first 300 chars):\n```\n{test_info['input_snippet'][:300]}...\n```\n"
                    
                    # Try to add full test input if available
                    if 'full_input' in test_info:
                        prompt += f"\nFull Test Input:\n```\n{test_info['full_input']}\n```\n"
                    
                    # Try to add full expected output if available
                    if 'expected_output' in test_info:
                        prompt += f"\nFull Expected Output:\n```json\n{test_info['expected_output']}\n```\n"
        
        prompt += """

REQUIREMENTS:
1. Fix ONLY the specific issues causing test failures
2. Maintain all existing functionality (backward compatibility)
3. Use additive enhancement - don't remove existing patterns
4. Add clear comments explaining your fixes
5. Return the complete, corrected parser code

Key things to fix based on the failures:
- For execution errors: Fix the code that's crashing (check stack traces)
- For output mismatches: Fix the parsing logic to produce expected output
- If address parsing fails with comma issues, check the address parsing logic
- If transactions are missing, check the transaction parsing regex patterns
- Ensure all edge cases are handled properly

Return only the complete Python code, no explanations."""

        # Call the specified model for the fix using integrated LLM system
        app_logger.info(f"Calling {model} to fix parser issues...")
        
        # Import here to avoid circular imports
        from celi_framework.utils.llms import quick_ask_async
        import asyncio
        
        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an event loop, need to use a different approach
                import concurrent.futures
                import threading
                
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
        
        # Extract code if wrapped in markdown
        if "```python" in fixed_code:
            fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
        elif "```" in fixed_code:
            fixed_code = fixed_code.split("```")[1].split("```")[0].strip()
            
        return fixed_code
    
    def fix_parser_with_llm_comprehensive(self, parser_code: str, test_failures: str, detailed_test_info: list, all_test_cases: list, model: str = "gemini-2.5-flash") -> str:
        """
        Enhanced version of fix_parser_with_llm that includes ALL test case data.
        
        Args:
            parser_code: The current parser code
            test_failures: Description of which tests failed and why
            detailed_test_info: List of dicts with detailed test failure info
            all_test_cases: List of ALL test cases (both passing and failing) with inputs/outputs
            model: The model to use for fixing (defaults to gemini-2.5-flash)
            
        Returns:
            Fixed parser code
        """
        import difflib
        
        # Load the gold standard parser for reference
        gold_parser = self.read_parser(self.document_type, "JH")
        
        # Load example inputs and outputs for both banks
        jh_input = self.read_input(self.document_type, "JH")
        jh_output = self.read_expected_output(self.document_type, "JH")
        regional_input = self.read_input(self.document_type, self.bank_name)
        regional_output = self.read_expected_output(self.document_type, self.bank_name)
        
        # Prepare comprehensive prompt for Gemini
        prompt = f"""You are an expert Python parser developer. Fix the failing tests in this parser.

IMPORTANT CONTEXT - PLEASE READ CAREFULLY:
1. We started with a GOLD STANDARD parser that works perfectly for Jack Henry (JH) bank format
2. Claude has already attempted to adapt this parser for {self.bank_name} format while maintaining backward compatibility
3. Claude's approach was to make minimal changes - only adding new patterns without removing existing ones
4. However, Claude's adapted parser is failing some test cases for {self.bank_name}
5. Your job is to fix these specific failures while keeping Claude's correct adaptations

GOLD STANDARD PARSER (the original that works perfectly for JH format):
```python
{gold_parser}
```

ORIGINAL MAIN EXAMPLES (what the parsers were designed for):

1. Jack Henry (JH) Format - Original Input:
```
{jh_input}
```

Jack Henry (JH) Format - Expected Output:
```json
{jh_output}
```

2. {self.bank_name} Format - Target Input:
```
{regional_input}
```

{self.bank_name} Format - Target Expected Output:
```json
{regional_output}
```

CLAUDE'S ADAPTED PARSER (attempting to handle both JH and {self.bank_name}):
This is the parser that Claude created by adapting the gold standard. It's passing some tests but failing others.
```python
{parser_code}
```

COMPREHENSIVE TEST SUITE OVERVIEW:
Total tests: {len(all_test_cases)}
Passing tests: {sum(1 for t in all_test_cases if t.get('passed', False))}
Failing tests: {sum(1 for t in all_test_cases if not t.get('passed', False))}

ALL TEST CASES (INCLUDING PASSING ONES FOR CONTEXT):
"""
        
        # Add ALL test cases to give Gemini complete understanding
        for i, test_case in enumerate(all_test_cases):
            prompt += f"\n{'='*60}\nTest {i+1}: {test_case['test_name']} - {'PASS' if test_case.get('passed', False) else 'FAIL'}\n"
            
            if 'full_input' in test_case:
                prompt += f"\nTest Input (first 500 chars):\n```\n{test_case['full_input'][:500]}{'...' if len(test_case['full_input']) > 500 else ''}\n```\n"
            
            if 'expected_output' in test_case:
                try:
                    # Pretty print expected JSON
                    expected_json = json.loads(test_case['expected_output'])
                    prompt += f"\nExpected Output (first notice only for brevity):\n```json\n"
                    if 'notices' in expected_json and expected_json['notices']:
                        first_notice = {
                            "metadata": expected_json.get("metadata", {}),
                            "bank": expected_json.get("bank", {}),
                            "notices": [expected_json['notices'][0]],  # Just first notice
                            "extra": expected_json.get("extra", {})
                        }
                        prompt += json.dumps(first_notice, indent=2)[:1000]
                        if len(expected_json['notices']) > 1:
                            prompt += f"\n... ({len(expected_json['notices']) - 1} more notices) ..."
                    else:
                        prompt += json.dumps(expected_json, indent=2)[:1000]
                    prompt += "\n```\n"
                except:
                    prompt += f"\nExpected Output (raw, first 300 chars): {test_case['expected_output'][:300]}...\n"
        
        prompt += f"""

TEST FAILURES SUMMARY:
{test_failures}

WHAT CLAUDE GOT RIGHT AND WRONG:
Based on the test results above, Claude's parser successfully:
- Adapted the basic structure to handle {self.bank_name} format
- {f"Passed {sum(1 for t in all_test_cases if t.get('passed', False))} out of {len(all_test_cases)} tests"}
- Maintained backward compatibility with JH format (if applicable)

But Claude's parser is failing because:
- It didn't handle all the edge cases in the test suite
- The specific failures are detailed below
"""
        
        # Add detailed information about failures
        if detailed_test_info:
            prompt += "\n\nDETAILED FAILURE ANALYSIS:\n"
            
            for test_info in detailed_test_info:
                prompt += f"\n{'='*60}\nFailing Test: {test_info['test_name']}\n"
                prompt += f"Error Type: {test_info.get('error_type', 'Unknown')}\n"
                
                # If it's an execution error (parser crashed)
                if test_info.get('error_type') == 'execution_error':
                    prompt += f"Execution Error: {test_info['error_message']}\n"
                    if 'traceback' in test_info:
                        prompt += f"Traceback:\n{test_info['traceback']}\n"
                
                # If it's an output mismatch (parser ran but produced wrong output)
                elif test_info.get('error_type') == 'output_mismatch':
                    prompt += f"Output Mismatch: {test_info['error_message']}\n"
                    
                    # Add diff if we have both outputs
                    if 'actual_output' in test_info and 'expected_output' in test_info:
                        try:
                            # Parse JSON for pretty comparison
                            actual_json = json.loads(test_info['actual_output'])
                            expected_json = json.loads(test_info['expected_output'])
                            
                            # Pretty print both for diff
                            actual_lines = json.dumps(actual_json, indent=2, sort_keys=True).splitlines(keepends=True)
                            expected_lines = json.dumps(expected_json, indent=2, sort_keys=True).splitlines(keepends=True)
                            
                            # Generate unified diff
                            diff = difflib.unified_diff(
                                expected_lines,
                                actual_lines,
                                fromfile='expected_output.json',
                                tofile='actual_output.json',
                                n=5  # Context lines
                            )
                            
                            prompt += "\nJSON Diff (expected vs actual):\n```diff\n"
                            diff_lines = list(diff)
                            # Limit diff output to avoid token explosion
                            if len(diff_lines) > 100:
                                prompt += ''.join(diff_lines[:100])
                                prompt += f"\n... ({len(diff_lines) - 100} more lines) ...\n"
                            else:
                                prompt += ''.join(diff_lines)
                            prompt += "\n```\n"
                            
                        except json.JSONDecodeError:
                            # If JSON parsing fails, show the raw error
                            prompt += f"JSON parsing failed. Raw output comparison:\n"
                            prompt += f"Expected (first 200 chars): {test_info['expected_output'][:200]}...\n"
                            prompt += f"Actual (first 200 chars): {test_info['actual_output'][:200]}...\n"
        
        prompt += f"""

KEY OBSERVATIONS FROM ALL TEST CASES:
1. There are {len(all_test_cases)} test cases total that your parser must handle
2. Test cases include various edge cases like Unicode characters, special business names, complex addresses
3. The passing tests show patterns that Claude got RIGHT - don't break these!
4. The failing tests show specific patterns that Claude MISSED - these need surgical fixes

YOUR TASK:
You need to fix Claude's adapted parser so it passes ALL test cases. Claude already did the heavy lifting of:
- Adding support for {self.bank_name}'s different field names
- Handling the basic format differences
- Maintaining JH compatibility

But Claude missed some edge cases that are causing test failures. Your job is to:
1. Keep all of Claude's correct adaptations
2. Add the specific fixes for the failing test cases
3. Make minimal, surgical changes - don't rewrite what's already working

REQUIREMENTS:
1. Start with Claude's parser code (not the gold standard)
2. Fix ONLY the specific issues causing test failures
3. Preserve all of Claude's working adaptations
4. Add clear comments for your specific fixes (e.g., "# FIX: Added handling for negative amounts")
5. Ensure the parser handles ALL {len(all_test_cases)} test cases correctly
6. Return the complete, corrected parser code

COMMON ISSUES CLAUDE MIGHT HAVE MISSED:
- Address parsing with commas (e.g., "C/O EXECUTIVE PROPERTY MANAGEMENT, 9876 WALL STREET")
- Negative transaction amounts (e.g., "$-2.50")
- Edge cases in regex patterns that work for main examples but fail on test cases
- Special characters or Unicode handling in stress tests
- Multi-line address formatting

Return only the complete Python code with your fixes applied to Claude's parser."""

        # Call the specified model for the fix using integrated LLM system
        app_logger.info(f"Calling {model} to fix parser issues with comprehensive context...")
        app_logger.info(f"Providing context for all {len(all_test_cases)} test cases")
        
        # Import here to avoid circular imports
        from celi_framework.utils.llms import quick_ask_async
        import asyncio
        
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
        
        # Extract code if wrapped in markdown
        if "```python" in fixed_code:
            fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
        elif "```" in fixed_code:
            fixed_code = fixed_code.split("```")[1].split("```")[0].strip()
            
        return fixed_code
    
    def fix_parser_with_llm_comprehensive_iterative(self, parser_code: str, test_failures: str, detailed_test_info: list, all_test_cases: list, iteration_history: list, claude_analysis: str = None, model: str = "gemini-2.5-flash") -> str:
        """
        Enhanced version that includes COMPLETE iteration history with all previous prompts, responses, and results.
        
        Args:
            parser_code: The current parser code
            test_failures: Description of which tests failed and why  
            detailed_test_info: List of dicts with detailed test failure info
            all_test_cases: List of ALL test cases (both passing and failing) with inputs/outputs
            iteration_history: Complete history of all previous fix attempts
            claude_analysis: Claude's initial analysis of format differences (optional)
            model: The model to use for fixing (defaults to gemini-2.5-flash)
            
        Returns:
            Fixed parser code
        """
        import difflib
        
        # Load the gold standard parser for reference
        gold_parser = self.read_parser(self.document_type, "JH")
        
        # Load example inputs and outputs for both banks
        jh_input = self.read_input(self.document_type, "JH")
        jh_output = self.read_expected_output(self.document_type, "JH")
        regional_input = self.read_input(self.document_type, self.bank_name)
        regional_output = self.read_expected_output(self.document_type, self.bank_name)
        
        # Start with base prompt
        prompt = f"""You are an expert Python parser developer. Fix the failing tests in this parser.

IMPORTANT CONTEXT - PLEASE READ CAREFULLY:
1. We started with a GOLD STANDARD parser that works perfectly for Jack Henry (JH) bank format
2. Claude has already attempted to adapt this parser for {self.bank_name} format while maintaining backward compatibility
3. You are now on iteration {len(iteration_history) + 1} of fixing the remaining issues
4. Below is the COMPLETE HISTORY of all previous attempts, including the exact prompts and your responses"""
        
        # Add Claude's initial analysis if provided
        if claude_analysis:
            prompt += f"""

CLAUDE'S INITIAL ANALYSIS OF FORMAT DIFFERENCES:
{claude_analysis}

This analysis identified the key differences between JH and {self.bank_name} formats that Claude addressed in the initial parser adaptation."""
        
        prompt += f"""

GOLD STANDARD PARSER (the original that works perfectly for JH format):
```python
{gold_parser}
```

ORIGINAL MAIN EXAMPLES (what the parsers were designed for):

1. Jack Henry (JH) Format - Original Input:
```
{jh_input}
```

Jack Henry (JH) Format - Expected Output:
```json
{jh_output}
```

2. {self.bank_name} Format - Target Input:
```
{regional_input}
```

{self.bank_name} Format - Target Expected Output:
```json
{regional_output}
```

"""

        # Add complete iteration history
        if iteration_history:
            prompt += "\n\n=== COMPLETE ITERATION HISTORY ===\n"
            prompt += "Below is the FULL HISTORY of all previous fix attempts, including prompts and results:\n\n"
            
            for idx, iteration in enumerate(iteration_history):
                prompt += f"--- ITERATION {iteration['iteration']} ---\n"
                prompt += f"Tests Status: {iteration['failing_tests']} failing out of {iteration['total_tests']} total\n"
                prompt += f"\nParser Code at Start of Iteration {iteration['iteration']}:\n```python\n{iteration['parser_code']}\n```\n"
                prompt += f"\nTest Results for this Code:\n{iteration['test_results']}\n"
                prompt += "\n" + "="*80 + "\n\n"

        # Add current state
        prompt += f"""\n\n=== CURRENT STATE (ITERATION {len(iteration_history) + 1}) ===

CURRENT PARSER CODE (after {len(iteration_history)} previous fix attempts):
```python
{parser_code}
```

CURRENT TEST RESULTS:
Total tests: {len(all_test_cases)}
Passing tests: {sum(1 for t in all_test_cases if t.get('passed', False))}
Failing tests: {sum(1 for t in all_test_cases if not t.get('passed', False))}

CURRENT TEST FAILURES:
{test_failures}

"""

        # Add all test cases
        prompt += "\nALL TEST CASES (INCLUDING PASSING ONES FOR CONTEXT):\n"
        
        for i, test_case in enumerate(all_test_cases):
            prompt += f"\n{'='*60}\nTest {i+1}: {test_case['test_name']} - {'PASS' if test_case.get('passed', False) else 'FAIL'}\n"
            
            if 'full_input' in test_case:
                prompt += f"\nTest Input (first 500 chars):\n```\n{test_case['full_input'][:500]}{'...' if len(test_case['full_input']) > 500 else ''}\n```\n"
            
            if 'expected_output' in test_case:
                try:
                    # Pretty print expected JSON
                    expected_json = json.loads(test_case['expected_output'])
                    prompt += f"\nExpected Output (first notice only for brevity):\n```json\n"
                    if 'notices' in expected_json and expected_json['notices']:
                        first_notice = {
                            "metadata": expected_json.get("metadata", {}),
                            "bank": expected_json.get("bank", {}),
                            "notices": [expected_json['notices'][0]],  # Just first notice
                            "extra": expected_json.get("extra", {})
                        }
                        prompt += json.dumps(first_notice, indent=2)[:1000]
                        if len(expected_json['notices']) > 1:
                            prompt += f"\n... ({len(expected_json['notices']) - 1} more notices) ..."
                    else:
                        prompt += json.dumps(expected_json, indent=2)[:1000]
                    prompt += "\n```\n"
                except:
                    prompt += f"\nExpected Output (raw, first 300 chars): {test_case['expected_output'][:300]}...\n"

        # Add detailed failure analysis
        if detailed_test_info:
            prompt += "\n\nDETAILED FAILURE ANALYSIS FOR CURRENT ITERATION:\n"
            
            for test_info in detailed_test_info:
                prompt += f"\n{'='*60}\nFailing Test: {test_info['test_name']}\n"
                prompt += f"Error Type: {test_info.get('error_type', 'Unknown')}\n"
                
                if test_info.get('error_type') == 'execution_error':
                    prompt += f"Execution Error: {test_info['error_message']}\n"
                    if 'traceback' in test_info:
                        prompt += f"Traceback:\n{test_info['traceback']}\n"
                
                elif test_info.get('error_type') == 'output_mismatch':
                    prompt += f"Output Mismatch: {test_info['error_message']}\n"
                    
                    if 'actual_output' in test_info and 'expected_output' in test_info:
                        try:
                            # Parse JSON for pretty comparison
                            actual_json = json.loads(test_info['actual_output'])
                            expected_json = json.loads(test_info['expected_output'])
                            
                            # Pretty print both for diff
                            actual_lines = json.dumps(actual_json, indent=2, sort_keys=True).splitlines(keepends=True)
                            expected_lines = json.dumps(expected_json, indent=2, sort_keys=True).splitlines(keepends=True)
                            
                            # Generate unified diff
                            diff = difflib.unified_diff(
                                expected_lines,
                                actual_lines,
                                fromfile='expected_output.json',
                                tofile='actual_output.json',
                                n=5
                            )
                            
                            prompt += "\nJSON Diff (expected vs actual):\n```diff\n"
                            diff_lines = list(diff)
                            if len(diff_lines) > 100:
                                prompt += ''.join(diff_lines[:100])
                                prompt += f"\n... ({len(diff_lines) - 100} more lines) ...\n"
                            else:
                                prompt += ''.join(diff_lines)
                            prompt += "\n```\n"
                            
                        except json.JSONDecodeError:
                            prompt += f"JSON parsing failed. Raw output comparison:\n"
                            prompt += f"Expected (first 200 chars): {test_info['expected_output'][:200]}...\n"
                            prompt += f"Actual (first 200 chars): {test_info['actual_output'][:200]}...\n"

        # Add specific instructions based on iteration
        if len(iteration_history) == 0:
            prompt += """
YOUR TASK:
This is your first attempt. You need to fix the failing tests while maintaining backward compatibility.
"""
        else:
            prompt += f"""
YOUR TASK - ITERATION {len(iteration_history) + 1}:
You have already tried {len(iteration_history)} time(s) to fix these issues. 
Review the complete history above to understand:
1. What fixes you've already attempted
2. Which fixes worked (tests that now pass)
3. Which fixes didn't work or caused new issues
4. What patterns or edge cases you might have missed

DO NOT repeat the same mistakes. Learn from the iteration history and make targeted fixes for the remaining issues.
"""

        prompt += """
REQUIREMENTS:
1. Fix ONLY the specific issues causing test failures
2. Maintain all existing functionality (backward compatibility)
3. Preserve all working fixes from previous iterations
4. Add clear comments for your specific fixes
5. Do not revert fixes that are already working
6. Return the complete, corrected parser code

Return only the complete Python code with your fixes applied."""

        # Call the specified model
        app_logger.info(f"Calling {model} for iteration {len(iteration_history) + 1} with full history context...")
        
        # Import here to avoid circular imports
        from celi_framework.utils.llms import quick_ask_async
        import asyncio
        
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
        
        # Extract code if wrapped in markdown
        if "```python" in fixed_code:
            fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
        elif "```" in fixed_code:
            fixed_code = fixed_code.split("```")[1].split("```")[0].strip()
            
        return fixed_code
    
    def run_comprehensive_tests_with_llm_fixes(self, parser_code: str, max_iterations: int = 3, claude_analysis: str = None) -> str:
        """
        Run comprehensive tests and automatically fix failures using an LLM with iterative refinement.
        
        Args:
            parser_code: The parser code to test and potentially fix
            max_iterations: Maximum number of fix attempts (default: 3)
            claude_analysis: Claude's initial analysis of format differences (optional)
            
        Returns:
            Final test results and fixed code if applicable
        """

        # Use stored analysis if not provided
        if claude_analysis is None and self.claude_analysis is not None:
            claude_analysis = self.claude_analysis

            app_logger.info("Using stored Claude analysis for Gemini context")
        # First run the tests with detailed errors
        initial_results = self.run_comprehensive_tests(parser_code, detailed_errors=True)
        
        # Check if any tests failed
        if "❌ FAIL" not in initial_results:
            return initial_results + "\n\nNo fixes needed - all tests passed!"
        
        result_lines = [initial_results]
        current_code = parser_code
        iteration_history = []  # Store history of all attempts
        
        # Iterative fixing loop
        for iteration in range(max_iterations):
            # Extract failure information and collect detailed data
            test_results = self.run_comprehensive_tests(current_code, detailed_errors=True)
            
            # Check if all tests pass
            if "🎉 ALL TESTS PASSED! 🎉" in test_results:
                result_lines.append(f"\n=== ITERATION {iteration + 1} SUCCESSFUL ===")
                result_lines.append(test_results)
                self.save_parser(current_code)
                result_lines.append("\n✅ Fixed parser saved successfully!")
                # Return both the results and the fixed parser code
                return '\n'.join(result_lines) + f"\n\n=== FIXED PARSER CODE ===\n```python\n{current_code}\n```"
            
            # Parse test results
            failure_info = []
            detailed_test_info = []
            all_test_cases = []
            lines = test_results.split('\n')
            
            # Parse test results to find all tests (both passing and failing)
            for i, line in enumerate(lines):
                if "✅ PASS" in line or "❌ FAIL" in line:
                    # Extract test name
                    test_name = line.split(":")[0].strip()
                    is_failing = "❌ FAIL" in line
                    
                    # Collect all test case information
                    test_info = {
                        "test_name": test_name,
                        "passed": not is_failing
                    }
                    
                    # Get test input and expected output for ALL tests
                    try:
                        # Handle different paths for main_example vs test_cases
                        if test_name == "main_example":
                            test_input_path = self.base_path / "demos" / self.document_type / self.bank_name / "input_output" / f"{self.document_type.lower()}_{self.bank_name.lower()}_input.txt"
                            test_output_path = self.base_path / "demos" / self.document_type / self.bank_name / "input_output" / f"{self.document_type.lower()}_{self.bank_name.lower()}_output.json"
                        else:
                            test_input_path = self.base_path / "demos" / self.document_type / self.bank_name / "test_cases" / f"{test_name}_input.txt"
                            test_output_path = self.base_path / "demos" / self.document_type / self.bank_name / "test_cases" / f"{test_name}_output.json"
                        
                        # Read test input
                        if test_input_path.exists():
                            with open(test_input_path, 'r') as f:
                                test_info["full_input"] = f.read()
                        
                        # Read expected output
                        if test_output_path.exists():
                            with open(test_output_path, 'r') as f:
                                test_info["expected_output"] = f.read()
                                
                    except Exception as e:
                        test_info["collection_error"] = str(e)
                    
                    all_test_cases.append(test_info)
                    
                    # For failing tests, collect additional error details
                    if is_failing:
                        current_test = test_info.copy()
                        failure_info.append(line)
                        
                        # Get the error message if available
                        if i + 2 < len(lines) and "Error:" in lines[i + 2]:
                            error_msg = lines[i + 2]
                            failure_info.append(error_msg)
                            current_test["error_message"] = error_msg.replace("Error: ", "").strip()
                        
                        # Try to run the test individually to get actual output
                        if "full_input" in test_info:
                            actual_output, exec_error = self._execute_parser_code(current_code, test_info["full_input"])
                            
                            if exec_error:
                                # Parser crashed
                                current_test["error_type"] = "execution_error"
                                current_test["traceback"] = exec_error
                            else:
                                # Parser ran, check output
                                current_test["error_type"] = "output_mismatch"
                                current_test["actual_output"] = actual_output
                        
                        detailed_test_info.append(current_test)
            
            # No more failures to fix
            if not detailed_test_info:
                break
                
            failures_text = '\n'.join(failure_info)
            
            # Store this iteration's state
            iteration_data = {
                "iteration": iteration + 1,
                "test_results": test_results,
                "failing_tests": len(detailed_test_info),
                "total_tests": len(all_test_cases),
                "parser_code": current_code
            }
            iteration_history.append(iteration_data)
            
            # Prepare for LLM fix
            result_lines.append(f"\n=== ITERATION {iteration + 1}: ATTEMPTING LLM FIX ===")
            result_lines.append(f"Detected {len(detailed_test_info)} failing tests out of {len(all_test_cases)} total tests")
            result_lines.append(f"Calling {self.fix_model} to fix the parser...\n")
            
            # Call LLM with comprehensive information including iteration history
            fixed_code = self.fix_parser_with_llm_comprehensive_iterative(
                current_code, 
                failures_text, 
                detailed_test_info, 
                all_test_cases,
                iteration_history,
                claude_analysis=claude_analysis,
                model=self.fix_model
            )
            
            if "Error calling" in fixed_code:
                result_lines.append(f"Failed to get fix from LLM: {fixed_code}")
                break
            
            # Update current code for next iteration
            current_code = fixed_code
            
            # Test the fixed code
            result_lines.append(f"Testing {self.fix_model}'s iteration {iteration + 1} fix...")
            iteration_results = self.run_comprehensive_tests(current_code)
            result_lines.append(iteration_results)
            
            # Check if we should continue
            if "❌ FAIL" not in iteration_results:
                self.save_parser(current_code)
                result_lines.append("\n✅ Fixed parser saved successfully!")
                # Return both the results and the fixed parser code
                return '\n'.join(result_lines) + f"\n\n=== FIXED PARSER CODE ===\n```python\n{current_code}\n```"
            elif iteration < max_iterations - 1:
                result_lines.append(f"\n⚠️ Some tests still failing after iteration {iteration + 1}, trying again...")
            else:
                result_lines.append(f"\n⚠️ Reached maximum iterations ({max_iterations}). Some tests still failing.")
                
        # Return both the results and the final parser code (even if some tests failed)
        return '\n'.join(result_lines) + f"\n\n=== FINAL PARSER CODE ===\n```python\n{current_code}\n```"