"""Prepare Remotion-ready assets for DBAC composite.
- dbac_slides.mp4: cut-synced original recording, 1920x1080, MUTED, low bitrate (BASE layer)
- dbac_avatar.mp4: HeyGen video re-encoded smaller (PIP source)
"""
import json, subprocess, shutil
from pathlib import Path

ORIGINAL = r"C:\Users\sabaa\Downloads\The_DBAC_Diagnostic_Framework_(3).mp4"
HEYGEN_FRESH = r"C:\Users\sabaa\Downloads\YOUTUBE VID1 _1080p.mp4"
KEEPS_JSON = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\videos\DBAC_Episode\src\dbac-keeps.json"
PUB = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\videos\DBAC_Episode\public")

PUB.mkdir(parents=True, exist_ok=True)

# Clean stale files
for old in ["dbac_heygen.mp4", "dbac_original.mp4", "dbac_pip.mp4"]:
    p = PUB / old
    if p.exists():
        p.unlink()
        print(f"Removed stale: {old}")

# ===== Stage 1: cut-synced slides (BASE), 1920x1080, muted =====
data = json.loads(Path(KEEPS_JSON).read_text())
keeps = data["keeps"]
print(f"\nKeeps: {len(keeps)} segments")

list_path = PUB / ".concat_slides.txt"
src_norm = ORIGINAL.replace("\\", "/")
with open(list_path, "w", encoding="utf-8") as f:
    for s, e in keeps:
        f.write(f"file '{src_norm}'\ninpoint {s:.3f}\noutpoint {e:.3f}\n")

slides_out = PUB / "dbac_slides.mp4"
print("\nStage 1: cut-syncing slides at 1920x1080, muted, with -g 1 keyframes...")
subprocess.run([
    "ffmpeg", "-y", "-loglevel", "warning",
    "-f", "concat", "-safe", "0", "-i", str(list_path),
    "-vf", "scale=1920:1080,setsar=1",
    "-an",
    "-c:v", "libx264", "-preset", "fast", "-crf", "23",
    "-g", "1", "-keyint_min", "1",
    "-pix_fmt", "yuv420p", "-r", "30",
    str(slides_out)
], check=True)
list_path.unlink()
print(f"  -> {slides_out.name} ({slides_out.stat().st_size/1024/1024:.0f} MB)")

# ===== Stage 2: re-encode HeyGen avatar smaller, with -g 1 =====
avatar_out = PUB / "dbac_avatar.mp4"
print("\nStage 2: re-encoding HeyGen avatar at lower bitrate, with -g 1...")
subprocess.run([
    "ffmpeg", "-y", "-loglevel", "warning",
    "-i", HEYGEN_FRESH,
    "-vf", "scale=540:960",  # halve resolution: still plenty for PIP at 270x480
    "-c:v", "libx264", "-preset", "fast", "-crf", "23",
    "-g", "1", "-keyint_min", "1",
    "-pix_fmt", "yuv420p", "-r", "30",
    "-c:a", "aac", "-b:a", "192k",
    str(avatar_out)
], check=True)
print(f"  -> {avatar_out.name} ({avatar_out.stat().st_size/1024/1024:.0f} MB)")

print("\nDone. Both assets ready for Remotion.")
print(f"  Base:   public/dbac_slides.mp4")
print(f"  PIP:    public/dbac_avatar.mp4")
