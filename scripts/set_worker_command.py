"""Set the hermes worker dockerCommand to the plain proven gateway command, then redeploy.
Reads the Render API key from the user's Claude config so no secret is on the CLI.
"""
import json
import re
import urllib.request
from pathlib import Path

key = re.search(r'"Authorization":\s*"Bearer (rnd_[A-Za-z0-9]+)"',
                (Path.home() / ".claude.json").read_text(encoding="utf-8")).group(1)
SVC = "srv-d8d3etkm0tmc73dgjimg"
hdr = {"Authorization": f"Bearer {key}", "Content-Type": "application/json", "Accept": "application/json"}
CMD = "/opt/hermes/.venv/bin/hermes gateway run"


def call(method, path, body):
    req = urllib.request.Request(f"https://api.render.com/v1{path}",
                                 data=json.dumps(body).encode(), method=method, headers=hdr)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or "{}")


d = call("PATCH", f"/services/{SVC}",
         {"serviceDetails": {"envSpecificDetails": {"dockerCommand": CMD}}})
print("dockerCommand set to:", d.get("serviceDetails", {}).get("envSpecificDetails", {}).get("dockerCommand"))
dep = call("POST", f"/services/{SVC}/deploys", {"clearCache": "do_not_clear"})
print("deploy:", dep.get("id"), dep.get("status"))
