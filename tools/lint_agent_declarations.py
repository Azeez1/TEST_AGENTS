"""Declaration linter: verify every agent's declared tools/skills actually exist.

Checks each agent .md frontmatter against reality:
  - mcp__server__tool entries -> server must exist in .mcp.json and not be disabled
  - snake_case entries        -> tools/<name>.py at repo root or the agent's team tools/
  - kebab-case entries        -> .claude/skills/<name>/SKILL.md (root, document-skills, or team)
  - plugin:skill entries      -> skill part must resolve like a kebab-case skill
  - skills: entries           -> same skill resolution
  - name: field               -> must be kebab-case and match the filename stem

Usage:  python tools/lint_agent_declarations.py [--json]
Exit codes: 0 = clean, 1 = violations found.

Wired into /agent-health (section 1). Born from the 2026-07-12 Factory Audit,
which found phantom n8n tools, a chimera chrome/playwright tool, and a
nonexistent `filesystem` skill declared across 9 sales agents — none of which
any health check caught.
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Built-in Claude Code tools that are always valid in a tools: list.
CORE_TOOLS = {
    "Read", "Write", "Edit", "MultiEdit", "NotebookEdit", "Bash", "PowerShell",
    "Grep", "Glob", "WebFetch", "WebSearch", "Task", "Agent", "TodoWrite",
    "AskUserQuestion", "Skill", "SlashCommand", "KillShell", "BashOutput",
    "ListMcpResourcesTool", "ReadMcpResourceTool",
}

TEAM_DIRS = [
    "MARKETING_TEAM", "ENGINEERING_TEAM", "FINANCIAL_TEAM", "SALES_TEAM",
    "QA_TEAM", "VOICE_TEAM", "PROPOSAL_TEAM", "HEDGE_FUND",
]

# MCP servers that connect at session level (extensions, /chrome) and are
# legitimately absent from .mcp.json.
SESSION_SERVERS = {"claude-in-chrome"}


def load_mcp_servers():
    """Return {server_name: enabled_bool} from .mcp.json (never expose env values)."""
    mcp_path = REPO / ".mcp.json"
    if not mcp_path.exists():
        return {}
    data = json.loads(mcp_path.read_text(encoding="utf-8"))
    servers = {}
    for name, cfg in data.get("mcpServers", {}).items():
        servers[name] = cfg.get("enabled", True) is not False
    return servers


def skill_exists(name: str, team: str | None) -> bool:
    candidates = [
        REPO / ".claude" / "skills" / name / "SKILL.md",
        REPO / ".claude" / "skills" / "document-skills" / name / "SKILL.md",
    ]
    if team:
        candidates.append(REPO / team / ".claude" / "skills" / name / "SKILL.md")
    return any(p.exists() for p in candidates)


def python_tool_exists(name: str, team: str | None) -> bool:
    candidates = [REPO / "tools" / f"{name}.py"]
    if team:
        candidates.append(REPO / team / "tools" / f"{name}.py")
    return any(p.exists() for p in candidates)


def parse_frontmatter_lists(text: str):
    """Return (name_value, tools_list, skills_list) from YAML frontmatter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, [], []
    name_val, tools, skills = None, [], []
    current_key = None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        top = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", line)
        if top:
            key, inline = top.group(1), top.group(2).strip()
            current_key = key
            if key == "name":
                name_val = inline
            # inline empty list form: `skills: []`
            if key in ("tools", "skills") and inline in ("[]", ""):
                continue
        elif current_key in ("tools", "skills"):
            item = re.match(r"^\s+-\s+(.+?)\s*$", line)
            if item:
                (tools if current_key == "tools" else skills).append(item.group(1))
    return name_val, tools, skills


def classify_and_check(entry: str, team: str | None, servers: dict) -> str | None:
    """Return a violation message for this tools: entry, or None if it resolves."""
    if entry in CORE_TOOLS:
        return None
    if entry.startswith("mcp__"):
        parts = entry.split("__")
        if len(parts) < 3:
            return f"malformed MCP tool name: {entry}"
        server = parts[1]
        if server in SESSION_SERVERS:
            return None
        if server not in servers:
            return f"MCP server '{server}' not in .mcp.json (entry: {entry})"
        if not servers[server]:
            return f"MCP server '{server}' is disabled in .mcp.json (entry: {entry})"
        return None
    if ":" in entry:  # plugin:skill form
        skill = entry.split(":", 1)[1]
        if skill_exists(skill, team):
            return None
        return f"plugin skill not found: {entry}"
    if "_" in entry and "-" not in entry:  # snake_case -> python tool
        if python_tool_exists(entry, team):
            return None
        # some snake_case entries are really skills (e.g. wiki tools)
        if skill_exists(entry, team):
            return None
        return f"python tool not found: {entry} (looked in tools/ and {team or 'ROOT'}/tools/)"
    # kebab-case or single word -> skill, then python fallback
    if skill_exists(entry, team):
        return None
    if python_tool_exists(entry, team):
        return None
    return f"skill not found: {entry}"


def main():
    servers = load_mcp_servers()
    agent_files = sorted((REPO / ".claude" / "agents").glob("*.md"))
    for team in TEAM_DIRS:
        agent_files += sorted((REPO / team / ".claude" / "agents").glob("*.md"))

    violations = {}
    for path in agent_files:
        team = path.parts[len(REPO.parts)] if path.parts[len(REPO.parts)] in TEAM_DIRS else None
        text = path.read_text(encoding="utf-8", errors="replace")
        name_val, tools, skills = parse_frontmatter_lists(text)
        problems = []

        stem = path.stem
        if name_val is None:
            problems.append("missing name: field in frontmatter")
        elif name_val != stem:
            problems.append(f"name '{name_val}' != filename stem '{stem}' (must match, kebab-case)")

        for entry in tools:
            msg = classify_and_check(entry, team, servers)
            if msg:
                problems.append(f"tools: {msg}")
        for entry in skills:
            skill = entry.split(":", 1)[1] if ":" in entry else entry
            if not skill_exists(skill, team):
                problems.append(f"skills: skill not found: {entry}")

        if problems:
            violations[str(path.relative_to(REPO))] = problems

    if "--json" in sys.argv:
        print(json.dumps({"agents_scanned": len(agent_files), "violations": violations}, indent=2))
    else:
        print(f"Scanned {len(agent_files)} agent files against {len(servers)} MCP servers.")
        if not violations:
            print("CLEAN: every declared tool and skill resolves.")
        else:
            print(f"VIOLATIONS in {len(violations)} file(s):")
            for f, probs in violations.items():
                print(f"\n  {f}")
                for p in probs:
                    print(f"    - {p}")
    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    main()
