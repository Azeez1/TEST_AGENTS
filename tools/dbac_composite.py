"""DBAC composite pipeline:
1. Apply same audio cuts to original recording -> muted, silence-stripped video
2. Resize to PIP size
3. Overlay on HeyGen vertical video (HeyGen audio wins)
"""
import json, subprocess, shutil
from pathlib import Path

ORIGINAL = r"C:\Users\sabaa\Downloads\The_DBAC_Diagnostic_Framework_(3).mp4"
HEYGEN = r"C:\Users\sabaa\Downloads\YOUTUBE VID1 _1080p.mp4"
TRANS = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\dbac_transcript.json"
SILS = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\dbac_silences.json"

TMP = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\dbac_video_segs")
CLEANED_PIP = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\dbac_pip_cleaned.mp4"
OUT_FINAL = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\videos\dbac_final_composite.mp4"

# Same constants as audio cleanup
BREATH = 0.20
MIN_SILENCE = 0.40
FILLER_PAD = 0.10
FILLERS = {"basically", "literally", "actually", "right", "like", "um", "uh", "ah", "er", "hmm"}
FILLER_PHRASES = [["you", "know"], ["i", "mean"], ["sort", "of"], ["kind", "of"]]

# PIP sizing for vertical 1080x1920 canvas
PIP_W = 480       # 16:9 source
PIP_H = 270
PIP_MARGIN = 24
# Bottom-right placement: x = canvas_w - pip_w - margin, y = canvas_h - pip_h - margin
PIP_X = 1080 - PIP_W - PIP_MARGIN  # 576
PIP_Y = 1920 - PIP_H - PIP_MARGIN  # 1626

def norm(w):
    return w["w"].strip().lower().rstrip(",.?!").lstrip()

def build_keeps():
    transcript = json.loads(Path(TRANS).read_text(encoding="utf-8"))
    silences = json.loads(Path(SILS).read_text(encoding="utf-8"))
    duration = transcript["duration"]
    words = transcript["words"]

    kills = []
    for s in silences:
        if s["d"] >= MIN_SILENCE:
            kills.append((s["s"] + BREATH, s["e"]))
    for i, w in enumerate(words):
        n = norm(w)
        if n in FILLERS:
            if n == "right":
                next_w = words[i+1] if i+1 < len(words) else None
                if w["w"].rstrip().endswith("?") or (next_w and next_w["s"] - w["e"] > 0.3):
                    kills.append((max(0, w["s"] - FILLER_PAD), w["e"] + FILLER_PAD))
            else:
                kills.append((max(0, w["s"] - FILLER_PAD), w["e"] + FILLER_PAD))
    for i in range(len(words) - 1):
        for phrase in FILLER_PHRASES:
            if i + len(phrase) <= len(words) and all(norm(words[i+j]) == phrase[j] for j in range(len(phrase))):
                kills.append((max(0, words[i]["s"] - FILLER_PAD),
                              words[i+len(phrase)-1]["e"] + FILLER_PAD))
    for i in range(1, len(words)):
        if norm(words[i-1]) == norm(words[i]) and norm(words[i]) not in {"the","a","to","of"}:
            if words[i]["s"] - words[i-1]["e"] < 0.6:
                kills.append((words[i-1]["s"], words[i-1]["e"] + FILLER_PAD))

    kills.sort()
    merged = []
    for s, e in kills:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))

    keeps = []
    cursor = 0.0
    for ks, ke in merged:
        if cursor < ks:
            keeps.append((cursor, ks))
        cursor = max(cursor, ke)
    if cursor < duration:
        keeps.append((cursor, duration))
    keeps = [(s, e) for s, e in keeps if e - s > 0.05]
    return keeps

def main():
    keeps = build_keeps()
    print(f"Keep segments: {len(keeps)}")
    print(f"Output duration: {sum(e-s for s,e in keeps):.1f}s")

    # Stage 1: Apply cuts to original video (muted, resized to PIP size)
    if TMP.exists():
        shutil.rmtree(TMP, ignore_errors=True)
    TMP.mkdir(parents=True, exist_ok=True)

    print(f"\nStage 1: Extracting {len(keeps)} video segments at PIP size {PIP_W}x{PIP_H}...")
    for i, (s, e) in enumerate(keeps):
        out = TMP / f"seg_{i:04d}.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error",
             "-i", ORIGINAL,
             "-ss", f"{s:.3f}", "-to", f"{e:.3f}",
             "-an",  # mute
             "-vf", f"scale={PIP_W}:{PIP_H},setsar=1",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
             "-r", "30", "-pix_fmt", "yuv420p",
             str(out)], check=True
        )
        if (i+1) % 50 == 0:
            print(f"  {i+1}/{len(keeps)}...")
    print("  Done extracting.")

    # Concat all PIP segments into one
    concat_list = TMP / "concat.txt"
    with open(concat_list, "w") as f:
        for i in range(len(keeps)):
            f.write(f"file 'seg_{i:04d}.mp4'\n")

    print("\nStage 2: Concatenating PIP video...")
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(concat_list),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-pix_fmt", "yuv420p", "-an",
         CLEANED_PIP], check=True
    )
    print(f"  PIP video: {CLEANED_PIP}")

    # Stage 3: Composite PIP on HeyGen video, use HeyGen audio
    print("\nStage 3: Compositing final output...")
    Path(OUT_FINAL).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-i", HEYGEN,
         "-i", CLEANED_PIP,
         "-filter_complex",
         f"[0:v][1:v]overlay={PIP_X}:{PIP_Y}:shortest=1[v]",
         "-map", "[v]", "-map", "0:a",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart",
         OUT_FINAL], check=True
    )

    actual = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", OUT_FINAL]).strip())
    size_mb = Path(OUT_FINAL).stat().st_size / 1024 / 1024
    print(f"\nDone: {OUT_FINAL}")
    print(f"Duration: {actual:.1f}s ({actual/60:.2f} min)")
    print(f"Size: {size_mb:.1f} MB")

if __name__ == "__main__":
    main()
