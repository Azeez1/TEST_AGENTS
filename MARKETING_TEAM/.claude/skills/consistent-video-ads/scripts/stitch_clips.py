#!/usr/bin/env python3
"""
Stitch Clips - FFmpeg wrapper for combining multiple video clips

Combines multiple short video clips into a single longer video with optional
transitions (crossfade, hard cut) and audio normalization.

Usage:
    python stitch_clips.py --clips clip1.mp4 clip2.mp4 clip3.mp4 --output final.mp4
    python stitch_clips.py --clips clip1.mp4 clip2.mp4 --output final.mp4 --transition crossfade --duration 0.5

Requirements:
    - FFmpeg installed and in PATH
    - Python 3.7+
"""

import argparse
import subprocess
import os
import sys
import tempfile
from pathlib import Path
from typing import List, Optional


def check_ffmpeg() -> bool:
    """Check if FFmpeg is installed and accessible."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def get_video_duration(video_path: str) -> float:
    """Get duration of a video file in seconds."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


def stitch_hard_cut(clips: List[str], output: str) -> bool:
    """
    Combine clips with hard cuts (no transition).

    Uses FFmpeg concat demuxer for lossless concatenation.
    """
    # Create temporary file list
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for clip in clips:
            # FFmpeg requires forward slashes and escaped paths
            clip_path = Path(clip).absolute()
            f.write(f"file '{clip_path}'\n")
        list_file = f.name

    try:
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",  # Copy without re-encoding (fast)
            output
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}", file=sys.stderr)
            return False

        return True

    finally:
        os.unlink(list_file)


def stitch_crossfade(clips: List[str], output: str, fade_duration: float = 0.5) -> bool:
    """
    Combine clips with crossfade transitions.

    Uses FFmpeg xfade filter for smooth transitions between clips.
    """
    if len(clips) < 2:
        print("Need at least 2 clips for crossfade", file=sys.stderr)
        return False

    # Get durations for calculating offset times
    durations = [get_video_duration(clip) for clip in clips]

    # Build complex filter graph
    filter_parts = []

    # First, add all inputs
    inputs = " ".join([f"-i \"{clip}\"" for clip in clips])

    # Build xfade chain
    # For n clips, we need n-1 xfade filters
    current_output = "[0:v]"

    for i in range(1, len(clips)):
        # Calculate offset (when the fade should start)
        # Sum of previous durations minus accumulated fade durations
        offset = sum(durations[:i]) - (fade_duration * i)

        next_input = f"[{i}:v]"
        output_label = f"[v{i}]" if i < len(clips) - 1 else "[outv]"

        filter_parts.append(
            f"{current_output}{next_input}xfade=transition=fade:duration={fade_duration}:offset={offset}{output_label}"
        )

        current_output = output_label

    # Audio: concat all audio streams
    audio_inputs = "".join([f"[{i}:a]" for i in range(len(clips))])
    filter_parts.append(f"{audio_inputs}concat=n={len(clips)}:v=0:a=1[outa]")

    filter_complex = ";".join(filter_parts)

    # Build full command
    cmd = f'ffmpeg -y {inputs} -filter_complex "{filter_complex}" -map "[outv]" -map "[outa]" "{output}"'

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"FFmpeg error: {result.stderr}", file=sys.stderr)
        return False

    return True


def normalize_audio(input_path: str, output_path: str) -> bool:
    """
    Normalize audio levels using FFmpeg loudnorm filter.

    Targets -14 LUFS (standard for social media).
    """
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-af", "loudnorm=I=-14:TP=-1:LRA=11",
        "-c:v", "copy",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="Combine multiple video clips into one video"
    )
    parser.add_argument(
        "--clips",
        nargs="+",
        required=True,
        help="List of video clips to combine (in order)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output video file path"
    )
    parser.add_argument(
        "--transition",
        choices=["hardcut", "crossfade"],
        default="hardcut",
        help="Transition type between clips (default: hardcut)"
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=0.5,
        help="Transition duration in seconds (for crossfade, default: 0.5)"
    )
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="Normalize audio levels after stitching"
    )

    args = parser.parse_args()

    # Check FFmpeg
    if not check_ffmpeg():
        print("Error: FFmpeg not found. Please install FFmpeg and add to PATH.", file=sys.stderr)
        sys.exit(1)

    # Validate input files
    for clip in args.clips:
        if not os.path.exists(clip):
            print(f"Error: Clip not found: {clip}", file=sys.stderr)
            sys.exit(1)

    # Create output directory if needed
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Perform stitching
    print(f"Stitching {len(args.clips)} clips with {args.transition} transition...")

    if args.transition == "hardcut":
        success = stitch_hard_cut(args.clips, args.output)
    else:
        success = stitch_crossfade(args.clips, args.output, args.duration)

    if not success:
        print("Error: Stitching failed", file=sys.stderr)
        sys.exit(1)

    # Optional audio normalization
    if args.normalize:
        print("Normalizing audio levels...")
        temp_output = args.output + ".temp.mp4"
        os.rename(args.output, temp_output)

        if not normalize_audio(temp_output, args.output):
            print("Warning: Audio normalization failed, using unnormalized version")
            os.rename(temp_output, args.output)
        else:
            os.unlink(temp_output)

    # Get final duration
    final_duration = get_video_duration(args.output)
    print(f"Success! Output: {args.output} ({final_duration:.1f}s)")


if __name__ == "__main__":
    main()
