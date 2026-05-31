"""Parse ffmpeg silencedetect output and compute cut profiles."""
import subprocess, re, json
from pathlib import Path

SRC = r"C:\Users\sabaa\Downloads\The_DBAC_Diagnostic_Framework_(3).mp4"
OUT = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\dbac_silences.json"

# Run ffmpeg silencedetect, capture all output
result = subprocess.run(
    ["ffmpeg", "-i", SRC, "-af", "silencedetect=noise=-30dB:d=0.5", "-f", "null", "-"],
    capture_output=True, text=True
)
log = result.stderr

silences = []
current_start = None
for line in log.splitlines():
    m = re.search(r"silence_start: ([\d.]+)", line)
    if m:
        current_start = float(m.group(1))
    m = re.search(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", line)
    if m and current_start is not None:
        silences.append({"s": round(current_start, 3), "e": round(float(m.group(1)), 3),
                         "d": round(float(m.group(2)), 3)})
        current_start = None

# Bucket by duration
buckets = {"0.5-1.0s": [], "1.0-2.0s": [], "2.0-5.0s": [], "5.0+s": []}
for s in silences:
    if s["d"] < 1.0: buckets["0.5-1.0s"].append(s)
    elif s["d"] < 2.0: buckets["1.0-2.0s"].append(s)
    elif s["d"] < 5.0: buckets["2.0-5.0s"].append(s)
    else: buckets["5.0+s"].append(s)

print(f"Total silences detected: {len(silences)}")
print(f"Total silence time: {sum(s['d'] for s in silences):.1f}s\n")
print(f"{'Bucket':<12} {'Count':>5} {'Total time':>12}")
for name, items in buckets.items():
    total = sum(s["d"] for s in items)
    print(f"{name:<12} {len(items):>5} {total:>10.1f}s")

# Compute reduction for each profile
def estimate_reduction(min_dur, breath):
    cut = sum(max(0, s["d"] - breath) for s in silences if s["d"] >= min_dur)
    return cut

print("\n=== Cut profile estimates ===")
print(f"{'Profile':<25} {'Min silence':>12} {'Breath':>8} {'Cuts':>6} {'Time saved':>12}")
profiles = [
    ("A. Aggressive",      0.5, 0.25),
    ("B. Moderate (rec)",  1.0, 0.40),
    ("C. Conservative",    2.0, 0.50),
]
for name, min_d, breath in profiles:
    cuts = sum(1 for s in silences if s["d"] >= min_d)
    saved = estimate_reduction(min_d, breath)
    new_dur = 1105 - saved
    print(f"{name:<25} {min_d:>11.1f}s {breath:>7.2f}s {cuts:>6} {saved:>10.1f}s  -> {new_dur/60:.1f} min ({saved/1105*100:.1f}% cut)")

Path(OUT).write_text(json.dumps(silences, indent=2), encoding="utf-8")
print(f"\nSaved silence list: {OUT}")
