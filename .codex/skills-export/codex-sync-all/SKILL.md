---
name: codex-sync-all
description: Refresh Codex agents, skills, local secrets, and MCP config from Claude-side files.
---

# Codex Sync All

Run this command from the TEST_AGENTS repo root:

```powershell
python scripts\export_codex_layer.py --write-local-secrets --install-global-skills --write-codex-mcp-config
```

This refreshes agents, skills, local secret handoff, and local Codex MCP config.

Rules:
- Do not print secret files or MCP config values.
- Report counts and MCP server names only.
- Restart Codex after this command so skills and MCP servers are discovered.

