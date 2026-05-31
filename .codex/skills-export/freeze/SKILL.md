---
name: "freeze"
description: "File protection guard that blocks Edit and Write operations outside a specified directory. Use when debugging to add logs without accidentally modifying unrelated code, or when locking down the codebase except for one specific area. Configure the allowed directory in config.json within this skill folder. Complements the careful skill which blocks destructive Bash commands."
---

# Freeze — File Protection Guard

## What It Does

Blocks all Edit and Write operations outside a specified directory. Everything inside the allowed directory is writable. Everything outside is frozen.

## How to Configure

Edit `config.json` in this skill folder to set your allowed directory:

```json
{
  "allowed_directory": "ENGINEERING_TEAM/",
  "note": "Only this directory is writable. All others are frozen."
}
```

When this skill is invoked, Claude should ask which directory to allow and update config.json accordingly.

## When to Use

- **Debugging:** You want to add console.log / print statements but Claude keeps "fixing" unrelated code it notices
- **Focused refactoring:** You're rewriting one module and want to ensure nothing else gets touched
- **Code review sessions:** Reading and commenting only, with writes locked down
- **Training:** Let a junior developer use Claude on a specific directory without risking the rest of the codebase

## When NOT to Use

- Cross-team work that legitimately needs to touch multiple directories
- Initial project setup where many files need creation
- When you want to block destructive Bash commands (use `careful` for that)

## How It Works

Two PreToolUse hooks intercept Edit and Write tool calls. Each hook reads the target file path, compares it against `config.json`'s allowed_directory, and blocks if the path doesn't match.

## Pairing with Careful

For maximum protection, activate both skills:
- **careful** blocks destructive Bash commands (rm -rf, DROP TABLE, force-push)
- **freeze** blocks file edits outside your working directory

Together they create a safe sandbox for focused work.
