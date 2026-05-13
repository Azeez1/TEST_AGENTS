---
description: Copy local Claude memory (~/.claude/projects/.../memory/) to OneDrive so the other desktop can see it
allowed-tools: Bash
---

Sync local Claude memory to OneDrive backup so the other desktop sees the latest state.

Run this Bash command:

```bash
SRC="C:/Users/sabaa/.claude/projects/C--Users-sabaa-OneDrive-Desktop-Test-Agents/memory"
DST="C:/Users/sabaa/OneDrive/Desktop/MEMORY/claude-memory"
mkdir -p "$DST"
rsync -a --delete "$SRC"/ "$DST"/ 2>/dev/null || cp -r "$SRC"/* "$DST"/
echo "Synced $(ls "$DST" | wc -l) files | $(du -sh "$DST" | cut -f1) | $(date '+%Y-%m-%d %H:%M')"
```

Report back the file count, size, and timestamp from the output.
