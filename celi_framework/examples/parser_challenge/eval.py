#!/usr/bin/env python3
"""
Evaluation script for parser challenge - runs comprehensive tests on all generated parsers.

This script is designed to be run after CELI has generated parsers for the banks.
It will test each parser against all test cases and provide a comprehensive report.
"""

# Load environment variables FIRST before any other imports
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(env_path)

import json
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from test_harness import ParserTestHarness


def evaluate_parsers(document_type: str = "LN6280P", output_dir: Path = None):
    """
    Evaluate all generated parsers for a document type.
    
    Args:
        document_type: The document type to evaluate
        output_dir: Directory containing parser outputs
    
    Returns:
        Dictionary of results
    """
    harness = ParserTestHarness(document_type)
    
    if output_dir is None:
        output_dir = Path(__file__).parent / "output"
    
    print(f"Evaluating parsers in: {output_dir}")
    print(f"Document type: {document_type}")
    
    # Run all tests
    results = harness.run_all_tests(output_dir)
    
    # Print detailed results
    harness.print_results(results)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = output_dir / f"evaluation_results_{document_type}_{timestamp}.json"
    harness.save_results(results, results_file)
    
    return results


def generate_report(results):
    """Generate a detailed report of the evaluation results."""
    report_lines = []
    
    report_lines.append("# Parser Challenge Evaluation Report")
    report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("\n## Summary")
    
    # Calculate overall statistics
    total_banks = len(results)
    banks_with_perfect_score = sum(1 for r in results.values() if r.overall_passed)
    total_tests = sum(len(r.test_results) for r in results.values())
    total_passed = sum(sum(1 for t in r.test_results if t.passed) for r in results.values())
    
    report_lines.append(f"\n- **Total Banks Tested**: {total_banks}")
    report_lines.append(f"- **Banks with Perfect Score**: {banks_with_perfect_score}/{total_banks}")
    report_lines.append(f"- **Total Tests Run**: {total_tests}")
    report_lines.append(f"- **Total Tests Passed**: {total_passed}")
    report_lines.append(f"- **Overall Pass Rate**: {(total_passed/total_tests*100) if total_tests > 0 else 0:.1f}%")
    
    # Detailed results per bank
    report_lines.append("\n## Detailed Results")
    
    for bank_name, bank_results in sorted(results.items(), key=lambda x: x[0]):
        report_lines.append(f"\n### {bank_name} ({bank_results.difficulty})")
        report_lines.append(f"\n**Pass Rate**: {bank_results.pass_rate:.1f}%")
        report_lines.append("\n| Test Case | Status | Execution Time | Notes |")
        report_lines.append("|-----------|--------|----------------|-------|")
        
        for test in bank_results.test_results:
            status = "✅ Pass" if test.passed else "❌ Fail"
            exec_time = f"{test.execution_time:.2f}s" if test.execution_time else "N/A"
            
            # Truncate error message for table
            notes = ""
            if not test.passed and test.error_message:
                first_line = test.error_message.split('\n')[0]
                notes = first_line[:50] + "..." if len(first_line) > 50 else first_line
            
            report_lines.append(f"| {test.test_name} | {status} | {exec_time} | {notes} |")
    
    # Test case analysis
    report_lines.append("\n## Test Case Analysis")
    
    # Analyze by test type
    test_case_stats = {}
    for bank_results in results.values():
        for test in bank_results.test_results:
            if test.test_name not in test_case_stats:
                test_case_stats[test.test_name] = {"passed": 0, "total": 0}
            test_case_stats[test.test_name]["total"] += 1
            if test.passed:
                test_case_stats[test.test_name]["passed"] += 1
    
    report_lines.append("\n| Test Type | Pass Rate | Description |")
    report_lines.append("|-----------|-----------|-------------|")
    
    test_descriptions = {
        "main_example": "Primary input/output example",
        "test_case_1": "Standard test case 1",
        "test_case_2": "Standard test case 2",
        "stress_test_1": "Unicode and special characters",
        "stress_test_2": "Edge cases and business entities"
    }
    
    for test_name in ["main_example", "test_case_1", "test_case_2", "stress_test_1", "stress_test_2"]:
        if test_name in test_case_stats:
            stats = test_case_stats[test_name]
            pass_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            desc = test_descriptions.get(test_name, "")
            report_lines.append(f"| {test_name} | {pass_rate:.1f}% | {desc} |")
    
    # Common failure patterns
    report_lines.append("\n## Common Failure Patterns")
    
    failure_patterns = {}
    for bank_results in results.values():
        for test in bank_results.test_results:
            if not test.passed and test.error_message:
                # Extract key failure patterns
                if "Type mismatch" in test.error_message:
                    failure_patterns["Type mismatches"] = failure_patterns.get("Type mismatches", 0) + 1
                elif "Missing in actual" in test.error_message:
                    failure_patterns["Missing fields"] = failure_patterns.get("Missing fields", 0) + 1
                elif "List length mismatch" in test.error_message:
                    failure_patterns["Incorrect notice count"] = failure_patterns.get("Incorrect notice count", 0) + 1
                elif "JSON decode error" in test.error_message:
                    failure_patterns["Invalid JSON output"] = failure_patterns.get("Invalid JSON output", 0) + 1
                elif "Parser error" in test.error_message:
                    failure_patterns["Parser execution errors"] = failure_patterns.get("Parser execution errors", 0) + 1
    
    if failure_patterns:
        for pattern, count in sorted(failure_patterns.items(), key=lambda x: x[1], reverse=True):
            report_lines.append(f"\n- **{pattern}**: {count} occurrences")
    else:
        report_lines.append("\nNo failures detected! 🎉")
    
    return "\n".join(report_lines)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Evaluate generated parsers for the parser challenge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate all parsers in default output directory
  python eval.py
  
  # Evaluate parsers in a specific directory
  python eval.py --output-dir /path/to/parsers
  
  # Generate a markdown report
  python eval.py --report
"""
    )
    
    parser.add_argument(
        "--document-type",
        default="LN6280P",
        help="Document type to evaluate (default: LN6280P)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory containing parser outputs"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate a detailed markdown report"
    )
    
    args = parser.parse_args()
    
    # Run evaluation
    results = evaluate_parsers(args.document_type, args.output_dir)
    
    if not results:
        print("\nNo parsers found to evaluate!")
        return 1
    
    # Generate report if requested
    if args.report:
        report = generate_report(results)
        
        # Save report
        output_dir = args.output_dir or (Path(__file__).parent / "output")
        report_file = output_dir / f"evaluation_report_{args.document_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\nDetailed report saved to: {report_file}")
    
    # Return appropriate exit code
    all_passed = all(r.overall_passed for r in results.values())
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())