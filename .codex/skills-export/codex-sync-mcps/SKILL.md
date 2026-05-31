---
name: codex-sync-mcps
description: Generate the local Codex MCP config from Claude .mcp.json.
---

# Codex Sync MCPs

Run this command from the TEST_AGENTS repo root:

```powershell
python scripts\export_codex_layer.py --write-codex-mcp-config
```

This creates `.codex/config.toml` and `.codex/mcp.generated.toml` using the MCP servers from `.mcp.json`.

Rules:
- Do not print generated config contents because it may contain local API keys.
- Report only MCP server names.
- Restart Codex after regenerating MCP config.
- Do not modify `.claude/` or `.mcp.json`.

