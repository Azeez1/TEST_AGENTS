#!/usr/bin/env python3
"""
Find and validate backlinks ([[wikilinks]]) across the wiki.

Reports:
- All backlinks and what they point to
- Broken links (link to non-existent articles/concepts)
- Orphan articles (no incoming links)
- Suggested new links based on keyword matching

Usage:
    python find_backlinks.py [--vault PATH] [--fix]
"""

import sys
import os
import re
import json
from collections import defaultdict

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

DEFAULT_VAULT = r"C:\Users\sabaa\OneDrive\Desktop\MEMORY\VAULT"

WIKILINK_PATTERN = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')


def get_all_wiki_files(vault_path: str) -> dict:
    """Get all .md files in wiki/ mapped by title (from frontmatter and filename)."""
    wiki_dir = os.path.join(vault_path, "wiki")
    files = {}

    for subdir in ["articles", "concepts", "queries"]:
        dirpath = os.path.join(wiki_dir, subdir)
        if not os.path.exists(dirpath):
            continue
        for fname in os.listdir(dirpath):
            if fname.endswith(".md") and not fname.startswith("_"):
                filepath = os.path.join(dirpath, fname)
                info = {
                    "path": filepath,
                    "title": fname.replace(".md", "").replace("-", " ").title(),
                    "subdir": subdir,
                }

                # Extract frontmatter title for accurate matching
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            for line in parts[1].strip().split("\n"):
                                if line.strip().startswith("title:"):
                                    fm_title = line.split(":", 1)[1].strip().strip('"').strip("'")
                                    if fm_title:
                                        info["title"] = fm_title
                                    break
                except Exception:
                    pass

                # Map by frontmatter title (primary)
                files[info["title"].lower()] = info
                # Map by filename-derived title (fallback)
                filename_title = fname.replace(".md", "").replace("-", " ").title()
                files[filename_title.lower()] = info
                # Map by raw filename (fallback)
                raw_title = fname.replace(".md", "")
                files[raw_title.lower()] = info

    return files


def extract_wikilinks(filepath: str) -> list:
    """Extract all [[wikilinks]] from a file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return WIKILINK_PATTERN.findall(content)


def analyze_backlinks(vault_path: str) -> dict:
    """Analyze all backlinks in the wiki."""
    wiki_dir = os.path.join(vault_path, "wiki")
    all_files = get_all_wiki_files(vault_path)

    # Track links
    outgoing = defaultdict(list)  # file -> [linked titles]
    incoming = defaultdict(list)  # title -> [files that link to it]
    broken = []                   # links that don't resolve

    for subdir in ["articles", "concepts", "queries"]:
        dirpath = os.path.join(wiki_dir, subdir)
        if not os.path.exists(dirpath):
            continue

        for fname in os.listdir(dirpath):
            if not fname.endswith(".md") or fname.startswith("_"):
                continue

            filepath = os.path.join(dirpath, fname)
            source_title = fname.replace(".md", "")
            links = extract_wikilinks(filepath)

            for link in links:
                outgoing[source_title].append(link)
                if link.lower() in all_files:
                    incoming[link.lower()].append(source_title)
                else:
                    broken.append({
                        "source": source_title,
                        "source_path": filepath,
                        "broken_link": link,
                    })

    # Find orphans (files with no incoming links, excluding index files)
    orphans = []
    for title_lower, info in all_files.items():
        if title_lower not in incoming and info["subdir"] != "queries":
            orphans.append(info)

    # Deduplicate orphans by path
    seen_paths = set()
    unique_orphans = []
    for o in orphans:
        if o["path"] not in seen_paths:
            seen_paths.add(o["path"])
            unique_orphans.append(o)

    return {
        "outgoing_links": dict(outgoing),
        "incoming_links": {k: v for k, v in incoming.items()},
        "broken_links": broken,
        "orphan_articles": unique_orphans,
        "stats": {
            "total_links": sum(len(v) for v in outgoing.values()),
            "broken_count": len(broken),
            "orphan_count": len(unique_orphans),
        }
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Find and validate wiki backlinks")
    parser.add_argument("--vault", default=DEFAULT_VAULT, help="Vault path")
    args = parser.parse_args()

    result = analyze_backlinks(args.vault)
    stats = result["stats"]

    print(f"Links: {stats['total_links']} total, {stats['broken_count']} broken, "
          f"{stats['orphan_count']} orphan articles", file=sys.stderr)

    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
