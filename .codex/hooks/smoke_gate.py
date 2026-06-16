#!/usr/bin/env python3
"""Local smoke tests for Codex hook gates."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / ".codex" / "hooks" / "enforcement_gate.py"
BOUNDARY = ROOT / ".codex" / "hooks" / "claude_boundary_gate.py"
STATE_DIR = Path.home() / ".codex" / "test_agents_hooks"


def run(script: Path, payload: dict, expected: int) -> None:
    result = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        timeout=5,
    )
    print(f"{script.name}: {payload['tool_name']} -> {result.returncode}")
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())
    if result.returncode != expected:
        raise SystemExit(f"expected {expected}, got {result.returncode}")


def main() -> None:
    run(GATE, {"tool_name": "functions.shell_command", "tool_input": {"command": "Get-ChildItem"}}, 0)
    run(GATE, {"tool_name": "functions.shell_command", "tool_input": {"command": "Remove-Item -Recurse -Force tmp"}}, 1)
    run(GATE, {"tool_name": "mcp__google_workspace__send_gmail_message", "tool_input": {"to": "p@example.invalid", "subject": "", "body": "hello"}}, 1)
    run(GATE, {"tool_name": "mcp__google_workspace__create_drive_file", "tool_input": {"file_name": "valuation_deck.pdf", "content": "DCF valuation and investor deck"}}, 1)
    spend_file = STATE_DIR / f"api-spend-{date.today().isoformat()}.total"
    old_spend = spend_file.read_text(encoding="utf-8") if spend_file.exists() else None
    try:
        spend_file.parent.mkdir(parents=True, exist_ok=True)
        spend_file.write_text("49", encoding="utf-8")
        run(GATE, {"tool_name": "mcp__marketing_tools__generate_sora_video", "tool_input": {"filename": "smoke", "prompt": "short test"}}, 1)
    finally:
        if old_spend is None:
            spend_file.unlink(missing_ok=True)
        else:
            spend_file.write_text(old_spend, encoding="utf-8")
    run(BOUNDARY, {"tool_name": "functions.apply_patch", "tool_input": {"file_path": ".codex/AGENTS.md"}}, 0)
    run(BOUNDARY, {"tool_name": "functions.apply_patch", "tool_input": {"file_path": ".claude/skills/foo/SKILL.md"}}, 1)


if __name__ == "__main__":
    main()
