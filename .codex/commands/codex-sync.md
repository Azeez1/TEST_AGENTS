---
description: Refresh the local Codex sidecar layer from Claude agents and skills
---

# Codex Sync

Run the local exporter to refresh Codex-facing agents, skills, manifest, and docs from the Claude-first repository.

```powershell
python scripts\export_codex_layer.py
```

After it runs, summarize:
- number of agents exported
- number of skills processed
- any skills marked `missing_source` in `.codex/manifest.json`

Do not modify `.claude/`.
