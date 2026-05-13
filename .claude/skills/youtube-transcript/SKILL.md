---
name: youtube-transcript
description: >
  Scrape YouTube video transcripts and save them as structured Obsidian notes with YAML frontmatter,
  timestamps, and metadata. Use when the user wants to capture a YouTube video transcript, save video
  notes to Obsidian, or batch-process YouTube playlists/channels into their vault. Supports single
  videos, playlists, and full channel ingestion with smart selection (top-viewed, most-recent,
  longest, or a --smart-150 preset) so you can synthesize a creator's body of work without watching
  every video. Pair with wiki-ingest + wiki-compile to auto-extract repeated concepts across a
  creator's catalog.
argument-hint: "<youtube-url-or-channel> [--smart-150 | --top N --recent N --longest N] [--min-duration N] [--folder <subfolder>]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# YouTube Transcript → Obsidian Skill

Extracts YouTube video transcripts and saves them as well-formatted Markdown notes
in the user's Obsidian vault.

## Configuration

**Vault path:** `C:\Users\sabaa\OneDrive\Desktop\MEMORY\VAULT`
**Default subfolder:** `YouTube Transcripts`
**Config file:** `~/.config/youtube-transcript/config.json` (optional overrides)

## Workflow

### Step 1: Parse Input

Extract video ID(s) from the user's input. Supported formats:
- Single video: `https://www.youtube.com/watch?v=VIDEO_ID`
- Short URL: `https://youtu.be/VIDEO_ID`
- Playlist: `https://www.youtube.com/playlist?list=PLAYLIST_ID`
- Video with timestamp: `https://www.youtube.com/watch?v=VIDEO_ID&t=123`
- Just the ID: `dQw4w9WgXcQ`

### Step 2: Fetch Transcript

Run the fetch script:
```bash
python "C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\.claude\skills\youtube-transcript\scripts\fetch_transcript.py" "<youtube_url_or_id>" [options]
```

**Options:**
- `--no-timestamps` — Strip timestamps from output (default: include them)
- `--lang <code>` — Preferred language (default: `en`)
- `--folder <name>` — Subfolder within YouTube Transcripts (e.g., `Business`, `Tech`)
- `--format <type>` — Output format: `full` (default), `clean` (no timestamps), `chapters`
- `--max-playlist <n>` — Cap on videos pulled from a playlist/channel in default mode (default: 50)

**Smart Channel Selection (optional — channels only):**

These flags only apply when the URL is a channel. They're all optional; if none are passed,
the skill just grabs the first `--max-playlist` videos in the channel's default order.

- `--smart-150` — Preset: top 50 most-viewed + 50 most recent + 50 longest (deduped to ~130-150 unique)
- `--top <n>` — Top N by view count (proven hits)
- `--recent <n>` — N most recent uploads (current thinking)
- `--longest <n>` — N longest videos (podcasts/keynotes where creators go deep)
- `--min-duration <n>` — Skip videos shorter than N minutes (good for filtering Shorts, e.g., `--min-duration 10`)

Flags compose: `--top 30 --longest 20 --min-duration 15` = top 30 most-viewed + 20 longest,
all at least 15 minutes long, deduped.

### When to Use Channel Mode

**Single video:** just pass the URL, no flags needed.
```bash
python fetch_transcript.py "https://youtu.be/abc123"
```

**Whole channel, first 50 videos (default behavior):**
```bash
python fetch_transcript.py "https://youtube.com/@AlexHormozi/videos"
```

**Smart 150 from a channel (the "learn from a creator fast" preset):**
```bash
python fetch_transcript.py "https://youtube.com/@AlexHormozi/videos" --smart-150 --min-duration 5 --folder "Hormozi"
```

**Only their deep-dive podcasts:**
```bash
python fetch_transcript.py "https://youtube.com/@AlexHormozi/videos" --longest 20 --min-duration 30
```

### Step 3: Review Output

The script outputs the path to the created `.md` file. Verify:
1. File was created in the vault
2. YAML frontmatter is valid
3. Transcript content is present

### Step 4: Report to User

Tell the user:
- Video title and channel
- Where the file was saved
- Word count / duration
- Any issues (e.g., no captions available, used auto-generated)

### Step 5: Auto-Chain to Wiki (Channel Smart-Selection ONLY)

If the user ran this in **channel smart-selection mode** (i.e., any of `--smart-150`, `--top`,
`--recent`, `--longest` was passed), automatically continue the pipeline:

1. Invoke the `wiki-ingest` skill on the subfolder where transcripts were saved
2. Then invoke `wiki-compile` to extract concepts, build backlinks, rebuild the index
3. Tell the user the full pipeline completed and suggest sample `wiki-query` questions

**Do NOT auto-chain for:**
- Single video invocations (user just wants one transcript)
- Default playlist/channel mode without smart-selection flags (may be a small one-off)
- User explicitly passed `--no-ingest` (see future flag)

Rationale: smart-selection implies "I'm building a knowledge base from this creator" — the
synthesis step is the whole point. Single videos don't warrant recompiling the whole wiki.

## Output Format

Each transcript is saved as a Markdown file with this structure:

```markdown
---
title: "Video Title"
channel: "Channel Name"
date: 2026-04-05
published: "2026-03-15"
url: "https://youtube.com/watch?v=..."
video_id: "dQw4w9WgXcQ"
duration: "15:42"
language: "en"
caption_type: "auto-generated"
tags:
  - youtube
  - transcript
type: youtube-transcript
status: raw
---

# Video Title

**Channel:** [Channel Name](channel_url) | **Duration:** 15:42 | **Published:** 2026-03-15

---

## Transcript

[00:00] Introduction text here...
[01:23] Next segment of the video...
[05:45] Another part of the content...

---

## Notes

<!-- Your notes here -->
```

## Error Handling

- **No captions available:** Report to user, suggest trying with `--lang` flag for other languages
- **Video unavailable/private:** Report the error clearly
- **Rate limited:** Wait 5 seconds and retry once, then report failure
- **Network error:** Report and suggest retrying

## Batch Processing

For playlists or multiple URLs, the script accepts multiple arguments:
```bash
python fetch_transcript.py "url1" "url2" "url3" --folder "Course Notes"
```

Each video gets its own `.md` file in the target folder.
