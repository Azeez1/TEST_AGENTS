"""Generate one Seedance 2.5 video with the official Higgsfield Python SDK.

Run from the repository root with the locked uv environment:
    uv run --locked python ENGINEERING_TEAM/tools/higgsfield_seedance_2_5/main.py
"""

import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import higgsfield_client
from dotenv import load_dotenv


MODEL_ID = "bytedance/seedance-2.5/text-to-video"
ENV_FILE = Path(__file__).resolve().parents[3] / ".env.local"


class GenerationStopped(Exception):
    """The request reached a terminal state without a generated video."""


def main() -> int:
    """Submit one request and print the video URL only after completion."""
    load_dotenv(ENV_FILE, override=False)
    credentials = os.environ.get("HF_KEY", "")
    if (
        not credentials
        or credentials.count(":") != 1
        or not all(credentials.split(":"))
        or credentials == "YOUR_KEY_ID:YOUR_KEY_SECRET"
    ):
        print(
            "Set HF_KEY in the Git-ignored .env.local as key-id:key-secret "
            "with exactly one colon.",
            file=sys.stderr,
        )
        return 2

    completed = False

    def on_queue_update(status: higgsfield_client.Status) -> None:
        nonlocal completed
        if isinstance(status, higgsfield_client.Failed):
            raise GenerationStopped("failed")
        if isinstance(status, higgsfield_client.Cancelled):
            raise GenerationStopped("canceled")
        if isinstance(status, higgsfield_client.NSFW):
            raise GenerationStopped("moderated")
        if isinstance(status, higgsfield_client.Completed):
            completed = True

    try:
        result = higgsfield_client.subscribe(
            MODEL_ID,
            arguments={
                "prompt": "A cinematic scene at sunset",
                "duration": 5,
                "resolution": "720p",
                "aspect_ratio": "16:9",
            },
            on_queue_update=on_queue_update,
        )
    except GenerationStopped as exc:
        print(f"Seedance request {exc}.", file=sys.stderr)
        return 1
    except Exception as exc:
        # SDK/HTTP error messages can contain request details; never print them.
        response = getattr(exc.__cause__, "response", None)
        status_code = getattr(response, "status_code", None)
        if isinstance(status_code, int) and 400 <= status_code <= 599:
            print(f"Seedance request error (HTTP {status_code}).", file=sys.stderr)
        else:
            print(f"Seedance request error ({type(exc).__name__}).", file=sys.stderr)
        return 1

    if not completed or not isinstance(result, dict):
        print("Seedance request did not return a completed result.", file=sys.stderr)
        return 1

    result_status = result.get("status")
    if isinstance(result_status, str) and result_status.lower() in {
        "failed", "canceled", "cancelled", "moderated", "nsfw"
    }:
        print(f"Seedance request {result_status.lower()}.", file=sys.stderr)
        return 1

    video = result.get("video")
    video_url = video.get("url") if isinstance(video, dict) else video
    if not isinstance(video_url, str):
        print("Completed Seedance request returned no video URL.", file=sys.stderr)
        return 1

    parsed = urlparse(video_url)
    if parsed.scheme != "https" or not parsed.netloc:
        print("Completed Seedance request returned an invalid video URL.", file=sys.stderr)
        return 1

    print(video_url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
