# ADR-0001: Use Absolute Paths in Claude Code Hook Commands

## Status

**Accepted** — 2026-05-12

## Context

Claude Code hooks are wired in `.claude/settings.local.json` under `hooks.<event>[*].hooks[*].command`. The command string is executed by the system shell when the corresponding event fires (PreToolUse, PostToolUse, Stop, etc.).

When configuring PowerShell hooks with `-File <path>`, the path can be relative or absolute. Both technically parse, but they behave very differently at runtime.

Initial wiring of two new hooks on 2026-05-12 used **relative paths**:

```
powershell -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/log_agent_run.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/output_routing_gate.ps1
```

Observation after deployment:
- Hooks ran successfully when Claude Code's working directory matched the repo root
- Hooks **silently failed** when the user invoked terminal commands from any other directory, producing this error on every command:
  > `Stop hook error: Failed with non-blocking status code: The argument '.claude/hooks/log_agent_run.ps1' to the -File parameter does not exist.`

The existing `pe_validation_gate.ps1` hook (wired earlier in the project) used an **absolute path** and worked correctly across all cwds. That entry was the proof point that absolute paths are the convention to follow.

## Decision

**Hook commands in `.claude/settings.local.json` MUST use absolute paths for the `-File` argument.**

Format:
```
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\.claude\hooks\<hook_name>.ps1"
```

## Alternatives Considered

### 1. Relative paths
Rejected. The presenting bug. Silently fails when Claude Code spawns the hook from a cwd that isn't the repo root. The failure mode is not loud — it's reported as a "non-blocking status code" warning, which is easy to dismiss while observability quietly stops working.

### 2. Wrapper script that `cd`s to the repo root first
Rejected. Adds an extra indirection layer (one PowerShell process spawns another). Fragile if the wrapper script itself is moved. Doesn't solve anything that absolute paths don't already solve. Increases startup latency on every hook fire.

### 3. Use `$PSScriptRoot` inside the hook script to resolve sibling paths
Already done where applicable, but doesn't help here. `$PSScriptRoot` is resolved **inside** the script after it's been found and loaded. The `-File` argument is resolved by PowerShell **before** the script runs — so if PowerShell can't find the file at all, `$PSScriptRoot` never gets a chance to help.

## Consequences

### Positive
- **Reliable** hook execution across all cwds, all sessions, all entry points
- **Consistent** with the established convention in `pe_validation_gate.ps1`
- **Debuggable** — no cwd dependency to reason about when a hook misbehaves
- **Auditable** — each hook entry self-documents its target script location

### Negative
- **Less portable** if the repo physically moves to a new path on disk (every hook entry needs updating)
- **Verbose** — each new hook wiring requires typing out the full path

### Mitigations
- `.claude/settings.local.json` is gitignored. Per-machine paths are the expected design — this file is **not** meant to be portable.
- If the repo moves, one find-and-replace fixes all hook entries.
- This ADR plus the OPERATOR_CHEATSHEET.md "Hook authoring rules" section codify the convention so future hook authors don't re-derive it.

## Follow-up

- Update `.claude/OPERATOR_CHEATSHEET.md` to include a "Hook authoring rules" section that references this ADR.
- When wiring any future hook, reference this ADR in the commit message or PR description.
- If a tool emerges in a future Claude Code release that resolves the cwd issue cleanly, supersede this ADR with a new one.
