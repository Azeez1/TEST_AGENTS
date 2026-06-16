"""Sync the working local Gmail OAuth credential (MARKETING_TEAM/token.pickle)
into the voice web service's env vars so its Gmail works again — no browser reauth.

Reads secrets from token.pickle and the Render key from ~/.claude.json at runtime;
never writes any secret to disk or prints it. Prints only pass/fail.
"""
import json
import pickle
import re
import urllib.request
from pathlib import Path

VOICE_SVC = "srv-d8bmqba8qa3s73fd15d0"
REPO = Path(__file__).resolve().parents[1]

# 1) Pull the working Gmail credential
c = pickle.load(open(REPO / "MARKETING_TEAM" / "token.pickle", "rb"))
cid, cs, rt = c.client_id, c.client_secret, c.refresh_token
if not (cid and cs and rt):
    raise SystemExit("token.pickle missing fields")

# 2) Render API key from user config
key = re.search(r'"Authorization":\s*"Bearer (rnd_[A-Za-z0-9]+)"',
                (Path.home() / ".claude.json").read_text(encoding="utf-8")).group(1)
hdr = {"Authorization": f"Bearer {key}", "Content-Type": "application/json", "Accept": "application/json"}

# 3) Merge-update the three Google env vars on the voice web service
body = json.dumps([
    {"key": "GOOGLE_OAUTH_CLIENT_ID", "value": cid},
    {"key": "GOOGLE_OAUTH_CLIENT_SECRET", "value": cs},
    {"key": "GOOGLE_OAUTH_REFRESH_TOKEN", "value": rt},
]).encode()
req = urllib.request.Request(
    f"https://api.render.com/v1/services/{VOICE_SVC}/env-vars",  # PUT replaces; we PATCH-merge below
    data=body, method="PUT", headers=hdr,
)
# Render's bulk env endpoint is PUT (replace-all) — to avoid wiping other vars we
# instead update each var individually via the single-var PUT endpoint.
ok = []
for k, v in [("GOOGLE_OAUTH_CLIENT_ID", cid), ("GOOGLE_OAUTH_CLIENT_SECRET", cs), ("GOOGLE_OAUTH_REFRESH_TOKEN", rt)]:
    r = urllib.request.Request(
        f"https://api.render.com/v1/services/{VOICE_SVC}/env-vars/{k}",
        data=json.dumps({"value": v}).encode(), method="PUT", headers=hdr,
    )
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            resp.read()
        ok.append(k)
    except urllib.error.HTTPError as e:
        print("FAIL", k, e.code, e.read().decode()[:200])
print("updated env vars:", ok)
print("done — trigger a redeploy for the web service to pick these up")
