#!/usr/bin/env python3
"""
Build/rebuild the wiki _index.md from all articles, concepts, and queries.

Scans wiki/articles/, wiki/concepts/, wiki/queries/ and generates
a comprehensive index with summaries and stats.

Usage:
    python build_index.py [--vault PATH]
"""

import sys
import os
import re
import json
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

DEFAULT_VAULT = r"C:\Users\sabaa\OneDrive\Desktop\MEMORY\VAULT"


def extract_frontmatter(filepath: str) -> dict:
    """Extract YAML frontmatter from a markdown file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        return {"_content_words": len(content.split())}

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {"_content_words": len(content.split())}

    frontmatter = {}
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val:
                frontmatter[key] = val

    frontmatter["_content_words"] = len(parts[2].split())
    return frontmatter


def scan_directory(dirpath: str) -> list:
    """Scan a directory for .md files and extract metadata."""
    entries = []
    if not os.path.exists(dirpath):
        return entries

    for fname in sorted(os.listdir(dirpath)):
        if not fname.endswith(".md") or fname.startswith("_"):
            continue

        filepath = os.path.join(dirpath, fname)
        meta = extract_frontmatter(filepath)
        entries.append({
            "filename": fname,
            "path": filepath,
            "title": meta.get("title", fname.replace(".md", "").replace("-", " ").title()),
            "date": meta.get("date", ""),
            "words": meta.get("_content_words", 0),
            "tags": meta.get("tags", ""),
            "type": meta.get("type", ""),
            "source": meta.get("source", ""),
            "summary": meta.get("summary", ""),
        })

    return entries


def build_index(vault_path: str) -> dict:
    """Build the full index data structure."""
    wiki_dir = os.path.join(vault_path, "wiki")

    articles = scan_directory(os.path.join(wiki_dir, "articles"))
    concepts = scan_directory(os.path.join(wiki_dir, "concepts"))
    queries = scan_directory(os.path.join(wiki_dir, "queries"))

    total_words = sum(a["words"] for a in articles + concepts + queries)

    return {
        "articles": articles,
        "concepts": concepts,
        "queries": queries,
        "stats": {
            "article_count": len(articles),
            "concept_count": len(concepts),
            "query_count": len(queries),
            "total_words": total_words,
            "updated": datetime.now().strftime("%Y-%m-%d"),
        }
    }


def render_index_md(data: dict) -> str:
    """Render the index data as markdown."""
    stats = data["stats"]

    # Articles section
    if data["articles"]:
        article_lines = []
        for a in data["articles"]:
            summary = f" — {a['summary']}" if a["summary"] else ""
            article_lines.append(f"- [[{a['title']}]] ({a['words']:,} words){summary}")
        articles_section = "\n".join(article_lines)
    else:
        articles_section = "*No articles yet. Run `/wiki-ingest` to process raw files.*"

    # Concepts section
    if data["concepts"]:
        concept_lines = []
        for c in data["concepts"]:
            concept_lines.append(f"- [[{c['title']}]] — {c.get('summary', '')}")
        concepts_section = "\n".join(concept_lines)
    else:
        concepts_section = "*No concepts yet. Run `/wiki-compile` to extract concepts.*"

    # Queries section
    if data["queries"]:
        query_lines = []
        for q in sorted(data["queries"], key=lambda x: x["date"], reverse=True)[:20]:
            query_lines.append(f"- [[{q['title']}]] ({q['date']})")
        queries_section = "\n".join(query_lines)
    else:
        queries_section = "*No queries yet. Run `/wiki-query` to ask questions.*"

    return f"""---
title: "Wiki Index"
type: wiki-index
updated: {stats['updated']}
article_count: {stats['article_count']}
concept_count: {stats['concept_count']}
total_words: {stats['total_words']}
---

# Knowledge Base Index

> This index is auto-maintained by the wiki system. Do not edit manually.

## Articles ({stats['article_count']})

<!-- ARTICLES_START -->
{articles_section}
<!-- ARTICLES_END -->

## Concepts ({stats['concept_count']})

<!-- CONCEPTS_START -->
{concepts_section}
<!-- CONCEPTS_END -->

## Recent Queries ({stats['query_count']})

<!-- QUERIES_START -->
{queries_section}
<!-- QUERIES_END -->

## Stats

- **Articles:** {stats['article_count']}
- **Concepts:** {stats['concept_count']}
- **Queries:** {stats['query_count']}
- **Total Words:** {stats['total_words']:,}
- **Last Updated:** {stats['updated']}
"""


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build wiki index")
    parser.add_argument("--vault", default=DEFAULT_VAULT, help="Vault path")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of markdown")
    args = parser.parse_args()

    data = build_index(args.vault)

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        index_md = render_index_md(data)
        index_path = os.path.join(args.vault, "wiki", "_index.md")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_md)
        print(f"Index rebuilt: {data['stats']['article_count']} articles, "
              f"{data['stats']['concept_count']} concepts, "
              f"{data['stats']['total_words']:,} words", file=sys.stderr)
        print(index_path)


if __name__ == "__main__":
    main()
