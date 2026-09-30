"""Temporary YouTube caption timelines for timestamp grounding."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any


def _clock(seconds: float) -> str:
    value = max(0, int(seconds))
    minutes, secs = divmod(value, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}" if hours else f"{minutes:02d}:{secs:02d}"


def parse_json3_captions(payload: dict[str, Any]) -> str:
    """Convert YouTube json3 captions into compact, non-overlapping timeline lines."""
    cues: list[tuple[float, float, str]] = []
    for event in payload.get("events", []):
        segments = event.get("segs") or []
        text = "".join(str(segment.get("utf8", "")) for segment in segments)
        text = html.unescape(re.sub(r"\s+", " ", text)).strip()
        if not text or text in {"[Music]", "[Applause]"}:
            continue
        start = float(event.get("tStartMs", 0)) / 1000
        end = start + float(event.get("dDurationMs", 0)) / 1000
        cues.append((start, end, text))
    lines: list[str] = []
    bucket_start = bucket_end = 0.0
    bucket_text: list[str] = []
    for start, end, text in cues:
        if bucket_text and (start - bucket_start >= 8 or sum(map(len, bucket_text)) + len(text) > 220):
            lines.append(f"[{_clock(bucket_start)}-{_clock(bucket_end)}] {' '.join(bucket_text)}")
            bucket_text = []
        if not bucket_text:
            bucket_start = start
        bucket_end = max(bucket_end, end)
        if not bucket_text or text != bucket_text[-1]:
            bucket_text.append(text)
    if bucket_text:
        lines.append(f"[{_clock(bucket_start)}-{_clock(bucket_end)}] {' '.join(bucket_text)}")
    return "\n".join(lines)


def write_caption_timeline(info: dict[str, Any], destination: Path) -> Path | None:
    """Fetch the best English json3 caption track referenced by yt-dlp metadata."""
    tracks = (info.get("subtitles") or {}).get("en") or (info.get("automatic_captions") or {}).get("en") or []
    track = next((item for item in tracks if item.get("ext") == "json3" and item.get("url")), None)
    if not track:
        return None
    try:
        import requests

        response = requests.get(track["url"], headers=info.get("http_headers") or {}, timeout=30)
        response.raise_for_status()
        payload = response.json()
        timeline = parse_json3_captions(payload)
    except Exception:
        return None
    if not timeline:
        return None
    destination.write_text(timeline, encoding="utf-8")
    return destination
