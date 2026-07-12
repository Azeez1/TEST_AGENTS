# Start Paperclip Server (Dux Machina OS)

Boot the Paperclip company orchestrator at `http://localhost:3100`.

## What This Does

Starts the Paperclip server with PostgreSQL embedded database in a NEW PowerShell window that persists independently of this Claude Code session. The UI becomes available at `http://localhost:3100` where you can view your org chart, manage agents, assign tasks, and wake agents on demand.

The server runs in its own dedicated PowerShell window. Closing that window stops the server.

## Safety

- 72 of 73 agents use on-demand heartbeat (`intervalSec: 0, wakeOnDemand: true`) — no mass-launch (see CLAUDE.md — single source of truth for roster counts)
- CEO agent runs on a 15-minute cron (`intervalSec: 900`) — orchestrates worker agents
- Workers only activate when triggered by CEO assignment, comments, or manual wake
- Adapter uses `claude_local` — routes through Claude Code subscription, no API key metering

## Usage

```
/start-paperclip          # Start the server in a new PowerShell window
```

## Instructions

Run these steps via the Bash tool in this exact order:

### Step 1: Check if server is ALREADY running (and don't kill it if so)

CRITICAL: Do NOT blindly run `taskkill /F /IM tsx.exe` — that nukes the user's existing Paperclip server if it's already running. Always check first.

```bash
# Check if port 3100 is already listening (server already up)
if netstat -ano | grep -qE ':3100.*LISTEN'; then
  echo "Paperclip server is ALREADY running on port 3100. No action needed."
  exit 0
fi

# Only run cleanup if port is FREE (server isn't running)
rm -f /c/Users/sabaa/.paperclip/instances/default/db/postmaster.pid
```

Only kill postgres/tsx processes if the user explicitly asks for a hard restart OR if there's a stale postmaster.pid conflict that's preventing startup. Default behavior: leave existing processes alone.

### Step 2: Start server via bash + nohup (works reliably — Node 22 portable in PATH)

The pattern that works on Windows is plain bash + nohup with Node 22 portable in PATH. Earlier attempts to use PowerShell `Start-Process` spawns from bash were unreliable; this direct approach works.

```bash
export PATH="/c/Users/sabaa/.local/node22:$PATH"
cd "C:/Users/sabaa/ONEDRIVE/DESKTOP/TEST_AGENTS"
rm -f /tmp/paperclip-server.log
nohup pnpm --prefix INFRASTRUCTURE/paperclip --filter @paperclipai/server exec tsx src/index.ts > /tmp/paperclip-server.log 2>&1 &
SERVER_PID=$!
disown $SERVER_PID
echo "Server PID: $SERVER_PID"
```

Use `run_in_background: true` when running this so the bash tool returns immediately.

### Step 3: Wait + verify health (BE PATIENT — postgres needs ~90-120s on first boot)

CRITICAL: do NOT give up before 120 seconds. Embedded-postgres init + server boot takes 90-120s on this machine. Checking too early returns HTTP 000 even though the server is healthy and about to be ready.

```bash
sleep 120
netstat -ano | grep -E ':3100.*LISTEN' | head -3
curl -s -o /dev/null -w "HTTP %{http_code} on /api/companies\n" --max-time 8 http://localhost:3100/api/companies
tail -20 /tmp/paperclip-server.log
```

A 200 on `/api/companies` confirms the server is alive. The server log will show:
- `✅ Embedded PostgreSQL ready`
- `✅ Server listening on 127.0.0.1:3100`
- `✅ Migrations already applied`

### Step 4: Tell the user

Once verified, tell the user:
- ✅ Paperclip server is running at `http://localhost:3100`
- 📺 Server output is streaming in the new PowerShell window — keep it open
- 🛑 Closing that window stops the server
- 🔄 Use `/sync-paperclip` to push agent instruction updates from `.claude/agents/` into Paperclip's runtime

## Troubleshooting

**If port 3100 still isn't listening after 90 seconds**: check the new PowerShell window directly — the server may be showing an error there that didn't propagate back. Read whatever error message is in that window and report it.

**If the new PowerShell window flashes and closes immediately**: the `-NoExit` flag should prevent this. If it still happens, the spawn command itself has a syntax error — fall back to telling the user to manually run the PowerShell commands in their own terminal.

**If you see "ERR_PNPM_RECURSIVE_EXEC_FIRST_FAIL" or "tsx not recognized"**: pnpm is picking up backup workspace directories. Verify `INFRASTRUCTURE/` contains ONLY `paperclip/` (no `paperclip.OLD-*` or `paperclip.bak-*` siblings). Backups should live in `.backups/paperclip-snapshots/`.

**If postgres errors with "shared memory" or PID file conflict**: Step 1's cleanup should handle this. If it persists, manually delete `/c/Users/sabaa/.paperclip/instances/default/db/postmaster.pid` and retry.

## Prerequisites

- Portable Node 22 at `C:\Users\sabaa\.local\node22\` (see memory: `paperclip-node22-portable.md`)
- pnpm 10.14.0 (pnpm 11+ requires Node 22.13+)
- Paperclip vendored at `INFRASTRUCTURE/paperclip/` with `pnpm install` already run
- Backup snapshots stored OUTSIDE `INFRASTRUCTURE/` (e.g., `.backups/paperclip-snapshots/`)
- ANTHROPIC_API_KEY NOT required — `claude_local` adapter routes through Claude Code subscription

## Related

- `/sync-paperclip` — push `.claude/agents/*.md` updates into Paperclip's runtime instructions dir
- Memory: `paperclip-node22-portable.md` — full Node 22 portable + pnpm 10.14 setup
- Memory: `paperclip-agent-sync-workflow.md` — local vs runtime instruction stores
