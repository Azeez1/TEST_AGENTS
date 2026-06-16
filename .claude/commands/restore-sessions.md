---
description: Restore the latest Claude sessions + memory bundle from OneDrive into this machine's local drawer
allowed-tools: Bash
---

Pull the newest session+memory archive from OneDrive and extract it into THIS machine's local
Claude drawer (`~/.claude/projects/...`). Run this on the machine that needs catching up
(usually the desktop). The companion command on the source machine is `/sync-sessions`.

IMPORTANT: close any other Claude Code windows on this machine first, so nothing is writing to
the session folder mid-extract. This MERGES (adds files, overwrites only same-named sessions) —
it never wipes sessions that only exist on this machine.

Run this Bash command:

```bash
KEY="c--Users-sabaa-OneDrive-Desktop-TEST-AGENTS"
DST="$HOME/OneDrive/Desktop/MEMORY/claude-sessions-backup"
LATEST=$(ls -t "$DST"/TEST_AGENTS-sessions-*.tar.gz 2>/dev/null | head -1)

if [ -z "$LATEST" ]; then
  echo "No archive found in $DST"
  echo "Has OneDrive synced it down yet? Check the folder shows a green check, not a cloud icon."
  exit 1
fi

mkdir -p "$HOME/.claude/projects"
cd "$HOME/.claude/projects"
tar -xzf "$LATEST"

echo "Restored from: $(basename "$LATEST")"
echo "Sessions now in drawer: $(ls "$HOME/.claude/projects/$KEY"/*.jsonl 2>/dev/null | wc -l) | Memory files: $(ls "$HOME/.claude/projects/$KEY"/memory/*.md 2>/dev/null | wc -l)"
echo "Next: launch Claude Code from the TEST_AGENTS folder and run  claude -r"
```

Report which archive was restored and the session/memory counts. Tell the user to launch Claude Code from `TEST_AGENTS` and run `claude -r`.
