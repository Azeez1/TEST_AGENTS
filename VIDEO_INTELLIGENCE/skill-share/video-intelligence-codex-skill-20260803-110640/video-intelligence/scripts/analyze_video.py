#!/usr/bin/env python
"""Analyze arbitrary video with Gemini and emit validated evidence artifacts."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from video_intelligence import PIPELINE_VERSION, SCHEMA_VERSION
from video_intelligence.cache import load_cache, make_cache_key, save_cache
from video_intelligence.costs import estimate_cost, estimate_usage_cost, resolve_model
from video_intelligence.media import MediaSource, detect_rapid_change_segments, extract_clip, resolve_source, safe_slug
from video_intelligence.profiles import available_profiles, build_prompt, load_rubric
from video_intelligence.provider import GeminiProvider
from video_intelligence.render import render_markdown
from video_intelligence.schema import validate_analysis
from video_intelligence.security import load_gemini_api_key, redact
from video_intelligence.timeline import repair_timestamps


def _json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _log(path: Path, message: str) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{datetime.now(timezone.utc).isoformat()} {redact(message)}\n")


def _run_dir(root: Path, label: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    path = root / f"{stamp}-{safe_slug(label)}"
    path.mkdir(parents=True, exist_ok=False)
    return path


def _cache_payload(source: MediaSource, profile: str, question: str, model: str, rubric: str) -> dict[str, Any]:
    return {
        "source_identity": source.identity,
        "profile": profile,
        "question": question.strip(),
        "model": model,
        "rubric": rubric,
        "schema_version": SCHEMA_VERSION,
        "pipeline_version": PIPELINE_VERSION,
    }


def _normalize(analysis: dict[str, Any], source: MediaSource, profile: str) -> dict[str, Any]:
    analysis["schema_version"] = SCHEMA_VERSION
    analysis["profile"] = profile
    analysis["source"] = {"label": source.label, "kind": source.kind}
    analysis.setdefault("high_detail_findings", [])
    return analysis


def _sum_usage(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "input_tokens": sum(int(item.get("input_tokens", 0)) for item in items),
        "output_tokens": sum(int(item.get("output_tokens", 0)) for item in items),
        "thought_tokens": sum(int(item.get("thought_tokens", 0)) for item in items),
        "total_tokens": sum(int(item.get("total_tokens", 0)) for item in items),
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("source", help="Local video file, public YouTube URL, or downloadable media URL")
    result.add_argument("--output-dir", required=True, help="Approved workspace output directory")
    result.add_argument("--profile", choices=available_profiles(), default="general")
    result.add_argument("--question", default="")
    result.add_argument("--rubric-file")
    result.add_argument("--model", default="auto")
    result.add_argument(
        "--youtube-ingestion",
        choices=("auto", "direct", "download"),
        default="auto",
        help="Auto downloads YouTube for timestamp accuracy and falls back to direct URL if acquisition fails",
    )
    result.add_argument("--max-cost-usd", type=float, default=0.50)
    result.add_argument("--estimated-output-tokens", type=int, default=8000)
    result.add_argument("--dry-run", action="store_true")
    result.add_argument("--no-cache", action="store_true")
    result.add_argument("--no-escalate", action="store_true")
    result.add_argument("--max-escalations", type=int, default=2)
    result.add_argument("--env-file")
    result.add_argument("--keep-remote-file", action="store_true")
    return result


def main() -> int:
    args = parser().parse_args()
    if args.max_cost_usd <= 0:
        raise SystemExit("--max-cost-usd must be greater than zero")
    if args.estimated_output_tokens < 256:
        raise SystemExit("--estimated-output-tokens must be at least 256")
    if not 0 <= args.max_escalations <= 5:
        raise SystemExit("--max-escalations must be between 0 and 5")

    output_root = Path(args.output_dir).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    source: MediaSource | None = None
    run_dir: Path | None = None
    try:
        youtube_ingestion = (
            "direct" if args.dry_run and args.youtube_ingestion == "auto" else args.youtube_ingestion
        )
        source = resolve_source(args.source, youtube_ingestion=youtube_ingestion)
        run_dir = _run_dir(output_root, source.label)
        log_path = run_dir / "run.log"
        _log(log_path, f"resolved source kind={source.kind} identity={source.identity}")
        model = resolve_model(args.model)
        rubric = load_rubric(args.rubric_file)
        caption_timeline = ""
        if source.caption_path and Path(source.caption_path).is_file():
            caption_timeline = Path(source.caption_path).read_text(encoding="utf-8")
        prompt = build_prompt(
            profile=args.profile,
            question=args.question,
            source_label=source.label,
            duration_seconds=source.duration_seconds,
            caption_timeline=caption_timeline,
            rubric=rubric,
        )
        estimate = estimate_cost(model, source.duration_seconds, args.estimated_output_tokens)
        manifest: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "pipeline_version": PIPELINE_VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "planned" if args.dry_run else "running",
            "source": source.public_dict(),
            "profile": args.profile,
            "question": args.question,
            "model": model,
            "cost_cap_usd": args.max_cost_usd,
            "cost_estimate": estimate.to_dict(),
            "cost_usd": 0.0,
            "usage": {},
            "cache": {"enabled": not args.no_cache, "hit": False},
            "remote_cleanup": "not_started",
            "warnings": [],
            "caption_timeline": {
                "available": bool(caption_timeline),
                "provenance": "youtube_caption_track" if caption_timeline else "none",
            },
        }
        if args.youtube_ingestion == "auto" and not args.dry_run and source.kind == "youtube_url":
            manifest["warnings"].append(
                "Automatic YouTube download failed; direct URL ingestion was used and timestamp validation remains strict."
            )
        _json(run_dir / "manifest.json", manifest)
        if estimate.estimated_total_usd is None:
            manifest["warnings"].append("No price table is available for this explicit model; cap enforcement uses usage after the call.")
        elif estimate.estimated_total_usd > args.max_cost_usd:
            manifest["status"] = "refused_cost_cap"
            _json(run_dir / "manifest.json", manifest)
            _log(log_path, "refused call because conservative estimate exceeds cost cap")
            print(f"REFUSED: estimated ${estimate.estimated_total_usd:.4f} exceeds ${args.max_cost_usd:.4f}", file=sys.stderr)
            print(run_dir)
            return 2
        if args.dry_run:
            _log(log_path, "dry run completed without provider call")
            print(run_dir)
            return 0

        cache_key = make_cache_key(_cache_payload(source, args.profile, args.question, model, rubric))
        manifest["cache"]["key"] = cache_key
        cached = None if args.no_cache else load_cache(cache_key)
        if cached and isinstance(cached.get("analysis"), dict) and not validate_analysis(
            cached["analysis"], source.duration_seconds
        ):
            analysis = cached["analysis"]
            manifest["cache"]["hit"] = True
            manifest["status"] = "completed"
            manifest["usage"] = cached.get("usage", {})
            manifest["cost_usd"] = 0.0
            manifest["remote_cleanup"] = "not_applicable_cache_hit"
            _log(log_path, "used validated content-addressed cache entry")
        else:
            api_key, key_source = load_gemini_api_key(args.env_file)
            _log(log_path, f"loaded Gemini credential from {key_source}")
            provider = GeminiProvider(api_key, keep_remote_file=args.keep_remote_file)
            result = provider.analyze(source, prompt, model, args.estimated_output_tokens)
            analysis = _normalize(result.data, source, args.profile)
            usage_items = [result.usage]
            manifest["remote_cleanup"] = result.cleanup_status
            manifest["interaction_id"] = result.interaction_id

            quality = analysis.get("quality", {})
            requested_segments = list(quality.get("high_detail_segments", [])) if isinstance(quality, dict) else []
            rapid_terms = ("brief", "flash", "fleeting", "rapid", "quick", "frame", "fast cut")
            if source.local_path and any(term in args.question.lower() for term in rapid_terms):
                rapid_segments = detect_rapid_change_segments(source, max_segments=args.max_escalations)
                manifest["local_rapid_change_segments"] = rapid_segments
                for segment in rapid_segments:
                    requested_segments.insert(0, segment)
            if requested_segments and not args.no_escalate and args.max_escalations:
                if not source.local_path:
                    manifest["warnings"].append("High-detail pass requested but direct URL sources are not downloaded in v1.")
                else:
                    evidence_dir = run_dir / "evidence"
                    deduplicated: list[dict[str, Any]] = []
                    for segment in requested_segments:
                        start = float(segment.get("start_seconds", 0))
                        end = float(segment.get("end_seconds", start))
                        if any(start <= float(item.get("end_seconds", 0)) and end >= float(item.get("start_seconds", 0)) for item in deduplicated):
                            continue
                        deduplicated.append(segment)
                    for index, segment in enumerate(deduplicated[: args.max_escalations], start=1):
                        start = max(0.0, float(segment.get("start_seconds", 0)))
                        end = min(source.duration_seconds, float(segment.get("end_seconds", start + 3)))
                        if end <= start:
                            continue
                        reason = str(segment.get("reason", "ambiguity"))
                        slow_factor = 8.0 if any(term in reason.lower() for term in rapid_terms) else 1.0
                        clip_estimate = estimate_cost(model, (end - start) * slow_factor, 3000)
                        current = estimate_usage_cost(model, _sum_usage(usage_items)) or 0.0
                        predicted = current + float(clip_estimate.estimated_total_usd or args.max_cost_usd + 1)
                        if predicted > args.max_cost_usd:
                            manifest["warnings"].append("Skipped a high-detail pass to preserve the cost cap.")
                            break
                        clip_path = extract_clip(
                            source,
                            start,
                            end,
                            evidence_dir / f"segment-{index:02d}.mp4",
                            slow_factor=slow_factor,
                        )
                        detail_prompt = (
                            f"Inspect this clip in high visual detail. It corresponds to {start:.3f}s–{end:.3f}s "
                            f"in the original video and was slowed by {slow_factor:g}x. Reason: {reason}. "
                            "Report timestamps relative to the slowed clip and separate visual evidence from inference."
                        )
                        detail = provider.analyze_clip(clip_path, detail_prompt, model)
                        usage_items.append(detail.usage)
                        for finding in detail.data.get("findings", []):
                            finding["start_seconds"] = start + float(finding.get("start_seconds", 0)) / slow_factor
                            finding["end_seconds"] = start + float(finding.get("end_seconds", 0)) / slow_factor
                            finding["start_seconds"] = min(max(finding["start_seconds"], start), end)
                            finding["end_seconds"] = min(max(finding["end_seconds"], finding["start_seconds"]), end)
                            analysis["high_detail_findings"].append(finding)
                        manifest["remote_cleanup"] += f"; detail_{index}={detail.cleanup_status}"

            errors = validate_analysis(analysis, source.duration_seconds)
            if caption_timeline and any("exceeds source duration" in error for error in errors):
                manifest["timestamp_repair"] = repair_timestamps(
                    analysis,
                    caption_timeline,
                    source.duration_seconds,
                )
                errors = validate_analysis(analysis, source.duration_seconds)
            if errors:
                manifest["usage"] = _sum_usage(usage_items)
                manifest["cost_usd"] = estimate_usage_cost(model, manifest["usage"]) or 0.0
                _json(run_dir / "analysis.invalid.json", analysis)
                manifest["status"] = "validation_failed"
                manifest["validation_errors"] = errors
                _json(run_dir / "manifest.json", manifest)
                _log(log_path, f"structured output validation failed: {errors}")
                print(run_dir)
                return 3
            manifest["usage"] = _sum_usage(usage_items)
            realized = estimate_usage_cost(model, manifest["usage"])
            manifest["cost_usd"] = realized if realized is not None else 0.0
            if realized is None:
                manifest["warnings"].append("Realized cost unavailable for the selected model.")
            elif realized > args.max_cost_usd:
                manifest["warnings"].append("Provider-reported usage exceeded the preflight cap estimate; no further calls were made.")
            manifest["status"] = "completed"
            if not args.no_cache:
                save_cache(cache_key, {"analysis": analysis, "usage": manifest["usage"]})
                _log(log_path, "saved validated analysis to content-addressed cache")

        _json(run_dir / "analysis.json", analysis)
        _json(run_dir / "manifest.json", manifest)
        (run_dir / "report.md").write_text(render_markdown(analysis, manifest), encoding="utf-8")
        _log(log_path, f"completed status={manifest['status']} cost_usd={manifest['cost_usd']}")
        print(run_dir)
        return 0
    except Exception as exc:
        message = redact(exc)
        if run_dir:
            _log(run_dir / "run.log", f"failed: {message}")
            manifest_path = run_dir / "manifest.json"
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
                manifest["status"] = "failed"
                manifest["error"] = message
                _json(manifest_path, manifest)
            except Exception:
                pass
            print(run_dir)
        print(f"ERROR: {message}", file=sys.stderr)
        return 1
    finally:
        if source and source.temporary and source.local_path:
            try:
                shutil.rmtree(Path(source.local_path).parent)
            except OSError:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
