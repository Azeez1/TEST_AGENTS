"""Trigger a redeploy of the voice web service (to load new env vars), then poll.
Reads the Render API key from ~/.claude.json at runtime.
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

key = re.search(r'"Authorization":\s*"Bearer (rnd_[A-Za-z0-9]+)"',
                (Path.home() / ".claude.json").read_text(encoding="utf-8")).group(1)
SVC = "srv-d8bmqba8qa3s73fd15d0"
hdr = {"Authorization": f"Bearer {key}", "Content-Type": "application/json", "Accept": "application/json"}


def api(method, path, body=None):
    req = urllib.request.Request(f"https://api.render.com/v1{path}",
                                 data=json.dumps(body).encode() if body is not None else None,
                                 method=method, headers=hdr)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or "{}")


if sys.argv[1:] and sys.argv[1] == "status":
    d = api("GET", f"/services/{SVC}/deploys?limit=1")[0]["deploy"]
    print("status:", d["status"], d["id"])
else:
    d = api("POST", f"/services/{SVC}/deploys", {"clearCache": "do_not_clear"})
    print("triggered:", d.get("id"), d.get("status"))
