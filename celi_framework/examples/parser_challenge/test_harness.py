"""Test harness for parser challenge - runs comprehensive tests on generated parsers."""

import json
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TestResult:
    """Result of a single test case."""
    test_name: str
    passed: bool
    error_message: Optional[str] = None
    output_diff: Optional[str] = None
    execution_time: Optional[float] = None


@dataclass
class BankTestResults:
    """Results for all test cases of a single bank."""
    bank_name: str
    difficulty: str
    test_results: List[TestResult]
    overall_passed: bool
    
    @property
    def pass_rate(self) -> float:
        """Calculate the pass rate as a percentage."""
        if not self.test_results:
            return 0.0
        passed = sum(1 for r in self.test_results if r.passed)
        return (passed / len(self.test_results)) * 100


class ParserTestHarness:
    """Test harness for running parser tests."""
    
    def __init__(self, document_type: str = "LN6280P"):
        self.document_type = document_type
        self.base_path = Path("/home/sam/Projects/prog_parser_statements")
        self.celi_path = Path("/home/sam/Projects/celi/celi_framework/examples/parser_challenge")
        
        # Define the challenges with their difficulty levels
        self.challenges = {
            "RegionalBank": "easy",
            "CommunityCredit": "intermediate", 
            "MetroBank": "advanced"
        }
        
        # Test case names
        self.test_cases = [
            "test_case_1",
            "test_case_2", 
            "stress_test_1",
            "stress_test_2"
        ]
    
    def run_parser(self, parser_path: Path, input_path: Path, timeout: int = 10) -> Tuple[str, str]:
        """
        Run a parser on an input file and return output and error.
        
        Args:
            parser_path: Path to the parser file
            input_path: Path to the input file
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (output, error)
        """
        try:
            result = subprocess.run(
                [sys.executable, str(parser_path), str(input_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=parser_path.parent
            )
            
            if result.returncode != 0:
                return "", f"Parser error (exit code {result.returncode}):\n{result.stderr}"
            
            return result.stdout.strip(), ""
            
        except subprocess.TimeoutExpired:
            return "", f"Parser execution timed out after {timeout} seconds"
        except Exception as e:
            return "", f"Execution error: {str(e)}\n{traceback.format_exc()}"
    
    def compare_json_outputs(self, actual: str, expected: str) -> Tuple[bool, Optional[str]]:
        """
        Compare two JSON outputs for exact match.
        
        Args:
            actual: Actual output JSON string
            expected: Expected output JSON string
            
        Returns:
            Tuple of (matches, error_message)
        """
        try:
            actual_obj = json.loads(actual)
            expected_obj = json.loads(expected)
            
            # Normalize by pretty-printing with sorted keys
            actual_normalized = json.dumps(actual_obj, indent=2, sort_keys=True)
            expected_normalized = json.dumps(expected_obj, indent=2, sort_keys=True)
            
            if actual_normalized == expected_normalized:
                return True, None
            
            # Find differences
            diff_summary = self._summarize_json_differences(actual_obj, expected_obj)
            return False, diff_summary
            
        except json.JSONDecodeError as e:
            return False, f"JSON decode error: {e}"
        except Exception as e:
            return False, f"Comparison error: {e}"
    
    def _summarize_json_differences(self, obj1: any, obj2: any, path: str = "") -> str:
        """Summarize differences between two JSON objects."""
        differences = []
        
        def find_diffs(o1, o2, p):
            if type(o1) != type(o2):
                differences.append(f"{p}: Type mismatch - {type(o1).__name__} vs {type(o2).__name__}")
                return
            
            if isinstance(o1, dict):
                all_keys = set(o1.keys()) | set(o2.keys())
                for key in sorted(all_keys):
                    if key not in o1:
                        differences.append(f"{p}.{key}: Missing in actual")
                    elif key not in o2:
                        differences.append(f"{p}.{key}: Extra in actual")
                    else:
                        find_diffs(o1[key], o2[key], f"{p}.{key}")
            
            elif isinstance(o1, list):
                if len(o1) != len(o2):
                    differences.append(f"{p}: List length mismatch - {len(o1)} vs {len(o2)}")
                for i in range(min(len(o1), len(o2))):
                    find_diffs(o1[i], o2[i], f"{p}[{i}]")
            
            elif o1 != o2:
                differences.append(f"{p}: '{o1}' != '{o2}'")
        
        find_diffs(obj1, obj2, "root")
        
        # Return first 10 differences
        if len(differences) > 10:
            return "\n".join(differences[:10]) + f"\n... and {len(differences) - 10} more differences"
        return "\n".join(differences)
    
    def test_single_case(self, parser_path: Path, bank_name: str, test_case: str) -> TestResult:
        """
        Test a single test case.
        
        Args:
            parser_path: Path to the parser file
            bank_name: Name of the bank
            test_case: Name of the test case
            
        Returns:
            TestResult object
        """
        # Construct paths
        test_dir = self.base_path / "demos" / self.document_type / bank_name / "test_cases"
        input_path = test_dir / f"{test_case}_input.txt"
        expected_path = test_dir / f"{test_case}_output.json"
        
        # Check if files exist
        if not input_path.exists():
            return TestResult(test_case, False, f"Input file not found: {input_path}")
        if not expected_path.exists():
            return TestResult(test_case, False, f"Expected output file not found: {expected_path}")
        
        # Read expected output
        try:
            with open(expected_path, 'r', encoding='utf-8') as f:
                expected_output = f.read()
        except Exception as e:
            return TestResult(test_case, False, f"Error reading expected output: {e}")
        
        # Run parser
        start_time = datetime.now()
        actual_output, error = self.run_parser(parser_path, input_path)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        if error:
            return TestResult(test_case, False, error, execution_time=execution_time)
        
        # Compare outputs
        matches, diff = self.compare_json_outputs(actual_output, expected_output)
        
        return TestResult(
            test_case,
            matches,
            error_message=diff if not matches else None,
            execution_time=execution_time
        )
    
    def test_bank_parser(self, parser_path: Path, bank_name: str) -> BankTestResults:
        """
        Run all test cases for a specific bank parser.
        
        Args:
            parser_path: Path to the parser file
            bank_name: Name of the bank
            
        Returns:
            BankTestResults object
        """
        if bank_name not in self.challenges:
            raise ValueError(f"Unknown bank: {bank_name}")
        
        # Also test the main input/output example
        all_test_cases = ["main_example"] + self.test_cases
        test_results = []
        
        for test_case in all_test_cases:
            if test_case == "main_example":
                # Special handling for main example
                test_dir = self.base_path / "demos" / self.document_type / bank_name / "input_output"
                input_path = test_dir / f"{self.document_type.lower()}_{bank_name.lower()}_input.txt"
                expected_path = test_dir / f"{self.document_type.lower()}_{bank_name.lower()}_output.json"
                
                if not input_path.exists() or not expected_path.exists():
                    result = TestResult("main_example", False, "Main example files not found")
                else:
                    try:
                        with open(expected_path, 'r', encoding='utf-8') as f:
                            expected_output = f.read()
                        
                        start_time = datetime.now()
                        actual_output, error = self.run_parser(parser_path, input_path)
                        execution_time = (datetime.now() - start_time).total_seconds()
                        
                        if error:
                            result = TestResult("main_example", False, error, execution_time=execution_time)
                        else:
                            matches, diff = self.compare_json_outputs(actual_output, expected_output)
                            result = TestResult(
                                "main_example",
                                matches,
                                error_message=diff if not matches else None,
                                execution_time=execution_time
                            )
                    except Exception as e:
                        result = TestResult("main_example", False, f"Error: {e}")
                
                test_results.append(result)
            else:
                result = self.test_single_case(parser_path, bank_name, test_case)
                test_results.append(result)
        
        # Check if all tests passed
        all_passed = all(r.passed for r in test_results)
        
        return BankTestResults(
            bank_name=bank_name,
            difficulty=self.challenges[bank_name],
            test_results=test_results,
            overall_passed=all_passed
        )
    
    def run_all_tests(self, output_dir: Optional[Path] = None) -> Dict[str, BankTestResults]:
        """
        Run tests for all banks that have parsers in the output directory.
        
        Args:
            output_dir: Directory containing parser outputs (default: CELI output dir)
            
        Returns:
            Dictionary mapping bank names to test results
        """
        if output_dir is None:
            output_dir = self.celi_path / "output"
        
        results = {}
        
        for bank_name in self.challenges:
            parser_dir = output_dir / f"{self.document_type}_{bank_name}"
            parser_path = parser_dir / "parser.py"
            
            if parser_path.exists():
                print(f"\nTesting {bank_name} parser...")
                results[bank_name] = self.test_bank_parser(parser_path, bank_name)
            else:
                print(f"\nSkipping {bank_name} - parser not found at {parser_path}")
        
        return results
    
    def print_results(self, results: Dict[str, BankTestResults]):
        """Print a formatted summary of test results."""
        print("\n" + "="*80)
        print(f"PARSER CHALLENGE TEST RESULTS - {self.document_type}")
        print("="*80)
        
        for bank_name, bank_results in results.items():
            print(f"\n{bank_name} ({bank_results.difficulty}):")
            print("-" * 40)
            
            for test_result in bank_results.test_results:
                status = "✅ PASS" if test_result.passed else "❌ FAIL"
                print(f"  {test_result.test_name}: {status}", end="")
                if test_result.execution_time:
                    print(f" ({test_result.execution_time:.2f}s)")
                else:
                    print()
                
                if not test_result.passed and test_result.error_message:
                    # Print first few lines of error
                    error_lines = test_result.error_message.split('\n')[:3]
                    for line in error_lines:
                        print(f"    {line}")
                    if len(test_result.error_message.split('\n')) > 3:
                        print("    ...")
            
            print(f"\n  Overall: {bank_results.pass_rate:.1f}% ({sum(1 for r in bank_results.test_results if r.passed)}/{len(bank_results.test_results)} passed)")
        
        # Overall summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        
        total_tests = sum(len(r.test_results) for r in results.values())
        total_passed = sum(sum(1 for t in r.test_results if t.passed) for r in results.values())
        
        print(f"Total banks tested: {len(results)}")
        print(f"Total tests run: {total_tests}")
        print(f"Total tests passed: {total_passed}")
        print(f"Overall pass rate: {(total_passed/total_tests*100) if total_tests > 0 else 0:.1f}%")
        
        # Check if all banks passed all tests
        all_perfect = all(r.overall_passed for r in results.values())
        if all_perfect:
            print("\n🎉 All parsers passed all tests! 🎉")
        
        print("="*80)
    
    def save_results(self, results: Dict[str, BankTestResults], output_path: Optional[Path] = None):
        """Save test results to a JSON file."""
        if output_path is None:
            output_path = self.celi_path / "output" / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert results to JSON-serializable format
        json_results = {}
        for bank_name, bank_results in results.items():
            json_results[bank_name] = {
                "difficulty": bank_results.difficulty,
                "overall_passed": bank_results.overall_passed,
                "pass_rate": bank_results.pass_rate,
                "test_results": [
                    {
                        "test_name": r.test_name,
                        "passed": r.passed,
                        "error_message": r.error_message,
                        "execution_time": r.execution_time
                    }
                    for r in bank_results.test_results
                ]
            }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"\nTest results saved to: {output_path}")


def main():
    """Main entry point for running the test harness."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test harness for parser challenge",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--document-type",
        default="LN6280P",
        help="Document type to test (default: LN6280P)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory containing parser outputs"
    )
    
    parser.add_argument(
        "--bank",
        choices=["RegionalBank", "CommunityCredit", "MetroBank"],
        help="Test only a specific bank parser"
    )
    
    parser.add_argument(
        "--save-results",
        action="store_true",
        help="Save test results to JSON file"
    )
    
    args = parser.parse_args()
    
    # Create test harness
    harness = ParserTestHarness(args.document_type)
    
    # Run tests
    if args.bank:
        # Test single bank
        parser_path = (args.output_dir or harness.celi_path / "output") / f"{args.document_type}_{args.bank}" / "parser.py"
        if not parser_path.exists():
            print(f"Error: Parser not found at {parser_path}")
            return 1
        
        results = {args.bank: harness.test_bank_parser(parser_path, args.bank)}
    else:
        # Test all banks
        results = harness.run_all_tests(args.output_dir)
    
    # Print results
    harness.print_results(results)
    
    # Save results if requested
    if args.save_results:
        harness.save_results(results)
    
    # Return exit code based on results
    all_passed = all(r.overall_passed for r in results.values())
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())