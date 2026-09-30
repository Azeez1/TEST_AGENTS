# Install Video Intelligence for Claude Code

This bundle contains a Claude Code-ready version of the `video-intelligence`
skill.

## What the Skill Does

It lets Claude Code analyze videos with timestamped multimodal evidence. A
transcript only tells you what was said. This skill also looks at what happened
on screen, visible text, pacing, demonstrations, edits, UI states, visual
mistakes, and whether the visuals support the spoken content.

Good use cases:

- YouTube/video breakdowns
- Ads, UGC, and creative analysis
- Software QA recordings
- Product demos
- Tutorials and SOP extraction
- Lectures and explainers
- Interviews and meetings
- Compliance or claims review

## Install

1. Unzip this package.

2. Copy the `video-intelligence` folder into your Claude skills folder.

   Windows:

   ```powershell
   C:\Users\<you>\.claude\skills\video-intelligence
   ```

   macOS or Linux:

   ```bash
   ~/.claude/skills/video-intelligence
   ```

3. Install the Python dependencies.

   Windows:

   ```powershell
   python -m pip install -r "$env:USERPROFILE\.claude\skills\video-intelligence\requirements.txt"
   ```

   macOS or Linux:

   ```bash
   python -m pip install -r ~/.claude/skills/video-intelligence/requirements.txt
   ```

4. Add a Gemini Developer API key.

   Important: a normal Gemini consumer plan or Gemini Pro subscription does not
   usually cover API usage. This skill uses the Gemini API, so you need a
   `GEMINI_API_KEY`.

   Windows environment variable:

   ```powershell
   setx GEMINI_API_KEY "your_key_here"
   ```

   Or put this in a local secrets file that is not committed:

   ```text
   GEMINI_API_KEY=your_key_here
   ```

5. Restart Claude Code so the skill can be discovered.

## Test

Run the offline test suite:

```powershell
python "$env:USERPROFILE\.claude\skills\video-intelligence\scripts\test_video_intelligence.py"
```

Generate a tiny local test fixture:

```powershell
python "$env:USERPROFILE\.claude\skills\video-intelligence\scripts\generate_test_fixtures.py" --output-dir "$env:TEMP\video-intelligence-fixtures"
```

Do a dry run before spending API money:

```powershell
python "$env:USERPROFILE\.claude\skills\video-intelligence\scripts\analyze_video.py" "<video-path-or-url>" --output-dir ".\VIDEO_INTELLIGENCE\outputs\analyses" --profile general --question "Summarize this video with timestamped visual and spoken evidence." --dry-run
```

## Example Prompts

Basic:

```text
Use the video-intelligence skill to analyze this video. Tell me what is visually
shown, what is said, where the important moments happen, and what a transcript
alone would miss.
```

Creative/marketing:

```text
Use the video-intelligence skill with the creative-marketing profile. Break down
the hook, pacing, visuals, proof, CTA, audience angle, and what makes the video
work. Separate observed evidence from performance guesses.
```

Software QA:

```text
Use the video-intelligence skill with the software-qa profile. Extract the
reproduction steps, visible UI states, observed result, expected result, and
timestamped evidence.
```

Tutorial/SOP:

```text
Use the video-intelligence skill with the tutorial-sop profile. Turn the video
into a step-by-step SOP with timestamps, tools used, inputs, outputs, and
unclear steps.
```

## Privacy and Cost Notes

- The runner estimates cost before live API calls and defaults to a low cost
  cap.
- For public YouTube URLs, the runner may temporarily download the video for
  better timestamp accuracy.
- Gemini uploaded files are deleted after processing unless explicitly retained.
- The Gemini interaction is sent with `store=false`.
- Do not use private or client media unless you have permission.
- For legal, medical, financial, employment, safety, surveillance, or other
  high-stakes decisions, treat this as evidence organization, not final truth.

