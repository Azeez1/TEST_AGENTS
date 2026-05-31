---
name: codex-sync
description: Refresh the local Codex sidecar layer from Claude agents and skills.
---

# Codex Sync

Run this command from the TEST_AGENTS repo root:

```powershell
python scripts\export_codex_layer.py
```

After it runs, report the exported agent count, processed skill count, and any `missing_source` skills in `.codex/manifest.json`.

Do not modify `.claude/`.

