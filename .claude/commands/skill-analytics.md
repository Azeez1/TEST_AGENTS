Analyze skill usage data from `.claude/hooks/skill-usage.jsonl`.

Run the PowerShell analysis script:
```bash
powershell.exe -ExecutionPolicy Bypass -File ".claude/hooks/analyze-skill-usage.ps1"
```

Then present the results with additional analysis:

1. **Usage ranking** — which skills are used most and least
2. **Trend** — increasing or decreasing usage over time
3. **Recommendations:**
   - Skills to invest in (high usage, improve quality with gotchas, progressive disclosure)
   - Skills to review (never used or stale — bad description? not needed? wrong trigger words?)
   - Skills with routing problems (invoked but args suggest user wanted a different skill)

If no usage data exists yet, explain that the tracking hook needs to be enabled in settings.json and active for a period before analysis is meaningful. Show the user how to enable it by adding a PreToolUse hook for the Skill matcher.
