"""Content-addressed cache for validated analysis results."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


CACHE_ROOT = Path.home() / ".codex" / "cache" / "video-intelligence"


def make_cache_key(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def load_cache(key: str, root: Path = CACHE_ROOT) -> dict[str, Any] | None:
    path = root / f"{key}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def save_cache(key: str, data: dict[str, Any], root: Path = CACHE_ROOT) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{key}.json"
    temporary = root / f".{key}.tmp"
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(path)
    return path
