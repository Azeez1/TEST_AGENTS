# Video Intelligence Codex Skill

This skill helps Codex analyze video with timestamped multimodal evidence. It is
useful when the visuals matter, not only the transcript: demos, tutorials,
software recordings, ads, UGC, lectures, product walkthroughs, compliance
reviews, and creative comparisons.

## What it produces

Each run creates a timestamped analysis folder with:

- `manifest.json` for source metadata, model, cost, warnings, and cleanup status.
- `analysis.json` for the structured machine-readable result.
- `report.md` for the human-readable summary with timestamped evidence.
- `run.log` for redacted operational events.
- `evidence/` only when the runner needs targeted clips or frames.

## Install

1. Copy the whole `video-intelligence` folder into the Codex skills directory.

   Windows:

   ```powershell
   C:\Users\<you>\.codex\skills\video-intelligence
   ```

   macOS or Linux:

   ```bash
   ~/.codex/skills/video-intelligence
   ```

2. Install the Python dependencies.

   Windows:

   ```powershell
   python -m pip install -r "$env:USERPROFILE\.codex\skills\video-intelligence\requirements.txt"
   ```

   macOS or Linux:

   ```bash
   python -m pip install -r ~/.codex/skills/video-intelligence/requirements.txt
   ```

3. Add a Gemini Developer API key. A Gemini consumer or Pro subscription does
   not normally cover API usage; this uses API billing.

   Environment variable:

   ```powershell
   setx GEMINI_API_KEY "your_key_here"
   ```

   Or a local Codex secrets file:

   ```text
   GEMINI_API_KEY=your_key_here
   ```

   Save that as `.codex/secrets.local.env` in the active repo or in the user
   home `.codex` folder. Do not commit this file.

4. Restart Codex or refresh skills so `$video-intelligence` appears.

## First Test

Run the offline checks:

```powershell
python "$env:USERPROFILE\.codex\skills\video-intelligence\scripts\test_video_intelligence.py"
```

Generate a tiny rights-safe fixture:

```powershell
python "$env:USERPROFILE\.codex\skills\video-intelligence\scripts\generate_test_fixtures.py" --output-dir "$env:TEMP\video-intelligence-fixtures"
```

Run a dry run before spending API money:

```powershell
python "$env:USERPROFILE\.codex\skills\video-intelligence\scripts\analyze_video.py" "<video-path-or-url>" --output-dir ".\VIDEO_INTELLIGENCE\outputs\analyses" --profile general --question "Summarize this video with timestamped visual and spoken evidence." --dry-run
```

## How to Ask Codex to Use It

Good starter prompt:

```text
Use $video-intelligence to analyze this video. Tell me what is visually shown,
what is said, where the important moments happen, and what a transcript alone
would miss.
```

For creative or ad analysis:

```text
Use $video-intelligence with the creative-marketing profile. Break down the
hook, pacing, visuals, proof, CTA, and what makes this video work.
```

For software QA:

```text
Use $video-intelligence with the software-qa profile. Extract reproduction
steps, visible UI states, observed result, expected result, and timestamped
evidence.
```

## Cost and Privacy Notes

- The default model route uses Gemini Flash-style routing through the API.
- The runner estimates cost before the live call and defaults to a `$0.50` cap.
- Public YouTube URLs are temporarily downloaded by default for better
  timestamp accuracy, then local temporary files are cleaned up.
- Gemini uploaded files are deleted after processing unless explicitly retained.
- The Gemini interaction is sent with `store=false`.
- Do not use private, client, or sensitive media unless you have permission.
- For legal, medical, financial, employment, safety, surveillance, or other
  high-stakes decisions, treat this as evidence organization, not final truth.

