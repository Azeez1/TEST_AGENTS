"""Surgically clean DBAC audio for AI avatar lip-sync.
Removes silences (>=0.5s) and filler words, keeps 0.2s breath between cuts.
Output: high-quality MP3 ready for HeyGen Avatar V."""
import json, subprocess, re
from pathlib import Path

SRC = r"C:\Users\sabaa\Downloads\The_DBAC_Diagnostic_Framework_(3).mp4"
TRANS = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\dbac_transcript.json"
SILS = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\dbac_silences.json"
OUT_MP3 = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\videos\dbac_cleaned_audio.mp3"

BREATH = 0.20          # seconds kept between cuts
MIN_SILENCE = 0.40     # silences shorter than this are kept fully
FILLER_PAD = 0.10      # extra trim around filler words

FILLERS = {
    "basically", "literally", "actually",
    "right",     # but only when standalone "right?" — handled below
    "like",      # filler context — risky, keep for now
    "um", "uh", "ah", "er", "hmm",
}
# Phrases (multi-word) to remove
FILLER_PHRASES = [
    ["you", "know"],
    ["i", "mean"],
    ["sort", "of"],
    ["kind", "of"],
]

def norm(w):
    return w["w"].strip().lower().rstrip(",.?!").lstrip()

def main():
    transcript = json.loads(Path(TRANS).read_text(encoding="utf-8"))
    silences = json.loads(Path(SILS).read_text(encoding="utf-8"))
    duration = transcript["duration"]
    words = transcript["words"]

    # Build kill list: (start, end) intervals to REMOVE
    kills = []

    # 1. Add silences >= MIN_SILENCE — keep BREATH at start, kill the rest
    for s in silences:
        if s["d"] < MIN_SILENCE:
            continue
        kill_start = s["s"] + BREATH
        kill_end = s["e"]
        if kill_end > kill_start:
            kills.append((kill_start, kill_end))

    # 2. Add single-word fillers
    for i, w in enumerate(words):
        if norm(w) in FILLERS:
            # Only trim "right" if it's a question/standalone (followed by punctuation or pause)
            if norm(w) == "right":
                next_w = words[i+1] if i+1 < len(words) else None
                if w["w"].rstrip().endswith("?") or (next_w and next_w["s"] - w["e"] > 0.3):
                    kills.append((max(0, w["s"] - FILLER_PAD), w["e"] + FILLER_PAD))
            else:
                kills.append((max(0, w["s"] - FILLER_PAD), w["e"] + FILLER_PAD))

    # 3. Multi-word fillers
    for i in range(len(words) - 1):
        for phrase in FILLER_PHRASES:
            if all(norm(words[i+j]) == phrase[j] for j in range(len(phrase)) if i+j < len(words)):
                kills.append((max(0, words[i]["s"] - FILLER_PAD),
                              words[i+len(phrase)-1]["e"] + FILLER_PAD))

    # 4. Repeated consecutive words (within 0.6s)
    for i in range(1, len(words)):
        if norm(words[i-1]) == norm(words[i]) and norm(words[i]) not in {"the","a","to","of"}:
            if words[i]["s"] - words[i-1]["e"] < 0.6:
                kills.append((words[i-1]["s"], words[i-1]["e"] + FILLER_PAD))

    # Merge overlapping kills
    kills.sort()
    merged = []
    for s, e in kills:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))

    # Compute KEEP windows = inverse of kills
    keeps = []
    cursor = 0.0
    for ks, ke in merged:
        if cursor < ks:
            keeps.append((cursor, ks))
        cursor = max(cursor, ke)
    if cursor < duration:
        keeps.append((cursor, duration))

    total_kill = sum(e - s for s, e in merged)
    total_keep = sum(e - s for s, e in keeps)
    print(f"Source duration:     {duration:.1f}s ({duration/60:.1f} min)")
    print(f"Kill segments:       {len(merged)}")
    print(f"Keep segments:       {len(keeps)}")
    print(f"Time removed:        {total_kill:.1f}s ({total_kill/60:.1f} min)")
    print(f"Output duration:     {total_keep:.1f}s ({total_keep/60:.1f} min)")
    print(f"Reduction:           {total_kill/duration*100:.1f}%")

    # Build ffmpeg filter_complex
    # aselect with multiple between() ranges
    select_expr = "+".join(f"between(t,{s:.3f},{e:.3f})" for s, e in keeps)
    filter_str = f"aselect='{select_expr}',asetpts=N/SR/TB"

    Path(OUT_MP3).parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-i", SRC,
        "-vn",
        "-af", filter_str,
        "-ac", "1",                    # mono — better for AI avatars
        "-ar", "44100",
        "-c:a", "libmp3lame", "-b:a", "192k",
        OUT_MP3,
    ]
    print(f"\nRunning ffmpeg with {len(keeps)} keep windows...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("FFMPEG ERROR:")
        print(result.stderr[-2000:])
        return
    size_mb = Path(OUT_MP3).stat().st_size / 1024 / 1024
    print(f"\nDone: {OUT_MP3}")
    print(f"Size: {size_mb:.1f} MB")

if __name__ == "__main__":
    main()
