#!/usr/bin/env python3
"""
YouTube Transcript → Obsidian Note

Fetches YouTube video transcripts and saves them as structured Markdown notes
in the Obsidian vault. Supports single videos, playlists, and channels.

Two-tier extraction:
  1. youtube-transcript-api (fast, free, no API key)
  2. Whisper fallback via OpenAI API (for videos without captions)

Usage:
    python fetch_transcript.py <url_or_id> [url2 ...] [options]

Options:
    --no-timestamps    Strip timestamps from output
    --lang <code>      Preferred language (default: en)
    --folder <name>    Subfolder within YouTube Transcripts
    --tags <t1,t2>     Additional tags (comma-separated)
    --no-whisper       Disable Whisper fallback
    --max-playlist <n> Max videos from playlist (default: 50)
"""

import sys
import os
import json
import argparse
import time

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Add lib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from youtube_api import extract_video_id, fetch_video_metadata, fetch_transcript, estimate_duration
from formatter import build_full_note
from obsidian import save_to_vault, DEFAULT_SUBFOLDER
from playlist import is_playlist_or_channel, extract_video_ids_from_playlist


def process_video(
    url_or_id: str,
    lang: str = "en",
    include_timestamps: bool = True,
    subfolder: str = DEFAULT_SUBFOLDER,
    extra_tags: list = None,
    use_whisper: bool = True,
) -> dict:
    """Process a single YouTube video: fetch transcript → format → save."""
    result = {
        "url": url_or_id,
        "success": False,
        "file_path": None,
        "title": None,
        "channel": None,
        "duration": None,
        "word_count": 0,
        "source": None,  # "captions" or "whisper"
        "error": None,
    }

    # Step 1: Extract video ID
    try:
        video_id = extract_video_id(url_or_id)
    except ValueError as e:
        result["error"] = str(e)
        return result

    # Step 2: Fetch metadata
    metadata = fetch_video_metadata(video_id)
    result["title"] = metadata["title"]
    result["channel"] = metadata["channel"]

    # Step 3: Fetch transcript (Tier 1: captions)
    transcript_data = fetch_transcript(video_id, lang=lang)

    # Step 4: Whisper fallback (Tier 2) if captions failed
    if (transcript_data["error"] or not transcript_data["segments"]) and use_whisper:
        from whisper_fallback import is_available, fetch_transcript_whisper

        if is_available():
            print(f"  ↳ No captions found, trying Whisper fallback for {video_id}...", file=sys.stderr)
            transcript_data = fetch_transcript_whisper(video_id)
            if not transcript_data["error"]:
                result["source"] = "whisper"
        else:
            # Keep original error, add note about Whisper
            if not os.getenv("OPENAI_API_KEY"):
                transcript_data["error"] += " (Whisper fallback unavailable: OPENAI_API_KEY not set)"

    if transcript_data["error"]:
        result["error"] = transcript_data["error"]
        return result

    if not transcript_data["segments"]:
        result["error"] = "Transcript returned empty segments."
        return result

    if result["source"] is None:
        result["source"] = "captions"

    # Step 5: Build tags
    tags = ["youtube", "transcript"]
    if result["source"] == "whisper":
        tags.append("whisper-transcribed")
    if extra_tags:
        tags.extend(extra_tags)

    # Step 6: Estimate duration
    duration = estimate_duration(transcript_data["segments"])
    result["duration"] = duration

    # Step 7: Build the note
    word_count = len(" ".join(seg["text"] for seg in transcript_data["segments"]).split())
    result["word_count"] = word_count

    note_content = build_full_note(
        title=metadata["title"],
        channel=metadata["channel"],
        channel_url=metadata.get("channel_url", ""),
        video_id=video_id,
        duration=duration,
        language=transcript_data["language"],
        is_generated=transcript_data["is_generated"],
        segments=transcript_data["segments"],
        include_timestamps=include_timestamps,
        tags=tags,
    )

    # Step 8: Save to vault
    file_path = save_to_vault(
        content=note_content,
        title=metadata["title"],
        subfolder=subfolder,
    )

    result["success"] = True
    result["file_path"] = file_path
    return result


def expand_urls(urls: list, max_playlist: int = 50) -> list:
    """Expand playlist/channel URLs into individual video URLs."""
    expanded = []
    for url in urls:
        if is_playlist_or_channel(url):
            print(f"Expanding playlist/channel: {url}", file=sys.stderr)
            try:
                videos = extract_video_ids_from_playlist(url, max_videos=max_playlist)
                print(f"  ↳ Found {len(videos)} videos", file=sys.stderr)
                for v in videos:
                    expanded.append(v["id"])
            except RuntimeError as e:
                print(f"  ↳ Failed to expand: {e}", file=sys.stderr)
        else:
            expanded.append(url)
    return expanded


def main():
    parser = argparse.ArgumentParser(description="YouTube Transcript → Obsidian")
    parser.add_argument("urls", nargs="+", help="YouTube URLs, video IDs, playlist URLs, or channel URLs")
    parser.add_argument("--no-timestamps", action="store_true", help="Strip timestamps")
    parser.add_argument("--lang", default="en", help="Preferred language (default: en)")
    parser.add_argument("--folder", default=DEFAULT_SUBFOLDER, help="Subfolder in vault")
    parser.add_argument("--tags", default="", help="Extra tags (comma-separated)")
    parser.add_argument("--no-whisper", action="store_true", help="Disable Whisper fallback")
    parser.add_argument("--max-playlist", type=int, default=50, help="Max videos from playlist (default: 50)")

    args = parser.parse_args()

    extra_tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else None
    include_timestamps = not args.no_timestamps
    use_whisper = not args.no_whisper

    # Expand playlists/channels to individual video IDs
    all_urls = expand_urls(args.urls, max_playlist=args.max_playlist)

    if not all_urls:
        print("No videos found to process.", file=sys.stderr)
        sys.exit(1)

    print(f"Processing {len(all_urls)} video(s)...\n", file=sys.stderr)

    results = []
    success_count = 0
    fail_count = 0

    for i, url in enumerate(all_urls):
        if i > 0:
            time.sleep(2)  # Rate limit: 2s delay between videos

        result = process_video(
            url_or_id=url,
            lang=args.lang,
            include_timestamps=include_timestamps,
            subfolder=args.folder,
            extra_tags=extra_tags,
            use_whisper=use_whisper,
        )
        results.append(result)

        if result["success"]:
            success_count += 1
            print(f"OK | {result['title']} | {result['word_count']:,} words | [{result['source']}] | {result['file_path']}")
        else:
            fail_count += 1
            print(f"FAIL | {url} | {result['error']}", file=sys.stderr)

    # Summary
    print(f"\n--- Done: {success_count} saved, {fail_count} failed ---", file=sys.stderr)

    # Output JSON summary for programmatic use
    print("\n---JSON---")
    print(json.dumps(results, indent=2, ensure_ascii=False))

    # Exit with error if any failed
    if fail_count > 0 and success_count == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
