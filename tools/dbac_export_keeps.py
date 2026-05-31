"""Export keep windows as JSON for Remotion composition."""
import json
from pathlib import Path

TRANS = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\dbac_transcript.json"
SILS = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\dbac_silences.json"
OUT = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\videos\remotion-test\src\dbac-keeps.json"

BREATH = 0.20
MIN_SILENCE = 0.40
FILLER_PAD = 0.10
FILLERS = {"basically", "literally", "actually", "right", "like", "um", "uh", "ah", "er", "hmm"}
FILLER_PHRASES = [["you", "know"], ["i", "mean"], ["sort", "of"], ["kind", "of"]]

def norm(w):
    return w["w"].strip().lower().rstrip(",.?!").lstrip()

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
        keeps.append([round(cursor, 3), round(ks, 3)])
    cursor = max(cursor, ke)
if cursor < duration:
    keeps.append([round(cursor, 3), round(duration, 3)])
keeps = [[s, e] for s, e in keeps if e - s > 0.05]

total_keep = sum(e - s for s, e in keeps)
Path(OUT).parent.mkdir(parents=True, exist_ok=True)
Path(OUT).write_text(json.dumps({"keeps": keeps, "totalDuration": round(total_keep, 3)}, indent=2))
print(f"Keeps: {len(keeps)}")
print(f"Total cleaned duration: {total_keep:.2f}s")
print(f"Saved: {OUT}")
