"""Roster census: count agents, skills, and MCP servers on disk and compare with CLAUDE.md.

CLAUDE.md is the single source of truth for counts (doc-hygiene rule). This script keeps it
honest: counts are derived from the filesystem, never typed by hand.

Usage:
    python tools/census.py           # check; exit 1 if CLAUDE.md disagrees with disk
    python tools/census.py --write   # rewrite the CLAUDE.md header line + team table
    python tools/census.py --json    # print the raw census
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from tools.workspace_registry import discover_agents  # noqa: E402

CODEX_TEAM = "CODEX_TEAM"
HEADER_RE = re.compile(
    r"^(?P<claude>\d+) agents across (?P<teams>\d+) teams, plus (?P<codex>\d+) Codex-native agents "
    r"in CODEX_TEAM \(census (?P<d1>[\d-]+)\) \+ (?P<skills>\d+) skills \((?P<top>\d+) top-level \+ "
    r"(?P<docs>\d+) document-skills; census (?P<d2>[\d-]+)\) \+ (?P<mcp>\d+) MCP servers",
    re.M,
)
ROW_RE = re.compile(r"^\| (?P<team>[A-Z_]+)(?P<rest>[^|]*)\| (?P<n>\d+) \|", re.M)


def take_census(root: Path = REPO) -> dict:
    teams = {team: len(paths) for team, paths in discover_agents(root).items()}
    skills_dir = root / ".claude/skills"
    top = sorted(p.name for p in skills_dir.iterdir()
                 if p.is_dir() and p.name != "document-skills" and (p / "SKILL.md").is_file())
    docs = sorted(p.parent.name for p in (skills_dir / "document-skills").glob("*/SKILL.md"))
    mcp_path = root / ".mcp.json"  # gitignored: absent in fresh clones / cloud sessions
    mcp = len(json.loads(mcp_path.read_text(encoding="utf-8-sig")).get("mcpServers", {})) if mcp_path.is_file() else None
    claude_teams = {t: n for t, n in teams.items() if t != CODEX_TEAM}
    return {
        "teams": teams,
        "claude_agents": sum(claude_teams.values()),
        "claude_team_count": len([t for t in claude_teams if t != "ROOT"]),
        "codex_agents": teams.get(CODEX_TEAM, 0),
        "top_level_skills": len(top),
        "document_skills": len(docs),
        "skill_names": top,
        "mcp_servers": mcp,
    }


def check(text: str, c: dict) -> list[str]:
    problems = []
    m = HEADER_RE.search(text)
    if not m:
        return ["CLAUDE.md header line not found (format changed?)"]
    expect = {"claude": c["claude_agents"], "teams": c["claude_team_count"], "codex": c["codex_agents"],
              "skills": c["top_level_skills"] + c["document_skills"], "top": c["top_level_skills"],
              "docs": c["document_skills"], "mcp": c["mcp_servers"]}
    for key, value in expect.items():
        if value is not None and int(m[key]) != value:
            problems.append(f"Header '{key}' says {m[key]}, disk says {value}")
    rows = {r["team"]: int(r["n"]) for r in ROW_RE.finditer(text)}
    for team, n in c["teams"].items():
        if rows.get(team) != n:
            problems.append(f"Table row {team} says {rows.get(team)}, disk says {n}")
    for team in set(rows) - set(c["teams"]):
        problems.append(f"Table row {team} has no agents on disk")
    return problems


def write(text: str, c: dict, today: str) -> str:
    m = HEADER_RE.search(text)
    mcp = c["mcp_servers"] if c["mcp_servers"] is not None else int(m["mcp"])
    header = (f"{c['claude_agents']} agents across {c['claude_team_count']} teams, plus {c['codex_agents']} "
              f"Codex-native agents in CODEX_TEAM (census {today}) + "
              f"{c['top_level_skills'] + c['document_skills']} skills ({c['top_level_skills']} top-level + "
              f"{c['document_skills']} document-skills; census {today}) + {mcp} MCP servers")
    text = text[:m.start()] + header + text[m.end():]
    return ROW_RE.sub(lambda r: f"| {r['team']}{r['rest']}| {c['teams'].get(r['team'], r['n'])} |", text)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    c = take_census()
    if args.json:
        print(json.dumps(c, indent=2))
        return
    path = REPO / "CLAUDE.md"
    text = path.read_text(encoding="utf-8")
    if args.write:
        path.write_text(write(text, c, dt.date.today().isoformat()), encoding="utf-8")
        text = path.read_text(encoding="utf-8")
    problems = check(text, c)
    print(json.dumps({"ok": not problems, "problems": problems,
                      "census": {k: v for k, v in c.items() if k != "skill_names"}}, indent=2))
    raise SystemExit(0 if not problems else 1)


if __name__ == "__main__":
    main()
