"""Extract video IDs from YouTube playlists and channels using yt-dlp."""

import re
import subprocess


def is_playlist_or_channel(url: str) -> bool:
    """Check if a URL is a playlist, channel, or regular video."""
    playlist_patterns = [
        r'youtube\.com/playlist\?list=',
        r'youtube\.com/@[\w.-]+(/videos|/streams|/shorts)?$',
        r'youtube\.com/@[\w.-]+$',
        r'youtube\.com/channel/',
        r'youtube\.com/c/',
        r'youtube\.com/user/',
    ]
    return any(re.search(p, url) for p in playlist_patterns)


def extract_video_ids_from_playlist(url: str, max_videos: int = 50) -> list:
    """Extract video IDs from a playlist/channel URL (lightweight: id + title only).

    Kept for backward compatibility. For metadata-rich extraction use
    extract_videos_with_metadata().
    """
    videos = extract_videos_with_metadata(url, max_videos=max_videos)
    return [{"id": v["id"], "title": v["title"]} for v in videos]


def extract_videos_with_metadata(url: str, max_videos: int = 1000) -> list:
    """Extract videos with metadata needed for smart selection.

    Returns list of dicts:
        [{"id", "title", "view_count", "duration_sec", "upload_date"}]

    `upload_date` is YYYYMMDD string (yt-dlp default).
    Missing fields default to 0 / "" so sorting is safe.
    """
    # Tab-separated columns: id | title | views | duration | upload_date
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "%(id)s\t%(title)s\t%(view_count)s\t%(duration)s\t%(upload_date)s",
        "--no-warnings",
        "--quiet",
        "--playlist-end", str(max_videos),
        url,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,
            encoding="utf-8",
            errors="replace",
        )

        if result.stdout is None:
            raise RuntimeError(f"yt-dlp returned no output. stderr: {(result.stderr or '').strip()}")

        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp extraction failed: {result.stderr.strip()}")

        videos = []
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split("\t")
            # Pad to 5 columns in case yt-dlp returned fewer
            parts += [""] * (5 - len(parts))
            video_id, title, views_raw, duration_raw, upload_date = parts[:5]
            video_id = video_id.strip()
            if not video_id or len(video_id) != 11:
                continue

            videos.append({
                "id": video_id,
                "title": title.strip(),
                "view_count": _safe_int(views_raw),
                "duration_sec": _safe_int(duration_raw),
                "upload_date": upload_date.strip(),
            })

        return videos

    except subprocess.TimeoutExpired:
        raise RuntimeError("Channel extraction timed out (180s limit)")
    except FileNotFoundError:
        raise RuntimeError("yt-dlp not found. Install with: pip install yt-dlp")


def _safe_int(value: str) -> int:
    """Parse int from yt-dlp output; handles '2059', '2059.0', 'NA', empty, None."""
    if value is None:
        return 0
    value = str(value).strip()
    if not value or value == "NA":
        return 0
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def select_videos(
    videos: list,
    top: int = 0,
    recent: int = 0,
    longest: int = 0,
    min_duration_sec: int = 0,
) -> list:
    """Select a subset of videos using top/recent/longest strategies.

    When multiple strategies are provided, results are unioned and deduped
    by video_id. Order of appearance is stable: top → recent → longest.

    Args:
        videos: list of dicts from extract_videos_with_metadata()
        top: pick N most-viewed
        recent: pick N most recent by upload_date
        longest: pick N longest by duration_sec
        min_duration_sec: filter out anything shorter than this (applied first)

    Returns filtered, deduped list. If all selection params are 0, returns
    the original (filtered) list unchanged.
    """
    filtered = [v for v in videos if v["duration_sec"] >= min_duration_sec]

    if top == 0 and recent == 0 and longest == 0:
        return filtered

    seen = set()
    selected = []

    def _add(pool):
        for v in pool:
            if v["id"] not in seen:
                seen.add(v["id"])
                selected.append(v)

    if top > 0:
        _add(sorted(filtered, key=lambda v: v["view_count"], reverse=True)[:top])
    if recent > 0:
        _add(sorted(filtered, key=lambda v: v["upload_date"], reverse=True)[:recent])
    if longest > 0:
        _add(sorted(filtered, key=lambda v: v["duration_sec"], reverse=True)[:longest])

    return selected
