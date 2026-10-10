"""YouTube transcript extraction.

Tier 1: yt-dlp (ban-resistant, uses the player-style captions endpoint)
Tier 2: youtube-transcript-api library (fallback; IP-banned under heavy batch use)
"""

import os
import re
import json
import glob
import subprocess
import tempfile
import urllib.request
import urllib.error
from typing import Optional


def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from various YouTube URL formats or a raw ID."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from: {url_or_id}")


def fetch_video_metadata(video_id: str) -> dict:
    """Fetch video metadata from YouTube's oembed endpoint (no API key needed)."""
    oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    try:
        req = urllib.request.Request(oembed_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {
                "title": data.get("title", "Untitled"),
                "channel": data.get("author_name", "Unknown Channel"),
                "channel_url": data.get("author_url", ""),
            }
    except (urllib.error.URLError, json.JSONDecodeError):
        return {
            "title": f"Video {video_id}",
            "channel": "Unknown Channel",
            "channel_url": "",
        }


def _parse_vtt(vtt_content: str) -> list:
    """Parse WebVTT content into [{text, start, duration}] segments.

    YouTube auto-captions contain overlapping cues for word-by-word highlighting,
    so we dedupe by exact text to avoid 3-5x transcript bloat.
    """
    segments = []
    seen_texts = set()
    ts_pattern = re.compile(
        r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s+-->\s+(\d{2}):(\d{2}):(\d{2})\.(\d{3})'
    )

    lines = vtt_content.split("\n")
    i = 0
    while i < len(lines):
        m = ts_pattern.match(lines[i].strip())
        if m:
            h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, m.groups())
            start = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000
            end = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000

            text_parts = []
            i += 1
            while i < len(lines) and lines[i].strip():
                # Strip VTT/HTML tags (e.g. <c>, <00:00:01.000>, <c.colorE5E5E5>)
                clean = re.sub(r'<[^>]*>', '', lines[i]).strip()
                if clean:
                    text_parts.append(clean)
                i += 1

            text = " ".join(text_parts).strip()
            if text and text not in seen_texts:
                seen_texts.add(text)
                segments.append({
                    "text": text,
                    "start": start,
                    "duration": max(0.0, end - start),
                })
        i += 1

    return segments


def fetch_transcript_ytdlp(video_id: str, lang: str = "en", cookies_file: str = None) -> dict:
    """Tier 1: Fetch captions via yt-dlp (uses player-style endpoint, rarely IP-banned).

    Cookie resolution order:
      1. Explicit cookies_file arg (Netscape format, e.g. from "Get cookies.txt LOCALLY" extension)
      2. YT_COOKIES_FILE env var (same format)
      3. --cookies-from-browser chrome (broken on Windows Chrome 127+ due to DPAPI)
      4. Unauthenticated (will hit rate limits on batch work)

    Set YT_TRANSCRIPT_NO_COOKIES=1 to force unauthenticated mode.
    """
    result = {
        "segments": [],
        "language": lang,
        "is_generated": False,
        "error": None,
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output_template = os.path.join(tmpdir, "%(id)s.%(ext)s")
        url = f"https://www.youtube.com/watch?v={video_id}"

        cmd = [
            "yt-dlp",
            "--skip-download",
            "--write-sub",
            "--write-auto-sub",
            "--sub-lang", f"{lang},{lang}-orig,{lang}.*",
            "--sub-format", "vtt",
            "--no-warnings",
            "--quiet",
            "-o", output_template,
        ]

        # Cookie auth dramatically reduces rate-limiting.
        if os.getenv("YT_TRANSCRIPT_NO_COOKIES") != "1":
            resolved_cookies = cookies_file or os.getenv("YT_COOKIES_FILE")
            if resolved_cookies and os.path.isfile(resolved_cookies):
                cmd += ["--cookies", resolved_cookies]
            else:
                # Fallback: try Chrome directly. Broken on Windows Chrome 127+
                # (DPAPI), but works on Firefox / older Chrome / Mac / Linux.
                cmd += ["--cookies-from-browser", "chrome"]

        cmd.append(url)

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=90,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.TimeoutExpired:
            result["error"] = "yt-dlp captions fetch timed out (90s)"
            return result
        except FileNotFoundError:
            result["error"] = "yt-dlp not found on PATH"
            return result

        if proc.returncode != 0:
            stderr = (proc.stderr or "").strip()[:300]
            result["error"] = f"yt-dlp exited {proc.returncode}: {stderr}"
            return result

        vtt_files = glob.glob(os.path.join(tmpdir, f"{video_id}*.vtt"))
        if not vtt_files:
            result["error"] = "No captions available (yt-dlp produced no .vtt file)"
            return result

        # Prefer manual captions over auto-generated. yt-dlp names auto subs like
        # "{id}.en.vtt" for manual and "{id}.en.vtt" for auto too, but when both
        # exist the auto one has a different pattern; we just pick the one NOT
        # containing "auto" in the filename if possible.
        manual = [p for p in vtt_files if "auto" not in os.path.basename(p).lower()]
        vtt_path = manual[0] if manual else vtt_files[0]
        is_generated = vtt_path not in manual

        try:
            with open(vtt_path, "r", encoding="utf-8", errors="replace") as f:
                vtt_content = f.read()
        except OSError as e:
            result["error"] = f"Could not read VTT file: {e}"
            return result

        segments = _parse_vtt(vtt_content)
        if not segments:
            result["error"] = "VTT parsed to zero segments (empty or malformed captions)"
            return result

        result["segments"] = segments
        result["is_generated"] = is_generated
        return result


def fetch_transcript_api(video_id: str, lang: str = "en") -> dict:
    """Tier 2: youtube-transcript-api library (fallback; may be IP-banned)."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        # v1.x API: instantiate then call methods
        ytt = YouTubeTranscriptApi()
        transcript_list = ytt.list(video_id)

        # Try manual captions first, then auto-generated
        transcript_obj = None
        is_generated = False

        try:
            transcript_obj = transcript_list.find_manually_created_transcript([lang, "en"])
            is_generated = False
        except Exception:
            try:
                transcript_obj = transcript_list.find_generated_transcript([lang, "en"])
                is_generated = True
            except Exception:
                # Try any available transcript
                for t in transcript_list:
                    transcript_obj = t
                    is_generated = t.is_generated
                    break

        if transcript_obj is None:
            return {
                "segments": [],
                "language": lang,
                "is_generated": False,
                "error": "No transcripts available for this video.",
            }

        segments = transcript_obj.fetch()

        # Handle FetchedTranscript (iterable of Snippet objects in v1.x)
        parsed_segments = []
        for seg in segments:
            if hasattr(seg, "text"):
                parsed_segments.append({
                    "text": seg.text,
                    "start": seg.start if hasattr(seg, "start") else 0,
                    "duration": seg.duration if hasattr(seg, "duration") else 0,
                })
            elif isinstance(seg, dict):
                parsed_segments.append({
                    "text": seg.get("text", ""),
                    "start": seg.get("start", 0),
                    "duration": seg.get("duration", 0),
                })

        return {
            "segments": parsed_segments,
            "language": transcript_obj.language_code if hasattr(transcript_obj, 'language_code') else lang,
            "is_generated": is_generated,
            "error": None,
        }

    except Exception as e:
        error_msg = str(e)
        if "disabled" in error_msg.lower():
            error_msg = "Transcripts are disabled for this video."
        elif "no transcript" in error_msg.lower():
            error_msg = "No transcript found for this video."
        return {
            "segments": [],
            "language": lang,
            "is_generated": False,
            "error": error_msg,
        }


def fetch_transcript(video_id: str, lang: str = "en", cookies_file: str = None) -> dict:
    """Two-tier transcript fetch.

    Tries yt-dlp first (ban-resistant). If yt-dlp returns no captions — which
    can mean a real "no captions" state OR a yt-dlp issue — falls back to the
    youtube-transcript-api library.

    Returns dict: {segments, language, is_generated, error}
    """
    primary = fetch_transcript_ytdlp(video_id, lang=lang, cookies_file=cookies_file)
    if primary["segments"]:
        return primary

    # Fallback — note we carry the yt-dlp error forward if the API also fails
    fallback = fetch_transcript_api(video_id, lang=lang)
    if fallback["segments"]:
        return fallback

    # Both failed. Prefer yt-dlp's error message since it ran first.
    fallback["error"] = f"yt-dlp: {primary['error']} | api: {fallback['error']}"
    return fallback


def format_timestamp(seconds: float) -> str:
    """Convert seconds to [HH:MM:SS] or [MM:SS] format."""
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if hours > 0:
        return f"[{hours:02d}:{minutes:02d}:{secs:02d}]"
    return f"[{minutes:02d}:{secs:02d}]"


def estimate_duration(segments: list) -> str:
    """Estimate video duration from transcript segments."""
    if not segments:
        return "Unknown"
    last = segments[-1]
    total_seconds = int(last["start"] + last["duration"])
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"
