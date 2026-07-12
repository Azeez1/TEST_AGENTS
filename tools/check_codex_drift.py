"""Codex mirror drift checker: is .codex/ stale relative to .claude/?

The .codex/ layer is a GENERATED mirror (source of truth = .claude/; generator =
scripts/export_codex_layer.py, invoked via /sync-codex). This checker detects the
three ways the mirror rots, using .codex/manifest.json as the contract:

  1. GHOST    - manifest/mirror entry whose .claude source no longer exists
  2. STALE    - source file modified more recently than its mirror
  3. UNSEEN   - agent/skill on disk that the manifest has never exported

Usage:  python tools/check_codex_drift.py [--json]
Exit codes: 0 = mirror fresh, 1 = drift found (fix: run /sync-codex), 2 = no manifest.

Wired into /agent-health next to lint_agent_declarations.py. Born from the
2026-07-12 Factory Audit: the hand-maintained mirror had drifted to claiming
"62 agents" while reality moved to 73.
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / ".codex" / "manifest.json"

TEAM_DIRS = [
    "MARKETING_TEAM", "ENGINEERING_TEAM", "FINANCIAL_TEAM", "SALES_TEAM",
    "QA_TEAM", "VOICE_TEAM", "PROPOSAL_TEAM", "HEDGE_FUND",
]


def mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def on_disk_agent_sources() -> set[str]:
    """All .claude agent definition files, repo-relative with forward slashes."""
    files = list((REPO / ".claude" / "agents").glob("*.md"))
    for team in TEAM_DIRS:
        files += (REPO / team / ".claude" / "agents").glob("*.md")
    return {p.relative_to(REPO).as_posix() for p in files}


def on_disk_skill_sources() -> set[str]:
    """All root skill dirs (incl. document-skills children), repo-relative."""
    skills = set()
    root = REPO / ".claude" / "skills"
    for d in root.iterdir():
        if (d / "SKILL.md").exists():
            skills.add(d.relative_to(REPO).as_posix())
        if d.name == "document-skills":
            for sub in d.iterdir():
                if (sub / "SKILL.md").exists():
                    skills.add(sub.relative_to(REPO).as_posix())
    return skills


def main():
    if not MANIFEST.exists():
        print("NO MANIFEST at .codex/manifest.json - run /sync-codex to generate the mirror.")
        sys.exit(2)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ghosts, stale, unseen = [], [], []

    # --- agents ---------------------------------------------------------
    manifest_agent_sources = set()
    for a in manifest.get("agents", []):
        src_rel = a.get("source", "")
        if a.get("source_runtime") == "codex-native":
            continue  # native Codex agents have no .claude source to compare
        manifest_agent_sources.add(src_rel)
        src, mirror = REPO / src_rel, REPO / a.get("codex_instructions", "")
        if not src.exists():
            ghosts.append(f"agent {a.get('slug')}: source gone ({src_rel})")
            continue
        if not mirror.exists():
            stale.append(f"agent {a.get('slug')}: mirror missing ({a.get('codex_instructions')})")
        elif mtime(src) > mtime(mirror):
            stale.append(f"agent {a.get('slug')}: source newer than mirror ({src_rel})")

    for src_rel in sorted(on_disk_agent_sources() - manifest_agent_sources):
        unseen.append(f"agent never exported: {src_rel}")

    # --- skills ---------------------------------------------------------
    manifest_skill_sources = set()
    for s in manifest.get("skills", []):
        src_rel = s.get("source", "")
        if src_rel in ("", "generated"):
            continue  # exporter-generated pseudo-skills have no .claude source
        manifest_skill_sources.add(src_rel)
        src_md = REPO / src_rel / "SKILL.md"
        mirror = REPO / s.get("codexPath", "")
        if not src_md.exists():
            ghosts.append(f"skill {s.get('name')}: source gone ({src_rel})")
            continue
        if not mirror.exists():
            stale.append(f"skill {s.get('name')}: mirror missing ({s.get('codexPath')})")
        elif mtime(src_md) > mtime(mirror):
            stale.append(f"skill {s.get('name')}: source newer than mirror ({src_rel})")

    for src_rel in sorted(on_disk_skill_sources() - manifest_skill_sources):
        unseen.append(f"skill never exported: {src_rel}")

    drift = {"ghosts": ghosts, "stale": stale, "unseen": unseen}
    total = sum(len(v) for v in drift.values())

    if "--json" in sys.argv:
        print(json.dumps({"drift_count": total, **drift}, indent=2))
    else:
        print(f"Codex mirror check: {len(manifest.get('agents', []))} manifest agents, "
              f"{len(manifest.get('skills', []))} manifest skills.")
        if total == 0:
            print("FRESH: .codex mirror matches .claude sources.")
        else:
            print(f"DRIFT ({total} findings) - fix: run /sync-codex")
            for kind, items in drift.items():
                for item in items[:40]:
                    print(f"  [{kind.upper()[:-1]}] {item}")
                if len(items) > 40:
                    print(f"  ... and {len(items) - 40} more {kind}")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
