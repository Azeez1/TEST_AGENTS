"""One entry point for portable checks, with optional tests and local diagnostics."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tests", action="store_true", help="Also run the offline root tests with coverage")
    parser.add_argument("--local", action="store_true", help="Include legacy machine-specific diagnostics")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    commands = [
        ("declaration_references", ["tools/lint_agent_declarations.py", "--json"]),
        ("content_drift", ["tools/check_codex_drift.py", "--json"]),
        ("reproducible_routing_export", ["scripts/export_codex_layer.py", "--agents-only", "--check"]),
        ("workflow_contracts", ["tools/evaluate_workflows.py"]),
    ]
    if args.tests:
        commands.append(("offline_behavior", ["-m", "pytest", "tests/", "--cov", "--cov-report=term", "-q"]))
    if args.local:
        commands.append(("legacy_local_diagnostics", ["tools/verify_system.py", "--json"]))
    checks = []
    for name, command in commands:
        result = subprocess.run([sys.executable, *command], cwd=ROOT, capture_output=True,
                                text=True, encoding="utf-8", errors="replace")
        output = result.stdout.strip()
        try:
            details = json.loads(output)
        except ValueError:
            details = output
        checks.append({"name": name, "status": "passed" if result.returncode == 0 else "failed",
                       "exit_code": result.returncode, "details": details, "stderr": result.stderr.strip()})
    failed = [c for c in checks if c["status"] == "failed"]
    report = {"ok": not failed, "checks": checks,
              "unverified": ["Live connector authentication and callability", "Live hook dispatch by the desktop runtime",
                             "End-to-end model quality, latency and cost", "Third-party applications outside the core"]}
    print(json.dumps(report, indent=2))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
