#!/usr/bin/env python3
"""
Comprehensive Test Performance Analyzer
Runs all tests and collects detailed timing/performance metrics
"""

import subprocess
import time
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

class TestPerformanceAnalyzer:
    def __init__(self):
        self.results = []
        self.start_time = None
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {},
            "bottlenecks": [],
            "recommendations": []
        }

    def print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}{text.center(70)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.END}\n")

    def print_test_header(self, test_name: str):
        """Print test section header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'─'*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}▶ {test_name}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'─'*70}{Colors.END}")

    def run_test_script(self, script_path: str, test_name: str) -> Dict:
        """Run a test script and collect timing data"""
        self.print_test_header(test_name)

        start_time = time.time()
        result = {
            "name": test_name,
            "script": str(script_path),
            "start_time": start_time,
            "status": "unknown",
            "duration_ms": 0,
            "output": "",
            "error": ""
        }

        try:
            print(f"{Colors.BLUE}[*] Starting: {script_path}{Colors.END}")
            print(f"{Colors.BLUE}[*] Time: {datetime.now().strftime('%H:%M:%S')}{Colors.END}\n")

            # Run the test with timeout
            process = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
                cwd=Path(script_path).parent
            )

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            result["duration_ms"] = duration_ms
            result["end_time"] = end_time
            result["output"] = process.stdout
            result["error"] = process.stderr
            result["return_code"] = process.returncode

            # Determine status
            if process.returncode == 0:
                result["status"] = "PASSED"
                print(f"{Colors.GREEN}[✓] PASSED{Colors.END}")
            else:
                result["status"] = "FAILED"
                print(f"{Colors.RED}[✗] FAILED{Colors.END}")

            # Print timing
            print(f"\n{Colors.YELLOW}[⏱] Duration: {duration_ms:.2f}ms ({duration_ms/1000:.2f}s){Colors.END}")

            # Show output if available
            if process.stdout:
                print(f"\n{Colors.BOLD}Output:{Colors.END}")
                print(process.stdout[:500])  # First 500 chars
                if len(process.stdout) > 500:
                    print(f"... (truncated, {len(process.stdout)} total chars)")

            if process.stderr:
                print(f"\n{Colors.RED}Errors:{Colors.END}")
                print(process.stderr[:500])

        except subprocess.TimeoutExpired:
            end_time = time.time()
            result["duration_ms"] = (end_time - start_time) * 1000
            result["status"] = "TIMEOUT"
            result["error"] = "Test exceeded 120 second timeout"
            print(f"{Colors.RED}[✗] TIMEOUT (>120s){Colors.END}")

        except FileNotFoundError:
            result["status"] = "NOT_FOUND"
            result["error"] = "Python interpreter not found"
            print(f"{Colors.RED}[✗] NOT_FOUND{Colors.END}")

        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            print(f"{Colors.RED}[✗] ERROR: {e}{Colors.END}")

        self.results.append(result)
        return result

    def run_pytest_smoke_tests(self) -> Dict:
        """Run pytest with smoke test markers if they exist"""
        self.print_test_header("PYTEST SMOKE TESTS")

        start_time = time.time()
        result = {
            "name": "Pytest Smoke Tests",
            "script": "pytest -m smoke",
            "start_time": start_time,
            "status": "unknown",
            "duration_ms": 0,
            "output": "",
            "error": ""
        }

        try:
            print(f"{Colors.BLUE}[*] Running: pytest -m smoke -v --tb=short{Colors.END}\n")

            process = subprocess.run(
                ["pytest", "-m", "smoke", "-v", "--tb=short", "--timeout=60"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd="/home/user/TEST_AGENTS"
            )

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            result["duration_ms"] = duration_ms
            result["output"] = process.stdout
            result["error"] = process.stderr
            result["return_code"] = process.returncode

            if process.returncode == 0:
                result["status"] = "PASSED"
                print(f"{Colors.GREEN}[✓] PASSED{Colors.END}")
            elif "no tests ran" in process.stdout.lower():
                result["status"] = "NO_TESTS"
                print(f"{Colors.YELLOW}[!] NO SMOKE TESTS FOUND{Colors.END}")
            else:
                result["status"] = "FAILED"
                print(f"{Colors.RED}[✗] FAILED{Colors.END}")

            print(f"\n{Colors.YELLOW}[⏱] Duration: {duration_ms:.2f}ms ({duration_ms/1000:.2f}s){Colors.END}")

            if process.stdout:
                print(f"\n{Colors.BOLD}Output:{Colors.END}")
                print(process.stdout[:1000])

        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            print(f"{Colors.RED}[✗] ERROR: {e}{Colors.END}")

        self.results.append(result)
        return result

    def analyze_bottlenecks(self):
        """Analyze test results for bottlenecks"""
        print(f"\n{Colors.BOLD}{Colors.YELLOW}Analyzing Bottlenecks...{Colors.END}")

        # Sort by duration
        sorted_results = sorted(self.results, key=lambda x: x.get("duration_ms", 0), reverse=True)

        # Identify slow tests (>2 seconds)
        slow_tests = [r for r in sorted_results if r.get("duration_ms", 0) > 2000]

        if slow_tests:
            print(f"\n{Colors.RED}⚠ Found {len(slow_tests)} slow test(s) (>2s):{Colors.END}")
            for test in slow_tests:
                duration_s = test["duration_ms"] / 1000
                print(f"  • {test['name']}: {duration_s:.2f}s")
                self.report["bottlenecks"].append({
                    "test": test["name"],
                    "duration_ms": test["duration_ms"],
                    "duration_s": duration_s
                })
        else:
            print(f"{Colors.GREEN}✓ No slow tests detected (all <2s){Colors.END}")

        # Check for timeouts
        timeouts = [r for r in self.results if r.get("status") == "TIMEOUT"]
        if timeouts:
            print(f"\n{Colors.RED}⚠ Found {len(timeouts)} timeout(s):{Colors.END}")
            for test in timeouts:
                print(f"  • {test['name']}")

    def generate_recommendations(self):
        """Generate performance improvement recommendations"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}Generating Recommendations...{Colors.END}")

        recommendations = []

        # Check for slow tests
        slow_tests = [r for r in self.results if r.get("duration_ms", 0) > 2000]
        if slow_tests:
            recommendations.append({
                "priority": "HIGH",
                "issue": f"{len(slow_tests)} test(s) taking >2 seconds",
                "recommendation": "Consider parallelizing tests or reducing I/O operations"
            })

        # Check for timeouts
        timeouts = [r for r in self.results if r.get("status") == "TIMEOUT"]
        if timeouts:
            recommendations.append({
                "priority": "CRITICAL",
                "issue": f"{len(timeouts)} test(s) timing out (>120s)",
                "recommendation": "Investigate infinite loops, network calls, or resource contention"
            })

        # Check for failed tests
        failed = [r for r in self.results if r.get("status") == "FAILED"]
        if failed:
            recommendations.append({
                "priority": "HIGH",
                "issue": f"{len(failed)} test(s) failing",
                "recommendation": "Review test failures and fix underlying issues"
            })

        # Performance optimizations
        total_duration = sum(r.get("duration_ms", 0) for r in self.results)
        if total_duration > 60000:  # >1 minute
            recommendations.append({
                "priority": "MEDIUM",
                "issue": f"Total test duration: {total_duration/1000:.2f}s",
                "recommendation": "Consider pytest-xdist for parallel execution: pytest -n auto"
            })

        self.report["recommendations"] = recommendations

        if recommendations:
            print(f"\n{Colors.YELLOW}{'─'*70}{Colors.END}")
            for rec in recommendations:
                priority_color = Colors.RED if rec["priority"] == "CRITICAL" else Colors.YELLOW
                print(f"{priority_color}[{rec['priority']}]{Colors.END} {rec['issue']}")
                print(f"  → {rec['recommendation']}\n")
        else:
            print(f"{Colors.GREEN}✓ No performance issues detected!{Colors.END}")

    def print_summary(self):
        """Print test execution summary"""
        self.print_header("TEST EXECUTION SUMMARY")

        total_tests = len(self.results)
        passed = len([r for r in self.results if r.get("status") == "PASSED"])
        failed = len([r for r in self.results if r.get("status") == "FAILED"])
        timeouts = len([r for r in self.results if r.get("status") == "TIMEOUT"])
        errors = len([r for r in self.results if r.get("status") == "ERROR"])
        no_tests = len([r for r in self.results if r.get("status") == "NO_TESTS"])

        total_duration = sum(r.get("duration_ms", 0) for r in self.results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0

        # Summary stats
        print(f"{Colors.BOLD}Tests Run:{Colors.END} {total_tests}")
        print(f"{Colors.GREEN}  ✓ Passed:{Colors.END} {passed}")
        print(f"{Colors.RED}  ✗ Failed:{Colors.END} {failed}")
        print(f"{Colors.RED}  ⏱ Timeouts:{Colors.END} {timeouts}")
        print(f"{Colors.RED}  ⚠ Errors:{Colors.END} {errors}")
        print(f"{Colors.YELLOW}  ! No Tests:{Colors.END} {no_tests}")

        print(f"\n{Colors.BOLD}Performance:{Colors.END}")
        print(f"  Total Duration: {total_duration/1000:.2f}s")
        print(f"  Average Duration: {avg_duration:.2f}ms")

        # Find slowest test
        if self.results:
            slowest = max(self.results, key=lambda x: x.get("duration_ms", 0))
            print(f"  Slowest Test: {slowest['name']} ({slowest['duration_ms']/1000:.2f}s)")

        # Update report
        self.report["summary"] = {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "timeouts": timeouts,
            "errors": errors,
            "no_tests": no_tests,
            "total_duration_ms": total_duration,
            "average_duration_ms": avg_duration
        }

    def save_report(self, output_file: str = "test_performance_report.json"):
        """Save detailed report to JSON file"""
        self.report["tests"] = self.results

        output_path = Path("/home/user/TEST_AGENTS") / output_file
        with open(output_path, 'w') as f:
            json.dump(self.report, f, indent=2)

        print(f"\n{Colors.GREEN}[✓] Detailed report saved: {output_path}{Colors.END}")

    def run_all_tests(self):
        """Run all discovered tests"""
        self.print_header("TEST PERFORMANCE ANALYZER")
        print(f"{Colors.BOLD}Started:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Colors.BOLD}Working Directory:{Colors.END} /home/user/TEST_AGENTS\n")

        # Discover test scripts
        test_scripts = [
            ("MARKETING_TEAM/scripts/test_google_workspace_mcp.py", "Google Workspace MCP Connection"),
            ("MARKETING_TEAM/scripts/test_openai_connection.py", "OpenAI API Connection"),
            ("MARKETING_TEAM/scripts/test_perplexity_research.py", "Perplexity Research API"),
        ]

        print(f"{Colors.CYAN}Discovered {len(test_scripts)} test script(s){Colors.END}")

        # Run each test script
        for script_path, test_name in test_scripts:
            full_path = Path("/home/user/TEST_AGENTS") / script_path
            if full_path.exists():
                self.run_test_script(str(full_path), test_name)
            else:
                print(f"{Colors.YELLOW}[!] Skipped (not found): {script_path}{Colors.END}")

        # Run pytest smoke tests
        self.run_pytest_smoke_tests()

        # Analysis
        self.print_summary()
        self.analyze_bottlenecks()
        self.generate_recommendations()

        # Save report
        self.save_report()

        print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}Analysis Complete!{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.END}\n")

def main():
    """Main entry point"""
    analyzer = TestPerformanceAnalyzer()
    analyzer.run_all_tests()

if __name__ == "__main__":
    main()
