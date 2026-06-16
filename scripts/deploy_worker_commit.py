"""Deploy a specific commit of the hermes worker (image rollback).
Reads the Render API key from the user's Claude config so no secret is on the CLI.
Usage: python deploy_worker_commit.py <commitSha>
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

key = re.search(r'"Authorization":\s*"Bearer (rnd_[A-Za-z0-9]+)"',
                (Path.home() / ".claude.json").read_text(encoding="utf-8")).group(1)
SVC = "srv-d8d3etkm0tmc73dgjimg"
commit = sys.argv[1]
body = json.dumps({"commitId": commit, "clearCache": "do_not_clear"}).encode()
req = urllib.request.Request(
    f"https://api.render.com/v1/services/{SVC}/deploys",
    data=body, method="POST",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "Accept": "application/json"},
)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read())
    print("deploy:", d.get("id"), d.get("status"), "commit", d.get("commit", {}).get("id", "")[:9])
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read().decode()[:400])
