#!/usr/bin/env python3
"""Build a deterministic HyperFrames composition from the storyboard."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

from whiteboard_lib import load_storyboard, validate_storyboard, write_json


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


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
    scenes = sorted(storyboard["scenes"], key=lambda item: item["order"])
    total_duration = sum(scene["duration_seconds"] for scene in scenes)
    width = project.get("width", 1080 if project["aspect_ratio"] == "9:16" else 1920)
    height = project.get("height", 1920 if project["aspect_ratio"] == "9:16" else 1080)
    fps = project["fps"]

    media_nodes: list[str] = []
    overlay_nodes: list[str] = []
    timeline = []
    start = 0
    for index, scene in enumerate(scenes, start=1):
        scene_id = scene["id"]
        duration = scene["duration_seconds"]
        overlay = scene.get("overlay", {})
        headline = esc(overlay.get("headline", ""))
        caption = esc(overlay.get("caption") or scene["narration"])
        accent = esc(overlay.get("accent_color", "#2563EB"))
        clip_path = f"../seedance/clips/{scene_id}.mp4"
        media_nodes.append(
            f'      <video id="video-{scene_id}" data-start="{start}" '
            f'data-duration="{duration}" data-track-index="{10 + index}" '
            f'data-volume="0" data-has-audio="false" src="{clip_path}" '
            f'preload="auto"></video>'
        )
        overlay_nodes.append(
            f'      <section id="overlay-{scene_id}" class="clip overlay" data-start="{start}" '
            f'data-duration="{duration}" data-track-index="{100 + index}" '
            f'style="--accent:{accent}">\n'
            f'        <div class="headline">{headline}</div>\n'
            f'        <div class="caption">{caption}</div>\n'
            f'      </section>'
        )
        timeline.append(
            {
                "scene_id": scene_id,
                "start_seconds": start,
                "duration_seconds": duration,
                "end_seconds": start + duration,
                "clip": f"seedance/clips/{scene_id}.mp4",
            }
        )
        start += duration

    html_source = f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={width}, height={height}" />
    <title>{esc(project['title'])}</title>
    <style>
      * {{ box-sizing: border-box; }}
      html, body {{ margin: 0; width: {width}px; height: {height}px; overflow: hidden; }}
      body {{ background: #f7f4ec; color: #111827; font-family: Inter, Arial, sans-serif; }}
      #root {{ position: relative; width: {width}px; height: {height}px; overflow: hidden; }}
      .clip {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
      .paper {{ background: #f7f4ec; }}
      video {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .overlay {{ pointer-events: none; padding: 7% 6%; display: flex; flex-direction: column; justify-content: space-between; }}
      .headline {{ align-self: flex-start; max-width: 86%; padding: 0.22em 0.42em; background: rgba(247,244,236,.94); border-left: 0.16em solid var(--accent); font-size: clamp(42px, 5.4vw, 92px); line-height: .96; font-weight: 900; letter-spacing: -.035em; text-transform: uppercase; }}
      .caption {{ align-self: center; max-width: 92%; padding: .55em .72em; border-radius: .35em; background: rgba(17,24,39,.92); color: white; font-size: clamp(28px, 3vw, 54px); line-height: 1.14; font-weight: 750; text-align: center; text-wrap: balance; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="whiteboard-main" data-width="{width}" data-height="{height}" data-duration="{total_duration}" data-fps="{fps}">
      <div id="paper-background" class="clip paper" data-start="0" data-duration="{total_duration}" data-track-index="0"></div>
{chr(10).join(media_nodes)}
{chr(10).join(overlay_nodes)}
      <audio id="narration" data-start="0" data-duration="{total_duration}" data-track-index="500" data-volume="1" src="../audio/narration.mp3" preload="auto"></audio>
    </div>
  </body>
</html>
'''
    composition_dir = project_path / "composition"
    composition_dir.mkdir(parents=True, exist_ok=True)
    (composition_dir / "index.html").write_text(html_source, encoding="utf-8")
    write_json(
        composition_dir / "timeline.json",
        {
            "composition_id": "whiteboard-main",
            "width": width,
            "height": height,
            "fps": fps,
            "duration_seconds": total_duration,
            "scenes": timeline,
            "audio": "audio/narration.mp3",
        },
    )

    missing = [item["clip"] for item in timeline if not (project_path / item["clip"]).is_file()]
    if not (project_path / "audio" / "narration.mp3").is_file():
        missing.append("audio/narration.mp3")
    if missing:
        print("Composition created; media still required:")
        for item in missing:
            print(f"- {item}")
    else:
        print("Composition created with all expected media present.")
    print(composition_dir / "index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
