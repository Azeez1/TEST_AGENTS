"""Whisper fallback for videos without captions.

Downloads audio via yt-dlp, transcribes with OpenAI Whisper API.
Requires: OPENAI_API_KEY environment variable.
"""

import os
import sys
import tempfile
import subprocess


def is_available() -> bool:
    """Check if Whisper fallback is available (yt-dlp + OpenAI key)."""
    has_key = bool(os.getenv("OPENAI_API_KEY"))
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        has_ytdlp = True
    except (FileNotFoundError, subprocess.CalledProcessError):
        has_ytdlp = False
    return has_key and has_ytdlp


def download_audio(video_id: str, output_dir: str = None) -> str:
    """Download audio from a YouTube video using yt-dlp.

    Returns the path to the downloaded audio file.
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="yt_whisper_")

    output_path = os.path.join(output_dir, f"{video_id}.mp3")
    url = f"https://www.youtube.com/watch?v={video_id}"

    cmd = [
        "yt-dlp",
        "-x",                       # Extract audio only
        "--audio-format", "mp3",
        "--audio-quality", "5",      # Medium quality (good enough for speech)
        "-o", output_path,
        "--no-playlist",
        "--quiet",
        url,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {result.stderr.strip()}")

    if not os.path.exists(output_path):
        # yt-dlp sometimes adds extension
        for ext in [".mp3", ".m4a", ".webm", ".opus"]:
            candidate = os.path.join(output_dir, f"{video_id}{ext}")
            if os.path.exists(candidate):
                return candidate
        raise FileNotFoundError(f"Audio file not found after download: {output_path}")

    return output_path


def transcribe_with_whisper(audio_path: str) -> dict:
    """Transcribe audio using OpenAI Whisper API.

    Returns dict with:
        - segments: list of {text, start, duration}
        - language: str
        - error: str or None
    """
    try:
        from openai import OpenAI

        client = OpenAI()  # Uses OPENAI_API_KEY env var

        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )

        segments = []
        if hasattr(response, "segments") and response.segments:
            for seg in response.segments:
                segments.append({
                    "text": seg.get("text", seg.text if hasattr(seg, "text") else "").strip(),
                    "start": seg.get("start", seg.start if hasattr(seg, "start") else 0),
                    "duration": (
                        seg.get("end", seg.end if hasattr(seg, "end") else 0)
                        - seg.get("start", seg.start if hasattr(seg, "start") else 0)
                    ),
                })
        else:
            # Fallback: single segment with full text
            segments.append({
                "text": response.text,
                "start": 0,
                "duration": 0,
            })

        return {
            "segments": segments,
            "language": getattr(response, "language", "en"),
            "error": None,
        }

    except Exception as e:
        return {
            "segments": [],
            "language": "en",
            "error": f"Whisper transcription failed: {str(e)}",
        }


def fetch_transcript_whisper(video_id: str) -> dict:
    """Full pipeline: download audio → transcribe with Whisper.

    Returns dict compatible with youtube_api.fetch_transcript():
        - segments: list of {text, start, duration}
        - language: str
        - is_generated: bool (always True for Whisper)
        - error: str or None
    """
    if not os.getenv("OPENAI_API_KEY"):
        return {
            "segments": [],
            "language": "en",
            "is_generated": True,
            "error": "OPENAI_API_KEY not set. Cannot use Whisper fallback.",
        }

    audio_path = None
    try:
        # Download audio
        audio_path = download_audio(video_id)

        # Transcribe
        result = transcribe_with_whisper(audio_path)

        return {
            "segments": result["segments"],
            "language": result["language"],
            "is_generated": True,  # Whisper-generated
            "error": result["error"],
        }

    except Exception as e:
        return {
            "segments": [],
            "language": "en",
            "is_generated": True,
            "error": str(e),
        }
    finally:
        # Clean up audio file
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except OSError:
                pass
