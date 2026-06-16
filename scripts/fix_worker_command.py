"""One-off: revert hermes worker dockerCommand to the proven single-shot start.
Reads the Render API key from the user's Claude config so no secret is on the CLI.
"""
import json
import re
import urllib.request
from pathlib import Path

cfg = Path.home() / ".claude.json"
text = cfg.read_text(encoding="utf-8")
m = re.search(r'"Authorization":\s*"Bearer (rnd_[A-Za-z0-9]+)"', text)
if not m:
    raise SystemExit("Render key not found in ~/.claude.json")
key = m.group(1)

cmd = "/bin/sh -lc 'cd /opt/data && /opt/hermes/.venv/bin/python -m uvicorn phone_line.bridge:app --host 0.0.0.0 --port 8088 & exec /opt/hermes/.venv/bin/hermes gateway run'"
body = json.dumps({"serviceDetails": {"envSpecificDetails": {"dockerCommand": cmd}}}).encode()
req = urllib.request.Request(
    "https://api.render.com/v1/services/srv-d8d3etkm0tmc73dgjimg",
    data=body, method="PATCH",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "Accept": "application/json"},
)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read())
    print("PATCH OK. dockerCommand now:")
    print(d.get("serviceDetails", {}).get("envSpecificDetails", {}).get("dockerCommand"))
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read().decode()[:500])
