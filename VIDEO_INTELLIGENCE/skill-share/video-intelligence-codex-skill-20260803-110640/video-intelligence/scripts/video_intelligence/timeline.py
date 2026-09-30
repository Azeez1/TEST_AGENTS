"""Deterministic semantic alignment against an authoritative caption clock."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any


STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how", "in", "into",
    "is", "it", "of", "on", "or", "that", "the", "their", "this", "to", "using", "vs", "with",
}
LINE_RE = re.compile(r"^\[(\d{2}:\d{2}(?::\d{2})?)-(\d{2}:\d{2}(?::\d{2})?)\]\s+(.+)$")


@dataclass(frozen=True)
class CaptionCue:
    start: float
    end: float
    text: str
    tokens: frozenset[str]


def _seconds(clock: str) -> float:
    values = [int(value) for value in clock.split(":")]
    if len(values) == 2:
        return float(values[0] * 60 + values[1])
    return float(values[0] * 3600 + values[1] * 60 + values[2])


def _tokens(text: str) -> frozenset[str]:
    return frozenset(
        token for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2 and token not in STOP_WORDS
    )


def parse_caption_timeline(timeline: str) -> list[CaptionCue]:
    cues: list[CaptionCue] = []
    for line in timeline.splitlines():
        match = LINE_RE.match(line.strip())
        if not match:
            continue
        text = match.group(3)
        cues.append(CaptionCue(_seconds(match.group(1)), _seconds(match.group(2)), text, _tokens(text)))
    return cues


def _matcher(cues: list[CaptionCue]):
    frequencies = Counter(token for cue in cues for token in cue.tokens)
    total = max(len(cues), 1)

    def best(text: str, minimum_start: float = 0.0) -> CaptionCue | None:
        query = _tokens(text)
        if not query:
            return None
        scored: list[tuple[float, float, CaptionCue]] = []
        for cue in cues:
            if cue.start + 0.5 < minimum_start:
                continue
            overlap = query & cue.tokens
            if not overlap:
                continue
            score = sum(1.0 + math.log((total + 1) / (frequencies[token] + 1)) for token in overlap)
            score /= math.sqrt(len(query))
            scored.append((score, -cue.start, cue))
        if not scored:
            return None
        return max(scored, key=lambda item: (item[0], item[1]))[2]

    return best


def repair_timestamps(
    analysis: dict[str, Any],
    caption_timeline: str,
    duration_seconds: float,
) -> dict[str, int]:
    """Align model-generated timestamps to caption cues in place."""
    cues = parse_caption_timeline(caption_timeline)
    if not cues:
        return {"aligned": 0, "dropped": 0}
    best = _matcher(cues)
    aligned = dropped = 0

    chapters = analysis.get("chapters", [])
    chapter_starts: list[float] = []
    minimum = 0.0
    for index, chapter in enumerate(chapters):
        if index == 0:
            start = 0.0
        else:
            title = str(chapter.get("title", ""))
            title_tokens = _tokens(title)
            cue = None
            if title_tokens & {"summary", "conclusion", "recap"}:
                recap_candidates = [
                    item for item in cues
                    if item.start >= max(minimum, duration_seconds * 0.5)
                    and ({"summary", "recap"} & item.tokens or {"five", "ways"} <= item.tokens)
                ]
                cue = recap_candidates[0] if recap_candidates else None
            if cue is None:
                cue = best(title, minimum)
            if cue is None:
                cue = best(str(chapter.get("summary", "")), minimum)
            if cue is None:
                remaining = max(len(chapters) - index, 1)
                start = minimum + max((duration_seconds - minimum) / (remaining + 1), 1.0)
            else:
                start = cue.start
                aligned += 1
        start = min(max(start, minimum), duration_seconds)
        chapter_starts.append(start)
        minimum = start + 1.0
    for index, chapter in enumerate(chapters):
        chapter["start_seconds"] = round(chapter_starts[index], 3)
        chapter["end_seconds"] = round(
            chapter_starts[index + 1] if index + 1 < len(chapter_starts) else duration_seconds,
            3,
        )

    text_fields = {
        "events": ("event_type", "description"),
        "transcript_segments": ("speaker", "text"),
        "on_screen_text": ("text",),
        "claims": ("claim", "evidence_type"),
        "high_detail_findings": ("finding", "evidence_type"),
    }
    for collection, fields in text_fields.items():
        repaired: list[dict[str, Any]] = []
        for item in analysis.get(collection, []):
            query = " ".join(str(item.get(field, "")) for field in fields)
            cue = best(query)
            if cue is None:
                if float(item.get("end_seconds", 0)) > duration_seconds:
                    dropped += 1
                    continue
            else:
                item["start_seconds"] = round(cue.start, 3)
                item["end_seconds"] = round(min(cue.end, duration_seconds), 3)
                aligned += 1
            repaired.append(item)
        analysis[collection] = repaired

    for entity in analysis.get("entities", []):
        cue = best(f"{entity.get('label', '')} {entity.get('description', '')}")
        if cue:
            entity["first_seen_seconds"] = round(cue.start, 3)
            aligned += 1
        elif float(entity.get("first_seen_seconds", 0)) > duration_seconds:
            entity["first_seen_seconds"] = 0.0
            entity["confidence"] = min(float(entity.get("confidence", 0)), 0.5)

    for claim in analysis.get("claims", []):
        claim["verification_status"] = "unverified_external"
    quality = analysis.setdefault("quality", {})
    limitations = quality.setdefault("limitations", [])
    limitations.append(
        "Model timestamps failed duration validation and were semantically realigned to the YouTube caption clock."
    )
    return {"aligned": aligned, "dropped": dropped}
