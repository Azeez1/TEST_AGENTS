"""Format YouTube transcript data into Obsidian-compatible Markdown."""

from datetime import datetime
from typing import Optional


def build_frontmatter(
    title: str,
    channel: str,
    video_id: str,
    url: str,
    duration: str,
    language: str,
    is_generated: bool,
    channel_url: str = "",
    tags: Optional[list] = None,
) -> str:
    """Build YAML frontmatter for the Obsidian note."""
    if tags is None:
        tags = ["youtube", "transcript"]

    # Escape quotes in title
    safe_title = title.replace('"', '\\"')
    safe_channel = channel.replace('"', '\\"')

    caption_type = "auto-generated" if is_generated else "manual"
    today = datetime.now().strftime("%Y-%m-%d")

    tag_lines = "\n".join(f"  - {tag}" for tag in tags)

    return f"""---
title: "{safe_title}"
channel: "{safe_channel}"
date: {today}
url: "https://youtube.com/watch?v={video_id}"
video_id: "{video_id}"
duration: "{duration}"
language: "{language}"
caption_type: "{caption_type}"
tags:
{tag_lines}
type: youtube-transcript
status: raw
---"""


def build_header(title: str, channel: str, channel_url: str, duration: str) -> str:
    """Build the note header section."""
    if channel_url:
        channel_link = f"[{channel}]({channel_url})"
    else:
        channel_link = channel

    return f"""# {title}

**Channel:** {channel_link} | **Duration:** {duration}

---"""


def build_transcript_body(segments: list, include_timestamps: bool = True) -> str:
    """Build the transcript section from segments."""
    if not segments:
        return "> No transcript content available."

    lines = []
    for seg in segments:
        text = seg["text"].strip()
        if not text:
            continue

        if include_timestamps:
            timestamp = _format_timestamp(seg["start"])
            lines.append(f"{timestamp} {text}")
        else:
            lines.append(text)

    if include_timestamps:
        return "\n\n".join(lines)
    else:
        # Join without timestamps as flowing paragraphs
        return " ".join(lines)


def build_full_note(
    title: str,
    channel: str,
    channel_url: str,
    video_id: str,
    duration: str,
    language: str,
    is_generated: bool,
    segments: list,
    include_timestamps: bool = True,
    tags: Optional[list] = None,
) -> str:
    """Build the complete Obsidian note."""
    frontmatter = build_frontmatter(
        title=title,
        channel=channel,
        video_id=video_id,
        url=f"https://youtube.com/watch?v={video_id}",
        duration=duration,
        language=language,
        is_generated=is_generated,
        channel_url=channel_url,
        tags=tags,
    )

    header = build_header(title, channel, channel_url, duration)
    transcript = build_transcript_body(segments, include_timestamps)

    word_count = len(" ".join(seg["text"] for seg in segments).split())

    return f"""{frontmatter}

{header}

## Transcript

{transcript}

---

*{word_count:,} words | {"Auto-generated" if is_generated else "Manual"} captions | {language.upper()}*

## Notes

<!-- Your notes and takeaways here -->
"""


def _format_timestamp(seconds: float) -> str:
    """Convert seconds to [HH:MM:SS] or [MM:SS] format."""
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if hours > 0:
        return f"[{hours:02d}:{minutes:02d}:{secs:02d}]"
    return f"[{minutes:02d}:{secs:02d}]"
