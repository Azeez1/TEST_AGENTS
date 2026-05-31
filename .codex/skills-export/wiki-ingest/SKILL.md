---
name: "wiki-ingest"
description: ">"
---

# Wiki Ingest — Raw Data → Wiki Articles

Processes source files from `raw/` into structured wiki articles in `wiki/articles/`.

**IMPORTANT:** Before starting, read `VAULT/SCHEMA.md` for conventions and `VAULT/wiki/_index.md` for current wiki state.

## Configuration

- **Vault:** `C:\Users\sabaa\OneDrive\Desktop\MEMORY\VAULT`
- **Schema:** `VAULT/SCHEMA.md` ← READ THIS FIRST for conventions
- **Raw input:** `VAULT/raw/`
- **Article output:** `VAULT/wiki/articles/`
- **Tracker:** `VAULT/raw/_processed.json`
- **Log:** `VAULT/wiki/_log.md` ← APPEND after every operation

## Workflow

### Step 1: Scan for New Files

Run the scanner to find unprocessed raw files:
```bash
python "C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\.claude\skills\wiki-ingest\scripts\scan_raw.py"
```

If `--reprocess` flag was passed by user, add `--show-processed` to include already-processed files.

The scanner outputs JSON with file metadata. Read only files with status `"new"` or `"changed"`.

### Step 2: Process Each File

For each unprocessed raw file:

1. **Read the full file** using the Read tool
2. **Analyze the content** — identify:
   - Main topic/subject
   - Key claims, facts, data points
   - Concepts that should have their own wiki pages
   - Connections to existing wiki articles (check `wiki/_index.md` first)
3. **Generate the wiki article** with this structure:

```markdown
---
title: "Article Title"
summary: "One-sentence summary for the index"
date: YYYY-MM-DD
source: "raw/filename.md"
source_type: "transcript|article|paper|notes"
tags:
  - topic-tag-1
  - topic-tag-2
concepts:
  - "Concept Name 1"
  - "Concept Name 2"
type: wiki-article
status: draft
---

# Article Title

> **Source:** [[raw/filename]] | **Type:** transcript | **Date:** YYYY-MM-DD

## Summary

[2-3 paragraph summary of the key content. Not a paraphrase — a distillation
of the most important information, claims, and insights.]

## Key Points

- **Point 1:** [Specific fact, claim, or insight with context]
- **Point 2:** [Another key point]
- **Point 3:** [Continue as needed]

## Concepts

- [[Concept Name 1]] — [How this concept appears in this source]
- [[Concept Name 2]] — [How this concept appears in this source]

## Connections

- Related to [[Other Article]] because [reason]
- Contradicts/supports [[Another Article]] on [topic]

## Raw Quotes

> "Important direct quote from the source" — [speaker/author]

> "Another significant quote" — [speaker/author]

## Open Questions

- [Unanswered question raised by this content]
- [Something that needs further research]
```

### Step 3: Generate Filename

- Use kebab-case: `seedance-2-ugc-breakdown.md`
- Keep it descriptive but under 60 chars
- Prefix with topic area if useful: `ai-video-seedance-2.md`

### Step 4: Save Article

Write the article to `VAULT/wiki/articles/[filename].md`

### Step 5: Mark as Processed

After saving, run the tracker update:
```python
# In Python or via Bash
import sys
sys.path.insert(0, r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\.claude\skills\wiki-ingest\scripts")
from scan_raw import mark_processed
mark_processed(
    vault_path=r"C:\Users\sabaa\OneDrive\Desktop\MEMORY\VAULT",
    rel_path="filename.md",      # relative path within raw/
    file_hash="<hash from scan>",
    article_path="wiki/articles/output-name.md"
)
```

### Step 6: Cross-Update Existing Pages

**CRITICAL — this is what makes the wiki compound.** A single ingest should touch 5-15 pages.

For each concept extracted:
- **If concept page exists:** Read it, add new article to "Appears In", update "Key Facts" with any new information
- **If concept page doesn't exist:** Create it using the template in SCHEMA.md

For each existing article that relates to the new source:
- Read the article's "Connections" section
- Add a cross-reference to the new article if relevant

### Step 7: Update Index

After processing all files, rebuild the index:
```bash
python "C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\.claude\skills\wiki-compile\scripts\build_index.py"
```

### Step 8: Append to Log

Append an entry to `VAULT/wiki/_log.md`:
```markdown
## [YYYY-MM-DD] ingest | Article Title

Brief description of what was ingested.

- Source: `raw/filename.md`
- Pages created: [[New Page 1]], [[New Page 2]]
- Pages updated: [[Existing Page 1]], [[Existing Page 2]]
- Concepts extracted: N
```

### Step 9: Report

Tell the user:
- How many files were processed
- Article titles created
- **Pages updated** (not just created)
- Key concepts extracted
- Suggested next steps (e.g., "Run `/wiki-compile` to generate concept pages")

## Quality Standards

- **Summaries must distill, not paraphrase** — Apply Pareto (80/20): extract the 20% of content that carries the signal, cut the 80% that's filler, repetition, or tangents. No fixed word limit — a dense source keeps more, a rambling source keeps less
- **Always extract concepts** — Every article should link to 2-5 concepts
- **Cross-reference existing articles** — Check `wiki/_index.md` before writing, link to related articles
- **Preserve important quotes** — Direct quotes with attribution
- **Flag uncertainties** — If claims are unverified, note it in Open Questions

## Handling YouTube Transcripts

YouTube transcripts from the `YouTube Transcripts/` folder can be moved to `raw/` for ingestion.
When processing transcripts:
- The speaker is the channel name
- Timestamps can be referenced but focus on content
- Group related segments into coherent sections
- Extract the speaker's key arguments, not every sentence
