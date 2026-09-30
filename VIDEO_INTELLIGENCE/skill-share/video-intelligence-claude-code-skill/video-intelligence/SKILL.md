---
name: video-intelligence
description: Analyze, understand, compare, transcribe, and evaluate arbitrary video using native multimodal video input with timestamped evidence. Use for local video files, direct media URLs, or public YouTube URLs when the assistant needs scene timelines, visual events, dialogue with visual context, on-screen text, tutorial/SOP extraction, interviews, lectures, product demos, software QA recordings, creative or UGC analysis, compliance review, multi-video comparison, or a custom rubric. Do not use for video generation or editing.
---

# Video Intelligence

Use the deterministic runner for ingestion, provider calls, cost controls,
schema validation, caching, rendering, and remote cleanup. Keep interpretation
content-agnostic by selecting a profile instead of changing the core pipeline.

## Run the analysis

1. Identify the source, requested outcome, and owning workspace/team.
2. If the active repository contains `VIDEO_INTELLIGENCE/workspace.json`, read
   it and use its canonical directories. Otherwise choose an output directory
   inside the owning workspace's approved `outputs/` location. Never write to
   a repository root or another team's memory/output.
3. Select a profile from `references/profiles.md`. Default to `general`.
4. Run:

```powershell
python "$env:USERPROFILE\.claude\skills\video-intelligence\scripts\analyze_video.py" `
  "<video-path-or-url>" `
  --output-dir "<repo>\VIDEO_INTELLIGENCE\outputs\analyses" `
  --profile general `
  --question "<the user's requested outcome>"
```

Use `--model auto` unless the user asks for a specific model. Use `--dry-run`
to inspect metadata, routing, and estimated cost without calling Gemini.
For YouTube, the default `--youtube-ingestion auto` temporarily downloads the
source for timestamp accuracy, then deletes the local and remote copies. Use
`--youtube-ingestion direct` only when speed matters more than timeline fidelity.

## Apply the core contract

- Treat visual observations, spoken dialogue, platform captions, and model
  inference as separate evidence types.
- Require timestamps for material claims about the video's content.
- Preserve transcript provenance and uncertainty.
- Flag rapid cuts, fleeting text, unclear audio, and ambiguous identity instead
  of inventing detail.
- Let the runner perform bounded high-detail escalation when evidence is weak.
- Use `--no-escalate` only when speed or cost matters more than completeness.
- Never infer sensitive traits or identify an unknown person from appearance.
- Never claim business performance from creative content alone.
- Never publish, send, upload elsewhere, or scrape additional sources unless the
  user explicitly asks.

## Choose the right detail

- Read `references/profiles.md` when choosing or customizing a profile.
- Read `references/output-schema.md` when consuming `analysis.json` in another
  workflow or extending the provider-neutral contract.
- Read `references/model-routing.md` before changing models, token estimates,
  cost limits, or provider behavior.
- Read `references/privacy-and-rights.md` for client/private media, biometric
  risk, competitive research, retention, or publication questions.
- Read `references/evaluation.md` when testing, modifying, or benchmarking the
  skill.
- Read `references/workspace-layout.md` when a repository supplies a dedicated
  video-intelligence workspace or when organizing existing runs.

## Understand the outputs

Each run creates a timestamped directory containing:

- `manifest.json`: source, media metadata, model, provenance, usage, cost,
  cache status, warnings, and cleanup status.
- `analysis.json`: validated provider-neutral analysis.
- `report.md`: human-readable synthesis with timestamped evidence.
- `run.log`: redacted operational events; never secrets or raw credentials.
- `evidence/`: targeted clips or frames only when escalation requires them.

Treat the JSON as the machine contract and the Markdown as the human handoff.
Report partial completion when validation fails; do not disguise malformed or
unsupported output as a completed analysis.

## Validate after changes

Run all three checks after editing this skill:

```powershell
python "$env:USERPROFILE\.claude\skills\video-intelligence\scripts\test_video_intelligence.py"
python "$env:USERPROFILE\.claude\skills\video-intelligence\scripts\generate_test_fixtures.py" `
  --output-dir "$env:TEMP\video-intelligence-fixtures"
```

Use a short generated fixture for live API smoke testing. Do not use private or
client media as the first test.
