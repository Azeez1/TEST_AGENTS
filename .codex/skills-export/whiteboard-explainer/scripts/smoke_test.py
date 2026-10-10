#!/usr/bin/env python3
"""Run a no-network, no-cost smoke test of the project workflow."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def run(*args: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != expect:
        raise AssertionError(
            f"Expected exit {expect}, got {result.returncode}: {' '.join(args)}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="whiteboard-explainer-") as temp:
        repo = Path(temp) / "TEST_AGENTS"
        (repo / "MARKETING_TEAM" / "outputs" / "videos").mkdir(parents=True)
        (repo / "AGENTS.md").write_text("test\n", encoding="utf-8")
        init = run(
            str(SCRIPT_DIR / "init_project.py"),
            "Smoke Test",
            "--repo-root",
            str(repo),
        )
        project = Path(init.stdout.strip())
        assert project.is_dir()
        run(str(SCRIPT_DIR / "validate_project.py"), str(project))
        run(str(SCRIPT_DIR / "plan_seedance.py"), str(project))
        run(str(SCRIPT_DIR / "plan_narration.py"), str(project))
        run(str(SCRIPT_DIR / "build_composition.py"), str(project))

        cost_plan = json.loads((project / "seedance" / "cost-plan.json").read_text(encoding="utf-8"))
        assert cost_plan["dry_run_only"] is True
        assert cost_plan["estimated_seedance_cost_usd"] == 0.88
        assert (project / "audio" / "elevenlabs-request.json").is_file()
        assert (project / "composition" / "index.html").is_file()

        run(
            str(SCRIPT_DIR / "init_project.py"),
            "Smoke Test",
            "--repo-root",
            str(repo),
            expect=1,
        )
    print("Smoke test passed; no provider API calls were made.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

