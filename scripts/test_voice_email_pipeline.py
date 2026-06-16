"""One-shot test of the voice email+image pipeline (same path the phone uses):
generate an image via OpenAI dall-e-3, then email it to Z with the image attached
using the working Gmail credential (token.pickle). Proves the plumbing end-to-end.
"""
import base64
import json
import os
import pickle
import urllib.parse
import urllib.request
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

REPO = Path(__file__).resolve().parents[1]
load_dotenv(REPO / "MARKETING_TEAM" / ".env")
TO = "sabaazeez12@gmail.com"

# 1) Generate the image (same call as _generate_image_b64)
api_key = os.getenv("OPENAI_API_KEY", "")
assert api_key, "no OPENAI_API_KEY in MARKETING_TEAM/.env"
payload = {"model": "gpt-image-1", "prompt": "A vibrant, beautiful surprise: high-quality colorful digital art, uplifting and striking.", "n": 1, "size": "1024x1024"}
req = urllib.request.Request("https://api.openai.com/v1/images/generations",
                             data=json.dumps(payload).encode(), method="POST",
                             headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
print("generating image (dall-e-3, ~15-20s)...")
with urllib.request.urlopen(req, timeout=120) as r:
    img_b64 = json.loads(r.read())["data"][0]["b64_json"]
print("image generated, bytes:", len(base64.b64decode(img_b64)))

# 2) Gmail access token from the working token.pickle
c = pickle.load(open(REPO / "MARKETING_TEAM" / "token.pickle", "rb"))
data = urllib.parse.urlencode(
    {"client_id": c.client_id, "client_secret": c.client_secret, "refresh_token": c.refresh_token, "grant_type": "refresh_token"}).encode()
tok = json.loads(urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST"), timeout=20).read())["access_token"]

# 3) Build + send the email with the image attached
msg = MIMEMultipart()
msg["To"] = TO
msg["From"] = TO
msg["Subject"] = "Oshun pipeline test: your generated image"
msg.attach(MIMEText("This is a test of the phone email pipeline. If the image is attached, the full loop works.\n\n- Oshun", "plain"))
img = MIMEImage(base64.b64decode(img_b64), _subtype="png")
img.add_header("Content-Disposition", "attachment", filename="oshun-image.png")
msg.attach(img)
raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")
resp = urllib.request.urlopen(urllib.request.Request(
    "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
    data=json.dumps({"raw": raw}).encode(),
    headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}, method="POST"), timeout=30)
print("EMAIL SENT:", json.loads(resp.read()).get("id"))
