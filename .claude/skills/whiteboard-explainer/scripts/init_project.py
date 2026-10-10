#!/usr/bin/env python3
"""Create one organized whiteboard explainer project."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from whiteboard_lib import find_repo_root, project_output_root, slugify, write_json


DIRECTORIES = (
    "brief",
    "script",
    "storyboard",
    "audio/sfx",
    "keyframes",
    "seedance/requests",
    "seedance/clips",
    "composition/public",
    "composition/frames",
    "renders",
    "qa/video-intelligence",
    "logs",
)


def build_storyboard(title: str, slug: str) -> dict:
    return {
        "schema_version": 1,
        "project": {
            "slug": slug,
            "title": title,
            "aspect_ratio": "9:16",
            "width": 1080,
            "height": 1920,
            "fps": 30,
            "target_duration_seconds": 30,
        },
        "providers": {
            "seedance": {
                "task_type": "seedance-2-fast-less-restriction",
                "resolution": "720p",
                "stability_mode": "auto",
            },
            "elevenlabs": {
                "model_id": "eleven_multilingual_v2",
                "voice_id": "",
                "voice_name": "",
                "output_format": "mp3_44100_128",
                "speed": 1.0,
            },
        },
        "scenes": [
            {
                "id": "scene-001",
                "order": 1,
                "duration_seconds": 5,
                "narration": "Open with one surprising sentence that creates a clear knowledge gap.",
                "visual_goal": "A marker hand quickly reveals the central visual metaphor.",
                "transition": "cut",
                "seedance": {
                    "mode": "first_last_frames",
                    "prompt": (
                        "Overhead whiteboard shot. A natural hand with a black marker draws the "
                        "planned central symbol in confident strokes. Clean white surface, restrained "
                        "black line art, one blue accent, stable camera, consistent hand and marker. "
                        "No visible writing, labels, captions, logos, watermarks, or generated typography."
                    ),
                    "image_urls": [],
                    "reference_image_paths": [
                        "keyframes/scene-001-start.png",
                        "keyframes/scene-001-end.png",
                    ],
                    "video_urls": [],
                    "audio_urls": [],
                },
                "overlay": {
                    "headline": "THE HOOK",
                    "caption": "Replace this with the locked narration caption.",
                    "labels": [],
                    "accent_color": "#2563EB",
                },
            }
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_name", help="Human-readable project title")
    parser.add_argument("--repo-root", type=Path, help="TEST_AGENTS repository root")
    parser.add_argument("--output-root", type=Path, help="Override the canonical output root")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve() if args.repo_root else find_repo_root(Path.cwd())
    output_root = args.output_root.resolve() if args.output_root else project_output_root(repo_root)
    slug = slugify(args.project_name)
    project_path = output_root / slug
    if project_path.exists():
        raise SystemExit(f"Refusing to overwrite existing project: {project_path}")

    for relative in DIRECTORIES:
        (project_path / relative).mkdir(parents=True, exist_ok=False)

    created_at = datetime.now(timezone.utc).isoformat()
    write_json(
        project_path / "manifest.json",
        {
            "schema_version": 1,
            "project_slug": slug,
            "title": args.project_name,
            "created_at": created_at,
            "status": "initialized",
            "approvals": {
                "script": False,
                "storyboard": False,
                "voice": False,
                "cost": False,
                "preview": False,
            },
            "providers": {"video": "SeedDance 2", "voice": "ElevenLabs", "compositor": "HyperFrames"},
            "output_contract": "MARKETING_TEAM/outputs/videos/whiteboard-explainer/<project-slug>",
        },
    )
    write_json(
        project_path / "brief" / "brief.json",
        {
            "objective": "",
            "audience": "",
            "platform": "",
            "source_urls": [],
            "must_include": [],
            "must_avoid": [],
            "call_to_action": "",
        },
    )
    (project_path / "brief" / "source.txt").write_text(
        "Paste source material or research notes here.\n", encoding="utf-8"
    )
    (project_path / "script" / "SCRIPT.md").write_text(
        f"# {args.project_name}\n\n## Hook\n\n## Explanation\n\n## Payoff\n\n## Call to action\n",
        encoding="utf-8",
    )
    (project_path / "storyboard" / "STORYBOARD.md").write_text(
        "# Storyboard\n\nUse storyboard.json as the source of truth. Record creative rationale here.\n",
        encoding="utf-8",
    )
    write_json(project_path / "storyboard" / "storyboard.json", build_storyboard(args.project_name, slug))
    print(project_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

