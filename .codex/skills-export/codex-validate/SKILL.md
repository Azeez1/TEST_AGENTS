---
name: codex-validate
description: Validate the generated Codex sidecar manifest and installed skill status.
---

# Codex Validate

Validate the generated Codex sidecar layer:

```powershell
$m = Get-Content .codex\manifest.json -Raw | ConvertFrom-Json
"agents=$($m.agents.Count)"
"skills=$($m.skills.Count)"
$m.skills | Group-Object status | Select-Object Count,Name | Format-Table -AutoSize
git check-ignore -v .codex\secrets.local.env .codex\runtime.local.json
git check-ignore -v .codex\config.toml .codex\mcp.generated.toml
```

Report counts and any `missing_source` skills. Do not print secret file contents.

