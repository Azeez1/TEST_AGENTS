---
name: "careful"
description: "Safety guard that blocks destructive operations (rm -rf, DROP TABLE, force-push, kubectl delete, git reset --hard). Activate this skill when working on production systems, infrastructure, database migrations, or any task where destructive commands could cause data loss. Deactivates when the skill session ends. Only blocks Bash commands \u2014 use freeze skill for file edit protection."
---

# Careful — Destructive Command Guard

## What It Does

Blocks dangerous shell commands before they execute. This is a **hard gate** — the command is intercepted and blocked by a PreToolUse hook, not just discouraged by instructions.

## Blocked Patterns

| Pattern | Why |
|---------|-----|
| `rm -rf` | Recursive forced deletion |
| `DROP TABLE` / `drop table` | Database table destruction |
| `DROP DATABASE` / `drop database` | Entire database destruction |
| `TRUNCATE TABLE` / `truncate table` | Table data wipe |
| `git push -f` / `git push --force` | Force push (rewrites remote history) |
| `git reset --hard` | Discards all uncommitted changes |
| `git clean -f` | Deletes untracked files |
| `git checkout .` / `git restore .` | Discards all working tree changes |
| `kubectl delete` | Kubernetes resource deletion |
| `force-push` | Catch-all for force push references |

## When to Activate

- Production deployments
- Infrastructure changes (Kubernetes, cloud resources)
- Database migrations or maintenance
- Cleanup scripts that touch real data
- Any task where "oops" means data loss

## When NOT to Activate

- Local development with no production access
- Read-only analysis tasks
- Content generation (no shell commands involved)

## How It Works

The hook intercepts every Bash tool call, scans the command string for blocked patterns, and either approves or blocks. If blocked, Claude sees the reason and must find a non-destructive alternative.

## Limitations

- **Only blocks Bash** — does not block Edit or Write tools. Use the `freeze` skill for file protection.
- **Pattern matching** — scans for literal strings. A creatively obfuscated command could bypass it (but Claude won't try to bypass its own safety hooks).
- **Windows only** — the hook runs via PowerShell. Requires PowerShell to be available.

See `gotchas.md` for known false positives and workarounds.
