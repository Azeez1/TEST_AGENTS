# Hooks & Guardrails — Complete Reference

Every hook in this system, what it does, and when it runs.
Last updated 2026-06-02.

## What a hook is (plain version)

A hook is a small script the system runs automatically at a set moment. It reads
a description of what's about to happen (or just happened), then either lets it
through or stops it. Think of them as **staff standing at doorways** — most wave
you through; a few check your badge first.

There are four moments a hook can fire:
- **SessionStart** — when a chat session opens
- **PreToolUse** — right before an action runs (the only moment that can BLOCK)
- **PostToolUse** — right after an action finishes (cleanup / logging)
- **Stop** — when the session ends

A PreToolUse hook signals with an exit code: `0` = allow, `2` = block (its reason
is shown to the model so it can fix and retry). Almost all hooks **fail open** — if
the script itself errors, the action is allowed — so a buggy hook can never freeze
the whole system. The one exception is `pe_validation_gate` (fails closed).

---

## A. Blocking gates (PreToolUse) — the guardrails

All `$ENFORCE_MODE = $true`, all log to `LOGS/`, all fail open.

| Gate | Fires on | Blocks | Override token |
|------|----------|--------|----------------|
| `secret_scan_gate` | Write/Edit | Hardcoded API keys, OAuth secrets, JWTs, PATs | *(none — fix the secret)* |
| `destructive_bash_gate` | Bash/PowerShell | `rm -rf`, `Remove-Item -Recurse -Force`, `git reset --hard`, force-push, `git clean -f`, `DROP/TRUNCATE`, `kubectl delete`, `docker rm -f`, `dd`, `mkfs` | `[[CONFIRM-DESTRUCTIVE]]` |
| `money_rule_gate` | Bash/Write/Edit + trade tools | `place_order`, `execute_trade`, `send_wire`, `broker.buy/sell`, `live_trading=True`, Alpaca/IBKR/ccxt orders | `[[MONEY-APPROVED]]` |
| `financial_approval_gate` | Gmail send / Drive upload | Outbound valuation, DCF, deal memo, board deck, term sheet, forecast model | `[[CFO-APPROVED]]` |
| `voice_deploy_gate` | Bash/PowerShell | Voice agent go-live (cascading deploy, Retell deploy, phone-number attach) | `[[VOICE-DEPLOY-APPROVED]]` |
| `team_email_gate` | Gmail send | Do-Not-Email recipients, empty subject, >50 sends/day | `[[BULK-APPROVED]]` (rate limit only; blocklist never overridable) |
| `api_cost_gate` | marketing-tools `generate_*` | Paid video/image generation past $50/day | `[[SPEND-APPROVED]]` |
| `deploy_approval_gate` | Bash/PowerShell | `terraform apply/destroy`, `helm upgrade`, `kubectl apply`, Render/serverless/pulumi/gcloud deploy | `[[DEPLOY-APPROVED]]` or `[[DEPLOY-APPROVED:prod]]` |
| `proposal_placeholder_gate` | Write/Edit | Final PROPOSAL_TEAM deliverable still containing `[PLACEHOLDER]`, `[USER VERIFY]`, `TKTK`, `TBD`, `<FILL IN>` | `[[DRAFT-OK]]` (to save an intentional draft) |

### How overrides work
A block is a deliberate stop, not a wall. The gate tells you the token to add.
The **human** (not the agent acting alone) appends the token to the
command/email/content to consciously authorize the irreversible action. Every
override is recorded with an `[OVERRIDE]` tag in that gate's `LOGS/` file.
Example: `rm -rf ./build [[CONFIRM-DESTRUCTIVE]]`

---

## B. Pre-existing gates (were here before 2026-06-02)

| Hook | Event / fires on | What it does |
|------|------------------|--------------|
| `document_skill_gate` | PreToolUse — Read/Write/Edit/Bash/PowerShell | Won't let you create a `.docx/.pptx/.xlsx/.pdf` (direct, or via a library like python-docx/openpyxl/reportlab/pandoc) until you've Read that format's `SKILL.md` this session. Reading the SKILL.md lifts the gate. `exit 2`. |
| `voice_email_gate` | PreToolUse — `send_gmail_message` | Acts only on VOICE_TEAM intake emails. Blocks vendor-name leaks (Retell, ElevenLabs, Twilio…), missing `[Firm]` subject prefix, or missing Caller/Incident/Action-Required sections. |
| `output_routing_gate` | PreToolUse — Write/Edit/MultiEdit/NotebookEdit | Enforces the `{TEAM}/outputs/{subfolder}/` filing rule. Blocks repo-root content files, bare team-root files, bad ADR names, non-canonical docs subfolders. Flipped warn→enforce 2026-06-02. |
| `pe_validation_gate` | PreToolUse — Bash | Only on `upload_to_drive.py … *_diagnosis.pdf`. Blocks unless a fresh `.validation_pass` exists AND the PDF text contains your footer markers (verified via `pdftotext`). Tracks 3 retries per PDF, then logs to `LOGS/escalations.log` + Telegram alert. **Fails closed.** |

---

## C. Logging hooks (never block)

| Hook | Event / fires on | What it does |
|------|------------------|--------------|
| `session_start_time` | SessionStart | Prints date/time/day/timezone banner so time references stay accurate. |
| `proposal_tracker_trigger` | PostToolUse — Write to `.sbir_validation_*` | Re-runs `tools/proposal_tracker.py` to refresh `PROPOSAL_TRACKER.xlsx`. |
| `log_agent_run` | Stop | Appends one JSONL line per run to `LOGS/agent-runs.jsonl` (agent, status, duration, cost, model). |

---

## D. On disk but NOT wired (dormant features — not security)

| File | Would do | Status |
|------|----------|--------|
| `track-skill-usage.ps1` | Logs Skill invocations to `skill-usage.jsonl` | Optional; not wired. Turn on if you want usage analytics. |
| `analyze-skill-usage.ps1` | Reads that JSONL for `/skill-analytics` | Not a hook — a script the slash command runs. |

> Removed 2026-06-02: `pre_tool_use.py`, `post_tool_use.py`, their `lib/` modules,
> and `config/hook_policies.json`. They were never wired, and `pre_tool_use.py`
> blocked with `exit 1` (which the harness ignores). Their one real job —
> secret scanning — is now done properly by `secret_scan_gate.ps1`. Mirror copies
> in `.codex/hooks/` were removed too.

---

## Config knobs

- Do-Not-Email list: `.claude/hooks/config/do_not_email.txt`
- Daily email cap: `$DAILY_LIMIT` in `team_email_gate.ps1` (default 50)
- Daily media budget: `$DAILY_BUDGET` in `api_cost_gate.ps1` (default $50)
- Per-call cost estimates: `$COST` table in `api_cost_gate.ps1`
- Secret patterns: `$SECRET_PATTERNS` in `secret_scan_gate.ps1` (self-contained)
- Pause any gate: set its `$ENFORCE_MODE = $false` (becomes warn-only)

## Logs to glance at

`LOGS/`: `secret-violations.log`, `destructive-bash.log`, `money-rule.log`,
`financial-approval.log`, `voice-deploy.log`, `team-email.log`, `api-spend.log`,
`deploy-approval.log`, `proposal-placeholder.log`, `routing-violations.log`,
`escalations.log`, `agent-runs.jsonl`, `proposal-tracker.log`.

## Known limitation

Hooks see the **tool call**, not which sub-agent issued it. So gates enforce by
*operation* (what's being done), not by *actor* (which agent). A true per-agent
workspace lock can't be done reliably at the hook layer today; `output_routing_gate`
covers the path-routing half of that intent.

## Codex layer (the same guardrails, Codex-native)

Codex runs hooks too (`.codex/hooks.json`), but it names tools differently
(`command_execution`/`local_shell` not "Bash"; `apply_patch` not "Write") and
blocks with `exit 1` not `exit 2`. So the Claude `.ps1` gates copied into
`.codex/hooks/` mostly do NOT fire there (wrong tool names). The real Codex
enforcement is **`.codex/hooks/enforcement_gate.py`** — a single Python gate
wired with matcher `*` that classifies the tool itself and applies the SAME
rules + override tokens. It covers: secret_scan, destructive_bash, money_rule,
deploy_approval, voice_deploy, proposal_placeholder. It does NOT cover
financial_approval / team_email / api_cost — those gate Gmail/Drive/marketing
MCP tools that don't exist in the Codex runtime. Generated/wired by
`scripts/export_codex_layer.py` (`sync_codex_hooks()`), so `/sync-codex` keeps it
current. Edit the rules in the `.py` gate; the Claude `.ps1` gates stay the
source of truth for Claude Code.

> Unverified end-to-end: Codex's Windows sandbox currently errors on spawn
> (`windows sandbox: spawn setup refresh`), so a live in-Codex block couldn't be
> observed. The gate's logic is unit-tested 13/13 against Codex tool names.

## Wiring map

- `settings.json` → SessionStart (`session_start_time`) + PreToolUse (12 gates: the 3 pre-existing + 9 new)
- `settings.local.json` → PreToolUse (`pe_validation_gate`), PostToolUse (`proposal_tracker_trigger`), Stop (`log_agent_run`)
