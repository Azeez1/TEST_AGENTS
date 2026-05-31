---
name: "wiki-compile"
description: ">"
---

# Wiki Compile — Rebuild, Link, and Organize

Full wiki recompilation: indexes, concepts, backlinks, and consistency.

## Configuration

- **Vault:** `C:\Users\sabaa\OneDrive\Desktop\MEMORY\VAULT`
- **Wiki root:** `VAULT/wiki/`
- **Scripts:** `C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\.claude\skills\wiki-compile\scripts\`

## Workflow

### Step 1: Scan Current State

Read the current index to understand what exists:
```bash
python "C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\.claude\skills\wiki-compile\scripts\build_index.py" --json
```

This gives you the full state: articles, concepts, queries, word counts.

### Step 2: Extract Concepts from Articles

For each article in `wiki/articles/`:

1. **Read the article** — look at the `concepts:` field in frontmatter
2. **Check if concept page exists** in `wiki/concepts/`
3. **If concept page is missing, create it:**

```markdown
---
title: "Concept Name"
summary: "One-line definition of this concept"
date: YYYY-MM-DD
tags:
  - concept
  - domain-tag
related_concepts:
  - "Related Concept 1"
  - "Related Concept 2"
type: wiki-concept
status: draft
---

# Concept Name

## Definition

[Clear, concise definition of this concept — 2-3 sentences]

## Context

[Why this concept matters in the context of the wiki's research domain]

## Appears In

- [[Article 1]] — [how this concept is discussed]
- [[Article 2]] — [how this concept is discussed]

## Related Concepts

- [[Related Concept 1]] — [relationship]
- [[Related Concept 2]] — [relationship]

## Key Facts

- [Fact 1 from articles]
- [Fact 2 from articles]
```

4. **If concept page exists, update it** — add new article references to "Appears In"

### Step 3: Validate Backlinks

Run the backlink analyzer:
```bash
python "C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\.claude\skills\wiki-compile\scripts\find_backlinks.py"
```

The output includes:
- **Broken links:** [[links]] pointing to non-existent pages — create stubs or fix
- **Orphan articles:** Pages with no incoming links — add references from related articles
- **Link stats:** Total link count, connectivity metrics

For each broken link:
- If it's a concept: create the concept page (Step 2 template)
- If it's an article reference: fix the link text or create the article

For each orphan:
- Find the most related existing article and add a cross-reference

### Step 4: Update Concept Map

Read all concept pages and build `wiki/_concepts.md`:

```markdown
---
title: "Concept Map"
type: wiki-concepts
updated: YYYY-MM-DD
---

# Concept Map

> Auto-maintained concept index with backlinks to articles. Do not edit manually.

## [Domain Area 1]

- **[[Concept A]]** — [one-line summary] (appears in: [[Article 1]], [[Article 2]])
- **[[Concept B]]** — [one-line summary] (appears in: [[Article 3]])

## [Domain Area 2]

- **[[Concept C]]** — [one-line summary] (appears in: [[Article 1]], [[Article 4]])
```

Group concepts by domain area (infer from tags and content).

### Step 5: Rebuild Index

```bash
python "C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\.claude\skills\wiki-compile\scripts\build_index.py"
```

### Step 6: Report

Tell the user:
- Concepts created/updated
- Broken links found and fixed
- Orphan articles connected
- Total wiki stats (articles, concepts, words)
- Suggested improvements

## Compilation Modes

- **`--full`** (default): Run all steps
- **`--concepts-only`**: Only Steps 2 and 4 (extract and map concepts)
- **`--index-only`**: Only Step 5 (rebuild index file)

## Cross-Reference Rules

1. **Every article must link to at least 2 concepts**
2. **Every concept must list all articles it appears in**
3. **Related articles should cross-reference each other in their "Connections" section**
4. **Use [[wikilinks]] consistently** — match the exact title in the target file's frontmatter
5. **Concept names are title case:** [[AI Video Generation]], not [[ai video generation]]
