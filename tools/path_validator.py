"""Resolve team paths and enforce shared workspace boundaries.

These helpers validate paths; they are not an operating-system sandbox.
"""
from __future__ import annotations

from pathlib import Path, PureWindowsPath
from typing import Any

from tools.workspace_registry import (
    REPO_ROOT, contained_path, get_team, load_registry, output_paths,
)


def _get_repo_root() -> Path:
    """Resolve independently of the caller's current directory."""
    return REPO_ROOT


def _portable_path(value: str) -> Path:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise ValueError("A nonempty file path is required")
    path = Path(value.replace("\\", "/"))
    if PureWindowsPath(value).drive and not path.is_absolute():
        raise ValueError("Foreign or drive-relative path is not supported")
    return path


OUTPUT_STRUCTURES = {
    name: {"base": Path(cfg["outputs"]).name,
           "subfolders": [Path(p).name for p in output_paths(name).values()]}
    for name, cfg in load_registry()["teams"].items()
}


def validate_save_path(path: str, team: str, create_missing_folders: bool = False) -> str:
    """Return a contained output path; reject unsafe paths instead of redirecting."""
    root = _get_repo_root()
    cfg = get_team(team, root)
    allowed = root / cfg["outputs"]
    candidate = _portable_path(path)
    if not candidate.is_absolute():
        if candidate.parts[0] == Path(cfg["root"]).name:
            candidate = root / candidate
        elif candidate.parts[0] == allowed.name:
            candidate = allowed.parent / candidate
        else:
            candidate = allowed / candidate
    resolved = contained_path(allowed, candidate)
    if resolved == allowed.resolve():
        raise ValueError("Expected a file beneath the output root")
    if create_missing_folders:
        resolved.parent.mkdir(parents=True, exist_ok=True)
        # Recheck after directory creation to catch ordinary link redirection.
        resolved = contained_path(allowed, resolved)
    return str(resolved)


def validate_read_path(path: str, team: str, search_folders: list[str] | None = None) -> str:
    """Read within a team; tracked configuration precedes local-memory fallback."""
    root = _get_repo_root()
    cfg = get_team(team, root)
    base = root / cfg["root"]
    candidate = _portable_path(path)
    if candidate.is_absolute():
        candidates = [contained_path(base, candidate)]
    elif candidate.parts[0] == Path(cfg["root"]).name:
        candidates = [contained_path(base, root / candidate)]
    else:
        folders = search_folders if search_folders is not None else ["config", "memory", "outputs", "tests", "tools", "docs"]
        candidates = []
        for folder in folders:
            search_root = contained_path(base, folder)
            value = base / candidate if candidate.parts[0] == folder else search_root / candidate
            candidates.append(contained_path(base, value))
    for candidate in candidates:
        # ROOT access is deliberate and reserved for the cross-team supervisor.
        if candidate.is_file():
            return str(candidate)
    raise FileNotFoundError(f"File not found within {base}: {path}; searched {candidates}")


def validate_cross_team_path(
    path: str, source_team: str, target_team: str, operation: str = "read", *,
    infrastructure: bool = False,
) -> dict[str, Any]:
    """Check a deliberate cross-team operation against shared access policy.

    Infrastructure writes require an explicit flag and exclude private memory,
    deliverables, and runtime-owned source instructions. Those changes require
    an owner-specific operation instead of a generic cross-team write.
    """
    result = {"allowed": False, "path": path, "source_team": source_team,
              "target_team": target_team, "operation": operation,
              "message": "", "errors": []}
    try:
        if operation not in {"read", "write"}:
            raise ValueError("Operation must be read or write")
        root = _get_repo_root()
        get_team(source_team, root)
        target = get_team(target_team, root)
        target_root = (root / target["root"]).resolve()
        candidate = _portable_path(path)
        if not candidate.is_absolute():
            candidate = root / candidate if candidate.parts[0] == Path(target["root"]).name else target_root / candidate
        resolved = contained_path(target_root, candidate)
        result["path"] = str(resolved)
        # ROOT must not provide a shortcut around a nested team's private scope.
        if target_team == "ROOT" and source_team != "ROOT":
            owner = get_team_from_path(str(resolved))
            if owner:
                return validate_cross_team_path(str(resolved), source_team, owner, operation,
                                                infrastructure=infrastructure)
        relative = resolved.relative_to(target_root)
        first = relative.parts[0] if relative.parts else ""
        policy = load_registry(root)["cross_team_access"]
        if source_team == target_team:
            result["allowed"] = True
        elif operation == "read":
            private = first == "memory" or first.startswith(".env") or first in {".mcp.json", ".claude.json"}
            allowed = policy["read_memory"] if private else policy["read_code"]
            result["allowed"] = source_team in allowed
        else:
            public = first in {"config", "tools", "scripts", "tests", "docs"}
            result["allowed"] = (infrastructure and source_team in policy["write_infrastructure"] and public)
        if not result["allowed"]:
            raise ValueError("Cross-team access is outside the permitted scope")
        result["message"] = "Allowed by workspace policy"
    except (ValueError, OSError) as exc:
        result["allowed"] = False
        result["message"] = str(exc)
        result["errors"] = [str(exc)]
    return result


def get_team_from_path(path: str) -> str | None:
    """Find the actual owning team after resolving the path."""
    root = _get_repo_root()
    candidate = _portable_path(path)
    try:
        resolved = contained_path(root, candidate)
    except ValueError:
        return None
    for name, cfg in load_registry(root)["teams"].items():
        if name != "ROOT" and resolved.is_relative_to((root / cfg["root"]).resolve()):
            return name
    return None
