#!/usr/bin/env python3
"""Generate the machine-readable /agent-health artifacts from the filesystem.

Writes LOGS/agent-inventory.json and LOGS/performance-metrics.json.
Everything here is derived, never hand-typed (see .claude/rules/doc-hygiene.md).

Usage:  python tools/gen_health_artifacts.py [--stamp YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import ast
import collections
import json
import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEAMS = [
    "MARKETING_TEAM",
    "ENGINEERING_TEAM",
    "FINANCIAL_TEAM",
    "SALES_TEAM",
    "QA_TEAM",
    "VOICE_TEAM",
    "PROPOSAL_TEAM",
    "HEDGE_FUND",
]


def frontmatter(path: Path) -> dict:
    """Parse the YAML-ish frontmatter of an agent file without a yaml dependency."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    head = text.split("---", 2)[1]
    out: dict = {}
    # NOTE: [ \t]* not \s* — \s eats the newline and would pull in the next line.
    for key in ("name", "description", "model"):
        m = re.search(rf"^{key}:[ \t]*(.+)$", head, re.M)
        if m:
            out[key] = m.group(1).strip()
    # tools/skills may be inline lists or block lists
    for key in ("tools", "skills"):
        m = re.search(rf"^{key}:[ \t]*(.*)$", head, re.M)
        if not m:
            continue
        inline = m.group(1).strip()
        if inline and inline not in ("|", ">"):
            items = [x.strip().strip("[]") for x in inline.split(",")]
            out[key] = [x for x in items if x and x != "[]"]
        else:
            block = head[m.end():]
            items = []
            for line in block.splitlines():
                if re.match(r"^\s*-\s+", line):
                    items.append(re.sub(r"^\s*-\s+", "", line).strip())
                elif line.strip() and not line.startswith(" "):
                    break
            out[key] = items
    return out


def agent_inventory() -> dict:
    agents = []
    for team, root in [("ROOT", REPO / ".claude/agents")] + [
        (t, REPO / t / ".claude/agents") for t in TEAMS
    ]:
        if not root.is_dir():
            continue
        for f in sorted(root.glob("*.md")):
            fm = frontmatter(f)
            agents.append(
                {
                    "name": fm.get("name", ""),
                    "team": team,
                    "path": str(f.relative_to(REPO)).replace("\\", "/"),
                    "filename_stem": f.stem,
                    "name_matches_filename": fm.get("name", "") == f.stem,
                    "has_description": bool(fm.get("description")),
                    "model_pin": fm.get("model"),
                    "tool_count": len(fm.get("tools", [])),
                    "skill_count": len(fm.get("skills", [])),
                    "bytes": f.stat().st_size,
                }
            )
    codex = sorted((REPO / "CODEX_TEAM/.codex/agents").glob("*.md")) if (
        REPO / "CODEX_TEAM/.codex/agents"
    ).is_dir() else []
    by_team = collections.Counter(a["team"] for a in agents)
    tool_counts = [a["tool_count"] for a in agents if a["tool_count"]]
    return {
        "generated_by": "tools/gen_health_artifacts.py",
        "claude_agents": len(agents),
        "codex_native_agents": len(codex),
        "total_agents": len(agents) + len(codex),
        "by_team": dict(sorted(by_team.items())),
        "frontmatter_complete": sum(
            1 for a in agents if a["name"] and a["has_description"] and a["tool_count"]
        ),
        "name_filename_mismatches": [
            a["path"] for a in agents if not a["name_matches_filename"]
        ],
        "avg_tools_per_agent": round(sum(tool_counts) / len(tool_counts), 1)
        if tool_counts
        else 0,
        "model_pins": dict(
            collections.Counter(a["model_pin"] for a in agents if a["model_pin"])
        ),
        "agents": agents,
        "codex_native": [
            str(p.relative_to(REPO)).replace("\\", "/") for p in codex
        ],
    }


def tool_inventory() -> dict:
    dirs = [REPO / "tools", REPO / "tools/archive"] + [
        REPO / t / "tools" for t in TEAMS
    ]
    tools, unparseable, nodoc = [], [], []
    for d in dirs:
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.py")):
            rel = str(f.relative_to(REPO)).replace("\\", "/")
            tools.append(rel)
            try:
                tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
                if not ast.get_docstring(tree):
                    nodoc.append(rel)
            except (SyntaxError, OSError) as e:
                unparseable.append({"path": rel, "error": type(e).__name__})
    return {
        "total": len(tools),
        "unparseable": unparseable,
        "missing_module_docstring": nodoc,
        "paths": tools,
    }


def run_log_metrics() -> dict:
    log = REPO / "LOGS/agent-runs.jsonl"
    rows, malformed = [], 0
    if log.exists():
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                malformed += 1
    keys = collections.Counter()
    for r in rows:
        keys.update(r.keys())
    # fields tools/agent_log_query.py expects
    expected = ["ts", "agent", "status", "duration_ms", "cost_usd"]
    per_day = collections.Counter(str(r.get("ts", ""))[:10] for r in rows if r.get("ts"))
    conflicts = [
        p.name
        for p in (REPO / "LOGS").glob("agent-runs-*.jsonl")
    ]
    return {
        "records": len(rows),
        "malformed_lines": malformed,
        "observed_fields": dict(keys),
        "expected_by_agent_log_query": expected,
        "missing_fields": [k for k in expected if k not in keys],
        "status_breakdown": dict(
            collections.Counter(str(r.get("status")) for r in rows)
        ),
        "first_ts": min((r["ts"] for r in rows if r.get("ts")), default=None),
        "last_ts": max((r["ts"] for r in rows if r.get("ts")), default=None),
        "active_days": len(per_day),
        "busiest_days": dict(per_day.most_common(5)),
        "per_agent_attribution_possible": "agent" in keys,
        "sync_conflict_copies": len(conflicts),
        "sync_conflict_mb": round(
            sum((REPO / "LOGS" / c).stat().st_size for c in conflicts) / 1048576, 1
        ),
    }


def skill_census() -> dict:
    d = REPO / ".claude/skills"
    dirs = sorted(x.name for x in d.iterdir() if x.is_dir())
    with_md = [x for x in dirs if (d / x / "SKILL.md").exists()]
    ez = [x for x in with_md if x.endswith("-EZ")]
    doc = (
        sorted(x.name for x in (d / "document-skills").iterdir() if x.is_dir())
        if (d / "document-skills").is_dir()
        else []
    )
    team = {}
    for t in TEAMS:
        p = REPO / t / ".claude/skills"
        if p.is_dir():
            team[t] = sorted(x.name for x in p.iterdir() if x.is_dir())
    return {
        "top_level_dirs": len(dirs),
        "top_level_with_skill_md": len(with_md),
        "canonical_top_level": len([x for x in with_md if not x.endswith("-EZ")]),
        "ez_duplicates": ez,
        "ez_duplicate_count": len(ez),
        "document_skills": doc,
        "team_skills": team,
    }


def hook_census() -> dict:
    registered, files = {}, sorted(
        p.name for p in (REPO / ".claude/hooks").glob("*.ps1")
    )
    for cfg in (".claude/settings.json", ".claude/settings.local.json"):
        p = REPO / cfg
        if not p.exists():
            continue
        s = json.loads(p.read_text(encoding="utf-8"))
        for event, groups in s.get("hooks", {}).items():
            for g in groups:
                for h in g.get("hooks", []):
                    m = re.search(r'-File "([^"]+)"', h.get("command", ""))
                    if m:
                        registered.setdefault(os.path.basename(m.group(1)), []).append(
                            {"config": cfg, "event": event}
                        )
    return {
        "scripts_on_disk": len(files),
        "registered": len(registered),
        "orphans": [f for f in files if f not in registered],
        "double_registered": {
            k: v for k, v in registered.items() if len(v) > 1
        },
        "by_event": dict(
            collections.Counter(
                e["event"] for v in registered.values() for e in v
            )
        ),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stamp", required=True, help="report date, YYYY-MM-DD")
    args = ap.parse_args()

    inv = agent_inventory()
    inv["generated_on"] = args.stamp
    inv["skills"] = skill_census()
    inv["tools"] = tool_inventory()
    (REPO / "LOGS/agent-inventory.json").write_text(
        json.dumps(inv, indent=2), encoding="utf-8"
    )

    perf = {
        "generated_by": "tools/gen_health_artifacts.py",
        "generated_on": args.stamp,
        "run_log": run_log_metrics(),
        "hooks": hook_census(),
        "caveat": (
            "LOGS/agent-runs.jsonl is written by the Stop hook and records one row per "
            "session stop, not per subagent run. It carries no agent identity, duration, "
            "or cost, so per-agent invocation counts, response times, and error rates "
            "are NOT derivable. tools/agent_log_query.py reads fields that are never written."
        ),
    }
    (REPO / "LOGS/performance-metrics.json").write_text(
        json.dumps(perf, indent=2), encoding="utf-8"
    )

    print("wrote LOGS/agent-inventory.json")
    print("  claude agents:", inv["claude_agents"], "| codex-native:", inv["codex_native_agents"])
    print("  frontmatter complete:", inv["frontmatter_complete"], "/", inv["claude_agents"])
    print("  name/filename mismatches:", len(inv["name_filename_mismatches"]))
    print("  avg tools/agent:", inv["avg_tools_per_agent"])
    print("  python tools:", inv["tools"]["total"], "| unparseable:", len(inv["tools"]["unparseable"]))
    print("wrote LOGS/performance-metrics.json")
    print("  run-log records:", perf["run_log"]["records"])
    print("  observed fields:", list(perf["run_log"]["observed_fields"]))
    print("  missing fields:", perf["run_log"]["missing_fields"])
    print("  sync-conflict copies:", perf["run_log"]["sync_conflict_copies"],
          "(%.1f MB)" % perf["run_log"]["sync_conflict_mb"])
    print("  hook orphans:", perf["hooks"]["orphans"])
    print("  double-registered:", list(perf["hooks"]["double_registered"]))


if __name__ == "__main__":
    main()
