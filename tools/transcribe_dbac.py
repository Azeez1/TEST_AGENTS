"""Transcribe DBAC framework recording with word-level timestamps."""
from faster_whisper import WhisperModel
import json
from pathlib import Path

SRC = r"C:\Users\sabaa\Downloads\The_DBAC_Diagnostic_Framework_(3).mp4"
OUT = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\dbac_transcript.json"

model = WhisperModel("base.en", device="cpu", compute_type="int8")
segments, info = model.transcribe(SRC, word_timestamps=True, beam_size=5, vad_filter=True)

all_words = []
segs_out = []
for seg in segments:
    words = [{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2)} for w in (seg.words or [])]
    all_words.extend(words)
    segs_out.append({
        "start": round(seg.start, 2),
        "end": round(seg.end, 2),
        "text": seg.text.strip(),
        "words": words,
    })

Path(OUT).parent.mkdir(parents=True, exist_ok=True)
Path(OUT).write_text(
    json.dumps({"duration": info.duration, "words": all_words, "segments": segs_out}, indent=2),
    encoding="utf-8",
)
print(f"Words: {len(all_words)}, segments: {len(segs_out)}, duration: {info.duration:.2f}s")
print(f"Transcript: {OUT}")
