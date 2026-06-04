"""Export Claude-first agents and skills into a Codex-facing layer.

This script does not modify .claude infrastructure. It creates a parallel
.codex layer with:
- agent instruction mirrors under .codex/agents/
- skill mirrors under .codex/skills-export/
- a manifest that maps source files to Codex files
- a secrets template for local runtime configuration

Secrets are never copied from .mcp.json into generated files.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path.cwd()

AGENT_DIRS = {
    "ROOT": ROOT / ".claude" / "agents",
    "MARKETING_TEAM": ROOT / "MARKETING_TEAM" / ".claude" / "agents",
    "ENGINEERING_TEAM": ROOT / "ENGINEERING_TEAM" / ".claude" / "agents",
    "QA_TEAM": ROOT / "QA_TEAM" / ".claude" / "agents",
    "PROPOSAL_TEAM": ROOT / "PROPOSAL_TEAM" / ".claude" / "agents",
    "FINANCIAL_TEAM": ROOT / "FINANCIAL_TEAM" / ".claude" / "agents",
    "SALES_TEAM": ROOT / "SALES_TEAM" / ".claude" / "agents",
}

NATIVE_CODEX_AGENT_DIRS = {
    "CODEX_TEAM": ROOT / "CODEX_TEAM" / ".codex" / "agents",
}

CODEX_DIR = ROOT / ".codex"
CODEX_AGENTS_DIR = CODEX_DIR / "agents"
CODEX_COMMANDS_DIR = CODEX_DIR / "commands"
CODEX_SKILLS_EXPORT_DIR = CODEX_DIR / "skills-export"
CODEX_HOME = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
GLOBAL_CODEX_SKILLS_DIR = CODEX_HOME / "skills"
CLAUDE_SKILLS_DIR = ROOT / ".claude" / "skills"
CLAUDE_SETTINGS_PATH = ROOT / ".claude" / "settings.json"
CLAUDE_SETTINGS_LOCAL_PATH = ROOT / ".claude" / "settings.local.json"
CLAUDE_HOOKS_DIR = ROOT / ".claude" / "hooks"
CODEX_HOOKS_DIR = CODEX_DIR / "hooks"
MCP_PATH = ROOT / ".mcp.json"

MODEL_MAP = {
    "claude-opus-4-6": "gpt-5.5",
    "claude-sonnet-4-6": "gpt-5.4",
}

NATIVE_CODEX_SKILLS = {
    "agent-auditor": ".codex/skills/agent-auditor/SKILL.md",
    "code-review": ".codex/skills/code-review/SKILL.md",
    "debug-investigator": ".codex/skills/debug-investigator/SKILL.md",
}

NATIVE_OR_EXTERNAL_CAPABILITIES = {
    "filesystem": "Codex native file tools and sandbox permissions",
    "figma": "Codex Figma connector when available",
    "context7": "Use web/docs lookup or a configured docs MCP equivalent",
}

SECRET_ENV_NAMES = {
    "OPENAI_API_KEY",
    "GOOGLE_OAUTH_CLIENT_ID",
    "GOOGLE_OAUTH_CLIENT_SECRET",
    "PERPLEXITY_API_KEY",
    "PERPLEXITY_TIMEOUT_MS",
    "API_TOKEN",
    "N8N_API_URL",
    "N8N_API_KEY",
    "GEMINI_API_KEY",
    "PIAPI_API_KEY",
    "XAI_API_KEY",
}


@dataclass
class AgentExport:
    slug: str
    display_name: str
    team: str
    source: str
    codex_instructions: str
    source_runtime: str
    claude_model: str | None
    codex_model: str
    tools: list[str]
    skills: list[str]
    capabilities: list[str]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, flags=re.DOTALL)
    if not match:
        return {}, text
    return parse_simple_yaml(match.group(1)), text[match.end() :]


def parse_simple_yaml(frontmatter: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in frontmatter.splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        list_item = re.match(r"^\s*-\s*(.+?)\s*$", line)
        if list_item and current_key:
            data.setdefault(current_key, []).append(strip_quotes(list_item.group(1)))
            continue
        key_value = re.match(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$", line)
        if key_value:
            key, value = key_value.groups()
            current_key = key
            if value == "":
                data[key] = []
            elif value == "[]":
                data[key] = []
            elif value.startswith("[") and value.endswith("]"):
                inner = value[1:-1].strip()
                data[key] = [strip_quotes(item.strip()) for item in inner.split(",") if item.strip()]
            else:
                data[key] = strip_quotes(value)
    return data


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def sanitize_skill_frontmatter(skill_file: Path, fallback_name: str) -> None:
    text = skill_file.read_text(encoding="utf-8", errors="replace")
    frontmatter, body = parse_frontmatter(text)
    if not frontmatter:
        return
    name = str(frontmatter.get("name") or fallback_name)
    description = str(
        frontmatter.get("description")
        or f"Exported Claude skill for Codex use: {fallback_name}"
    )
    sanitized = (
        "---\n"
        f"name: {json.dumps(name)}\n"
        f"description: {json.dumps(description)}\n"
        "---\n\n"
        f"{body.lstrip()}"
    )
    skill_file.write_text(sanitized, encoding="utf-8", newline="\n")


def yaml_list(items: list[str]) -> str:
    if not items:
        return "[]"
    return "\n" + "\n".join(f"  - {item}" for item in items)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def remove_tree(path: Path) -> None:
    def handle_remove_error(function: Any, failed_path: str, _exc_info: Any) -> None:
        os.chmod(failed_path, 0o700)
        function(failed_path)

    if path.is_symlink():
        path.unlink()
        return
    if path.exists():
        shutil.rmtree(path, onerror=handle_remove_error)


def load_enabled_claude_skills() -> set[str]:
    if not CLAUDE_SETTINGS_PATH.exists():
        return set()
    try:
        settings = json.loads(CLAUDE_SETTINGS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    skills = settings.get("skills", {})
    return {
        name
        for name, config in skills.items()
        if isinstance(config, dict) and config.get("enabled") is True
    }


def find_skill_source(skill_name: str) -> Path | None:
    direct = CLAUDE_SKILLS_DIR / skill_name / "SKILL.md"
    if direct.exists():
        return direct.parent
    for skill_path in CLAUDE_SKILLS_DIR.rglob("SKILL.md"):
        if skill_path.parent.name == skill_name:
            return skill_path.parent
    nested = CLAUDE_SKILLS_DIR / skill_name
    if nested.exists() and nested.is_dir():
        found = list(nested.rglob("SKILL.md"))
        if found:
            return found[0].parent
    if "/" in skill_name:
        path = CLAUDE_SKILLS_DIR / skill_name / "SKILL.md"
        if path.exists():
            return path.parent
    return None


def extract_secret_env_names() -> list[str]:
    names = set(SECRET_ENV_NAMES)
    if MCP_PATH.exists():
        text = MCP_PATH.read_text(encoding="utf-8", errors="ignore")
        for match in re.finditer(r'"([A-Z][A-Z0-9_]+)"\s*:', text):
            key = match.group(1)
            if any(token in key for token in ("KEY", "TOKEN", "SECRET", "CLIENT", "URL", "TIMEOUT")):
                names.add(key)
    return sorted(names)


def build_agent_doc(export: AgentExport, body: str) -> str:
    runtime_notes = f"""---
name: {export.slug}
display_name: {export.display_name}
team: {export.team}
source: {export.source}
source_runtime: {export.source_runtime}
codex_model: {export.codex_model}
claude_model: {export.claude_model or ""}
skills:{yaml_list(export.skills)}
capabilities:{yaml_list(export.capabilities)}
---

# {export.display_name}

## Codex Runtime Notes

This file is generated for Codex from `{export.source}`. Do not edit it by hand;
update the Claude source or the exporter instead.

Codex does not receive Claude Code MCP tools or Claude runtime skill bindings
directly. Treat Claude `tools:` and `skills:` as capability documentation unless
a matching Codex skill, connector, MCP server, or local script is available.

Claude tools declared by the source agent:
{yaml_list(export.tools)}

When an API-backed capability is needed, prefer this order:
1. Use a Codex-native connector/tool if one is available in the current session.
2. Use a mirrored Codex skill from `.codex/skills-export/` when it is instruction-only or local-file based.
3. Use local Python tools only when required environment variables are present.
4. Produce a clear handoff if the capability is Claude-only in the current runtime.

"""
    return runtime_notes + body


def build_native_codex_agent_doc(export: AgentExport, body: str) -> str:
    runtime_notes = f"""---
name: {export.slug}
display_name: {export.display_name}
team: {export.team}
source: {export.source}
source_runtime: {export.source_runtime}
codex_model: {export.codex_model}
claude_model: {export.claude_model or ""}
skills:{yaml_list(export.skills)}
capabilities:{yaml_list(export.capabilities)}
---

# {export.display_name}

## Codex Runtime Notes

This file is generated for Codex from the Codex-native source `{export.source}`.
Do not edit this generated file by hand; update the source file under
`CODEX_TEAM/.codex/agents/` or the exporter instead.

This agent is allowed to work on Codex-facing infrastructure only. It must not
modify `.claude/`, Claude agent definitions, or `.mcp.json` unless the user
explicitly asks for that boundary to change.

Declared Codex tools/capabilities:
{yaml_list(export.tools)}

"""
    return runtime_notes + body


def export_agents() -> list[AgentExport]:
    exports: list[AgentExport] = []
    for team, directory in AGENT_DIRS.items():
        if not directory.exists():
            continue
        for source_path in sorted(directory.glob("*.md")):
            text = source_path.read_text(encoding="utf-8", errors="replace")
            frontmatter, body = parse_frontmatter(text)
            slug = source_path.stem
            display_name = str(frontmatter.get("name") or slug)
            claude_model = frontmatter.get("model")
            codex_model = MODEL_MAP.get(str(claude_model), "gpt-5.4")
            tools = [str(item) for item in frontmatter.get("tools", [])]
            skills = [str(item) for item in frontmatter.get("skills", [])]
            capabilities = [str(item) for item in frontmatter.get("capabilities", [])]
            target = CODEX_AGENTS_DIR / team / f"{slug}.md"
            export = AgentExport(
                slug=slug,
                display_name=display_name,
                team=team,
                source=rel(source_path),
                codex_instructions=rel(target),
                source_runtime="claude",
                claude_model=str(claude_model) if claude_model else None,
                codex_model=codex_model,
                tools=tools,
                skills=skills,
                capabilities=capabilities,
            )
            write_text(target, build_agent_doc(export, body))
            exports.append(export)
    for team, directory in NATIVE_CODEX_AGENT_DIRS.items():
        if not directory.exists():
            continue
        for source_path in sorted(directory.glob("*.md")):
            text = source_path.read_text(encoding="utf-8", errors="replace")
            frontmatter, body = parse_frontmatter(text)
            slug = source_path.stem
            display_name = str(frontmatter.get("name") or slug)
            codex_model = str(frontmatter.get("codex_model") or "gpt-5.4")
            tools = [str(item) for item in frontmatter.get("tools", [])]
            skills = [str(item) for item in frontmatter.get("skills", [])]
            capabilities = [str(item) for item in frontmatter.get("capabilities", [])]
            target = CODEX_AGENTS_DIR / team / f"{slug}.md"
            export = AgentExport(
                slug=slug,
                display_name=display_name,
                team=team,
                source=rel(source_path),
                codex_instructions=rel(target),
                source_runtime="codex",
                claude_model=None,
                codex_model=codex_model,
                tools=tools,
                skills=skills,
                capabilities=capabilities,
            )
            write_text(target, build_native_codex_agent_doc(export, body))
            exports.append(export)
    return exports


def export_skills() -> list[dict[str, Any]]:
    exported: list[dict[str, Any]] = []
    enabled = load_enabled_claude_skills()
    names = set(enabled)
    for skill_path in CLAUDE_SKILLS_DIR.rglob("SKILL.md"):
        names.add(skill_path.parent.name)

    remove_tree(CODEX_SKILLS_EXPORT_DIR)
    CODEX_SKILLS_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    for name in sorted(names):
        if name in NATIVE_CODEX_SKILLS:
            exported.append(
                {
                    "name": name,
                    "status": "codex_native",
                    "codexPath": NATIVE_CODEX_SKILLS[name],
                }
            )
            continue
        if name in NATIVE_OR_EXTERNAL_CAPABILITIES:
            exported.append(
                {
                    "name": name,
                    "status": "native_or_external",
                    "note": NATIVE_OR_EXTERNAL_CAPABILITIES[name],
                }
            )
            continue
        source_dir = find_skill_source(name)
        if source_dir is None:
            exported.append({"name": name, "status": "missing_source"})
            continue
        target_dir = CODEX_SKILLS_EXPORT_DIR / name
        shutil.copytree(source_dir, target_dir)
        sanitize_skill_frontmatter(target_dir / "SKILL.md", name)
        exported.append(
            {
                "name": name,
                "status": "exported",
                "source": rel(source_dir),
                "codexPath": rel(target_dir / "SKILL.md"),
            }
        )
    exported.extend(write_codex_workflow_skills())
    return exported


def write_codex_workflow_skills() -> list[dict[str, Any]]:
    workflow_skills = {
        "test-agents-router": {
            "description": "Select the right TEST_AGENTS specialist and load its Codex sidecar instructions.",
            "body": """# TEST_AGENTS Router

Use this skill when the user asks for work in TEST_AGENTS but does not name a specific agent.

## Routing Process

1. Read `.codex/manifest.json`.
2. Match the user's request against each agent's `team`, `slug`, `display_name`, `capabilities`, `skills`, and `tools`.
3. Choose the narrowest specialist that can complete the task.
4. Load that agent's `codex_instructions` file before doing the work.
5. Read the team's memory/config files referenced by that agent.
6. Save deliverables in the selected team's `outputs/` folder.

Do not read `.claude/agents/` directly unless the sidecar is missing or stale. If stale, run `$codex-sync-secrets` first.

## Fast Routing Map

- Broad marketing campaign, unclear marketing request: `MARKETING_TEAM/router-agent`
- Blog, article, web copy, internal comms: `MARKETING_TEAM/copywriter`
- Editorial calendar or content plan: `MARKETING_TEAM/content-strategist`
- Social posts or platform content: `MARKETING_TEAM/social-media-manager`
- Images, graphics, visual prompts: `MARKETING_TEAM/visual-designer`
- Video, Sora, Veo, UGC ads: `MARKETING_TEAM/video-producer`
- Email campaigns/newsletters: `MARKETING_TEAM/email-specialist` or `MARKETING_TEAM/newsletter-agent`
- Gmail/search/send/read email: `MARKETING_TEAM/gmail-agent`
- SEO/keywords/rank research: `MARKETING_TEAM/seo-specialist`
- Market research or competitive intel: `MARKETING_TEAM/research-agent`
- Lead generation/prospecting: `MARKETING_TEAM/lead-gen-agent`
- Landing pages: `MARKETING_TEAM/landing-page-specialist`
- Presentations: `MARKETING_TEAM/presentation-designer`
- PDFs: `MARKETING_TEAM/pdf-specialist`
- n8n/workflow automation: `MARKETING_TEAM/automation-agent`
- Broad engineering or architecture: `ENGINEERING_TEAM/cto`
- Frontend/UI implementation: `ENGINEERING_TEAM/frontend-developer`
- Backend/API/database systems: `ENGINEERING_TEAM/backend-architect` or `ENGINEERING_TEAM/database-architect`
- Security review: `ENGINEERING_TEAM/security-auditor`
- Debugging/root cause: `ENGINEERING_TEAM/debugger`
- Code review: `ENGINEERING_TEAM/code-reviewer`
- Tests/QA automation: `ENGINEERING_TEAM/test-engineer` or `QA_TEAM/test-orchestrator`
- Unit tests: `QA_TEAM/unit-test-agent`
- Integration/API tests: `QA_TEAM/integration-test-agent`
- Edge cases: `QA_TEAM/edge-case-agent`
- Fixtures/mock data: `QA_TEAM/fixture-agent`
- RFP/proposal automation: `PROPOSAL_TEAM/rfp-agent`
- Finance strategy: `FINANCIAL_TEAM/cfo-agent`
- Deal/M&A analysis: `FINANCIAL_TEAM/deal-analyst`
- Valuation/DCF: `FINANCIAL_TEAM/valuation-agent`
- Forecasting/FP&A: `FINANCIAL_TEAM/forecasting-agent` or `FINANCIAL_TEAM/fpna-agent`
- Accounting/controller/tax/treasury: matching FINANCIAL_TEAM specialist
- Broad sales workflow: `SALES_TEAM/sales-manager`
- SDR/outbound prospecting: `SALES_TEAM/sdr-agent` or `SALES_TEAM/outbound-specialist`
- Account execution/deal management: `SALES_TEAM/account-executive`
- CRM/pipeline ops: `SALES_TEAM/sales-operations`
- Sales metrics: `SALES_TEAM/sales-analyst`
- Sales proposals/pricing: `SALES_TEAM/proposal-specialist`
- Customer success/retention: `SALES_TEAM/customer-success-manager`
- PE investor outreach: `SALES_TEAM/pe-outreach-agent`
- Cross-team QA/verification: `ROOT/supervisor`
- Personal wiki/second brain: `ROOT/oracle`

## Tie Breakers

If the task is broad, use the team's orchestrator. If the task names a concrete artifact or workflow, use the specialist. If the request needs multiple teams, start with the orchestrator for the user's primary outcome and mention secondary agents as needed.
""",
        },
        "codex-sync": {
            "description": "Refresh the local Codex sidecar layer from Claude agents and skills.",
            "body": """# Codex Sync

Run this command from the TEST_AGENTS repo root:

```powershell
python scripts\\export_codex_layer.py
```

After it runs, report the exported agent count, processed skill count, and any `missing_source` skills in `.codex/manifest.json`.

Do not modify `.claude/`.
""",
        },
        "codex-sync-secrets": {
            "description": "Refresh Codex sidecar files and sync local API key env values from Claude MCP config.",
            "body": """# Codex Sync Secrets

Run this command from the TEST_AGENTS repo root:

```powershell
python scripts\\export_codex_layer.py --write-local-secrets --install-global-skills --write-codex-mcp-config
```

Rules:
- Do not print `.codex/secrets.local.env`.
- Do not reveal API keys, tokens, OAuth secrets, or credential values.
- Confirm only that local env files exist and are ignored by git.
- Confirm only MCP server names, not secret values.
- Prefer Codex-native connectors/tools when available.

Do not modify `.claude/`.
""",
        },
        "codex-validate": {
            "description": "Validate the generated Codex sidecar manifest and installed skill status.",
            "body": """# Codex Validate

Validate the generated Codex sidecar layer:

```powershell
$m = Get-Content .codex\\manifest.json -Raw | ConvertFrom-Json
"agents=$($m.agents.Count)"
"skills=$($m.skills.Count)"
$m.skills | Group-Object status | Select-Object Count,Name | Format-Table -AutoSize
git check-ignore -v .codex\\secrets.local.env .codex\\runtime.local.json
git check-ignore -v .codex\\config.toml .codex\\mcp.generated.toml
```

Report counts and any `missing_source` skills. Do not print secret file contents.
""",
        },
        "codex-sync-mcps": {
            "description": "Generate the local Codex MCP config from Claude .mcp.json.",
            "body": """# Codex Sync MCPs

Run this command from the TEST_AGENTS repo root:

```powershell
python scripts\\export_codex_layer.py --write-codex-mcp-config
```

This creates `.codex/config.toml` and `.codex/mcp.generated.toml` using the MCP servers from `.mcp.json`.

Rules:
- Do not print generated config contents because it may contain local API keys.
- Report only MCP server names.
- Restart Codex after regenerating MCP config.
- Do not modify `.claude/` or `.mcp.json`.
""",
        },
        "codex-sync-all": {
            "description": "Refresh Codex agents, skills, local secrets, and MCP config from Claude-side files.",
            "body": """# Codex Sync All

Run this command from the TEST_AGENTS repo root:

```powershell
python scripts\\export_codex_layer.py --write-local-secrets --install-global-skills --write-codex-mcp-config
```

This refreshes agents, skills, local secret handoff, and local Codex MCP config.

Rules:
- Do not print secret files or MCP config values.
- Report counts and MCP server names only.
- Restart Codex after this command so skills and MCP servers are discovered.
""",
        },
    }
    exports: list[dict[str, Any]] = []
    for name, spec in workflow_skills.items():
        target_dir = CODEX_SKILLS_EXPORT_DIR / name
        target_dir.mkdir(parents=True, exist_ok=True)
        content = f"""---
name: {name}
description: {spec["description"]}
---

{spec["body"]}
"""
        write_text(target_dir / "SKILL.md", content)
        exports.append(
            {
                "name": name,
                "status": "exported",
                "source": "generated",
                "codexPath": rel(target_dir / "SKILL.md"),
            }
        )
    return exports


def write_codex_root_doc(agent_exports: list[AgentExport]) -> None:
    by_team: dict[str, list[AgentExport]] = {}
    for agent in agent_exports:
        by_team.setdefault(agent.team, []).append(agent)

    lines = [
        "# TEST_AGENTS Codex Layer",
        "",
        "This directory is generated from Claude-first sources plus Codex-native sources without modifying `.claude/`.",
        "",
        "- Claude mirrors come from team `.claude/agents/` files.",
        "- Codex-native agents come from `CODEX_TEAM/.codex/agents/`.",
        "",
        "## Runtime Rules",
        "",
        "- Load agent instructions from `.codex/agents/<team>/<agent>.md`.",
        "- Load exported skills from `.codex/skills-export/<skill>/SKILL.md` when no native Codex skill exists.",
        "- Use Codex-native tools/connectors first when available.",
        "- Do not assume Claude MCP tools are callable from Codex.",
        "- Do not write secrets into generated files. Use `.codex/secrets.local.env` locally.",
        "",
        "## Local Slash Commands",
        "",
        "- `/codex-sync`: refresh Codex agents, skills, manifest, and docs from Claude and Codex-native sources.",
        "- `/codex-sync-secrets`: refresh Codex agents/skills and update local Codex env values from `.mcp.json`.",
        "- `$codex-sync-mcps`: generate local Codex MCP config from Claude `.mcp.json`.",
        "- `$codex-sync-all`: refresh agents, skills, secrets, and MCP config.",
        "",
        "## Agent Index",
        "",
    ]
    for team in sorted(by_team):
        lines.append(f"### {team}")
        for agent in sorted(by_team[team], key=lambda item: item.slug):
            lines.append(f"- `{agent.slug}`: `{agent.codex_instructions}`")
        lines.append("")
    write_text(CODEX_DIR / "AGENTS.md", "\n".join(lines))


def write_codex_commands() -> None:
    sync_command = """---
description: Refresh the local Codex sidecar layer from Claude agents and skills
---

# Codex Sync

Run the local exporter to refresh Codex-facing agents, skills, manifest, and docs from the Claude-first repository.

```powershell
python scripts\\export_codex_layer.py
```

After it runs, summarize:
- number of agents exported
- number of skills processed
- any skills marked `missing_source` in `.codex/manifest.json`

Do not modify `.claude/`.
"""
    secrets_command = """---
description: Refresh Codex sidecar layer and sync local API key env values from Claude MCP config
---

# Codex Sync Secrets

Run the local exporter with secret handoff enabled. This copies environment variable values from local `.mcp.json` into `.codex/secrets.local.env`, which is gitignored.

```powershell
python scripts\\export_codex_layer.py --write-local-secrets
```

Rules:
- Do not print `.codex/secrets.local.env`.
- Do not reveal API keys, tokens, OAuth secrets, or credential values.
- Confirm only that the local env file exists and is ignored by git.
- Prefer Codex-native connectors/tools at runtime when available.
- Use `.codex/secrets.local.env` only for local script/tool fallbacks.

Do not modify `.claude/`.
"""
    validate_command = """---
description: Check the generated Codex sidecar manifest and local ignore rules
---

# Codex Validate

Validate the generated Codex sidecar layer.

Run:

```powershell
$m = Get-Content .codex\\manifest.json -Raw | ConvertFrom-Json
"agents=$($m.agents.Count)"
"skills=$($m.skills.Count)"
$m.skills | Group-Object status | Select-Object Count,Name | Format-Table -AutoSize
git check-ignore -v .codex\\secrets.local.env .codex\\runtime.local.json
```

Report counts and any `missing_source` skills. Do not print secret file contents.
"""
    write_text(CODEX_COMMANDS_DIR / "codex-sync.md", sync_command)
    write_text(CODEX_COMMANDS_DIR / "codex-sync-secrets.md", secrets_command)
    write_text(CODEX_COMMANDS_DIR / "codex-validate.md", validate_command)


def write_secret_template() -> None:
    names = extract_secret_env_names()
    lines = [
        "# Local Codex secrets template.",
        "# Copy to .codex/secrets.local.env and fill values locally.",
        "# This file intentionally contains no secret values.",
        "",
    ]
    lines.extend(f"{name}=" for name in names)
    write_text(CODEX_DIR / "secrets.example.env", "\n".join(lines) + "\n")


def collect_mcp_env_values() -> dict[str, str]:
    if not MCP_PATH.exists():
        return {}
    try:
        config = json.loads(MCP_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    values: dict[str, str] = {}
    servers = config.get("mcpServers", {})
    if not isinstance(servers, dict):
        return values
    for server_config in servers.values():
        if not isinstance(server_config, dict):
            continue
        env = server_config.get("env", {})
        if not isinstance(env, dict):
            continue
        for key, value in env.items():
            if isinstance(key, str) and isinstance(value, str):
                values[key] = value
    return values


def write_local_secrets() -> None:
    names = extract_secret_env_names()
    values = collect_mcp_env_values()
    lines = [
        "# Local Codex secrets generated from .mcp.json.",
        "# This file is gitignored. Do not commit it.",
        "",
    ]
    for name in names:
        lines.append(f"{name}={values.get(name, '')}")
    target = CODEX_DIR / "secrets.local.env"
    write_text(target, "\n".join(lines) + "\n")
    os.chmod(target, 0o600)
    runtime = {
        "schema": "test-agents/codex-runtime-local/v1",
        "envFile": ".codex/secrets.local.env",
        "mcpSource": ".mcp.json",
        "notes": [
            "Generated local runtime file. It contains no secret values.",
            "Load envFile before running local API-backed tools from Codex.",
            "Prefer Codex-native tools/connectors when they are available.",
        ],
    }
    write_text(CODEX_DIR / "runtime.local.json", json.dumps(runtime, indent=2) + "\n")


def toml_string(value: str) -> str:
    return json.dumps(value)


def toml_array(values: list[str]) -> str:
    return "[" + ", ".join(toml_string(value) for value in values) + "]"


def toml_inline_env(env: dict[str, str]) -> str:
    if not env:
        return "{}"
    parts = [f"{toml_string(key)} = {toml_string(value)}" for key, value in sorted(env.items())]
    return "{ " + ", ".join(parts) + " }"


def write_codex_mcp_config() -> list[str]:
    if not MCP_PATH.exists():
        raise FileNotFoundError(".mcp.json not found")
    config = json.loads(MCP_PATH.read_text(encoding="utf-8"))
    servers = config.get("mcpServers", {})
    if not isinstance(servers, dict):
        raise ValueError(".mcp.json does not contain an mcpServers object")

    lines = [
        "# Generated from ../.mcp.json for local Codex use.",
        "# This file is gitignored because it may contain local API keys.",
        "# Regenerate with: python scripts\\export_codex_layer.py --write-codex-mcp-config",
        "",
    ]
    written_names: list[str] = []
    for name, server in sorted(servers.items()):
        if not isinstance(server, dict):
            continue
        block: list[str] = [f"[mcp_servers.{name}]"]
        if server.get("url"):
            block.append(f"url = {toml_string(str(server['url']))}")
        else:
            command = server.get("command")
            if not command:
                continue
            command_text = str(command)
            if os.name == "nt" and command_text == "npx":
                command_text = "npx.cmd"
            block.append(f"command = {toml_string(command_text)}")
            args = server.get("args", [])
            if isinstance(args, list):
                arg_values = [str(item) for item in args]
                if command_text == "npx.cmd" and arg_values and arg_values[0] not in {"-y", "--yes"}:
                    arg_values = ["-y", *arg_values]
                block.append(f"args = {toml_array(arg_values)}")
            env = server.get("env", {})
            if isinstance(env, dict):
                block.append(f"env = {toml_inline_env({str(k): str(v) for k, v in env.items()})}")
        block.extend(["enabled = true", "startup_timeout_sec = 90", "tool_timeout_sec = 120", ""])
        lines.extend(block)
        written_names.append(str(name))

    content = "\n".join(lines)
    write_text(CODEX_DIR / "mcp.generated.toml", content)
    write_text(CODEX_DIR / "config.toml", content)
    return written_names


# --- Hook sync ---------------------------------------------------------------
# Codex runs the SAME hook schema as Claude Code (.codex/hooks.json mirrors the
# .claude settings hooks block, and Codex already executes .ps1 gates). So we
# reuse the IDENTICAL PowerShell gate files instead of maintaining a divergent
# Python port — Codex enforcement stays byte-for-byte in sync with Claude. The
# Codex-only claude_boundary_gate.py is preserved and kept first in PreToolUse.

CODEX_BOUNDARY_GATE_ENTRY = {
    "matcher": "*",
    "hooks": [
        {
            "type": "command",
            "command": 'python "' + str(CODEX_HOOKS_DIR / "claude_boundary_gate.py") + '"',
        }
    ],
}

# Codex-native consolidation of the Claude guardrail gates. Wired with matcher
# "*" because Codex names tools differently (command_execution / apply_patch),
# so Claude's tool-name matchers ("Bash"/"Write") would never fire. This gate
# classifies the tool itself and blocks with the Codex exit-1 contract. Lives at
# .codex/hooks/enforcement_gate.py (hand-maintained, like claude_boundary_gate.py;
# sync copies *.ps1 only, so it is preserved across runs).
CODEX_ENFORCEMENT_GATE_ENTRY = {
    "matcher": "*",
    "hooks": [
        {
            "type": "command",
            "command": 'python "' + str(CODEX_HOOKS_DIR / "enforcement_gate.py") + '"',
        }
    ],
}


def rewrite_hook_command(command: str) -> str:
    """Point a Claude hook command at its Codex mirror copy."""
    return command.replace(".claude\\hooks", ".codex\\hooks").replace(
        ".claude/hooks", ".codex/hooks"
    )


def load_hooks_block(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    hooks = data.get("hooks", {})
    return hooks if isinstance(hooks, dict) else {}


def sync_codex_hooks() -> dict[str, int]:
    """Mirror Claude PowerShell hook scripts + wiring into the Codex layer.

    1. Copy every *.ps1 gate and the config/ dir from .claude/hooks into
       .codex/hooks (overwrite). The Codex-native claude_boundary_gate.py is
       left untouched.
    2. Regenerate .codex/hooks.json from BOTH Claude settings files, rewriting
       paths to the Codex copies and injecting the boundary gate first.
    """
    CODEX_HOOKS_DIR.mkdir(parents=True, exist_ok=True)

    copied = 0
    if CLAUDE_HOOKS_DIR.exists():
        for ps1 in sorted(CLAUDE_HOOKS_DIR.glob("*.ps1")):
            shutil.copy2(ps1, CODEX_HOOKS_DIR / ps1.name)
            copied += 1
        claude_config = CLAUDE_HOOKS_DIR / "config"
        if claude_config.exists():
            codex_config = CODEX_HOOKS_DIR / "config"
            codex_config.mkdir(parents=True, exist_ok=True)
            for cfg in sorted(claude_config.glob("*")):
                if cfg.is_file():
                    shutil.copy2(cfg, codex_config / cfg.name)
        for doc in ("GUARDRAILS.md", "README.md"):
            src = CLAUDE_HOOKS_DIR / doc
            if src.exists():
                shutil.copy2(src, CODEX_HOOKS_DIR / doc)

    merged: dict[str, list[Any]] = {}
    for settings_path in (CLAUDE_SETTINGS_PATH, CLAUDE_SETTINGS_LOCAL_PATH):
        for event, entries in load_hooks_block(settings_path).items():
            if not isinstance(entries, list):
                continue
            bucket = merged.setdefault(event, [])
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                bucket.append(
                    {
                        "matcher": entry.get("matcher", "*"),
                        "hooks": [
                            {
                                "type": h.get("type", "command"),
                                "command": rewrite_hook_command(str(h.get("command", ""))),
                            }
                            for h in entry.get("hooks", [])
                            if isinstance(h, dict)
                        ],
                    }
                )

    pre = merged.setdefault("PreToolUse", [])
    pre.insert(0, CODEX_ENFORCEMENT_GATE_ENTRY)
    pre.insert(0, CODEX_BOUNDARY_GATE_ENTRY)

    # Dedupe identical entries that appear in both settings files.
    wired = 0
    for event, entries in merged.items():
        seen: set[str] = set()
        unique: list[Any] = []
        for entry in entries:
            key = json.dumps(entry, sort_keys=True)
            if key in seen:
                continue
            seen.add(key)
            unique.append(entry)
            wired += len(entry.get("hooks", []))
        merged[event] = unique

    write_text(CODEX_DIR / "hooks.json", json.dumps({"hooks": merged}, indent=2) + "\n")
    return {"copied": copied, "wired": wired}


def write_manifest(agent_exports: list[AgentExport], skill_exports: list[dict[str, Any]]) -> None:
    manifest = {
        "schema": "test-agents/codex-layer/v1",
        "sourceRuntime": "claude+codex-native",
        "targetRuntime": "codex",
        "notes": [
            "Generated without modifying .claude infrastructure.",
            "Codex-native agents are loaded from CODEX_TEAM/.codex/agents.",
            "Secrets are referenced by environment variable name only.",
            "Claude MCP tools are treated as capability documentation for Codex.",
        ],
        "agents": [agent.__dict__ for agent in agent_exports],
        "skills": skill_exports,
        "installedSkillsDir": str(GLOBAL_CODEX_SKILLS_DIR),
        "codexMcpConfig": {
            "projectConfig": ".codex/config.toml",
            "generatedConfig": ".codex/mcp.generated.toml",
            "generatedFrom": ".mcp.json",
        },
        "secrets": {
            "template": ".codex/secrets.example.env",
            "local": ".codex/secrets.local.env",
            "envNames": extract_secret_env_names(),
        },
    }
    write_text(CODEX_DIR / "manifest.json", json.dumps(manifest, indent=2) + "\n")


def install_global_skills(skill_exports: list[dict[str, Any]]) -> int:
    GLOBAL_CODEX_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    installed = 0
    for skill in skill_exports:
        if skill.get("status") != "exported":
            continue
        name = str(skill["name"])
        source = CODEX_SKILLS_EXPORT_DIR / name
        if not source.exists():
            continue
        target = GLOBAL_CODEX_SKILLS_DIR / name
        remove_tree(target)
        shutil.copytree(source, target)
        installed += 1
    return installed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export TEST_AGENTS Claude assets for Codex.")
    parser.add_argument(
        "--write-local-secrets",
        action="store_true",
        help="Create .codex/secrets.local.env from local .mcp.json env values. The file is gitignored.",
    )
    parser.add_argument(
        "--install-global-skills",
        action="store_true",
        help="Install exported skills into the local Codex home so /skills can discover them after restart.",
    )
    parser.add_argument(
        "--write-codex-mcp-config",
        action="store_true",
        help="Create local project .codex/config.toml MCP config from Claude .mcp.json.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    CODEX_DIR.mkdir(exist_ok=True)
    agent_exports = export_agents()
    skill_exports = export_skills()
    write_codex_root_doc(agent_exports)
    write_codex_commands()
    write_secret_template()
    if args.write_local_secrets:
        write_local_secrets()
    mcp_names: list[str] = []
    if args.write_codex_mcp_config:
        mcp_names = write_codex_mcp_config()
    installed = install_global_skills(skill_exports) if args.install_global_skills else 0
    hook_stats = sync_codex_hooks()
    write_manifest(agent_exports, skill_exports)
    print(f"Exported {len(agent_exports)} agents to {rel(CODEX_AGENTS_DIR)}")
    print(f"Processed {len(skill_exports)} skills into {rel(CODEX_SKILLS_EXPORT_DIR)}")
    print(
        f"Synced {hook_stats['copied']} hook scripts and wired {hook_stats['wired']} "
        f"Codex hooks into {rel(CODEX_DIR / 'hooks.json')}"
    )
    print(f"Wrote {rel(CODEX_DIR / 'manifest.json')}")
    if args.write_local_secrets:
        print("Wrote local Codex secrets env file without printing secret values")
    if args.install_global_skills:
        print(f"Installed {installed} skills into {GLOBAL_CODEX_SKILLS_DIR}")
    if args.write_codex_mcp_config:
        print("Wrote local Codex MCP config for servers: " + ", ".join(mcp_names))


if __name__ == "__main__":
    main()
