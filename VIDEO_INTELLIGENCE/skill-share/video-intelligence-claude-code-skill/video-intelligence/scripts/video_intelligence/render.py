"""Human-readable rendering for the provider-neutral analysis."""

from __future__ import annotations

from typing import Any


def timestamp(seconds: float) -> str:
    seconds = max(0, int(round(float(seconds))))
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}" if hours else f"{minutes:02d}:{secs:02d}"


def _range(item: dict[str, Any]) -> str:
    return f"{timestamp(item.get('start_seconds', 0))}–{timestamp(item.get('end_seconds', 0))}"


def render_markdown(analysis: dict[str, Any], manifest: dict[str, Any]) -> str:
    cost = manifest.get("cost_usd")
    cost_text = f"${cost:.4f}" if isinstance(cost, (int, float)) else "unavailable"
    lines = [
        f"# Video intelligence: {analysis['source']['label']}",
        "",
        analysis.get("summary", ""),
        "",
        "## Run context",
        "",
        f"- Profile: `{analysis.get('profile', '')}`",
        f"- Model: `{manifest.get('model', '')}`",
        f"- Overall confidence: {analysis.get('quality', {}).get('overall_confidence', 0):.0%}",
        f"- Estimated cost: {cost_text}",
    ]
    chapters = analysis.get("chapters", [])
    if chapters:
        lines.extend(["", "## Chapters", ""])
        for chapter in chapters:
            lines.append(f"- **{_range(chapter)} — {chapter['title']}**: {chapter['summary']}")
    findings = analysis.get("profile_analysis", [])
    if findings:
        lines.extend(["", "## Analysis", ""])
        for finding in findings:
            evidence = ", ".join(finding.get("evidence_ids", [])) or "no linked evidence"
            score = finding.get("score", -1)
            score_text = f"; score {score:g}" if isinstance(score, (int, float)) and score >= 0 else ""
            lines.append(f"- **{finding['title']}** ({finding.get('confidence', 0):.0%}{score_text}): {finding['finding']} _Evidence: {evidence}._")
    events = analysis.get("events", [])
    if events:
        lines.extend(["", "## Timestamped evidence", ""])
        for event in events:
            lines.append(f"- `{event['id']}` **{_range(event)}** [{event['evidence_type']}, {event['confidence']:.0%}] — {event['description']}")
    transcript = analysis.get("transcript_segments", [])
    if transcript:
        lines.extend(["", "## Transcript", ""])
        for segment in transcript:
            lines.append(f"- **{_range(segment)} — {segment['speaker']}**: {segment['text']} _({segment['provenance']}, {segment['confidence']:.0%})_")
    text_items = analysis.get("on_screen_text", [])
    if text_items:
        lines.extend(["", "## On-screen text", ""])
        for item in text_items:
            lines.append(f"- **{_range(item)}**: “{item['text']}” — {item['location']} ({item['confidence']:.0%})")
    detail = analysis.get("high_detail_findings", [])
    if detail:
        lines.extend(["", "## High-detail findings", ""])
        for item in detail:
            lines.append(f"- **{_range(item)}** [{item['evidence_type']}, {item['confidence']:.0%}] — {item['finding']}")
    quality = analysis.get("quality", {})
    limitations = quality.get("limitations", [])
    questions = analysis.get("open_questions", [])
    if limitations or questions:
        lines.extend(["", "## Limitations and open questions", ""])
        lines.extend(f"- Limitation: {item}" for item in limitations)
        lines.extend(f"- Open question: {item}" for item in questions)
    lines.append("")
    return "\n".join(lines)
