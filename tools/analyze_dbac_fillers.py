"""Find filler words, dead air, and false starts in DBAC transcript."""
import json
import re
from pathlib import Path

SRC = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\dbac_transcript.json"
data = json.loads(Path(SRC).read_text(encoding="utf-8"))
words = data["words"]
total_dur = data["duration"]

# Filler categories
hard_fillers = {"um", "uh", "ah", "er", "hmm"}
soft_fillers = {"basically", "literally", "actually"}
verbal_pauses = {"like", "right", "you know", "so", "well", "i mean"}

# Normalize word text
def norm(w):
    return w["w"].strip().lower().rstrip(",.?!").lstrip()

filler_words_found = []
dead_air_segments = []
repeated_words = []

prev_word = None
for i, w in enumerate(words):
    text = norm(w)
    # Hard fillers
    if text in hard_fillers:
        filler_words_found.append({
            "type": "hard_filler",
            "word": w["w"].strip(),
            "start": w["s"],
            "end": w["e"],
        })
    # Soft fillers — only when isolated/verbal-stall, not always
    elif text in soft_fillers:
        filler_words_found.append({
            "type": "soft_filler",
            "word": w["w"].strip(),
            "start": w["s"],
            "end": w["e"],
        })
    # Repeated word (same word within 0.6 sec)
    if prev_word and norm(prev_word) == text and text not in {"the", "a", "to", "of"} and (w["s"] - prev_word["e"]) < 0.6:
        repeated_words.append({
            "type": "repeated",
            "word": text,
            "start": prev_word["s"],
            "end": w["e"],
        })
    # Dead air — gap between words > 1.0 sec
    if prev_word and (w["s"] - prev_word["e"]) > 1.0:
        dead_air_segments.append({
            "type": "dead_air",
            "start": prev_word["e"],
            "end": w["s"],
            "duration": round(w["s"] - prev_word["e"], 2),
        })
    prev_word = w

# Summary
total_filler_time = sum(f["end"] - f["start"] for f in filler_words_found)
total_dead_air = sum(d["duration"] for d in dead_air_segments)
total_repeated = sum(r["end"] - r["start"] for r in repeated_words)

print(f"=== DBAC Recording Analysis ({total_dur:.1f}s = {total_dur/60:.1f} min) ===\n")
print(f"Hard fillers (um/uh/ah/er/hmm):  {sum(1 for f in filler_words_found if f['type']=='hard_filler'):>4}")
print(f"Soft fillers (basically/literally/actually):  {sum(1 for f in filler_words_found if f['type']=='soft_filler'):>4}")
print(f"Dead air > 1.0 sec:              {len(dead_air_segments):>4}")
print(f"Repeated words:                   {len(repeated_words):>4}")
print()
print(f"Time potentially recoverable:")
print(f"  Hard+soft fillers:  ~{total_filler_time:.1f}s")
print(f"  Dead air:           ~{total_dead_air:.1f}s")
print(f"  Repeated words:     ~{total_repeated:.1f}s")
print(f"  TOTAL CONSERVATIVE: ~{total_filler_time + total_dead_air + total_repeated:.1f}s ({(total_filler_time + total_dead_air + total_repeated)/total_dur*100:.1f}% reduction)")
print()

# Top 10 dead air segments by duration
print("=== Top 10 longest dead air gaps ===")
for d in sorted(dead_air_segments, key=lambda x: -x["duration"])[:10]:
    mins = int(d["start"] // 60)
    secs = d["start"] % 60
    print(f"  {mins:>2}:{secs:05.2f}  -> {d['duration']:.2f}s gap")

# First 20 hard fillers
print("\n=== First 20 hard fillers ===")
for f in [x for x in filler_words_found if x["type"] == "hard_filler"][:20]:
    mins = int(f["start"] // 60)
    secs = f["start"] % 60
    print(f"  {mins:>2}:{secs:05.2f}  {f['word']!r}")

# Save cut list
cuts = filler_words_found + dead_air_segments + repeated_words
cuts.sort(key=lambda x: x["start"])
out_cuts = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\dbac_cuts.json"
Path(out_cuts).write_text(json.dumps(cuts, indent=2), encoding="utf-8")
print(f"\nCut list saved: {out_cuts}")
print(f"Total cut events: {len(cuts)}")
