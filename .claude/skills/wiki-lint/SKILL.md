---
name: wiki-lint
description: >
  Run health checks on the wiki knowledge base: find inconsistencies, broken backlinks,
  missing concepts, short articles, stale data, tag inconsistencies, and suggest improvements.
  Use when the user says "lint", "health check", "audit the wiki", "clean up wiki",
  or wants to improve wiki quality and data integrity.
argument-hint: "[--fix] [--suggest]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# Wiki Lint — Health Checks and Quality Improvement

Audit the wiki for consistency, completeness, and quality.

## Configuration

- **Vault:** `C:\Users\sabaa\OneDrive\Desktop\MEMORY\VAULT`
- **Stats script:** `C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\.claude\skills\wiki-lint\scripts\wiki_stats.py`
- **Backlink script:** `C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\.claude\skills\wiki-compile\scripts\find_backlinks.py`

## Workflow

### Step 1: Gather Stats

```bash
python "C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\.claude\skills\wiki-lint\scripts\wiki_stats.py"
```

This gives: file counts, word counts, tag distribution, and basic health warnings.

### Step 2: Check Backlinks

```bash
python "C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\.claude\skills\wiki-compile\scripts\find_backlinks.py"
```

This gives: broken links, orphan articles, link density.

### Step 3: Deep Content Audit

Read each article in `wiki/articles/` and check for:

#### Structural Issues
- [ ] Missing YAML frontmatter fields (title, summary, date, source, tags, concepts, type, status)
- [ ] Empty sections (Summary, Key Points, Concepts with no content)
- [ ] Missing `summary` field (critical — used by the index)
- [ ] No `concepts` in frontmatter (every article should extract concepts)

#### Content Quality
- [ ] Articles under 100 words (too thin — may need expansion)
- [ ] Articles without any [[wikilinks]] (isolated, not connected)
- [ ] Articles without "Connections" section (no cross-references)
- [ ] Empty "Open Questions" sections (should have genuine questions or be removed)
- [ ] Duplicate content across articles (>50% overlap)

#### Concept Quality
- [ ] Concepts without a clear Definition section
- [ ] Concepts with empty "Appears In" (not referenced by any article)
- [ ] Concepts that appear in articles but have no concept page

#### Tag Consistency
- [ ] Tags that appear only once (may be typos or too specific)
- [ ] Similar tags that should be merged (e.g., "ai-video" vs "ai_video" vs "AI Video")
- [ ] Articles without any topic-specific tags (only have generic "youtube", "transcript")

#### Data Integrity
- [ ] Claims that contradict each other across articles
- [ ] Dates that don't make sense (future dates, impossible timelines)
- [ ] Sources referenced but not linked

### Step 4: Generate Report

Output a structured health report:

```markdown
# Wiki Health Report — YYYY-MM-DD

## Overview
- **Articles:** N | **Concepts:** N | **Queries:** N
- **Total Words:** N | **Avg Article Length:** N words
- **Health Score:** X/10

## Critical Issues (must fix)
1. [Issue with specific file reference]
2. [Another critical issue]

## Warnings (should fix)
1. [Non-critical issue]
2. [Another warning]

## Suggestions (nice to have)
1. [Improvement idea]
2. [New article candidate]

## Missing Concepts
These concepts are mentioned in articles but don't have their own pages:
- "Concept X" (mentioned in: Article A, Article B)
- "Concept Y" (mentioned in: Article C)

## Suggested New Articles
Based on patterns in the wiki, these topics would fill gaps:
- [Topic 1] — because [reason based on existing content]
- [Topic 2] — because [reason]

## Tag Cleanup
- Merge: "ai-video" + "ai_video" → "ai-video"
- Remove: "misc" (only used once)
```

### Step 5: Auto-Fix (with `--fix` flag)

If the user passed `--fix`, automatically:
1. Add missing frontmatter fields with sensible defaults
2. Fix broken backlinks by creating stub concept pages
3. Merge duplicate tags
4. Connect orphan articles to related articles
5. Rebuild the index after fixes

### Step 6: Suggest Research (with `--suggest` flag)

If the user passed `--suggest`, use the wiki content to:
1. Identify knowledge gaps (concepts mentioned but not explored)
2. Suggest new topics based on connections between existing articles
3. Recommend specific YouTube videos or articles to research next
4. Propose analytical queries that would generate useful insights

## Health Score Rubric

| Score | Criteria |
|-------|----------|
| 10/10 | All articles have full frontmatter, summaries, concepts, backlinks. No broken links. Rich cross-references. |
| 8/10 | Minor gaps: a few missing summaries or thin articles |
| 6/10 | Some broken links, several orphan articles, inconsistent tags |
| 4/10 | Many articles lack concepts, minimal cross-referencing, tag chaos |
| 2/10 | Mostly raw dumps with no structure or connections |
