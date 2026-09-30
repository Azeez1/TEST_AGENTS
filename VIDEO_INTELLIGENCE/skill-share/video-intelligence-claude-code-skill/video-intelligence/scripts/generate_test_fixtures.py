#!/usr/bin/env python
"""Generate a tiny deterministic audiovisual video fixture."""

from __future__ import annotations

import argparse
import json
import math
import struct
import subprocess
import wave
from pathlib import Path


def generate(output_dir: Path) -> dict[str, object]:
    import cv2
    import imageio_ffmpeg
    import numpy as np

    output_dir.mkdir(parents=True, exist_ok=True)
    fps, duration, width, height = 24, 6.0, 640, 360
    silent = output_dir / "fixture-silent.mp4"
    audio = output_dir / "fixture-audio.wav"
    final = output_dir / "fixture.mp4"
    writer = cv2.VideoWriter(str(silent), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    if not writer.isOpened():
        raise RuntimeError("OpenCV could not create the fixture video")
    phases = [
        (0, 2, (0, 0, 255), "RED PHASE"),
        (2, 4, (0, 255, 0), "GREEN PHASE"),
        (4, 6, (255, 0, 0), "BLUE PHASE"),
    ]
    for frame_index in range(round(duration * fps)):
        seconds = frame_index / fps
        color, label = next((color, label) for start, end, color, label in phases if start <= seconds < end)
        frame = np.full((height, width, 3), color, dtype=np.uint8)
        if 3.00 <= seconds < 3.30:
            frame[:] = (0, 255, 255)
            label = "QUICK YELLOW FLASH"
        cv2.putText(frame, label, (55, 165), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 3, cv2.LINE_AA)
        cv2.putText(frame, f"T={seconds:04.2f}s", (55, 225), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
        writer.write(frame)
    writer.release()

    sample_rate = 16000
    with wave.open(str(audio), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        for index in range(round(duration * sample_rate)):
            seconds = index / sample_rate
            frequency = 440 if seconds < 2 else 660 if seconds < 4 else 880
            value = int(0.18 * 32767 * math.sin(2 * math.pi * frequency * seconds))
            wav.writeframesraw(struct.pack("<h", value))
    command = [
        imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-i", str(silent), "-i", str(audio),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(final),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg fixture mux failed: {result.stderr[-1000:]}")
    manifest = {
        "video": str(final.resolve()),
        "duration_seconds": duration,
        "fps": fps,
        "expected_visual_events": [
            {"start": 0.0, "end": 2.0, "text": "RED PHASE"},
            {"start": 2.0, "end": 4.0, "text": "GREEN PHASE"},
            {"start": 3.0, "end": 3.3, "text": "QUICK YELLOW FLASH"},
            {"start": 4.0, "end": 6.0, "text": "BLUE PHASE"},
        ],
        "expected_audio_tones_hz": [440, 660, 880],
    }
    (output_dir / "fixture-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    manifest = generate(Path(args.output_dir).expanduser().resolve())
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
