"""V2: Surgically clean DBAC audio using temp-file concat approach.
More reliable than single-filter aselect when many segments are involved."""
import json, subprocess, shutil
from pathlib import Path

SRC = r"C:\Users\sabaa\Downloads\The_DBAC_Diagnostic_Framework_(3).mp4"
TRANS = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\dbac_transcript.json"
SILS = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\dbac_silences.json"
OUT_MP3 = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\videos\dbac_cleaned_audio.mp3"
TMP = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\audio_segments")

BREATH = 0.20
MIN_SILENCE = 0.40
FILLER_PAD = 0.10
FILLERS = {"basically", "literally", "actually", "right", "like", "um", "uh", "ah", "er", "hmm"}
FILLER_PHRASES = [["you", "know"], ["i", "mean"], ["sort", "of"], ["kind", "of"]]

def norm(w):
    return w["w"].strip().lower().rstrip(",.?!").lstrip()

def main():
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

    # Filter out tiny windows
    keeps = [(s, e) for s, e in keeps if e - s > 0.05]

    total_keep = sum(e - s for s, e in keeps)
    print(f"Source duration:     {duration:.1f}s")
    print(f"Keep segments:       {len(keeps)}")
    print(f"Output duration:     {total_keep:.1f}s ({total_keep/60:.1f} min)")
    print(f"Reduction:           {(duration - total_keep)/duration*100:.1f}%")

    # Clean tmp dir
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)

    # Extract each keep window as a separate WAV (lossless intermediate)
    print(f"\nExtracting {len(keeps)} segments...")
    for i, (s, e) in enumerate(keeps):
        out = TMP / f"seg_{i:04d}.wav"
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", SRC,
             "-ss", f"{s:.3f}", "-to", f"{e:.3f}",
             "-vn", "-ac", "1", "-ar", "44100",
             "-c:a", "pcm_s16le", str(out)],
            check=True
        )
        if (i+1) % 50 == 0:
            print(f"  {i+1}/{len(keeps)}...")
    print(f"  Done extracting.")

    # Build concat list
    concat_list = TMP / "concat.txt"
    with open(concat_list, "w") as f:
        for i in range(len(keeps)):
            f.write(f"file 'seg_{i:04d}.wav'\n")

    # Concat to single MP3
    Path(OUT_MP3).parent.mkdir(parents=True, exist_ok=True)
    print(f"\nEncoding final MP3...")
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(concat_list),
         "-c:a", "libmp3lame", "-b:a", "192k",
         OUT_MP3],
        check=True
    )

    actual_dur = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", OUT_MP3]
    ).strip())
    size_mb = Path(OUT_MP3).stat().st_size / 1024 / 1024
    print(f"\nDone: {OUT_MP3}")
    print(f"Actual duration: {actual_dur:.1f}s ({actual_dur/60:.2f} min)")
    print(f"Size: {size_mb:.1f} MB")

    # Cleanup temp
    shutil.rmtree(TMP)

if __name__ == "__main__":
    main()
