"""Workspace discovery shared by Claude and Codex; local memory is optional."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.workspace_registry import REPO_ROOT, discover_agents, get_team, load_registry


def _get_repo_root() -> Path:
    """Return the source repository regardless of cwd or checkout directory name."""
    return REPO_ROOT


def _workspace_structure() -> dict[str, dict[str, Any]]:
    registry = load_registry()
    sources = discover_agents()
    return {name: {
        **cfg, "agents": len(sources[name]),
        "agents_list": [path.stem for path in sources[name]],
        "folders": [".codex/agents" if cfg["runtime"] == "codex" else ".claude/agents"],
        "memory_files": [],
    } for name, cfg in registry["teams"].items()}


WORKSPACE_STRUCTURE = _workspace_structure()


def validate_workspace(agent_name: str, expected_team: str) -> dict[str, Any]:
    """Validate a real source agent; output/state directories are created on demand."""
    root = _get_repo_root()
    errors = []
    try:
        cfg = get_team(expected_team, root)
    except ValueError as exc:
        return {"valid": False, "errors": [str(exc)], "message": str(exc), "suggestions": []}
    team_path = root / cfg["root"]
    agent = root / cfg["agent_dir"] / f"{agent_name}.md"
    # Avoid accepting a traversal-shaped agent name.
    exists = agent_name in {p.stem for p in discover_agents(root)[expected_team]}
    if not exists:
        errors.append(f"Agent {agent_name!r} is not registered in {expected_team}")
    if not team_path.is_dir():
        errors.append(f"Team folder missing: {team_path}")
    return {
        "valid": not errors, "agent_name": agent_name, "expected_team": expected_team,
        "current_directory": str(Path.cwd()), "repo_root": str(root),
        "team_path": str(team_path), "workspace_path": str(team_path),
        "agent_exists": exists and agent.is_file(), "team_folders_exist": team_path.is_dir(),
        "message": "Workspace valid" if not errors else "Workspace validation failed",
        "errors": errors, "suggestions": [],
    }


def get_absolute_paths(team: str) -> dict[str, str]:
    """Return safe paths without requiring private local configuration."""
    root = _get_repo_root()
    cfg = get_team(team, root)
    base = root / cfg["root"]
    return {"repo_root": str(root), "team_root": str(base),
            "agents": str(root / cfg["agent_dir"]), "outputs": str(root / cfg["outputs"]),
            **{key: str(base / key) for key in ("config", "memory", "tools", "docs", "tests")}}


def ensure_team_context(team: str) -> dict[str, Any]:
    """Report cwd context using resolved containment, not substring matching."""
    paths = get_absolute_paths(team)
    current = Path.cwd().resolve()
    expected = Path(paths["team_root"]).resolve()
    correct = current == _get_repo_root() or current.is_relative_to(expected)
    return {"correct_context": correct, "current_directory": str(current),
            "expected_directory": str(expected), "team": team,
            "message": "Context valid" if correct else "Use the team's absolute paths",
            "navigation_command": "" if correct else f'cd "{expected}"'}


def get_team_info(team: str) -> dict[str, Any]:
    """Return current team metadata and discovered agent names."""
    get_team(team)
    return _workspace_structure()[team].copy()


def list_all_workspaces() -> dict[str, list[str]]:
    """Return the current roster without maintained count snapshots."""
    return {team: [p.stem for p in paths] for team, paths in discover_agents().items()}


def list_all_agents() -> dict[str, list[str]]:
    """Backward-compatible public name for roster discovery."""
    return list_all_workspaces()
