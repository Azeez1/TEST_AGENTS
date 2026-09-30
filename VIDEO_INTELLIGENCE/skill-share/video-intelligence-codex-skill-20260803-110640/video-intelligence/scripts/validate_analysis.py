#!/usr/bin/env python
"""Validate a video-intelligence analysis JSON artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from video_intelligence.schema import validate_analysis


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("analysis", help="Path to analysis.json")
    args = parser.parse_args()
    path = Path(args.analysis).expanduser().resolve()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    duration = None
    manifest_path = path.parent / "manifest.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            duration = float(manifest.get("source", {}).get("duration_seconds") or 0) or None
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            duration = None
    errors = validate_analysis(data, duration)
    if errors:
        print("INVALID:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"VALID: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
