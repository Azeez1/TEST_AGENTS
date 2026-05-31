---
name: codex-sync-secrets
description: Refresh Codex sidecar files and sync local API key env values from Claude MCP config.
---

# Codex Sync Secrets

Run this command from the TEST_AGENTS repo root:

```powershell
python scripts\export_codex_layer.py --write-local-secrets --install-global-skills --write-codex-mcp-config
```

Rules:
- Do not print `.codex/secrets.local.env`.
- Do not reveal API keys, tokens, OAuth secrets, or credential values.
- Confirm only that local env files exist and are ignored by git.
- Confirm only MCP server names, not secret values.
- Prefer Codex-native connectors/tools when available.

Do not modify `.claude/`.

