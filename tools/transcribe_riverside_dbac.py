"""Transcribe the May 1 Riverside DBAC final to extract chapter timestamps."""
from faster_whisper import WhisperModel
import json, re
from pathlib import Path

SRC = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\videos\DBAC_Episode\output\DBAC_Framework_Episode.mp4"
OUT = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\dbac_final_transcript.json"

model = WhisperModel("base.en", device="cpu", compute_type="int8")
segments, info = model.transcribe(SRC, beam_size=5, vad_filter=True)

segs_out = []
for seg in segments:
    segs_out.append({
        "start": round(seg.start, 2),
        "end": round(seg.end, 2),
        "text": seg.text.strip(),
    })

Path(OUT).write_text(json.dumps({"duration": info.duration, "segments": segs_out}, indent=2), encoding="utf-8")
print(f"Segments: {len(segs_out)}, duration: {info.duration:.2f}s")

# Find chapter markers
markers = {
    "data": [],
    "brain": [],
    "action": [],
    "check": [],
    "money rule": [],
    "money": [],
    "73%": [],
    "73 percent": [],
}
for s in segs_out:
    t = s["text"].lower()
    for key in markers:
        if key in t:
            markers[key].append((s["start"], s["text"][:120]))

print("\n=== Chapter marker hits ===")
for key, hits in markers.items():
    if hits:
        print(f"\n[{key}] ({len(hits)} hits)")
        for ts, txt in hits[:5]:
            mins = int(ts // 60)
            secs = int(ts % 60)
            print(f"  {mins}:{secs:02d}  {txt}")
