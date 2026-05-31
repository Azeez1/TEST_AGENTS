"""Pre-process PIP video in single ffmpeg pass using concat demuxer.
Output: cut-synced + muted + scaled to 480x270 PIP-ready video."""
import json, subprocess
from pathlib import Path

ORIGINAL = r"C:\Users\sabaa\Downloads\The_DBAC_Diagnostic_Framework_(3).mp4"
KEEPS_JSON = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\videos\DBAC_Episode\src\dbac-keeps.json"
PUB = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\videos\DBAC_Episode\public")
CONCAT_LIST = PUB / ".concat_list.txt"

data = json.loads(Path(KEEPS_JSON).read_text())
keeps = data["keeps"]

src_path = ORIGINAL.replace("\\", "/")
with open(CONCAT_LIST, "w", encoding="utf-8") as f:
    for s, e in keeps:
        f.write(f"file '{src_path}'\n")
        f.write(f"inpoint {s:.3f}\n")
        f.write(f"outpoint {e:.3f}\n")

print(f"Concat list: {len(keeps)} segments")

# Single ffmpeg pass: concat demuxer -> scale to PIP -> mute -> -g 1 keyframes
out = PUB / "dbac_pip.mp4"
subprocess.run([
    "ffmpeg", "-y", "-loglevel", "info",
    "-f", "concat", "-safe", "0", "-i", str(CONCAT_LIST),
    "-vf", "scale=480:270,setsar=1",
    "-an",
    "-c:v", "libx264", "-preset", "fast", "-crf", "22",
    "-g", "1", "-keyint_min", "1",
    "-pix_fmt", "yuv420p", "-r", "30",
    str(out)
], check=True)

actual = float(subprocess.check_output([
    "ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1", str(out)
]).strip())
size_mb = out.stat().st_size / 1024 / 1024
print(f"\nPIP video: {out}")
print(f"Duration: {actual:.1f}s ({actual/60:.2f} min)")
print(f"Size: {size_mb:.1f} MB")
CONCAT_LIST.unlink()
