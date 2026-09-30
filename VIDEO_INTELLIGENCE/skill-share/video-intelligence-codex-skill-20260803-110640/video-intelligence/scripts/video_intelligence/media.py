"""Media acquisition, metadata, hashing, and clip extraction."""

from __future__ import annotations

import hashlib
import mimetypes
import re
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlparse


YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}


@dataclass
class MediaSource:
    original: str
    kind: str
    label: str
    identity: str
    local_path: str = ""
    direct_uri: str = ""
    mime_type: str = "video/mp4"
    duration_seconds: float = 0.0
    fps: float = 0.0
    width: int = 0
    height: int = 0
    temporary: bool = False
    caption_path: str = ""

    def public_dict(self) -> dict:
        data = asdict(self)
        if self.local_path:
            data["local_path"] = str(Path(self.local_path).resolve())
        return data


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _probe_local(path: Path, original: str | None = None, temporary: bool = False) -> MediaSource:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("opencv-python is required to inspect local video") from exc
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise ValueError(f"unable to open video: {path}")
    fps = float(capture.get(cv2.CAP_PROP_FPS) or 0)
    frames = float(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    capture.release()
    duration = frames / fps if fps > 0 else 0.0
    mime = mimetypes.guess_type(path.name)[0] or "video/mp4"
    return MediaSource(
        original=original or str(path),
        kind="local_file",
        label=path.name,
        identity=f"sha256:{_sha256(path)}",
        local_path=str(path.resolve()),
        mime_type=mime,
        duration_seconds=round(duration, 3),
        fps=round(fps, 3),
        width=width,
        height=height,
        temporary=temporary,
    )


def _is_youtube(parsed) -> bool:
    return parsed.netloc.lower().split(":")[0] in YOUTUBE_HOSTS


def _youtube_source(url: str) -> MediaSource:
    try:
        import yt_dlp
    except ImportError as exc:
        raise RuntimeError("yt-dlp is required for YouTube metadata") from exc
    options = {"quiet": True, "no_warnings": True, "skip_download": True, "noplaylist": True}
    with yt_dlp.YoutubeDL(options) as downloader:
        info = downloader.extract_info(url, download=False)
    video_id = str(info.get("id") or hashlib.sha256(url.encode()).hexdigest()[:16])
    return MediaSource(
        original=url,
        kind="youtube_url",
        label=str(info.get("title") or video_id),
        identity=f"youtube:{video_id}",
        direct_uri=url,
        mime_type="video/mp4",
        duration_seconds=float(info.get("duration") or 0),
        fps=float(info.get("fps") or 0),
        width=int(info.get("width") or 0),
        height=int(info.get("height") or 0),
    )


def _download_url(url: str) -> MediaSource:
    try:
        import yt_dlp
        import imageio_ffmpeg
    except ImportError as exc:
        raise RuntimeError("yt-dlp and imageio-ffmpeg are required to acquire remote video") from exc
    temp_dir = Path(tempfile.mkdtemp(prefix="video-intelligence-"))
    output = str(temp_dir / "source.%(ext)s")
    options = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "outtmpl": output,
        "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
        "merge_output_format": "mp4",
        "ffmpeg_location": imageio_ffmpeg.get_ffmpeg_exe(),
    }
    with yt_dlp.YoutubeDL(options) as downloader:
        info = downloader.extract_info(url, download=True)
        requested = info.get("requested_downloads") or []
        candidate = requested[0].get("filepath") if requested else downloader.prepare_filename(info)
    path = Path(candidate)
    if not path.exists():
        files = list(temp_dir.glob("source.*"))
        if not files:
            raise RuntimeError("remote video download completed without a media file")
        path = files[0]
    source = _probe_local(path, original=url, temporary=True)
    parsed = urlparse(url)
    if _is_youtube(parsed):
        from .captions import write_caption_timeline

        source.kind = "downloaded_youtube"
        source.label = str(info.get("title") or source.label)
        source.identity = f"youtube:{info.get('id', source.identity)}:{source.identity}"
        caption_path = write_caption_timeline(info, temp_dir / "source.captions.txt")
        source.caption_path = str(caption_path.resolve()) if caption_path else ""
    else:
        source.kind = "downloaded_url"
        source.label = str(info.get("title") or source.label)
    return source


def resolve_source(source: str, *, youtube_ingestion: str = "direct") -> MediaSource:
    path = Path(source).expanduser()
    if path.exists():
        if not path.is_file():
            raise ValueError("video source must be a file")
        return _probe_local(path.resolve())
    parsed = urlparse(source)
    if parsed.scheme not in {"http", "https"}:
        raise FileNotFoundError(f"video source not found: {source}")
    if _is_youtube(parsed):
        if youtube_ingestion not in {"auto", "direct", "download"}:
            raise ValueError("youtube_ingestion must be auto, direct, or download")
        if youtube_ingestion in {"auto", "download"}:
            try:
                return _download_url(source)
            except Exception:
                if youtube_ingestion == "download":
                    raise
        return _youtube_source(source)
    return _download_url(source)


def safe_slug(value: str, limit: int = 60) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")
    return (value or "video")[:limit]


def detect_rapid_change_segments(
    source: MediaSource,
    *,
    max_segments: int = 2,
    difference_threshold: float = 22.0,
) -> list[dict[str, float | str]]:
    """Find short visual excursions using paired frame-change boundaries.

    This deterministic detector does not label content. It only identifies
    candidate windows that a multimodal model should inspect at higher detail.
    """
    if not source.local_path or source.fps <= 0:
        return []
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("opencv-python is required for rapid-change detection") from exc
    capture = cv2.VideoCapture(source.local_path)
    if not capture.isOpened():
        return []
    stride = max(1, round(source.fps / 12.0))
    previous = None
    frame_index = 0
    boundaries: list[tuple[float, float]] = []
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        if frame_index % stride == 0:
            small = cv2.resize(frame, (160, 90))
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            if previous is not None:
                difference = float(cv2.absdiff(previous, gray).mean())
                if difference >= difference_threshold:
                    boundaries.append((frame_index / source.fps, difference))
            previous = gray
        frame_index += 1
    capture.release()

    candidates: list[dict[str, float | str]] = []
    for index, (first_time, first_score) in enumerate(boundaries):
        for second_time, second_score in boundaries[index + 1 :]:
            gap = second_time - first_time
            if gap > 0.75:
                break
            if 0.08 <= gap <= 0.75:
                start = max(0.0, first_time - 0.25)
                end = min(source.duration_seconds, second_time + 0.25)
                if any(not (end < item["start_seconds"] or start > item["end_seconds"]) for item in candidates):
                    continue
                candidates.append(
                    {
                        "start_seconds": round(start, 3),
                        "end_seconds": round(end, 3),
                        "reason": "paired rapid visual changes detected locally",
                        "change_score": round(max(first_score, second_score), 3),
                    }
                )
                break
        if len(candidates) >= max_segments:
            break
    return candidates


def extract_clip(
    source: MediaSource,
    start: float,
    end: float,
    destination: Path,
    *,
    slow_factor: float = 1.0,
) -> Path:
    if not source.local_path:
        raise ValueError("high-detail clips require a local media source")
    start = max(0.0, float(start))
    end = min(source.duration_seconds or float(end), float(end))
    if end <= start:
        raise ValueError("clip end must be after start")
    try:
        import imageio_ffmpeg
    except ImportError as exc:
        raise RuntimeError("imageio-ffmpeg is required for clip extraction") from exc
    destination.parent.mkdir(parents=True, exist_ok=True)
    duration = end - start
    command = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-ss", f"{start:.3f}", "-i", source.local_path]
    if slow_factor > 1:
        command.extend(["-vf", f"trim=duration={duration:.3f},setpts={float(slow_factor):g}*PTS", "-an"])
    else:
        command.extend(["-t", f"{duration:.3f}", "-c:a", "aac"])
    command.extend(["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-movflags", "+faststart", str(destination)])
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0 or not destination.exists():
        message = result.stderr[-1000:] if result.stderr else "unknown FFmpeg error"
        raise RuntimeError(f"clip extraction failed: {message}")
    return destination
