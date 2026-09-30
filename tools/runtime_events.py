"""Normalize Claude/Codex hook payloads without executing their contents."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


def strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for child in value.values() for text in strings(child)]
    if isinstance(value, list):
        return [text for child in value for text in strings(child)]
    return []


@dataclass(frozen=True)
class ToolEvent:
    name: str
    raw_input: Any
    arguments: dict[str, Any]
    command: str


def parse_event(payload: Any) -> ToolEvent:
    """Accept native names, namespaced names and JSON-encoded arguments."""
    if not isinstance(payload, dict):
        raise ValueError("Hook event must be an object")
    name = str(payload.get("tool_name") or payload.get("tool") or payload.get("name") or "")
    raw = next((payload[k] for k in ("tool_input", "input", "arguments")
                if k in payload and payload[k] is not None), {})
    if isinstance(raw, str):
        try:
            decoded = json.loads(raw)
            if isinstance(decoded, dict):
                raw = decoded
        except json.JSONDecodeError:
            pass
    arguments = raw if isinstance(raw, dict) else {}
    command = arguments.get("cmd") or arguments.get("command") or arguments.get("code")
    if isinstance(command, list):
        command = " ".join(strings(command))
    if not isinstance(command, str):
        command = " ".join(strings(raw))
    return ToolEvent(name, raw, arguments, command)


def is_shell_tool(name: str) -> bool:
    normalized = name.lower().replace("-", "_")
    return any(part in normalized for part in ("shell", "bash", "command", "exec"))


def is_write_tool(name: str) -> bool:
    return any(part in name.lower() for part in ("write", "edit", "patch", "notebook"))
