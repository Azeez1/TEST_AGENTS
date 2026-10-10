#!/usr/bin/env python3
"""Create dry-run SeedDance request manifests and a cost preview."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from whiteboard_lib import load_storyboard, validate_storyboard, write_json


PRICE_PER_SECOND = {
    "seedance-2": {"480p": 0.10, "720p": 0.20, "1080p": 0.50},
    "seedance-2-fast": {"480p": 0.08, "720p": 0.16},
    "seedance-2-mini": {"480p": 0.07, "720p": 0.14},
    "seedance-2-less-restriction": {"480p": 0.11, "720p": 0.22, "1080p": 0.55},
    "seedance-2-fast-less-restriction": {"480p": 0.088, "720p": 0.176},
    "seedance-2-mini-less-restriction": {"480p": 0.077, "720p": 0.154},
}


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

    project = storyboard["project"]
    seedance_defaults = storyboard["providers"]["seedance"]
    task_type = seedance_defaults["task_type"]
    resolution = seedance_defaults["resolution"]
    price_per_second = PRICE_PER_SECOND[task_type][resolution]
    requests_dir = project_path / "seedance" / "requests"
    total_seconds = 0
    total_cost = 0.0
    scene_summaries = []

    for scene in sorted(storyboard["scenes"], key=lambda item: item["order"]):
        scene_id = scene["id"]
        duration = scene["duration_seconds"]
        scene_cost = round(duration * price_per_second, 4)
        total_seconds += duration
        total_cost += scene_cost
        spec = scene["seedance"]
        local_refs = spec.get("reference_image_paths", [])
        ready = not local_refs or bool(spec.get("image_urls"))
        request = {
            "tool": "generate_seedance_video",
            "approved_for_execution": False,
            "ready_for_execution": ready,
            "blocked_reason": (
                None if ready else "Upload local keyframes and populate image_urls before execution."
            ),
            "arguments": {
                "prompt": spec["prompt"],
                "duration": duration,
                "aspect_ratio": project["aspect_ratio"],
                "filename": f"whiteboard-explainer/{project['slug']}/seedance/clips/{scene_id}.mp4",
                "image_urls": spec.get("image_urls", []),
                "video_urls": spec.get("video_urls", []),
                "audio_urls": spec.get("audio_urls", []),
                "task_type": task_type,
                "mode": spec["mode"],
                "resolution": resolution,
                "stability_mode": seedance_defaults.get("stability_mode", "auto"),
            },
            "local_reference_image_paths": local_refs,
            "estimated_cost_usd": scene_cost,
        }
        write_json(requests_dir / f"{scene_id}.json", request)
        scene_summaries.append(
            {
                "scene_id": scene_id,
                "duration_seconds": duration,
                "estimated_cost_usd": scene_cost,
                "ready_for_execution": ready,
            }
        )

    plan = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dry_run_only": True,
        "approval_required": True,
        "task_type": task_type,
        "resolution": resolution,
        "price_per_second_usd": price_per_second,
        "pricing_source": "TEST_AGENTS MARKETING_TEAM/tools/mcp_server.py snapshot",
        "pricing_must_be_reconfirmed_before_execution": True,
        "total_generated_seconds": total_seconds,
        "estimated_seedance_cost_usd": round(total_cost, 2),
        "excludes": ["ElevenLabs usage", "reference-video input surcharges", "retries", "alternate takes"],
        "scenes": scene_summaries,
    }
    write_json(project_path / "seedance" / "cost-plan.json", plan)
    print(f"Planned {len(scene_summaries)} scene(s), {total_seconds}s, estimated ${total_cost:.2f}.")
    print(project_path / "seedance" / "cost-plan.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

