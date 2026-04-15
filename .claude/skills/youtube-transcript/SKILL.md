---
name: youtube-transcript
description: >
  Scrape YouTube video transcripts and save them as structured Obsidian notes with YAML frontmatter,
  timestamps, and metadata. Use when the user wants to capture a YouTube video transcript, save video
  notes to Obsidian, or batch-process YouTube playlists/channels into their vault.
  Supports single videos, playlists, and channel URLs.
argument-hint: "<youtube-url> [--summary] [--timestamps] [--folder <subfolder>]"
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
