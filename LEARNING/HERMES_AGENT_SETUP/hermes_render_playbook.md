# Hermes Agent → Render: 24/7 Deployment Playbook

**Goal:** Deploy a NousResearch *Hermes* agent to Render as an always-on Background Worker, reachable from your phone via Telegram, thinking on your **ChatGPT/Codex subscription** (OAuth — no metered API keys).

**Status of reference deployment:** Live. Service `srv-d8d3etkm0tmc73dgjimg`, bot `@Oshunhermes_bot`, model `gpt-5.5` via `openai-codex`.

> ⚠️ **The single biggest time-saver: START FROM THE LATEST UPSTREAM CODE.** Our first attempt deployed a fork that was **765 commits behind** NousResearch, which had a broken Codex response parser (`'NoneType' object is not iterable`). Syncing to upstream fixed it instantly. **Do step 1 below before anything else.**

---

## 0. What you're building (plain version)

- **Render Background Worker** (not a Web Service): the agent dials *out* to Telegram via long-polling, so there's no inbound port / health check to satisfy.
- **Persistent disk** at `/opt/data` (= `HERMES_HOME`): holds `auth.json` (OAuth tokens), `config.yaml`, memories, sessions, pairing. Survives restarts & redeploys.
- **Cost:** Standard worker ~$25/mo + 10 GB disk ~$2.50/mo ≈ **$27.50/mo**. Billed monthly to the card on file.

---

## 1. Prerequisites

| Need | How |
|---|---|
| GitHub fork of Hermes | Fork `github.com/NousResearch/hermes-agent` → your account (e.g. `Azeez1/hermes-agent`) |
| **Fork synced to upstream** | `git remote add upstream https://github.com/NousResearch/hermes-agent.git` → `git fetch upstream` → `git merge upstream/main` → `git push origin main` |
| Render account | render.com, card on file (Standard worker has no free tier) |
| Telegram bot | Message **@BotFather** → `/newbot` → name it → copy the **token** (`NNNNNN:AA...`) |
| ChatGPT/Codex subscription | Pro/Plus account that can use Codex (OAuth) |
| Local Hermes (for auth) | Install Hermes locally and run `hermes model` → log into **OpenAI Codex** so you have a working `auth.json` to seed |

---

## 2. STEP 1 — Sync the fork to upstream FIRST (do not skip)

```bash
cd path/to/hermes-agent
git remote -v                       # confirm origin=your fork, upstream=NousResearch
git fetch upstream
git merge upstream/main             # our only custom file is render.yaml → clean merge
git push origin main
```
Deploying stale code is the #1 cause of mysterious model-call crashes. If you start fresh from a current fork, you skip the worst bug entirely.

---

## 3. STEP 2 — The Blueprint (`render.yaml`)

Place this at the repo root. (Note: dashboard settings can override this; see the Docker Command gotcha in §6.)

```yaml
services:
  - type: worker
    name: hermes-agent
    runtime: docker
    repo: https://github.com/<you>/hermes-agent
    branch: main
    dockerfilePath: ./Dockerfile
    dockerContext: .
    # IMPORTANT: absolute venv path — NOT bare "gateway run" or "hermes gateway run". See §6.
    dockerCommand: /opt/hermes/.venv/bin/hermes gateway run
    plan: standard            # 2 GB RAM / 1 CPU — framework + chromium need headroom
    region: virginia
    autoDeploy: false         # manual control over deploys
    disk:
      name: hermes-data
      mountPath: /opt/data    # = HERMES_HOME; holds auth.json, config.yaml, memories, sessions
      sizeGB: 10
    envVars:
      - key: HERMES_HOME
        value: /opt/data
      - key: PYTHONUNBUFFERED
        value: "1"
      - key: HERMES_ALLOW_ROOT_GATEWAY   # see §6 — required because the container runs the gateway as root
        value: "1"
      - key: TELEGRAM_BOT_TOKEN
        sync: false           # paste the real value in the Render dashboard
      - key: WHATSAPP_ENABLED
        value: "false"
```

---

## 4. STEP 3 — Create the service on Render

1. Render Dashboard → **New → Blueprint** → pick your repo → **Apply**.
2. Fill the `sync:false` secret (`TELEGRAM_BOT_TOKEN`) when prompted.
3. **Gotcha:** a Blueprint creates the service at the **workspace** level; it may land under **"Ungrouped Services"** and show "Production is empty" in the *project* view. That's normal — the service exists; look in the workspace Dashboard, not the project page.

---

## 5. STEP 4 — Seed auth + config onto the disk

The disk starts empty, so the agent has no login until seeded. Two options:

**A. Seed from your local working install (fastest):** upload your local `auth.json` (with Codex OAuth tokens) and `config.yaml` to `/opt/data/` via the Render Shell.

**B. Authenticate in the container:** keep the container alive (temporarily set Docker Command to `sleep infinity`, deploy), open Render **Shell**, then:
```
HERMES_HOME=/opt/data /opt/hermes/.venv/bin/hermes model
```
Select **OpenAI Codex (OAuth)**, complete the device-code login on your phone, pick a model (`gpt-5.5`). Then set Docker Command back to the absolute gateway path and redeploy.

> The `sleep infinity` trick = a start command that keeps the container alive even when the real app would crash, so you can open a shell and debug. Indispensable.

---

## 6. THE BUG GAUNTLET (every fix we needed — read this!)

These are the exact failures we hit, in order. Knowing them turns a 6-hour debug into a 20-minute setup.

| # | Symptom (in logs) | Root cause | Fix |
|---|---|---|---|
| 1 | `Exited with status 128`, **no app output** | Start command `gateway run` — there is **no `gateway` console script** (only `hermes`) | Use `hermes gateway run`… but see #2 |
| 2 | Still `128`, silent, even with `hermes gateway run` | A stale/broken `gateway` shim on the persistent disk (`/opt/data/.local/bin` is **prepended to PATH** in the Dockerfile) shadows the real binary | **Use the ABSOLUTE path:** `dockerCommand: /opt/hermes/.venv/bin/hermes gateway run` (bypasses PATH entirely) |
| 3 | `Refusing to run the Hermes gateway as root` | Container runs the gateway as root; Hermes refuses by default | Set env `HERMES_ALLOW_ROOT_GATEWAY=1` |
| 4 | `telegram.error.InvalidToken: ... rejected by the server` | Wrong/old/rotated Telegram token | Create a fresh bot in @BotFather, set `TELEGRAM_BOT_TOKEN` |
| 5 | Bot replies *"I don't recognize you… pairing code: XXXX"* | Hermes denies all users by default (no allowlist) | In the container: `HERMES_HOME=/opt/data /opt/hermes/.venv/bin/hermes pairing approve telegram <CODE>` |
| 6 | `'NoneType' object is not iterable` on every model call (reaches `chatgpt.com/backend-api/codex`, runs ~3s, then crashes) | **Deployed build was 765 commits behind** → old Codex response parser | **Sync fork to upstream + rebuild** (§2). This is why §2 is step 1. |
| — | Config/Docker-Command changes "don't take" | Service is **Blueprint-managed**; a plain "Deploy latest commit" does **not** re-read `render.yaml`. Dashboard edits can also be reverted by a blueprint sync. | Edit the **Docker Command in Settings** directly (it persists across rebuilds), or re-sync the blueprint. Env vars + dashboard Docker Command survive rebuilds; `config.yaml` lives on the disk and survives too. |

---

## 7. STEP 5 — Pairing (first contact)

1. Once live, message your bot on Telegram. It replies with a **pairing code**.
2. In the Render Shell:
   ```
   HERMES_HOME=/opt/data /opt/hermes/.venv/bin/hermes pairing approve telegram <CODE>
   ```
3. Message again → it now recognizes you. (Pairing is stored on the disk → survives redeploys.)

---

## 8. STEP 6 — Set the model (subscription brain)

Hermes reads the model from `/opt/data/config.yaml`. To use your ChatGPT/Codex subscription:
```
provider: openai-codex
default: gpt-5.5
```
Change it in the Shell (paste-safe single line; the gateway only reads it at **startup**, so restart after):
```
sed -i 's/^  default:.*/  default: gpt-5.5/' /opt/data/config.yaml
```
Then **restart the service** (redeploy, or Render API — see §9) so it reloads.

> **Model names:** the real Codex-backend models are the `*-codex` slugs and the current `gpt-5.x` that your plan serves. `gpt-5.5` works once you're on current Hermes. If a model gives `NoneType`, it's usually the *old build*, not the model.
>
> **The bot lies about its own model.** It may say "I'm claude-opus-4-7/anthropic" — LLMs can't reliably introspect their routing. Trust the **logs / config**, not the bot's self-report.

---

## 9. DIAGNOSTICS — use the Render REST API, not the browser

The dashboard UI was flaky/slow for us; the **REST API was reliable**. Get an API key from Render Account Settings.

```powershell
$key = "rnd_..."                      # Render API key
$h = @{ Authorization = "Bearer $key"; Accept = "application/json" }
$svc = "srv-XXXXXXXX"                 # your service id
$owner = "tea-XXXXXXXX"               # from $svc.ownerId

# Current config (Docker Command, suspended state)
Invoke-RestMethod "https://api.render.com/v1/services/$svc" -Headers $h | ConvertTo-Json -Depth 6

# Recent deploys + status (live / update_failed / build_in_progress)
Invoke-RestMethod "https://api.render.com/v1/services/$svc/deploys?limit=5" -Headers $h

# Trigger a deploy (restart)
$hp = $h + @{ "Content-Type"="application/json" }
Invoke-RestMethod "https://api.render.com/v1/services/$svc/deploys" -Headers $hp -Method Post -Body '{"clearCache":"do_not_clear"}'   # clearCache:"clear" for a full cold rebuild

# Change the Docker Command via API
$body = @{ serviceDetails=@{ envSpecificDetails=@{ dockerCommand='/opt/hermes/.venv/bin/hermes gateway run' } } } | ConvertTo-Json -Depth 8
Invoke-RestMethod "https://api.render.com/v1/services/$svc" -Headers $hp -Method Patch -Body $body

# Add/update an env var
Invoke-RestMethod "https://api.render.com/v1/services/$svc/env-vars/HERMES_ALLOW_ROOT_GATEWAY" -Headers $hp -Method Put -Body '{"value":"1"}'

# Suspend / Resume (breaks a Telegram getUpdates crash-loop cleanly)
Invoke-RestMethod "https://api.render.com/v1/services/$svc/suspend" -Headers $h -Method Post
Invoke-RestMethod "https://api.render.com/v1/services/$svc/resume"  -Headers $h -Method Post

# READ LOGS for a time window (the killer feature — pulls the real runtime error)
$uri = "https://api.render.com/v1/logs?ownerId=$owner&resource=$svc&startTime=2026-01-01T00:00:00Z&endTime=2026-01-01T00:05:00Z&limit=200&direction=forward"
(Invoke-RestMethod $uri -Headers $h).logs.message
```

**Tip:** filter logs to a *tight time window* around a failed run — otherwise cached build logs (~115 lines) bury the runtime error.

---

## 10. Telegram single-poller rule (important)

A Telegram bot token allows **exactly one** `getUpdates` long-poll at a time. If a second instance polls (e.g. a copy still running on your laptop, or overlapping deploys), you get `409 Conflict` and a crash-loop.

- Kill any **local** Hermes before relying on the cloud one. On Windows it can have a **self-relaunch watchdog** + scheduled tasks — disable the tasks (admin) AND tree-kill the watchdog (`taskkill /PID <root> /F /T`).
- If the cloud service crash-loops on 409: **Suspend → wait ~60-90s (Telegram releases the poll) → Resume** = one clean instance.

---

## 11. Verification checklist (done = all green)

- [ ] Deploy status `live` (via API or dashboard)
- [ ] Logs show gateway started, Telegram connected, no `NoneType` / `Refusing` / `128`
- [ ] You're paired (`hermes pairing approve` ran)
- [ ] Bot replies to a real question in Telegram
- [ ] `config.yaml` shows `provider: openai-codex` + your chosen model
- [ ] No `api.anthropic.com` / "credit balance too low" in logs (= it's on your subscription, not a paid API)

---

## 12. Operating notes

- **Restart / reload config:** trigger a deploy (API or dashboard). Config + auth on the disk persist.
- **Roll back:** redeploy a known-good prior commit.
- **Update Hermes:** `git fetch upstream && git merge upstream/main && git push origin main` → redeploy (cold build, 10-20 min).
- **ROTATE SECRETS** after setup if any were pasted into chats/tickets: Render API key, GitHub token, Telegram bot token.
- **Durability:** keep `render.yaml` in sync with the working dashboard settings (Docker Command + `HERMES_ALLOW_ROOT_GATEWAY`) so a future blueprint sync can't silently revert you.

---

*Built from the real deployment session on 2026-05-30/31. Every fix in §6 was hit and solved live.*
