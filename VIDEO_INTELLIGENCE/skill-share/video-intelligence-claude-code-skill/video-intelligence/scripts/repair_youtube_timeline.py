#!/usr/bin/env python
"""Repair a failed YouTube analysis offline using its caption clock."""

from __future__ import annotations

import argparse
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yt_dlp

from video_intelligence import PIPELINE_VERSION, SCHEMA_VERSION
from video_intelligence.cache import make_cache_key, save_cache
from video_intelligence.captions import write_caption_timeline
from video_intelligence.render import render_markdown
from video_intelligence.schema import validate_analysis
from video_intelligence.timeline import repair_timestamps


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run", required=True)
    parser.add_argument("--youtube-url", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    source_run = Path(args.source_run).expanduser().resolve()
    source_manifest = json.loads((source_run / "manifest.json").read_text(encoding="utf-8"))
    analysis_path = source_run / "analysis.invalid.json"
    if not analysis_path.is_file():
        analysis_path = source_run / "analysis.json"
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    duration = float(source_manifest.get("source", {}).get("duration_seconds") or 0)
    with tempfile.TemporaryDirectory(prefix="video-intelligence-caption-") as directory:
        options = {"quiet": True, "no_warnings": True, "skip_download": True, "noplaylist": True}
        with yt_dlp.YoutubeDL(options) as downloader:
            info = downloader.extract_info(args.youtube_url, download=False)
        caption_path = write_caption_timeline(info, Path(directory) / "captions.txt")
        if not caption_path:
            raise RuntimeError("No English JSON3 caption track was available")
        timeline = caption_path.read_text(encoding="utf-8")
        stats = repair_timestamps(analysis, timeline, duration)
    errors = validate_analysis(analysis, duration)
    if errors:
        raise RuntimeError(f"Repaired analysis remains invalid: {errors}")

    root = Path(args.output_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    run_dir = root / f"{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}-caption-repaired"
    run_dir.mkdir()
    usage = source_manifest.get("usage", {})
    manifest = dict(source_manifest)
    manifest.update(
        {
            "schema_version": SCHEMA_VERSION,
            "pipeline_version": PIPELINE_VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed_offline_timeline_repair",
            "derived_from": str(source_run),
            "timestamp_repair": stats,
            "caption_timeline": {"available": True, "provenance": "youtube_caption_track"},
            "remote_cleanup": "not_applicable_offline_repair",
            "validation_errors": [],
        }
    )
    if not usage:
        manifest["cost_usd"] = None
        manifest.setdefault("warnings", []).append(
            "Provider usage was unavailable in the failed source run; consult the Gemini billing console for actual cost."
        )
    cache_payload = {
        "source_identity": source_manifest["source"]["identity"],
        "profile": source_manifest["profile"],
        "question": source_manifest.get("question", "").strip(),
        "model": source_manifest["model"],
        "rubric": "",
        "schema_version": SCHEMA_VERSION,
        "pipeline_version": PIPELINE_VERSION,
    }
    key = make_cache_key(cache_payload)
    save_cache(key, {"analysis": analysis, "usage": usage})
    manifest["cache"] = {"enabled": True, "hit": False, "key": key, "populated_by": "offline_timeline_repair"}
    (run_dir / "analysis.json").write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "report.md").write_text(render_markdown(analysis, manifest), encoding="utf-8")
    (run_dir / "run.log").write_text(
        f"{datetime.now(timezone.utc).isoformat()} repaired offline from {source_run}\n",
        encoding="utf-8",
    )
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
