"""Split cleaned DBAC audio into 5 chunks <=180s each, snapped to silence breaks."""
import subprocess, re
from pathlib import Path

SRC = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\videos\dbac_cleaned_audio.mp3"
OUT_DIR = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\videos")

MAX_SCENE = 180.0
N_PARTS = 5
SEARCH_WINDOW = 12.0  # tighter window so chunks stay under 180

# Detect silences
result = subprocess.run(
    ["ffmpeg", "-i", SRC, "-af", "silencedetect=noise=-30dB:d=0.15", "-f", "null", "-"],
    capture_output=True, text=True
)
silences = []
current_start = None
for line in result.stderr.splitlines():
    m = re.search(r"silence_start: ([\d.]+)", line)
    if m: current_start = float(m.group(1))
    m = re.search(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", line)
    if m and current_start is not None:
        silences.append({
            "s": float(current_start),
            "e": float(m.group(1)),
            "mid": (current_start + float(m.group(1))) / 2,
            "d": float(m.group(2)),
        })
        current_start = None

src_dur = float(subprocess.check_output(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
     "-of", "default=noprint_wrappers=1:nokey=1", SRC]
).strip())

# Targets evenly spaced
target_chunk = src_dur / N_PARTS
targets = [target_chunk * i for i in range(1, N_PARTS)]

def find_split(target, silences, window, max_allowed):
    candidates = [s for s in silences if abs(s["mid"] - target) <= window
                  and s["mid"] < max_allowed]
    if not candidates:
        return min(target, max_allowed - 0.5)
    return max(candidates, key=lambda s: s["d"])["mid"]

# Build split points respecting MAX_SCENE constraint
split_points = []
prev = 0.0
for t in targets:
    max_allowed = prev + MAX_SCENE
    if t > max_allowed:
        t = max_allowed - 1.0
    sp = find_split(t, silences, SEARCH_WINDOW, max_allowed)
    split_points.append(sp)
    prev = sp

boundaries = [0.0] + split_points + [src_dur]

print(f"Source duration: {src_dur:.1f}s")
print(f"Split points: {[f'{p:.1f}s' for p in split_points]}")
print()

OUT_DIR.mkdir(parents=True, exist_ok=True)
# Remove old part files first
for old in OUT_DIR.glob("dbac_part*.mp3"):
    old.unlink()

for i in range(N_PARTS):
    start, end = boundaries[i], boundaries[i+1]
    out = OUT_DIR / f"dbac_part{i+1}.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", SRC,
         "-ss", f"{start:.3f}", "-to", f"{end:.3f}",
         "-c:a", "libmp3lame", "-b:a", "192k", str(out)], check=True
    )
    actual = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(out)]
    ).strip())
    size_mb = out.stat().st_size / 1024 / 1024
    status = "OK" if actual <= MAX_SCENE else "OVER LIMIT"
    print(f"part{i+1}: {actual:6.1f}s ({actual/60:.2f} min)  {size_mb:.1f}MB  {status}")
