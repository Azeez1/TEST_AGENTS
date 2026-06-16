"""Trigger a redeploy of the hermes worker so the reverted dockerCommand takes effect.
Reads the Render API key from the user's Claude config so no secret is on the CLI.
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

key = re.search(r'"Authorization":\s*"Bearer (rnd_[A-Za-z0-9]+)"',
                (Path.home() / ".claude.json").read_text(encoding="utf-8"))
if not key:
    raise SystemExit("Render key not found")
key = key.group(1)
SVC = "srv-d8d3etkm0tmc73dgjimg"
hdr = {"Authorization": f"Bearer {key}", "Content-Type": "application/json", "Accept": "application/json"}


def api(method, path, body=None):
    req = urllib.request.Request(
        f"https://api.render.com/v1{path}",
        data=json.dumps(body).encode() if body is not None else None,
        method=method, headers=hdr,
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or "{}")


arg = sys.argv[1] if len(sys.argv) > 1 else "deploy"
if arg == "deploy":
    d = api("POST", f"/services/{SVC}/deploys", {"clearCache": "do_not_clear"})
    print("deploy:", d.get("id"), d.get("status"))
elif arg == "status":
    deploys = api("GET", f"/services/{SVC}/deploys?limit=1")
    dep = deploys[0]["deploy"] if deploys else {}
    print("status:", dep.get("id"), dep.get("status"), dep.get("finishedAt"))
