---
description: Bundle this project's Claude sessions + memory into a dated archive on OneDrive so the other machine can restore them
allowed-tools: Bash
---

Package this project's local Claude sessions AND memory into a single dated `.tar.gz` on OneDrive.
Run this on whichever machine has the freshest work (usually the laptop). The companion command
on the other machine is `/restore-sessions`.

Memory rides inside this same archive (it lives in the project's session folder), so this one
command carries both sessions and memory.

Run this Bash command:

```bash
KEY="c--Users-sabaa-OneDrive-Desktop-TEST-AGENTS"
SRC="$HOME/.claude/projects/$KEY"
DST="$HOME/OneDrive/Desktop/MEMORY/claude-sessions-backup"
STAMP=$(date +%Y-%m-%d)
ARCHIVE="$DST/TEST_AGENTS-sessions-$STAMP.tar.gz"

if [ ! -d "$SRC" ]; then echo "Session folder not found: $SRC"; exit 1; fi
mkdir -p "$DST"
cd "$HOME/.claude/projects"
tar -czf "$ARCHIVE" "$KEY"

# keep only the 5 newest archives
ls -t "$DST"/TEST_AGENTS-sessions-*.tar.gz 2>/dev/null | tail -n +6 | xargs -r rm -f

echo "Bundled sessions+memory -> $ARCHIVE"
echo "Size: $(du -h "$ARCHIVE" | cut -f1) | Sessions: $(ls "$SRC"/*.jsonl 2>/dev/null | wc -l) | Memory files: $(ls "$SRC"/memory/*.md 2>/dev/null | wc -l)"
echo "Now wait for OneDrive to upload (green check), then run /restore-sessions on the other machine."
```

Report the archive path, size, session count, and memory file count from the output.
Remind the user the other machine needs OneDrive to finish downloading (green check, not a cloud icon) before running `/restore-sessions`.
