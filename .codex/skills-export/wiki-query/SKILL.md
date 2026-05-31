---
name: "wiki-query"
description: ">"
---

# Wiki Query — Q&A Against Your Knowledge Base

Ask questions, get answers synthesized from your wiki articles and concepts.

## Configuration

- **Vault:** `C:\Users\sabaa\OneDrive\Desktop\MEMORY\VAULT`
- **Wiki root:** `VAULT/wiki/`

## Workflow

### Step 1: Read the Index

Read `VAULT/wiki/_index.md` to understand what's in the knowledge base.
Also read `VAULT/wiki/_concepts.md` for the concept map.

This gives you the full inventory: article titles, summaries, concept definitions.

### Step 2: Identify Relevant Sources

Based on the user's question:

1. **Scan article titles and summaries** in the index for relevance
2. **Check concept map** for related concepts
3. **Use keyword search** if needed:
   ```bash
   # Search across all wiki files for specific terms
   ```
   Use Grep tool to search across `VAULT/wiki/` for keywords from the question.

4. **Pull in relevant files** — Read the full content of the most relevant articles
   (typically 3-8 articles depending on question complexity)

### Step 3: Synthesize Answer

Write a comprehensive answer that:

- **Directly answers the question** with specific information from the wiki
- **Cites sources** — reference which articles/concepts the answer draws from using [[wikilinks]]
- **Identifies gaps** — if the wiki doesn't fully cover the question, say what's missing
- **Suggests connections** the user might not have noticed across their articles
- **Distinguishes certainty levels** — what's well-supported vs. mentioned only once

### Step 4: Output Format

**Default (terminal response):**
Present the answer directly in the conversation. Include article references.

**With `--file-back` flag:**
Also save the answer as a wiki query file:

```markdown
---
title: "Query: [Short Question Title]"
date: YYYY-MM-DD
question: "The full question asked"
sources:
  - "Article 1 Title"
  - "Article 2 Title"
tags:
  - query
  - topic-tag
type: wiki-query
status: final
---

# [Short Question Title]

> **Question:** [The full question asked]
> **Date:** YYYY-MM-DD
> **Sources consulted:** [N] articles, [M] concepts

## Answer

[Comprehensive answer synthesized from wiki sources]

## Sources

- [[Article 1]] — [what it contributed to the answer]
- [[Article 2]] — [what it contributed to the answer]

## Gaps

- [Information that was missing or unclear in the wiki]
- [Suggested topics to research further]
```

Save to: `VAULT/wiki/queries/[kebab-case-question].md`

Then rebuild the index:
```bash
python "C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\.claude\skills\wiki-compile\scripts\build_index.py"
```

### Step 5: Report

Tell the user:
- The synthesized answer
- How many sources were consulted
- Confidence level (well-covered / partially covered / sparse)
- Knowledge gaps and suggested next research steps

## Query Modes

- **Standard:** Read index + relevant articles, answer in conversation
- **`--deep`:** Read ALL articles in the wiki (for complex cross-cutting questions)
- **`--file-back`:** Save the answer as a query document in the wiki

## Query Types

The system handles various question types:

| Type | Example | Approach |
|------|---------|----------|
| **Factual** | "What is Seedance 2?" | Find the concept/article, extract facts |
| **Comparative** | "How does X compare to Y?" | Pull both articles, synthesize differences |
| **Analytical** | "What trends do I see across my research?" | Read all articles, find patterns |
| **Gap analysis** | "What haven't I covered yet?" | Compare concept map to article coverage |
| **Synthesis** | "What's my overall thesis on AI video?" | Cross-reference all relevant articles |

## Important Rules

1. **Never fabricate information** — Only use what's in the wiki. If the wiki doesn't cover it, say so.
2. **Always cite sources** — Every claim should reference which article it came from.
3. **Flag contradictions** — If two articles say different things, highlight the contradiction.
4. **Suggest next steps** — After answering, suggest what to ingest or research next.
