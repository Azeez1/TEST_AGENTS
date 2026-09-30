---
name: codex-validate
description: Validate the generated Codex sidecar manifest and installed skill status.
---

# Codex Validate

Validate the generated Codex sidecar layer:

```powershell
python tools/project_health.py
```

For offline behavior and coverage, add `--tests`. Local hook dispatch and connector authentication require separate live verification.

Report counts and any `missing_source` skills. Do not print secret file contents.

