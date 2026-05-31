---
description: Check the generated Codex sidecar manifest and local ignore rules
---

# Codex Validate

Validate the generated Codex sidecar layer.

Run:

```powershell
$m = Get-Content .codex\manifest.json -Raw | ConvertFrom-Json
"agents=$($m.agents.Count)"
"skills=$($m.skills.Count)"
$m.skills | Group-Object status | Select-Object Count,Name | Format-Table -AutoSize
git check-ignore -v .codex\secrets.local.env .codex\runtime.local.json
```

Report counts and any `missing_source` skills. Do not print secret file contents.
