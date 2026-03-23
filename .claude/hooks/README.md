# Skill Usage Tracking

## What This Does

A PreToolUse hook that logs every skill invocation to a JSONL file. This lets you see which skills are popular, undertriggering, or never used — so you can invest in the right skills and remove dead weight.

## How to Enable

Add this to your `.claude/settings.json` (or `.claude/settings.local.json`) under hooks:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Skill",
        "hook_command": "powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/track-skill-usage.ps1"
      }
    ]
  }
}
```

## How to Run Analytics

Use the slash command:
```
/skill-analytics
```

Or run directly:
```bash
powershell.exe -ExecutionPolicy Bypass -File ".claude/hooks/analyze-skill-usage.ps1"
```

## Data Format

Each line in `skill-usage.jsonl` is a JSON object:
```json
{"timestamp":"2026-03-22T14:30:00.0000000-05:00","skill":"canvas-design","args":"create a poster","session_id":"abc123"}
```

## Manual Queries

Count invocations per skill:
```powershell
Get-Content .claude/hooks/skill-usage.jsonl | ConvertFrom-Json | Group-Object skill | Sort-Object Count -Descending | Format-Table Count, Name
```

Last 10 invocations:
```powershell
Get-Content .claude/hooks/skill-usage.jsonl | Select-Object -Last 10
```

## Privacy

- All data stays local on your machine
- No external transmission of any kind
- The hook NEVER blocks — always approves
- You can delete `skill-usage.jsonl` at any time

## Log Cleanup

The JSONL file grows unbounded. Periodically clean it up:
```powershell
# Keep only last 30 days
$cutoff = (Get-Date).AddDays(-30).ToString("o")
$lines = Get-Content .claude/hooks/skill-usage.jsonl | Where-Object {
    try { ($_ | ConvertFrom-Json).timestamp -gt $cutoff } catch { $false }
}
$lines | Set-Content .claude/hooks/skill-usage.jsonl
```
