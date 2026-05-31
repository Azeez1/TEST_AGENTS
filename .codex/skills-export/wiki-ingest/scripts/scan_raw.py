#!/usr/bin/env python3
"""
Scan the raw/ folder and report files available for ingestion.
Tracks which files have already been processed to avoid duplicates.

Usage:
    python scan_raw.py [--vault PATH] [--show-processed]

Output: JSON list of files with metadata (path, size, modified, processed status)
"""

import sys
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

DEFAULT_VAULT = r"C:\Users\sabaa\OneDrive\Desktop\MEMORY\VAULT"
TRACKER_FILE = "_processed.json"


def get_file_hash(filepath: str) -> str:
    """Get MD5 hash of file contents for change detection."""
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_tracker(vault_path: str) -> dict:
    """Load the processed files tracker."""
    tracker_path = os.path.join(vault_path, "raw", TRACKER_FILE)
    if os.path.exists(tracker_path):
        with open(tracker_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_tracker(vault_path: str, tracker: dict):
    """Save the processed files tracker."""
    tracker_path = os.path.join(vault_path, "raw", TRACKER_FILE)
    with open(tracker_path, "w", encoding="utf-8") as f:
        json.dump(tracker, f, indent=2, ensure_ascii=False)


def scan_raw(vault_path: str, show_processed: bool = False) -> list:
    """Scan raw/ folder and return file metadata."""
    raw_dir = os.path.join(vault_path, "raw")
    tracker = load_tracker(vault_path)

    files = []
    supported_extensions = {".md", ".txt", ".html", ".json", ".csv", ".pdf"}

    for root, dirs, filenames in os.walk(raw_dir):
        # Skip hidden dirs and tracker file
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in sorted(filenames):
            if fname.startswith("_") or fname.startswith("."):
                continue
            ext = os.path.splitext(fname)[1].lower()
            if ext not in supported_extensions:
                continue

            filepath = os.path.join(root, fname)
            rel_path = os.path.relpath(filepath, raw_dir)
            stat = os.stat(filepath)
            file_hash = get_file_hash(filepath)

            is_processed = rel_path in tracker
            has_changed = is_processed and tracker[rel_path].get("hash") != file_hash

            if not show_processed and is_processed and not has_changed:
                continue

            files.append({
                "path": filepath,
                "relative_path": rel_path,
                "name": fname,
                "extension": ext,
                "size_bytes": stat.st_size,
                "size_kb": round(stat.st_size / 1024, 1),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "status": "changed" if has_changed else ("processed" if is_processed else "new"),
                "hash": file_hash,
            })

    return files


def mark_processed(vault_path: str, rel_path: str, file_hash: str, article_path: str):
    """Mark a file as processed in the tracker."""
    tracker = load_tracker(vault_path)
    tracker[rel_path] = {
        "hash": file_hash,
        "processed_at": datetime.now().isoformat(),
        "article_path": article_path,
    }
    save_tracker(vault_path, tracker)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Scan raw/ folder for ingestion")
    parser.add_argument("--vault", default=DEFAULT_VAULT, help="Vault path")
    parser.add_argument("--show-processed", action="store_true", help="Include already-processed files")
    args = parser.parse_args()

    files = scan_raw(args.vault, show_processed=args.show_processed)

    new_count = sum(1 for f in files if f["status"] == "new")
    changed_count = sum(1 for f in files if f["status"] == "changed")

    print(f"Found {len(files)} file(s): {new_count} new, {changed_count} changed", file=sys.stderr)

    print(json.dumps(files, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
