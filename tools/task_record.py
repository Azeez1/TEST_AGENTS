"""Persist explicit task outcomes and artifact fingerprints outside OneDrive.

Check results are supplied by the caller; this is provenance bookkeeping, not
an independent verifier of the check's claim.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.workspace_registry import contained_path, discover_agents


def state_directory() -> Path:
    """Allow an explicit state root; otherwise use the machine's local cache."""
    fallback = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".cache"))) / "TEST_AGENTS/tasks"
    return Path(os.environ.get("TEST_AGENTS_STATE_DIR", str(fallback))).resolve()


def fingerprint(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def record_task(data: dict, *, root: Path = ROOT, state: Path | None = None) -> Path:
    """Create/update a task; validation requires passing checks and real files."""
    record = dict(data)
    task_id = record.get("task_id") or str(uuid.uuid4())
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", task_id):
        raise ValueError("Invalid task id")
    for key in ("objective", "team", "role", "runtime"):
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise ValueError(f"Missing {key}")
    sources = discover_agents(root)
    if record["role"] not in {p.stem for p in sources.get(record["team"], [])}:
        raise ValueError("Task owner must be a registered source role")
    status = record.get("status")
    if status not in {"running", "blocked", "completed", "validated", "failed"}:
        raise ValueError("Explicit task status required")
    checks = record.get("checks", [])
    if not isinstance(checks, list) or any(not isinstance(c, dict) or not c.get("name")
            or c.get("status") not in {"passed", "failed", "skipped"} for c in checks):
        raise ValueError("Checks require a name and passed/failed/skipped status")
    artifacts = []
    for value in record.get("artifacts", []):
        path = contained_path(root, value if isinstance(value, str) else value["path"])
        if not path.is_file():
            raise ValueError(f"Artifact does not exist: {path}")
        artifacts.append({"path": path.relative_to(root).as_posix(), "sha256": fingerprint(path)})
    if status == "validated" and (not artifacts or not checks or any(c["status"] != "passed" for c in checks)):
        raise ValueError("Validated requires artifacts and exclusively passing checks")
    if status in {"running", "blocked"} and not record.get("next_step"):
        raise ValueError("Active or blocked tasks require a next step")
    state = (state or state_directory()).resolve()
    state.mkdir(parents=True, exist_ok=True)
    destination = contained_path(state, f"{task_id}.json")
    previous = json.loads(destination.read_text(encoding="utf-8")) if destination.exists() else {}
    now = datetime.now(timezone.utc).isoformat()
    record.update(schema="test-agents/task/v1", task_id=task_id,
                  created_at=previous.get("created_at", now), updated_at=now,
                  artifacts=artifacts, checks=checks,
                  cost_usd=record.get("cost_usd"), duration_seconds=record.get("duration_seconds"))
    descriptor, temporary = tempfile.mkstemp(prefix=".task-", dir=state)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(record, handle, indent=2)
            handle.write("\n")
        os.replace(temporary, destination)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return destination


def resume_task(task_id: str, *, root: Path = ROOT, state: Path | None = None) -> dict:
    """Return saved context and flag missing or changed artifacts."""
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", task_id):
        raise ValueError("Invalid task id")
    record = json.loads(contained_path(state or state_directory(), f"{task_id}.json").read_text(encoding="utf-8"))
    changed = []
    for artifact in record.get("artifacts", []):
        path = contained_path(root, artifact["path"])
        if not path.is_file() or fingerprint(path) != artifact["sha256"]:
            changed.append(artifact["path"])
    return {"record": record, "changed_artifacts": changed,
            "validation_current": record["status"] == "validated" and not changed}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("record").add_argument("input_json", type=Path)
    commands.add_parser("resume").add_argument("task_id")
    args = parser.parse_args()
    if args.command == "record":
        print(record_task(json.loads(args.input_json.read_text(encoding="utf-8"))))
    else:
        print(json.dumps(resume_task(args.task_id), indent=2))


if __name__ == "__main__":
    main()
