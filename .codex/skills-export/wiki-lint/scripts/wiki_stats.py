#!/usr/bin/env python3
"""
Generate comprehensive wiki health statistics.

Reports: file counts, word counts, freshness, coverage gaps,
consistency checks, and suggestions for improvement.

Usage:
    python wiki_stats.py [--vault PATH]
"""

import sys
import os
import json
from datetime import datetime, timedelta
from collections import Counter

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

DEFAULT_VAULT = r"C:\Users\sabaa\OneDrive\Desktop\MEMORY\VAULT"


def count_words(filepath: str) -> int:
    """Count words in a file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return len(f.read().split())


def extract_tags(filepath: str) -> list:
    """Extract tags from YAML frontmatter."""
    tags = []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        return tags

    parts = content.split("---", 2)
    if len(parts) < 3:
        return tags

    in_tags = False
    for line in parts[1].strip().split("\n"):
        if line.strip().startswith("tags:"):
            in_tags = True
            # Inline tags: tags: [a, b, c]
            inline = line.split(":", 1)[1].strip()
            if inline.startswith("["):
                tags = [t.strip().strip('"').strip("'") for t in inline.strip("[]").split(",")]
                in_tags = False
            continue
        if in_tags:
            if line.strip().startswith("- "):
                tags.append(line.strip().lstrip("- ").strip())
            else:
                in_tags = False

    return tags


def generate_stats(vault_path: str) -> dict:
    """Generate comprehensive wiki statistics."""
    wiki_dir = os.path.join(vault_path, "wiki")
    raw_dir = os.path.join(vault_path, "raw")

    stats = {
        "raw": {"count": 0, "total_words": 0, "files": []},
        "articles": {"count": 0, "total_words": 0, "files": []},
        "concepts": {"count": 0, "total_words": 0, "files": []},
        "queries": {"count": 0, "total_words": 0, "files": []},
        "tags": Counter(),
        "health": [],
    }

    # Scan raw/
    if os.path.exists(raw_dir):
        for fname in os.listdir(raw_dir):
            fpath = os.path.join(raw_dir, fname)
            if os.path.isfile(fpath) and fname.endswith(".md") and not fname.startswith("_"):
                words = count_words(fpath)
                stats["raw"]["count"] += 1
                stats["raw"]["total_words"] += words
                stats["raw"]["files"].append({"name": fname, "words": words})

    # Scan wiki subdirs
    for subdir in ["articles", "concepts", "queries"]:
        dirpath = os.path.join(wiki_dir, subdir)
        if not os.path.exists(dirpath):
            continue
        for fname in sorted(os.listdir(dirpath)):
            if not fname.endswith(".md") or fname.startswith("_"):
                continue
            fpath = os.path.join(dirpath, fname)
            words = count_words(fpath)
            tags = extract_tags(fpath)

            stats[subdir]["count"] += 1
            stats[subdir]["total_words"] += words
            stats[subdir]["files"].append({"name": fname, "words": words, "tags": tags})

            for tag in tags:
                stats["tags"][tag] += 1

    # Health checks
    total_articles = stats["articles"]["count"]
    total_concepts = stats["concepts"]["count"]
    total_words = sum(s["total_words"] for s in [stats["articles"], stats["concepts"], stats["queries"]])

    # Check: raw files not yet ingested
    tracker_path = os.path.join(raw_dir, "_processed.json")
    unprocessed = 0
    if os.path.exists(tracker_path):
        with open(tracker_path, "r", encoding="utf-8") as f:
            processed = json.load(f)
        unprocessed = stats["raw"]["count"] - len(processed)
    else:
        unprocessed = stats["raw"]["count"]

    if unprocessed > 0:
        stats["health"].append({
            "level": "warning",
            "message": f"{unprocessed} raw file(s) not yet ingested. Run `/wiki-ingest`.",
        })

    # Check: articles without concepts
    if total_articles > 3 and total_concepts == 0:
        stats["health"].append({
            "level": "warning",
            "message": "Articles exist but no concepts extracted. Run `/wiki-compile`.",
        })

    # Check: concept-to-article ratio
    if total_articles > 0 and total_concepts > 0:
        ratio = total_concepts / total_articles
        if ratio < 0.5:
            stats["health"].append({
                "level": "info",
                "message": f"Low concept density ({ratio:.1f} concepts/article). Consider extracting more concepts.",
            })

    # Check: very short articles
    short_articles = [f for f in stats["articles"]["files"] if f["words"] < 100]
    if short_articles:
        stats["health"].append({
            "level": "info",
            "message": f"{len(short_articles)} article(s) under 100 words: {', '.join(a['name'] for a in short_articles)}",
        })

    # Summary
    stats["summary"] = {
        "total_files": total_articles + total_concepts + stats["queries"]["count"],
        "total_words": total_words,
        "raw_pending": unprocessed,
        "top_tags": stats["tags"].most_common(10),
        "health_issues": len(stats["health"]),
    }

    # Convert Counter to dict for JSON
    stats["tags"] = dict(stats["tags"].most_common(20))

    return stats


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Wiki health statistics")
    parser.add_argument("--vault", default=DEFAULT_VAULT, help="Vault path")
    args = parser.parse_args()

    stats = generate_stats(args.vault)

    summary = stats["summary"]
    print(f"Wiki: {summary['total_files']} files, {summary['total_words']:,} words, "
          f"{summary['raw_pending']} raw pending, {summary['health_issues']} health issues",
          file=sys.stderr)

    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
