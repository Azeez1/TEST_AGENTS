---
name: whiteboard-explainer
description: Build polished, topic-agnostic whiteboard explainer videos using SeedDance as the primary scene generator, ElevenLabs for narration, and HyperFrames for deterministic assembly, captions, overlays, and rendering. Use when a user wants a hand-drawn explainer, visual essay, educational short, diagram-led story, or a reusable faceless video pipeline from a topic, script, article, transcript, or brief.
---

# Whiteboard Explainer

Create an organized, reviewable whiteboard-video project. SeedDance owns visual motion; ElevenLabs owns narration; HyperFrames owns final timing, readable text, captions, audio, and export.

## Non-negotiable architecture

- Treat SeedDance as the default and primary video generator.
- Use ElevenLabs for narration unless the user requests another voice source.
- Use HyperFrames for final composition and deterministic text; never rely on a video model to spell important copy.
- Keep generated work under `MARKETING_TEAM/outputs/videos/whiteboard-explainer/<project-slug>/`.
- Do not create a new repo-level team, root folder, or scattered output files.
- Do not run paid generation until the user approves the script, storyboard, voice direction, and cost preview.

## Workflow

### 1. Initialize one project

Run:

```powershell
python "$env:USERPROFILE\.codex\skills\whiteboard-explainer\scripts\init_project.py" "Project Name"
```

Use `--repo-root` when the current directory is outside TEST_AGENTS. The initializer creates one self-contained project and refuses to overwrite an existing one.

### 2. Lock the brief and script

Fill `brief/brief.json`, `brief/source.txt`, and `script/SCRIPT.md`. Make the hook legible without audio and structure the explanation as visual beats, not a lecture transcript.

Read [references/visual-system.md](references/visual-system.md) for the whiteboard grammar. For longer or sourced material, preserve claims and citations in the brief.

### 3. Build and validate the storyboard

Edit `storyboard/storyboard.json`, then run:

```powershell
python "$env:USERPROFILE\.codex\skills\whiteboard-explainer\scripts\validate_project.py" <project-path>
```

Each scene must have narration, a visual goal, a SeedDance prompt, an allowed duration, and deterministic overlay copy. Read [references/scene-schema.md](references/scene-schema.md) when changing the schema.

### 4. Preview cost and approve

Generate SeedDance request manifests without spending:

```powershell
python "$env:USERPROFILE\.codex\skills\whiteboard-explainer\scripts\plan_seedance.py" <project-path>
```

Show the user `seedance/cost-plan.json`, the total generated seconds, model tier, resolution, and estimated cost. Treat the estimate as a planning value; confirm the current provider price immediately before execution. Read [references/cost-and-gates.md](references/cost-and-gates.md).

### 5. Produce narration

First run `scripts/plan_narration.py <project-path>` and show its character count. After approval, call ElevenLabs `text_to_speech` with the locked narration, selected voice, and the project's `audio/` directory. Default to `eleven_multilingual_v2` for quality unless the user prefers lower latency. Save the response details to `audio/narration.json` and the audio as `audio/narration.mp3` or `.wav`.

Do not silently choose a cloned or branded voice. Preview a voice sample first when voice identity is not already established. Read [references/elevenlabs-narration.md](references/elevenlabs-narration.md).

### 6. Generate SeedDance scenes

Use the existing `MARKETING_TEAM/tools/mcp_server.py` SeedDance 2 integration. Prefer `first_last_frames` when a planned drawing must land on an exact final diagram; use `omni_reference` for recurring hands, characters, products, or style references; use `text_to_video` only when continuity is unimportant.

Generate one approved scene at a time, save it to `seedance/clips/scene-###.mp4`, and update `manifest.json`. Never ask SeedDance to render important words, numbers, labels, logos, or captions. Read [references/seedance-primary.md](references/seedance-primary.md).

### 7. Assemble with HyperFrames

Run:

```powershell
python "$env:USERPROFILE\.codex\skills\whiteboard-explainer\scripts\build_composition.py" <project-path>
```

This creates `composition/index.html` with SeedDance clips, narration, and deterministic overlays. Before modifying its HTML, use the `hyperframes`, `hyperframes-core`, and relevant animation/media skills. Install or initialize the current HyperFrames CLI only inside the composition project when needed.

Run `npx hyperframes lint`, `validate`, `inspect`, and snapshots before a render. Render only after the user approves the preview.

### 8. QA the finished video

Check hook clarity, narration sync, diagram continuity, spelling, safe margins, audio levels, dead air, final-frame hold, and black/reset tails. Use `video-intelligence` for frame-aware final review and store its report under `qa/video-intelligence/`.

## Project contract

The canonical layout is documented in [references/production-pipeline.md](references/production-pipeline.md). Keep temporary and provider files inside the active project. Do not commit generated outputs or secrets.
