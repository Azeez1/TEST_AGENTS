---
description: Refresh Codex sidecar layer and sync local API key env values from Claude MCP config
---

# Codex Sync Secrets

Run the local exporter with secret handoff enabled. This copies environment variable values from local `.mcp.json` into `.codex/secrets.local.env`, which is gitignored.

```powershell
python scripts\export_codex_layer.py --write-local-secrets
```

Rules:
- Do not print `.codex/secrets.local.env`.
- Do not reveal API keys, tokens, OAuth secrets, or credential values.
- Confirm only that the local env file exists and is ignored by git.
- Prefer Codex-native connectors/tools at runtime when available.
- Use `.codex/secrets.local.env` only for local script/tool fallbacks.

Do not modify `.claude/`.
