"""Provider-neutral schemas and deterministic validation."""

from __future__ import annotations

from typing import Any

from . import SCHEMA_VERSION
from .profiles import PROFILE_INSTRUCTIONS


def _array(items: dict[str, Any]) -> dict[str, Any]:
    return {"type": "array", "items": items}


def _object(properties: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


TIMED_BASE = {
    "id": {"type": "string"},
    "start_seconds": {"type": "number"},
    "end_seconds": {"type": "number"},
}

ANALYSIS_SCHEMA: dict[str, Any] = _object(
    {
        "schema_version": {"type": "string"},
        "profile": {"type": "string"},
        "source": _object(
            {
                "label": {"type": "string"},
                "kind": {"type": "string"},
            }
        ),
        "summary": {"type": "string"},
        "chapters": _array(
            _object(
                {
                    **TIMED_BASE,
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                }
            )
        ),
        "events": _array(
            _object(
                {
                    **TIMED_BASE,
                    "event_type": {"type": "string"},
                    "description": {"type": "string"},
                    "evidence_type": {"type": "string"},
                    "confidence": {"type": "number"},
                }
            )
        ),
        "transcript_segments": _array(
            _object(
                {
                    **TIMED_BASE,
                    "speaker": {"type": "string"},
                    "text": {"type": "string"},
                    "provenance": {"type": "string"},
                    "confidence": {"type": "number"},
                }
            )
        ),
        "on_screen_text": _array(
            _object(
                {
                    **TIMED_BASE,
                    "text": {"type": "string"},
                    "location": {"type": "string"},
                    "confidence": {"type": "number"},
                }
            )
        ),
        "entities": _array(
            _object(
                {
                    "id": {"type": "string"},
                    "label": {"type": "string"},
                    "entity_type": {"type": "string"},
                    "description": {"type": "string"},
                    "first_seen_seconds": {"type": "number"},
                    "confidence": {"type": "number"},
                    "identity_basis": {"type": "string"},
                }
            )
        ),
        "claims": _array(
            _object(
                {
                    **TIMED_BASE,
                    "claim": {"type": "string"},
                    "evidence_type": {"type": "string"},
                    "verification_status": {"type": "string"},
                    "confidence": {"type": "number"},
                }
            )
        ),
        "profile_analysis": _array(
            _object(
                {
                    "title": {"type": "string"},
                    "finding": {"type": "string"},
                    "evidence_ids": _array({"type": "string"}),
                    "score": {"type": "number"},
                    "confidence": {"type": "number"},
                }
            )
        ),
        "quality": _object(
            {
                "overall_confidence": {"type": "number"},
                "limitations": _array({"type": "string"}),
                "requires_high_detail_pass": {"type": "boolean"},
                "high_detail_segments": _array(
                    _object(
                        {
                            "start_seconds": {"type": "number"},
                            "end_seconds": {"type": "number"},
                            "reason": {"type": "string"},
                        }
                    )
                ),
            }
        ),
        "high_detail_findings": _array(
            _object(
                {
                    **TIMED_BASE,
                    "finding": {"type": "string"},
                    "evidence_type": {"type": "string"},
                    "confidence": {"type": "number"},
                }
            )
        ),
        "open_questions": _array({"type": "string"}),
    }
)

HIGH_DETAIL_SCHEMA: dict[str, Any] = _object(
    {
        "findings": _array(
            _object(
                {
                    "start_seconds": {"type": "number"},
                    "end_seconds": {"type": "number"},
                    "finding": {"type": "string"},
                    "evidence_type": {"type": "string"},
                    "confidence": {"type": "number"},
                }
            )
        ),
        "limitations": _array({"type": "string"}),
    }
)


def validate_analysis(data: Any, duration_seconds: float | None = None) -> list[str]:
    """Return validation errors without requiring a JSON Schema dependency."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["analysis must be a JSON object"]
    for field in ANALYSIS_SCHEMA["required"]:
        if field not in data:
            errors.append(f"missing top-level field: {field}")
    if errors:
        return errors
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if data.get("profile") not in PROFILE_INSTRUCTIONS:
        errors.append(f"unknown profile: {data.get('profile')}")

    timed_collections = (
        "chapters",
        "events",
        "transcript_segments",
        "on_screen_text",
        "claims",
        "high_detail_findings",
    )
    for name in timed_collections:
        values = data.get(name)
        if not isinstance(values, list):
            errors.append(f"{name} must be a list")
            continue
        for index, item in enumerate(values):
            if not isinstance(item, dict):
                errors.append(f"{name}[{index}] must be an object")
                continue
            start = item.get("start_seconds")
            end = item.get("end_seconds")
            if not isinstance(start, (int, float)) or start < 0:
                errors.append(f"{name}[{index}].start_seconds must be >= 0")
            if not isinstance(end, (int, float)) or end < 0:
                errors.append(f"{name}[{index}].end_seconds must be >= 0")
            if isinstance(start, (int, float)) and isinstance(end, (int, float)) and end < start:
                errors.append(f"{name}[{index}] ends before it starts")
            if duration_seconds and isinstance(end, (int, float)) and end > duration_seconds + 0.5:
                errors.append(f"{name}[{index}].end_seconds exceeds source duration {duration_seconds}")

    confidence_locations = ["events", "transcript_segments", "on_screen_text", "entities", "claims", "profile_analysis", "high_detail_findings"]
    for name in confidence_locations:
        for index, item in enumerate(data.get(name, [])):
            value = item.get("confidence") if isinstance(item, dict) else None
            if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                errors.append(f"{name}[{index}].confidence must be between 0 and 1")
    quality = data.get("quality")
    if not isinstance(quality, dict):
        errors.append("quality must be an object")
    else:
        overall = quality.get("overall_confidence")
        if not isinstance(overall, (int, float)) or not 0 <= overall <= 1:
            errors.append("quality.overall_confidence must be between 0 and 1")
        segments = quality.get("high_detail_segments")
        if not isinstance(segments, list):
            errors.append("quality.high_detail_segments must be a list")
        elif len(segments) > 5:
            errors.append("quality.high_detail_segments may contain at most 5 items")
        else:
            for index, segment in enumerate(segments):
                if not isinstance(segment, dict):
                    errors.append(f"quality.high_detail_segments[{index}] must be an object")
                    continue
                start, end = segment.get("start_seconds"), segment.get("end_seconds")
                if not isinstance(start, (int, float)) or start < 0:
                    errors.append(f"quality.high_detail_segments[{index}].start_seconds must be >= 0")
                if not isinstance(end, (int, float)) or end < 0:
                    errors.append(f"quality.high_detail_segments[{index}].end_seconds must be >= 0")
                if isinstance(start, (int, float)) and isinstance(end, (int, float)) and end < start:
                    errors.append(f"quality.high_detail_segments[{index}] ends before it starts")
                if duration_seconds and isinstance(end, (int, float)) and end > duration_seconds + 0.5:
                    errors.append(
                        f"quality.high_detail_segments[{index}].end_seconds exceeds source duration {duration_seconds}"
                    )
    if duration_seconds:
        for index, entity in enumerate(data.get("entities", [])):
            if isinstance(entity, dict):
                first_seen = entity.get("first_seen_seconds")
                if isinstance(first_seen, (int, float)) and first_seen > duration_seconds + 0.5:
                    errors.append(f"entities[{index}].first_seen_seconds exceeds source duration {duration_seconds}")
    return errors
