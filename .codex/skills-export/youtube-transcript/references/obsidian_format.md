# Obsidian Note Format Reference

## YAML Frontmatter Schema

Every YouTube transcript note includes this frontmatter:

```yaml
---
title: "Video Title"           # Required - video title from YouTube
channel: "Channel Name"        # Required - uploader name
date: 2026-04-05               # Required - date note was created
url: "https://youtube.com/..." # Required - full video URL
video_id: "dQw4w9WgXcQ"       # Required - 11-char YouTube ID
duration: "15:42"              # Required - estimated from transcript
language: "en"                 # Required - transcript language code
caption_type: "auto-generated" # Required - "auto-generated", "manual", or "whisper"
tags:                          # Required - always includes youtube, transcript
  - youtube
  - transcript
type: youtube-transcript       # Required - fixed value for Dataview queries
status: raw                    # Required - "raw", "reviewed", or "annotated"
---
```

## Dataview Queries

### List all transcripts
```dataview
TABLE channel, duration, caption_type, date
FROM #youtube AND #transcript
SORT date DESC
```

### Filter by channel
```dataview
TABLE duration, date
FROM #youtube
WHERE channel = "Channel Name"
SORT date DESC
```

### Find Whisper-transcribed notes
```dataview
LIST
FROM #whisper-transcribed
SORT date DESC
```

## Tag Conventions

- `youtube` — all YouTube transcript notes
- `transcript` — all transcript notes
- `whisper-transcribed` — notes transcribed via Whisper (no YouTube captions)
- Custom tags added via `--tags` flag

## File Organization

```
VAULT/
└── YouTube Transcripts/          # Default subfolder
    ├── Video Title.md
    ├── Another Video.md
    ├── Business/                  # Custom subfolder via --folder
    │   └── Business Video.md
    └── Tech/
        └── Tech Talk.md
```
