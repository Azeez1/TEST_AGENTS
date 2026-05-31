"""verify_system.py - audit the TEST_AGENTS infrastructure.

Runs a battery of property checks against the system and reports PASS/FAIL for each.
Designed to be run weekly (or whenever something feels broken).
Standalone - no third-party dependencies.

Usage:
    python tools/verify_system.py            # show only failures + summary
    python tools/verify_system.py --verbose  # show every check
    python tools/verify_system.py --json     # machine-readable output

Exit codes:
    0 - all checks passed
    1 - at least one check failed
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# ANSI codes (modern Windows terminals support these; fallback is plain text)
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
DIM = '\033[2m'
RESET = '\033[0m'

results = []  # list of dict: {name, category, status (bool), reason}


def record(name, category, status, reason=""):
    results.append({
        "name": name,
        "category": category,
        "status": "PASS" if status else "FAIL",
        "reason": reason,
    })


# ---------------------------------------------------------------------------
# CHECK FUNCTIONS
# ---------------------------------------------------------------------------

def check_hooks_exist():
    """All three core hook scripts exist."""
    expected = [
        '.claude/hooks/pe_validation_gate.ps1',
        '.claude/hooks/output_routing_gate.ps1',
        '.claude/hooks/log_agent_run.ps1',
    ]
    for path in expected:
        full = REPO_ROOT / path
        record(f"Hook file present: {path}", "hooks",
               full.exists(), "" if full.exists() else f"missing at {full}")


def check_hook_encoding():
    """ADR-0002: hooks must be ASCII-only or UTF-8 with BOM."""
    hooks_dir = REPO_ROOT / '.claude' / 'hooks'
    if not hooks_dir.exists():
        record("Hook encoding check (ADR-0002)", "hooks", False, "no .claude/hooks/ dir")
        return
    for ps1 in sorted(hooks_dir.glob('*.ps1')):
        try:
            with open(ps1, 'rb') as f:
                head = f.read(3)
            has_bom = head == b'\xef\xbb\xbf'

            with open(ps1, 'r', encoding='utf-8-sig', errors='replace') as f:
                content = f.read()
            ascii_only = all(ord(c) < 128 for c in content)
            passed = ascii_only or has_bom
            reason = ""
            if not passed:
                offenders = [(i, c, ord(c)) for i, c in enumerate(content) if ord(c) >= 128][:3]
                reason = f"non-ASCII without BOM. Sample: {offenders}"
            record(f"Encoding OK (ADR-0002): {ps1.name}", "hooks", passed, reason)
        except Exception as e:
            record(f"Encoding check failed: {ps1.name}", "hooks", False, str(e))


def check_hook_paths_absolute():
    """ADR-0001: hook commands in settings.local.json use absolute paths."""
    settings = REPO_ROOT / '.claude' / 'settings.local.json'
    if not settings.exists():
        record("settings.local.json present", "hooks", False, "not found")
        return
    try:
        with open(settings, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
    except Exception as e:
        record("settings.local.json parseable", "hooks", False, str(e))
        return

    hooks = cfg.get('hooks', {})
    if not hooks:
        record("settings.local.json has hooks key", "hooks", False, "no hooks key")
        return

    for event_name, entries in hooks.items():
        for entry in entries:
            for h in entry.get('hooks', []):
                cmd = h.get('command', '')
                if '.claude/hooks/' not in cmd and '.claude\\hooks\\' not in cmd:
                    continue  # not one of our hook commands
                # Look for relative path pattern (no drive letter + colon)
                is_relative = ('.claude/hooks/' in cmd
                               and not re.search(r'[A-Z]:[\\/]', cmd))
                tail = cmd.split('-File')[-1].strip().strip('"').strip()[:60]
                if is_relative:
                    record(f"Hook path absolute ({event_name}): {tail}",
                           "hooks", False, "uses relative path - see ADR-0001")
                else:
                    record(f"Hook path absolute ({event_name}): {tail}",
                           "hooks", True)


def check_reviewer_subagents_readonly():
    """Lesson 6: reviewer subagents have Write/Edit excluded from tools."""
    reviewers = [
        '.claude/agents/pe-diagnosis-visual-reviewer.md',
        '.claude/agents/linkedin-brand-reviewer.md',
    ]
    forbidden = {'Write', 'Edit', 'MultiEdit', 'NotebookEdit'}
    for r in reviewers:
        full = REPO_ROOT / r
        if not full.exists():
            record(f"Reviewer present: {Path(r).name}", "agents", False, "missing")
            continue
        with open(full, 'r', encoding='utf-8') as f:
            content = f.read()
        # Find tools: block (YAML frontmatter)
        m = re.search(r'^tools:\s*\n((?:\s+-\s+\S+.*\n?)+)', content, re.MULTILINE)
        if not m:
            record(f"Reviewer has tools list: {Path(r).name}", "agents",
                   False, "no tools: block in frontmatter")
            continue
        tools_text = m.group(1)
        violations = [t for t in forbidden
                      if re.search(rf'^\s+-\s+{t}\s*$', tools_text, re.MULTILINE)]
        passed = not violations
        reason = f"forbidden tools present: {violations}" if violations else ""
        record(f"Reviewer is Read-only (L6): {Path(r).name}", "agents", passed, reason)


def check_logs_dir():
    """LOGS/ directory exists with .gitignore."""
    logs = REPO_ROOT / 'LOGS'
    record("LOGS/ directory exists", "observability", logs.exists(),
           "" if logs.exists() else "missing")
    if logs.exists():
        gi = logs / '.gitignore'
        record("LOGS/.gitignore present", "observability", gi.exists(),
               "" if gi.exists() else "no .gitignore - JSONL might pollute git")


def check_memory_health():
    """MEMORY.md size and presence of MEMORY-archive.md."""
    user_mem = Path(os.path.expanduser('~')) / '.claude' / 'projects'
    candidates = list(user_mem.glob('C--*TEST-AGENTS*/memory/MEMORY.md'))
    if not candidates:
        record("MEMORY.md found in user memory dir", "memory", False,
               f"no MEMORY.md under {user_mem}")
        return
    mem = candidates[0]
    size_kb = mem.stat().st_size / 1024
    target = 20.0
    record(f"MEMORY.md size <= {target} KB", "memory", size_kb < target,
           f"{size_kb:.1f} KB" if size_kb < target else f"{size_kb:.1f} KB (over target)")
    archive = mem.parent / 'MEMORY-archive.md'
    record("MEMORY-archive.md present (cold storage)", "memory",
           archive.exists(),
           "" if archive.exists() else "no archive file")


def check_governance_docs():
    """Governance documents exist and are findable."""
    docs = [
        'MEMORY_ROUTING.md',
        '.claude/OPERATOR_CHEATSHEET.md',
        'docs/adr/README.md',
        'docs/adr/ADR-0001-hooks-use-absolute-paths.md',
        'docs/adr/ADR-0002-hook-scripts-ascii-or-utf8-bom.md',
    ]
    for d in docs:
        full = REPO_ROOT / d
        record(f"Doc present: {d}", "governance",
               full.exists(), "" if full.exists() else "missing")


def check_skills_installed():
    """The two meta-skills shipped 2026-05-12."""
    skills = [
        ('.claude/skills/skill-builder/SKILL.md', 'skill-builder'),
        ('.claude/skills/capture-as-skill/SKILL.md', 'capture-as-skill'),
    ]
    for path, name in skills:
        full = REPO_ROOT / path
        record(f"Skill present: {name}", "skills", full.exists(),
               "" if full.exists() else f"missing at {path}")


def check_piter_script():
    """PITER pipeline for PE diagnosis."""
    piter = REPO_ROOT / 'tools' / 'piter' / 'pe-diagnosis.ps1'
    record("PITER pipeline present: tools/piter/pe-diagnosis.ps1", "piter",
           piter.exists(), "" if piter.exists() else "missing")


def check_orchestrator_consistency():
    """L12: agents whose prompts use Task(X) syntax 2+ times must have a clean
    `- Task` entry in their tools list. Otherwise the prompt narrates
    delegation the runtime cannot actually perform (the 'future-tense
    delegation' false-orchestrator pattern).
    """
    agent_dirs = [
        REPO_ROOT / '.claude' / 'agents',
        REPO_ROOT / 'MARKETING_TEAM' / '.claude' / 'agents',
        REPO_ROOT / 'ENGINEERING_TEAM' / '.claude' / 'agents',
        REPO_ROOT / 'FINANCIAL_TEAM' / '.claude' / 'agents',
        REPO_ROOT / 'SALES_TEAM' / '.claude' / 'agents',
        REPO_ROOT / 'QA_TEAM' / '.claude' / 'agents',
        REPO_ROOT / 'PROPOSAL_TEAM' / '.claude' / 'agents',
    ]
    flagged = 0
    for d in agent_dirs:
        if not d.exists():
            continue
        for agent_file in sorted(d.glob('*.md')):
            try:
                with open(agent_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue

            # Split frontmatter and body
            fm_match = re.search(
                r'^---\s*\n(.*?)\n---\s*\n(.*)$',
                content, re.DOTALL | re.MULTILINE,
            )
            if not fm_match:
                continue
            frontmatter, body = fm_match.group(1), fm_match.group(2)

            # Does body use Task(name) syntax 2+ times? (orchestration claim)
            task_calls = re.findall(r'Task\s*\(\s*[\w\-]+', body)
            if len(task_calls) < 2:
                continue  # Not a clear orchestrator-claim

            # Does tools: block have a clean `- Task` entry?
            tools_match = re.search(
                r'^tools:\s*\n((?:\s+-\s+.*\n?)+)',
                frontmatter, re.MULTILINE,
            )
            if not tools_match:
                # No tools block; can't verify
                continue
            tools_text = tools_match.group(1)
            has_clean_task = bool(
                re.search(r'^\s+-\s+Task\s*$', tools_text, re.MULTILINE)
            )

            rel_path = agent_file.relative_to(REPO_ROOT).as_posix()
            label = f"Orchestrator-Task consistency: {rel_path}"
            if has_clean_task:
                record(label, "orchestration", True)
            else:
                flagged += 1
                record(label, "orchestration", False,
                       f"prompt uses Task() {len(task_calls)}x but tools list "
                       f"lacks clean '- Task' entry (L12 false-orchestrator)")

    if flagged == 0:
        # Optional: confirm nothing was found if nothing was flagged
        # (only show in verbose mode — see main output logic)
        pass


CHECKS = [
    check_hooks_exist,
    check_hook_encoding,
    check_hook_paths_absolute,
    check_reviewer_subagents_readonly,
    check_logs_dir,
    check_memory_health,
    check_governance_docs,
    check_skills_installed,
    check_piter_script,
    check_orchestrator_consistency,
]


# ---------------------------------------------------------------------------
# OUTPUT
# ---------------------------------------------------------------------------

def color(text, c):
    return f"{c}{text}{RESET}"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show every check, not just failures")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON instead of human-readable")
    args = parser.parse_args()

    for fn in CHECKS:
        try:
            fn()
        except Exception as e:
            record(f"Check failed with exception: {fn.__name__}",
                   "internal", False, str(e))

    if args.json:
        print(json.dumps(results, indent=2))
        passed = sum(1 for r in results if r['status'] == 'PASS')
        sys.exit(0 if passed == len(results) else 1)

    # Human-readable output
    by_category = {}
    for r in results:
        by_category.setdefault(r['category'], []).append(r)

    print()
    print(color("TEST_AGENTS System Verification", DIM))
    print(color("=" * 60, DIM))

    for cat, items in by_category.items():
        cat_passed = sum(1 for r in items if r['status'] == 'PASS')
        cat_total = len(items)
        cat_color = GREEN if cat_passed == cat_total else (YELLOW if cat_passed > 0 else RED)
        print(f"\n{color(cat.upper(), cat_color)}  ({cat_passed}/{cat_total})")
        for r in items:
            if r['status'] == 'PASS':
                if args.verbose:
                    print(f"  {color('[PASS]', GREEN)}  {r['name']}")
            else:
                line = f"  {color('[FAIL]', RED)}  {r['name']}"
                if r['reason']:
                    line += color(f"  - {r['reason']}", DIM)
                print(line)

    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')

    print()
    print(color("=" * 60, DIM))
    if failed == 0:
        print(color(f"All {passed} checks passed.", GREEN))
    else:
        print(f"{color(str(failed) + ' failed', RED)}, {color(str(passed) + ' passed', GREEN)} (out of {len(results)})")
    print(color("=" * 60, DIM))
    print()

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
