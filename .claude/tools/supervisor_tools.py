#!/usr/bin/env python3
"""
Supervisor Tools - Task Verification and Quality Assurance
Provides verification capabilities for the supervisor agent to validate task completion.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import re


class SupervisorTools:
    """Tools for verifying task completion across all teams."""

    def __init__(self):
        self.root_dir = Path("/home/user/TEST_AGENTS")
        self.teams = {
            "ENGINEERING_TEAM": self.root_dir / "ENGINEERING_TEAM",
            "MARKETING_TEAM": self.root_dir / "MARKETING_TEAM",
            "QA_TEAM": self.root_dir / "QA_TEAM"
        }

    def verify_task_completion(
        self,
        task_description: str,
        team: str = "ALL",
        agents_involved: Optional[List[str]] = None,
        expected_deliverables: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Main verification orchestrator that checks if a task is truly complete.

        Args:
            task_description: Description of the task to verify
            team: Which team(s) to check (ENGINEERING_TEAM, MARKETING_TEAM, QA_TEAM, or ALL)
            agents_involved: List of agent names that worked on the task
            expected_deliverables: List of expected file paths or outputs

        Returns:
            Dict with verification results including status, findings, and evidence
        """
        results = {
            "task": task_description,
            "team": team,
            "agents": agents_involved or [],
            "timestamp": datetime.now().isoformat(),
            "status": "UNKNOWN",
            "findings": {},
            "issues": [],
            "evidence": {}
        }

        # Check deliverables
        if expected_deliverables:
            deliverable_check = self.validate_deliverables(expected_deliverables)
            results["findings"]["deliverables"] = deliverable_check
            if not deliverable_check["all_found"]:
                results["issues"].append(f"Missing deliverables: {deliverable_check['missing']}")

        # Check git changes
        git_check = self.check_git_changes(expected_files=expected_deliverables)
        results["findings"]["git"] = git_check
        if not git_check["has_changes"]:
            results["issues"].append("No git changes found for this task")

        # Determine overall status
        if len(results["issues"]) == 0:
            results["status"] = "PASSED"
        elif len(results["issues"]) < 3:
            results["status"] = "PARTIAL"
        else:
            results["status"] = "FAILED"

        return results

    def check_git_changes(
        self,
        expected_files: Optional[List[str]] = None,
        branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify git commits and file changes.

        Args:
            expected_files: List of files that should have been changed
            branch: Branch to check (defaults to current branch)

        Returns:
            Dict with git verification results
        """
        results = {
            "has_changes": False,
            "branch": None,
            "commits": [],
            "changed_files": [],
            "expected_files_changed": [],
            "missing_files": []
        }

        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.root_dir,
                capture_output=True,
                text=True
            )
            results["branch"] = branch_result.stdout.strip()

            # Get recent commits (last 10)
            log_result = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                cwd=self.root_dir,
                capture_output=True,
                text=True
            )
            results["commits"] = [
                line.strip() for line in log_result.stdout.strip().split("\n")
                if line.strip()
            ]

            # Get changed files in last commit
            diff_result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                cwd=self.root_dir,
                capture_output=True,
                text=True
            )
            results["changed_files"] = [
                line.strip() for line in diff_result.stdout.strip().split("\n")
                if line.strip()
            ]

            results["has_changes"] = len(results["changed_files"]) > 0

            # Check if expected files were changed
            if expected_files:
                for expected_file in expected_files:
                    # Normalize paths
                    normalized_expected = expected_file.replace(str(self.root_dir) + "/", "")
                    if any(normalized_expected in cf for cf in results["changed_files"]):
                        results["expected_files_changed"].append(expected_file)
                    else:
                        results["missing_files"].append(expected_file)

        except Exception as e:
            results["error"] = str(e)

        return results

    def validate_deliverables(
        self,
        expected_deliverables: List[str]
    ) -> Dict[str, Any]:
        """
        Check that expected files or outputs exist.

        Args:
            expected_deliverables: List of file paths to check

        Returns:
            Dict with validation results
        """
        results = {
            "expected_count": len(expected_deliverables),
            "found_count": 0,
            "found": [],
            "missing": [],
            "all_found": False,
            "details": {}
        }

        for deliverable in expected_deliverables:
            # Handle both absolute and relative paths
            if deliverable.startswith("/"):
                file_path = Path(deliverable)
            else:
                file_path = self.root_dir / deliverable

            if file_path.exists():
                results["found"].append(str(deliverable))
                results["found_count"] += 1

                # Get file details
                stat = file_path.stat()
                results["details"][str(deliverable)] = {
                    "exists": True,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "is_empty": stat.st_size == 0
                }
            else:
                results["missing"].append(str(deliverable))
                results["details"][str(deliverable)] = {
                    "exists": False
                }

        results["all_found"] = results["found_count"] == results["expected_count"]

        return results

    def run_verification_tests(
        self,
        test_paths: List[str],
        test_type: str = "unit"
    ) -> Dict[str, Any]:
        """
        Run tests and collect results.

        Args:
            test_paths: List of test file or directory paths
            test_type: Type of tests (unit, integration, e2e)

        Returns:
            Dict with test results
        """
        results = {
            "test_type": test_type,
            "test_paths": test_paths,
            "all_passed": False,
            "summary": {},
            "output": ""
        }

        for test_path in test_paths:
            # Handle both absolute and relative paths
            if test_path.startswith("/"):
                full_path = Path(test_path)
            else:
                full_path = self.root_dir / test_path

            if not full_path.exists():
                results["summary"][test_path] = {
                    "status": "NOT_FOUND",
                    "error": f"Test path does not exist: {full_path}"
                }
                continue

            try:
                # Run pytest
                cmd_result = subprocess.run(
                    ["pytest", str(full_path), "-v", "--tb=short"],
                    cwd=self.root_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

                results["summary"][test_path] = {
                    "status": "PASSED" if cmd_result.returncode == 0 else "FAILED",
                    "return_code": cmd_result.returncode,
                    "stdout": cmd_result.stdout,
                    "stderr": cmd_result.stderr
                }

                results["output"] += cmd_result.stdout + "\n" + cmd_result.stderr

            except subprocess.TimeoutExpired:
                results["summary"][test_path] = {
                    "status": "TIMEOUT",
                    "error": "Test execution timed out after 5 minutes"
                }
            except Exception as e:
                results["summary"][test_path] = {
                    "status": "ERROR",
                    "error": str(e)
                }

        # Determine overall pass/fail
        all_passed = all(
            summary.get("status") == "PASSED"
            for summary in results["summary"].values()
        )
        results["all_passed"] = all_passed

        return results

    def check_code_quality(
        self,
        files: List[str],
        criteria: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform code quality checks.

        Args:
            files: List of file paths to check
            criteria: List of criteria to check (no_syntax_errors, has_docstrings, etc.)

        Returns:
            Dict with quality check results
        """
        if criteria is None:
            criteria = ["no_syntax_errors", "has_docstrings"]

        results = {
            "files_checked": len(files),
            "criteria": criteria,
            "passed": [],
            "failed": [],
            "issues": [],
            "all_passed": False
        }

        for file_path in files:
            # Handle both absolute and relative paths
            if file_path.startswith("/"):
                full_path = Path(file_path)
            else:
                full_path = self.root_dir / file_path

            if not full_path.exists():
                results["failed"].append(file_path)
                results["issues"].append(f"File not found: {file_path}")
                continue

            file_issues = []

            # Check syntax for Python files
            if full_path.suffix == ".py" and "no_syntax_errors" in criteria:
                try:
                    with open(full_path, 'r') as f:
                        compile(f.read(), str(full_path), 'exec')
                except SyntaxError as e:
                    file_issues.append(f"Syntax error in {file_path}:{e.lineno}: {e.msg}")

            # Check for docstrings in Python files
            if full_path.suffix == ".py" and "has_docstrings" in criteria:
                try:
                    with open(full_path, 'r') as f:
                        content = f.read()
                        # Simple check for module-level docstring
                        if not content.strip().startswith('"""') and not content.strip().startswith("'''"):
                            file_issues.append(f"Missing module docstring in {file_path}")
                except Exception as e:
                    file_issues.append(f"Error reading {file_path}: {e}")

            # Check for security issues (basic patterns)
            if "no_security_issues" in criteria:
                try:
                    with open(full_path, 'r') as f:
                        content = f.read()

                        # Check for hardcoded secrets
                        secret_patterns = [
                            r'password\s*=\s*["\'][^"\']+["\']',
                            r'api_key\s*=\s*["\'][^"\']+["\']',
                            r'secret\s*=\s*["\'][^"\']+["\']',
                            r'token\s*=\s*["\'][^"\']+["\']'
                        ]

                        for pattern in secret_patterns:
                            matches = re.finditer(pattern, content, re.IGNORECASE)
                            for match in matches:
                                line_num = content[:match.start()].count('\n') + 1
                                file_issues.append(
                                    f"Potential hardcoded secret in {file_path}:{line_num}"
                                )
                except Exception as e:
                    file_issues.append(f"Error checking security in {file_path}: {e}")

            if file_issues:
                results["failed"].append(file_path)
                results["issues"].extend(file_issues)
            else:
                results["passed"].append(file_path)

        results["all_passed"] = len(results["failed"]) == 0

        return results

    def verify_documentation(
        self,
        docs: List[str],
        required_sections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Verify documentation exists and is complete.

        Args:
            docs: List of documentation file paths
            required_sections: List of section headers that must be present

        Returns:
            Dict with documentation verification results
        """
        results = {
            "docs_checked": len(docs),
            "required_sections": required_sections or [],
            "found": [],
            "missing": [],
            "incomplete": [],
            "details": {},
            "all_complete": False
        }

        for doc_path in docs:
            # Handle both absolute and relative paths
            if doc_path.startswith("/"):
                full_path = Path(doc_path)
            else:
                full_path = self.root_dir / doc_path

            doc_info = {
                "exists": full_path.exists(),
                "missing_sections": []
            }

            if full_path.exists():
                results["found"].append(doc_path)

                try:
                    with open(full_path, 'r') as f:
                        content = f.read()
                        doc_info["size"] = len(content)
                        doc_info["is_empty"] = len(content.strip()) == 0

                        # Check for required sections
                        if required_sections:
                            for section in required_sections:
                                # Look for markdown headers
                                patterns = [
                                    f"# {section}",
                                    f"## {section}",
                                    f"### {section}"
                                ]
                                if not any(pattern.lower() in content.lower() for pattern in patterns):
                                    doc_info["missing_sections"].append(section)

                        if doc_info["missing_sections"]:
                            results["incomplete"].append(doc_path)

                except Exception as e:
                    doc_info["error"] = str(e)
            else:
                results["missing"].append(doc_path)

            results["details"][doc_path] = doc_info

        results["all_complete"] = (
            len(results["missing"]) == 0 and
            len(results["incomplete"]) == 0
        )

        return results

    def generate_verification_report(
        self,
        task_id: str,
        verification_status: str,
        findings: Dict[str, Any],
        issues_found: List[str],
        recommendations: List[str]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive verification report.

        Args:
            task_id: Unique identifier for the task
            verification_status: PASSED, FAILED, or PARTIAL
            findings: Dictionary of verification findings
            issues_found: List of issues discovered
            recommendations: List of recommended actions

        Returns:
            Dict containing the structured report
        """
        report = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "status": verification_status,
            "findings": findings,
            "issues": issues_found,
            "recommendations": recommendations,
            "summary": {}
        }

        # Calculate quality score (0-10)
        total_checks = len(findings)
        passed_checks = sum(
            1 for finding in findings.values()
            if isinstance(finding, dict) and finding.get("status") == "PASSED"
        )

        if total_checks > 0:
            report["summary"]["quality_score"] = round((passed_checks / total_checks) * 10, 1)
        else:
            report["summary"]["quality_score"] = 0

        report["summary"]["total_checks"] = total_checks
        report["summary"]["passed_checks"] = passed_checks
        report["summary"]["failed_checks"] = total_checks - passed_checks
        report["summary"]["issues_count"] = len(issues_found)

        # Determine deployment readiness
        if verification_status == "PASSED" and len(issues_found) == 0:
            report["summary"]["deployment_ready"] = True
            report["summary"]["recommendation"] = "Ready for deployment"
        elif verification_status == "PARTIAL" and len(issues_found) < 3:
            report["summary"]["deployment_ready"] = False
            report["summary"]["recommendation"] = "Address minor issues before deployment"
        else:
            report["summary"]["deployment_ready"] = False
            report["summary"]["recommendation"] = "NOT ready - critical issues must be resolved"

        return report


# MCP Server Interface
def main():
    """MCP server main function for supervisor tools."""
    import sys

    tools = SupervisorTools()

    # If called directly, provide a simple CLI
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "verify_task":
            result = tools.verify_task_completion(
                task_description=sys.argv[2] if len(sys.argv) > 2 else "Unknown task",
                team=sys.argv[3] if len(sys.argv) > 3 else "ALL"
            )
            print(json.dumps(result, indent=2))

        elif command == "check_git":
            result = tools.check_git_changes()
            print(json.dumps(result, indent=2))

        elif command == "validate_deliverables":
            deliverables = sys.argv[2:] if len(sys.argv) > 2 else []
            result = tools.validate_deliverables(deliverables)
            print(json.dumps(result, indent=2))

        else:
            print(f"Unknown command: {command}")
            print("Available commands: verify_task, check_git, validate_deliverables")
    else:
        print("Supervisor Tools - Task Verification System")
        print("Usage: supervisor_tools.py <command> [args...]")


if __name__ == "__main__":
    main()
