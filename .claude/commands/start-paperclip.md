# Start Paperclip Server (Dux Machina OS)

Boot the Paperclip company orchestrator at `http://localhost:3100`.

## What This Does

Starts the Paperclip server with PostgreSQL embedded database. The UI becomes available at `http://localhost:3100` where you can view your org chart, manage agents, assign tasks, and wake agents on demand.

## Safety

- All 63 agents use on-demand heartbeat (`intervalSec: 0, wakeOnDemand: true`) — no mass-launch
- Agents only activate when triggered by task assignment, comments, or manual wake
- No agent runs on a timer — only event-driven activation

## Usage

```
/start-paperclip          # Start the server
/start-paperclip bg       # Start in background
```

## Instructions

Start the Paperclip server. Run the command below in the user's terminal:

```bash
cd C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS && pnpm --prefix INFRASTRUCTURE/paperclip --filter @paperclipai/server exec tsx src/index.ts
```

If the user passed `bg` or `background` as an argument, run it in the background using `run_in_background: true`.

If the server fails with a PostgreSQL shared memory error:
1. Kill any existing postgres/node processes: `taskkill /F /IM postgres.exe 2>/dev/null; taskkill /F /IM node.exe 2>/dev/null`
2. Delete stale PID file: `rm -f ~/.paperclip/instances/default/db/postmaster.pid`
3. Retry the boot command

Once the server is running, tell the user:
- UI is at `http://localhost:3100`
- Agents wake on task events (assignment, comments, @mentions) — no mass-launch
- Use `/sync-paperclip` if agent instructions need updating

## Prerequisites

- Node.js and pnpm installed
- Paperclip cloned at `INFRASTRUCTURE/paperclip/`
- Dependencies installed (`pnpm install` in INFRASTRUCTURE/paperclip)
- `ANTHROPIC_API_KEY` set in environment (agents need it to run when woken)
