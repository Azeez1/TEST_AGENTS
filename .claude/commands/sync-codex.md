---
description: Mirror Claude Code agents, skills, slash commands, and MCP config into .codex/ so OpenAI Codex has the same setup
allowed-tools: Bash
---

Sync Claude Code infrastructure to the Codex layer. This re-runs `scripts/export_codex_layer.py` with full flags so OpenAI Codex CLI gets:
- All team agents (`.codex/agents/<TEAM>/<agent>.md`)
- All skills mirrored (`.codex/skills-export/`) AND installed globally (`~/.codex/skills/`) so Codex `/skills` discovers them
- Slash command mirrors (`.codex/commands/`)
- MCP server config (`.codex/config.toml` + `.codex/mcp.generated.toml`)
- Secret env file with real values (`.codex/secrets.local.env` — gitignored)
- Enforcement hooks (`.codex/hooks/*.ps1` + `.codex/hooks.json`) — the same guardrail gates that run in Claude Code, so Codex enforces secrets/money/destructive/deploy/etc. identically. The Codex-only `claude_boundary_gate.py` is preserved.
- Updated manifest mapping every source file to its Codex mirror

Run this Bash command:

```bash
cd "C:/Users/sabaa/ONEDRIVE/DESKTOP/TEST_AGENTS"
python scripts/export_codex_layer.py --write-local-secrets --install-global-skills --write-codex-mcp-config
```

Report back from the output:
- Number of agents exported (e.g., "Exported 64 agents to .codex/agents")
- Number of skills processed (e.g., "Processed 28 skills into .codex/skills-export")
- Number of skills installed globally to `~/.codex/skills/`
- Number of hook scripts synced + Codex hooks wired (e.g., "Synced 18 hook scripts and wired 17 Codex hooks")
- MCP server names wired into Codex config
- Any agents or skills that were skipped (with reason if shown)
- Confirmation that `secrets.local.env` was written without printing secret values

After running, do these two checks:
1. **Restart Codex CLI** so it discovers any newly installed skills (`/skills` listing should refresh)
2. **Spot-check one mirror** — open `.codex/agents/MARKETING_TEAM/router-agent.md` (or any recent agent you edited in Claude) and confirm the Codex version reflects your latest changes

If anything looks stale or wrong, re-run the same command — the export is idempotent and overwrites the Codex layer each time.

## When to run this

- After adding or modifying any agent in `.claude/agents/` or `{TEAM}/.claude/agents/`
- After installing a new skill in `.claude/skills/`
- After editing `.mcp.json` (MCP server changes)
- After adding or changing any hook/guardrail in `.claude/hooks/` or the hooks block of `.claude/settings.json` / `settings.local.json`
- After updating any slash command in `.claude/commands/`
- Routinely (e.g., end of any Claude Code session that touched the agent/skill/MCP layer)

## What this command does NOT do

- Does NOT modify any `.claude/` source files (Claude Code is source of truth; Codex is the mirror)
- Does NOT push to GitHub — that's a separate `git push` step
- Does NOT touch your interactive Codex usage — only updates what Codex can DISCOVER and INVOKE

## Related commands

- `/sync-memory` — copy user-level Claude memory to OneDrive for cross-desktop continuity
- `/sync-paperclip` — sync agent runtime instructions to Paperclip control plane
- `/knowledge-sync` — separate knowledge-graph sync flow
