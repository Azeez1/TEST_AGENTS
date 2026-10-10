"""Capture and verify selected source citations without executing repo code."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

SCHEMA = "eli5/source-evidence/v1"
MAX_BYTES = 2_000_000
MAX_LINES = 160
SENSITIVE_NAMES = {"credentials.json", "secrets.json", "id_rsa", "id_ed25519",
                   "token.json", "token.pickle", ".npmrc", ".pypirc"}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".pickle"}


def selected_file(root: Path, name: str) -> Path:
    """Reject traversal, symlink escapes, and common credential locations."""
    if not name or Path(name).is_absolute() or re.match(r"^[A-Za-z]:", name):
        raise ValueError("Use a repository-relative file path.")
    parts = Path(name.replace("\\", "/")).parts
    if ".." in parts:
        raise ValueError("Parent traversal is not allowed.")
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Selected file escapes the repository.")
    resolved_parts = path.relative_to(root.resolve()).parts
    if any(p.lower() in {".git", ".ssh"} for p in (*parts, *resolved_parts)):
        raise ValueError("Metadata/credential directories are excluded.")
    if path.name.lower().startswith(".env") or path.name.lower() in SENSITIVE_NAMES:
        raise ValueError("Common credential files are excluded.")
    if path.suffix.lower() in SENSITIVE_SUFFIXES:
        raise ValueError("Credential/binary file types are excluded.")
    return path


def read_source(path: Path) -> tuple[str, list[str]]:
    """Read a bounded UTF-8 file and hash exactly the bytes that were read."""
    with path.open("rb") as handle:
        data = handle.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES or b"\x00" in data:
        raise ValueError("Select a text source smaller than 2 MB.")
    return hashlib.sha256(data).hexdigest(), data.decode("utf-8-sig").splitlines()


def capture(root: Path, references: list[str]) -> dict:
    """Build a citation ledger from explicit file:start:end references."""
    root = root.resolve()
    if not root.is_dir() or not references:
        raise ValueError("An existing repository and at least one reference are required.")
    records = []
    for index, ref in enumerate(references, 1):
        match = re.fullmatch(r"(.+):(\d+):(\d+)", ref)
        if not match:
            raise ValueError("Reference must be relative/path:start:end.")
        name, start_text, end_text = match.groups()
        start, end = int(start_text), int(end_text)
        path = selected_file(root, name)
        digest, lines = read_source(path)
        if start < 1 or end < start or end > len(lines) or end - start + 1 > MAX_LINES:
            raise ValueError("Invalid line range or excerpt longer than 160 lines.")
        records.append({"id": f"E{index}", "path": path.relative_to(root).as_posix(),
                        "start": start, "end": end, "sha256": digest,
                        "excerpt": "\n".join(lines[start - 1:end])})
    return {"schema": SCHEMA, "captured_at": datetime.now(timezone.utc).isoformat(),
            "method": "static source inspection; code was not executed", "sources": records}


def verify(root: Path, document: dict) -> list[dict]:
    """Check source bytes and excerpts; no claim of semantic verification."""
    if not isinstance(document, dict) or document.get("schema") != SCHEMA or not isinstance(document.get("sources"), list) or not document["sources"]:
        raise ValueError("Invalid or empty evidence document.")
    results = []
    for item in document["sources"]:
        if not isinstance(item, dict):
            results.append({"id": "?", "path": "?", "status": "blocked_or_invalid"})
            continue
        status = "verified"
        try:
            path = selected_file(root.resolve(), item["path"])
            digest, lines = read_source(path)
            start, end = item["start"], item["end"]
            if not isinstance(start, int) or not isinstance(end, int) or not 1 <= start <= end <= len(lines):
                status = "invalid_range"
            elif digest != item["sha256"]:
                status = "changed"
            elif "\n".join(lines[start - 1:end]) != item["excerpt"]:
                status = "excerpt_mismatch"
        except FileNotFoundError:
            status = "missing"
        except (OSError, ValueError, KeyError, TypeError):
            status = "blocked_or_invalid"
        results.append({"id": item.get("id", "?"), "path": item.get("path", "?"), "status": status})
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--ref", action="append", default=[])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    try:
        if args.verify:
            if args.ref or args.output:
                raise ValueError("--verify cannot be combined with --ref or --output.")
            result = verify(args.root, json.loads(args.verify.read_text(encoding="utf-8")))
            print(json.dumps({"results": result}, indent=2))
            raise SystemExit(0 if all(r["status"] == "verified" for r in result) else 1)
        if not args.output:
            raise ValueError("--output is required for capture.")
        document = capture(args.root, args.ref)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as handle:
            json.dump(document, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        print(f"Captured {len(document['sources'])} references in {args.output}")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Evidence check failed: {exc}\n")


if __name__ == "__main__":
    main()
