# VOICE_TEAM Webhook Receiver — Deploy Guide

Auto-trigger calendar booking + email summary on every call. **No Claude Code session needed once deployed.**

## What This Does

```
Caller dials +13363238344
     ↓
Retell agent handles intake (24/7 — already running)
     ↓
Retell fires call_analyzed webhook → THIS SERVICE
     ↓
Service extracts intake fields → creates Google Calendar event → sends Gmail summary
     ↓
Done. Your laptop can be closed the entire time.
```

## Setup — 4 Steps (~20 min)

### Step 1: Get your Google OAuth refresh token (~5 min)

You already authorized Calendar + Gmail via the google-workspace MCP. The refresh token is in your credentials file:

```
C:\Users\sabaa\.google_workspace_mcp\credentials\sabaazeez12@gmail.com.json
```

Open it. Copy the `refresh_token` value (long string). Save it — you'll paste it into Render's env vars in Step 3.

Also note your `client_id` and `client_secret` from the same file. (These match what's in your repo `.mcp.json`.)

### Step 2: Push this folder to GitHub (~3 min)

The webhook receiver lives at `VOICE_TEAM/webhook/`. Push the repo (or this subfolder) to a GitHub repository.

Also copy your firm configs to `VOICE_TEAM/webhook/firms/`:
```powershell
Copy-Item C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\VOICE_TEAM\memory\firms\*.yml C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\VOICE_TEAM\webhook\firms\
```

The webhook reads firm configs from this bundled directory.

### Step 3: Deploy on Render (~5 min)

1. Go to https://render.com → sign up (free tier)
2. New → Web Service → connect your GitHub repo
3. Root directory: `VOICE_TEAM/webhook` (or wherever you placed it)
4. Render auto-detects `render.yaml` and uses it
5. Add the secret env vars when prompted:
   - `RETELL_API_KEY` → your Retell key
   - `RETELL_WEBHOOK_SECRET` → (optional, leave empty initially)
   - `GOOGLE_OAUTH_CLIENT_ID` → from Step 1
   - `GOOGLE_OAUTH_CLIENT_SECRET` → from Step 1
   - `GOOGLE_OAUTH_REFRESH_TOKEN` → from Step 1
6. Click Deploy. ~3 minutes later, you get a URL like `https://voice-team-webhook.onrender.com`

### Step 4: Wire the Retell webhook (~2 min)

In Retell dashboard → Settings → Webhooks (or per-agent webhook config):

- URL: `https://voice-team-webhook.onrender.com/retell/webhook`
- Events: check `call_analyzed`
- Save

Done. Place a test call to +13363238344 — calendar event + email should land within 30 seconds of you hanging up.

## Verification

After deploy, test with curl:
```
curl https://voice-team-webhook.onrender.com/health
# → {"ok": true}
```

After a real call:
- Calendar event appears at the requested slot
- Email arrives in inbox
- Render logs show `event=call_analyzed status=ok`

## Local Testing (Optional)

Before deploying, test locally with ngrok:
```
cd VOICE_TEAM/webhook
python -m pip install -r requirements.txt
cp .env.example .env  # fill in values
uvicorn main:app --port 8000

# in another shell:
ngrok http 8000
# point Retell webhook at the ngrok URL
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Render logs show `Invalid signature` | RETELL_WEBHOOK_SECRET mismatch | Either remove the secret env var (skip verification) or copy the secret from Retell dashboard |
| `event=call_analyzed status=no_firm_match` | Webhook fired but phone isn't bound to a firm in your bundled `firms/` configs | Copy firm.yml into `VOICE_TEAM/webhook/firms/`, redeploy |
| `Calendar event failed: 403` | OAuth scope missing | Re-authorize via the google-workspace MCP to add calendar.events scope |
| `Email send failed: 401` | Refresh token expired | Re-authorize via the MCP, copy new refresh token to Render |
| Render service sleeps | Free tier sleeps after 15 min idle | Either upgrade to $7/mo Starter plan OR set up a cron-job.org ping to /health every 10 min |

## Security Notes

- The webhook receiver has FULL access to your Google account via the refresh token. Don't expose Render's URL publicly beyond Retell.
- The `RETELL_WEBHOOK_SECRET` provides HMAC verification — set it once you're confident the basic flow works.
- Rotate the Retell API key the first time this goes to a real client.

## Cost

- Render free tier: $0/mo (with 15-min idle sleep)
- Render Starter: $7/mo (always-on, recommended for paying clients)
- Google API: free for normal volumes
- Retell webhook: included in your existing Retell account

## Architecture Note

This service uses your **user OAuth refresh token** (gmail.com personal account). For multi-firm deployments where different firms want emails sent from their own domains, you'd graduate to:

- Per-firm OAuth (each firm authorizes their own Gmail send-as)
- OR a Google Workspace service account with domain-wide delegation (requires Workspace admin)
- OR a transactional email service (SendGrid / Postmark) with per-firm sender domains

For Sterling Legal (your demo firm), the current setup is fine — emails arrive in your inbox to validate the flow works.
