"""Shared, nonsecret workspace contracts for Claude and Codex tooling."""
from __future__ import annotations

import json
from pathlib import Path, PureWindowsPath
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "config" / "workspaces.json"


def contained_path(root: Path, value: str | Path) -> Path:
    """Resolve a path and reject traversal, foreign roots, and symlink escapes."""
    raw = str(value)
    if not raw.strip() or "\x00" in raw:
        raise ValueError("A nonempty path without null bytes is required")
    base = root.resolve()
    path = Path(raw.replace("\\", "/"))
    if PureWindowsPath(raw).drive and not path.is_absolute():
        raise ValueError("Foreign or drive-relative path is not supported")
    path = (path if path.is_absolute() else base / path).resolve()
    if not path.is_relative_to(base):
        raise ValueError(f"Path escapes allowed root: {base}")
    return path


def load_registry(root: Path = REPO_ROOT) -> dict[str, Any]:
    """Load safe defaults; agent names are discovered from canonical sources."""
    data = json.loads((root / "config/workspaces.json").read_text(encoding="utf-8"))
    if data.get("schema") != "test-agents/workspaces/v1":
        raise ValueError("Unsupported workspace registry schema")
    for name, team in data["teams"].items():
        if not name or team["runtime"] not in {"claude", "codex"}:
            raise ValueError(f"Invalid workspace: {name}")
        for key in ("root", "agent_dir", "outputs"):
            contained_path(root, team[key])
    return data


def get_team(team: str, root: Path = REPO_ROOT) -> dict[str, Any]:
    """Return a workspace definition and reject unknown names."""
    teams = load_registry(root)["teams"]
    if team not in teams:
        raise ValueError(f"Unknown team: {team}")
    return teams[team]


def discover_agents(root: Path = REPO_ROOT) -> dict[str, list[Path]]:
    """Discover source agents in every configured runtime, without fixed counts."""
    return {
        name: sorted((root / cfg["agent_dir"]).glob("*.md"))
        for name, cfg in load_registry(root)["teams"].items()
    }


def output_paths(team: str, root: Path = REPO_ROOT) -> dict[str, str]:
    """Read tracked defaults first, with a legacy local-memory fallback."""
    cfg = get_team(team, root)
    base = root / cfg["root"]
    for folder in ("config", "memory"):
        path = base / folder / "output_paths.json"
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            result = {key: value for key, value in data.items()
                      if isinstance(value, str) and (value == cfg["outputs"] or value.startswith(cfg["outputs"] + "/"))}
            for value in result.values():
                contained_path(root / cfg["outputs"], root / value)
            return result or {"default": cfg["outputs"]}
    return {"default": cfg["outputs"]}
