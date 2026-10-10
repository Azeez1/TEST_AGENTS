#!/usr/bin/env python3
"""Validate a whiteboard explainer project before paid generation."""

from __future__ import annotations

import argparse
from pathlib import Path

from whiteboard_lib import load_storyboard, validate_storyboard


REQUIRED_DIRECTORIES = (
    "brief",
    "script",
    "storyboard",
    "audio",
    "keyframes",
    "seedance/requests",
    "seedance/clips",
    "composition",
    "renders",
    "qa",
    "logs",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_path", type=Path)
    args = parser.parse_args()
    project_path = args.project_path.resolve()

    errors = [
        f"Missing directory: {relative}"
        for relative in REQUIRED_DIRECTORIES
        if not (project_path / relative).is_dir()
    ]
    try:
        storyboard = load_storyboard(project_path)
        schema_errors, warnings = validate_storyboard(storyboard)
        errors.extend(schema_errors)
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
        warnings = []

    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Validation failed with {len(errors)} error(s).")
        return 1
    print("Project validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

