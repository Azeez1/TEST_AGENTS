"""
Coverage Analyzer and Test Runner Tools
Analyzes test coverage and runs pytest tests
"""

from claude_agent_sdk import tool
import json
import subprocess
import os
from pathlib import Path
from typing import Dict


@tool(
    "run_tests",
    "Execute pytest tests and capture results",
    {
        "test_path": str,  # Path to test file or directory
        "verbose": bool,  # Verbose output (default False)
        "coverage": bool,  # Run with coverage report (default True)
        "markers": str  # Run specific markers (e.g., "not slow")
    }
)
async def run_tests(args):
    """
    Run pytest tests and return results
    """
    test_path = args.get("test_path", "tests/")
    verbose = args.get("verbose", False)
    coverage = args.get("coverage", True)
    markers = args.get("markers", "")

    # Build pytest command
    cmd = ["pytest", test_path]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(["--cov", "--cov-report=term", "--cov-report=json"])

    if markers:
        cmd.extend(["-m", markers])

    # Add JSON report
    cmd.extend(["--json-report", "--json-report-file=test_report.json"])

    try:
        # Run pytest
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        # Parse results
        output = {
            "status": "completed",
            "exit_code": result.returncode,
            "passed": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

        # Try to read JSON report if available
        if os.path.exists("test_report.json"):
            with open("test_report.json") as f:
                output["detailed_report"] = json.load(f)

        # Try to read coverage report if available
        if coverage and os.path.exists(".coverage.json"):
            with open(".coverage.json") as f:
                output["coverage_data"] = json.load(f)

        return {
            "content": [{
                "type": "text",
                "text": json.dumps(output, indent=2)
            }]
        }

    except subprocess.TimeoutExpired:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "status": "timeout",
                    "error": "Tests exceeded 5 minute timeout"
                }, indent=2)
            }]
        }
    except FileNotFoundError:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "status": "error",
                    "error": "pytest not found. Install with: pip install pytest pytest-cov pytest-json-report"
                }, indent=2)
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "status": "error",
                    "error": str(e)
                }, indent=2)
            }]
        }


@tool(
    "analyze_coverage",
    "Analyze test coverage and identify gaps",
    {
        "source_path": str,  # Path to source code
        "test_path": str,  # Path to tests
        "min_coverage": int  # Minimum coverage threshold (default 80)
    }
)
async def analyze_coverage(args):
    """
    Analyze test coverage and provide recommendations
    """
    source_path = args.get("source_path", ".")
    test_path = args.get("test_path", "tests/")
    min_coverage = args.get("min_coverage", 80)

    try:
        # Run coverage
        cmd = [
            "pytest",
            test_path,
            "--cov=" + source_path,
            "--cov-report=json",
            "--cov-report=term-missing"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        # Parse coverage report
        coverage_data = {}
        if os.path.exists("coverage.json"):
            with open("coverage.json") as f:
                coverage_data = json.load(f)

        # Analyze coverage
        analysis = _analyze_coverage_data(coverage_data, min_coverage)

        # Add stdout for human-readable report
        analysis["coverage_report"] = result.stdout

        return {
            "content": [{
                "type": "text",
                "text": json.dumps(analysis, indent=2)
            }]
        }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "status": "error",
                    "error": str(e),
                    "note": "Make sure pytest-cov is installed: pip install pytest-cov"
                }, indent=2)
            }]
        }


@tool(
    "identify_edge_cases",
    "Identify potential edge cases for testing",
    {
        "function_info": dict  # Function information from code scanner
    }
)
async def identify_edge_cases(args):
    """
    Identify edge cases for a function
    """
    func_info = args["function_info"]

    edge_cases = {
        "function": func_info.get("name"),
        "boundary_cases": [],
        "error_cases": [],
        "special_cases": [],
        "priority": "medium"
    }

    # Analyze parameters for edge cases
    parameters = func_info.get("parameters", [])

    for param in parameters:
        param_name = param.get("name")
        param_type = param.get("annotation", "")

        # String edge cases
        if "str" in param_type.lower():
            edge_cases["boundary_cases"].extend([
                f"{param_name}: empty string ''",
                f"{param_name}: None",
                f"{param_name}: very long string (10000 chars)",
                f"{param_name}: unicode characters '日本語🔥'"
            ])
            edge_cases["special_cases"].extend([
                f"{param_name}: special chars '\\n\\t\\r'",
                f"{param_name}: SQL injection attempt \"'; DROP TABLE--\""
            ])

        # Numeric edge cases
        elif any(t in param_type.lower() for t in ["int", "float", "number"]):
            edge_cases["boundary_cases"].extend([
                f"{param_name}: zero (0)",
                f"{param_name}: negative (-1)",
                f"{param_name}: very large (sys.maxsize)",
                f"{param_name}: None"
            ])

        # Collection edge cases
        elif any(t in param_type.lower() for t in ["list", "dict", "set"]):
            edge_cases["boundary_cases"].extend([
                f"{param_name}: empty collection",
                f"{param_name}: single element",
                f"{param_name}: None",
                f"{param_name}: very large (10000+ items)"
            ])

        # Boolean edge cases
        elif "bool" in param_type.lower():
            edge_cases["boundary_cases"].extend([
                f"{param_name}: True",
                f"{param_name}: False",
                f"{param_name}: None"
            ])

    # Add general error cases
    if parameters:
        edge_cases["error_cases"].extend([
            "All parameters None",
            "Wrong parameter types",
            "Missing required parameters"
        ])

    # Determine priority based on complexity
    complexity = func_info.get("complexity", 1)
    if complexity > 5:
        edge_cases["priority"] = "high"
    elif complexity < 3:
        edge_cases["priority"] = "low"

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(edge_cases, indent=2)
        }]
    }


def _analyze_coverage_data(coverage_data: Dict, min_coverage: int) -> Dict:
    """Analyze coverage data and provide insights"""

    if not coverage_data:
        return {
            "status": "no_coverage_data",
            "message": "No coverage data available. Run tests with --cov flag."
        }

    totals = coverage_data.get("totals", {})
    files = coverage_data.get("files", {})

    total_coverage = totals.get("percent_covered", 0)

    analysis = {
        "status": "analyzed",
        "overall_coverage": f"{total_coverage:.2f}%",
        "meets_threshold": total_coverage >= min_coverage,
        "threshold": f"{min_coverage}%",
        "gap": f"{max(0, min_coverage - total_coverage):.2f}%",
        "files_analysis": [],
        "recommendations": []
    }

    # Analyze each file
    for file_path, file_data in files.items():
        file_coverage = file_data.get("summary", {}).get("percent_covered", 0)
        missing_lines = file_data.get("missing_lines", [])

        file_analysis = {
            "file": file_path,
            "coverage": f"{file_coverage:.2f}%",
            "missing_lines_count": len(missing_lines),
            "missing_lines": missing_lines[:10],  # First 10 missing lines
            "priority": "high" if file_coverage < 50 else "medium" if file_coverage < 80 else "low"
        }

        analysis["files_analysis"].append(file_analysis)

    # Generate recommendations
    low_coverage_files = [
        f for f in analysis["files_analysis"]
        if float(f["coverage"].rstrip("%")) < min_coverage
    ]

    if low_coverage_files:
        analysis["recommendations"].append(
            f"Improve coverage for {len(low_coverage_files)} files below threshold"
        )

    if total_coverage < min_coverage:
        analysis["recommendations"].append(
            f"Add {analysis['gap']} more coverage to meet threshold"
        )

    # Prioritize files needing tests
    priority_files = sorted(
        analysis["files_analysis"],
        key=lambda x: float(x["coverage"].rstrip("%"))
    )[:5]

    analysis["priority_files"] = [f["file"] for f in priority_files]

    return analysis
