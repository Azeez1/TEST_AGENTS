"""Secret discovery and redaction helpers."""

from __future__ import annotations

import os
import re
from pathlib import Path


SECRET_PATTERNS = (
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"sk-[0-9A-Za-z_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key\s*[=:]\s*)[^\s,;]+"),
)


def redact(value: object) -> str:
    """Remove recognizable credentials from diagnostic text."""

    text = str(value)
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(lambda match: (match.group(1) if match.lastindex else "") + "[REDACTED]", text)
    return text


def _parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def candidate_env_files(explicit: str | None = None) -> list[Path]:
    """Return explicit and conventional gitignored secret-file candidates."""

    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    current = Path.cwd().resolve()
    for parent in (current, *current.parents):
        candidates.append(parent / ".codex" / "secrets.local.env")
    candidates.append(Path.home() / ".codex" / "secrets.local.env")
    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate.resolve(strict=False)).lower()
        if key not in seen:
            seen.add(key)
            unique.append(candidate)
    return unique


def load_gemini_api_key(explicit_env_file: str | None = None) -> tuple[str, str]:
    """Load GEMINI_API_KEY without exposing its value."""

    existing = os.getenv("GEMINI_API_KEY", "").strip()
    if existing:
        return existing, "process_environment"
    for candidate in candidate_env_files(explicit_env_file):
        if not candidate.is_file():
            continue
        value = _parse_env_file(candidate).get("GEMINI_API_KEY", "").strip()
        if value:
            os.environ["GEMINI_API_KEY"] = value
            return value, str(candidate.resolve())
    raise RuntimeError(
        "GEMINI_API_KEY is unavailable. Set it in the process environment or pass --env-file."
    )

