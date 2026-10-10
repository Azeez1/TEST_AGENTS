#!/usr/bin/env python3
"""Create a dry-run ElevenLabs narration request from the locked storyboard."""

from __future__ import annotations

import argparse
from pathlib import Path

from whiteboard_lib import load_storyboard, validate_storyboard, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_path", type=Path)
    args = parser.parse_args()
    project_path = args.project_path.resolve()
    storyboard = load_storyboard(project_path)
    errors, warnings = validate_storyboard(storyboard)
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    config = storyboard["providers"]["elevenlabs"]
    text = "\n\n".join(
        scene["narration"].strip()
        for scene in sorted(storyboard["scenes"], key=lambda item: item["order"])
    )
    request = {
        "tool": "mcp__elevenlabs__text_to_speech",
        "approved_for_execution": False,
        "cost_quote_required": True,
        "arguments": {
            "text": text,
            "voice_id": config.get("voice_id") or None,
            "voice_name": config.get("voice_name") or None,
            "model_id": config["model_id"],
            "output_format": config.get("output_format", "mp3_44100_128"),
            "speed": config.get("speed", 1.0),
            "output_directory": str(project_path / "audio"),
        },
        "character_count": len(text),
        "expected_output": "audio/narration.mp3",
    }
    write_json(project_path / "audio" / "elevenlabs-request.json", request)
    print(f"Narration plan contains {len(text)} characters. No API call was made.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

