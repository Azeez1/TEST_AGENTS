#!/usr/bin/env python3
"""Block Codex from modifying Claude-owned infrastructure."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

PROTECTED_FILE_NAMES = {
    "claude.md",
    ".mcp.json",
    ".claude.json",
    ".claude.json.full-backup",
}

MUTATING_SHELL_PATTERNS = re.compile(
    r"(?i)\b("
    r"set-content|add-content|out-file|new-item|remove-item|move-item|copy-item|"
    r"clear-content|rename-item|ni|rm|del|erase|mv|cp|ren|mkdir|rmdir|"
    r"apply_patch|python|node|npm|npx|powershell|cmd"
    r")\b|>|>>"
)


def normalize_path(value: str) -> Path | None:
    if not value or "\x00" in value:
        return None
    expanded = value.strip().strip('"').strip("'")
    if not expanded:
        return None
    path = Path(expanded)
    if not path.is_absolute():
        path = ROOT / path
    try:
        return path.resolve(strict=False)
    except OSError:
        return None


def is_protected_path(path: Path) -> bool:
    parts = [part.lower() for part in path.parts]
    name = path.name.lower()
    if ".claude" in parts:
        return True
    if name in PROTECTED_FILE_NAMES:
        return True
    return False


def iter_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        output: list[str] = []
        for item in value.values():
            output.extend(iter_strings(item))
        return output
    if isinstance(value, list):
        output = []
        for item in value:
            output.extend(iter_strings(item))
        return output
    return []


def candidate_paths(tool_input: dict[str, Any]) -> list[Path]:
    candidates: list[Path] = []
    path_keys = {
        "path",
        "file_path",
        "filepath",
        "target",
        "target_path",
        "source",
        "source_path",
        "notebook_path",
    }
    for key, value in tool_input.items():
        if key.lower() in path_keys and isinstance(value, str):
            path = normalize_path(value)
            if path:
                candidates.append(path)
    return candidates


def command_mentions_protected_path(command: str) -> bool:
    lowered = command.lower()
    direct_tokens = (
        ".claude",
        "claude.md",
        ".mcp.json",
        ".claude.json",
    )
    return any(token in lowered for token in direct_tokens)


def block(message: str) -> None:
    print(json.dumps({"error": message}))
    sys.exit(1)


def main() -> None:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = str(payload.get("tool_name") or payload.get("tool") or "")
    raw_tool_input = payload.get("tool_input") or payload.get("input") or {}
    tool_input = raw_tool_input
    if not isinstance(tool_input, dict):
        tool_input = {}

    write_like_tools = {
        "write",
        "edit",
        "multiedit",
        "notebookedit",
        "apply_patch",
        "functions.apply_patch",
    }
    shell_like_tools = {
        "bash",
        "shell",
        "shell_command",
        "functions.shell_command",
        "powershell",
    }

    normalized_tool = tool_name.lower()

    if normalized_tool in write_like_tools or any(key in normalized_tool for key in ("write", "edit", "patch")):
        if isinstance(raw_tool_input, str) and command_mentions_protected_path(raw_tool_input):
            block(
                "Blocked by Codex Claude-boundary gate: patch/edit payload targets "
                "Claude-owned infrastructure. Protected paths include `.claude/**`, "
                "`CLAUDE.md`, `.mcp.json`, and `.claude.json`."
            )

        for path in candidate_paths(tool_input):
            if is_protected_path(path):
                block(
                    "Blocked by Codex Claude-boundary gate: Codex cannot modify "
                    f"Claude-owned path `{path}`. Ask explicitly if you want this boundary changed."
                )

        for value in iter_strings(tool_input):
            path = normalize_path(value)
            if path and is_protected_path(path):
                block(
                    "Blocked by Codex Claude-boundary gate: Codex cannot modify "
                    f"Claude-owned path `{path}`."
                )

    if normalized_tool in shell_like_tools or "shell" in normalized_tool or "bash" in normalized_tool:
        command = str(tool_input.get("command") or "")
        if command and command_mentions_protected_path(command) and MUTATING_SHELL_PATTERNS.search(command):
            block(
                "Blocked by Codex Claude-boundary gate: shell command appears to mutate "
                "Claude-owned infrastructure. Protected paths include `.claude/**`, "
                "`CLAUDE.md`, `.mcp.json`, and `.claude.json`."
            )

    sys.exit(0)


if __name__ == "__main__":
    main()
