"""Generate the custom-tool inventory in TOOL_REGISTRY.md from the filesystem, and check it.

The inventory section between the GENERATED markers is script output (doc-hygiene:
"generate, don't hand-maintain"). The hand-written capability tables above it stay
hand-written, but every `name.py` they mention must exist on disk unless the line marks it
retired (strikethrough, "retired", "deprecated", "archived", or the 🚫 marker).

Usage:
    python tools/gen_tool_registry.py           # check; exit 1 on drift or phantom entries
    python tools/gen_tool_registry.py --write   # regenerate the inventory section
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import warnings
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REGISTRY = REPO / "TOOL_REGISTRY.md"
BEGIN = "<!-- BEGIN GENERATED: custom-tools (python tools/gen_tool_registry.py --write) -->"
END = "<!-- END GENERATED: custom-tools -->"
RETIRED_MARKERS = ("retired", "deprecated", "archived", "🚫")


def tool_dirs(root: Path = REPO) -> list[Path]:
    """Root tools/ plus each team's tools/. archive/ is excluded: retired code is not inventory."""
    return [root / "tools"] + sorted(p for p in root.glob("*/tools") if p.parent.name != "archive")


def discover_tools(root: Path = REPO) -> list[dict]:
    tools = []
    for folder in tool_dirs(root):
        for path in sorted(folder.glob("*.py")):
            if path.name == "__init__.py":
                continue
            tools.append({"name": path.stem, "path": path.relative_to(root).as_posix(),
                          "summary": first_doc_line(path)})
    return tools


def first_doc_line(path: Path) -> str:
    try:
        with warnings.catch_warnings():  # tool files with bad escapes shouldn't spam the report
            warnings.simplefilter("ignore", SyntaxWarning)
            doc = ast.get_docstring(ast.parse(path.read_text(encoding="utf-8-sig")))
    except (SyntaxError, UnicodeDecodeError, ValueError):
        return "(could not parse)"
    line = (doc or "").strip().splitlines()[0].strip() if doc and doc.strip() else ""
    return line.replace("|", "\\|") or "(no docstring)"


def render(tools: list[dict]) -> str:
    out = [BEGIN, "", "## 🧰 Custom Tool Inventory (generated)", "",
           f"{len(tools)} Python tools on disk. Do not edit this section by hand; re-run the generator.", ""]
    by_folder: dict[str, list[dict]] = {}
    for t in tools:
        by_folder.setdefault(t["path"].rsplit("/", 1)[0], []).append(t)
    for folder, items in by_folder.items():
        out += [f"### `{folder}/` ({len(items)})", "", "| Tool | Summary |", "|------|---------|"]
        out += [f"| `{t['name']}` | {t['summary']} |" for t in items]
        out.append("")
    out.append(END)
    return "\n".join(out)


def split(text: str) -> tuple[str, str | None, str]:
    if BEGIN in text and END in text:
        head, rest = text.split(BEGIN, 1)
        body, tail = rest.split(END, 1)
        return head, BEGIN + body + END, tail
    return text, None, ""


def phantoms(hand_written: str, names: set[str]) -> list[str]:
    found = []
    for line in hand_written.splitlines():
        lowered = line.lower()
        for name in re.findall(r"([A-Za-z0-9_]+)\.py\b", line):
            if name in names or f"~~{name}.py~~" in line or any(m in lowered for m in RETIRED_MARKERS):
                continue
            found.append(name)
    return sorted(set(found))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    tools = discover_tools()
    text = REGISTRY.read_text(encoding="utf-8")
    head, current, tail = split(text)
    expected = render(tools)
    if args.write:
        if current is None:  # first run: insert before the MCP inventory section
            anchor = "## 📊 Complete MCP Server Inventory"
            head = head.replace(anchor, expected + "\n\n---\n\n" + anchor, 1) if anchor in head else head + "\n" + expected + "\n"
            text = head
        else:
            text = head + expected + tail
        REGISTRY.write_text(text, encoding="utf-8")
        head, current, tail = split(text)
    problems = []
    if current is None:
        problems.append("Generated inventory section missing; run with --write")
    elif current.strip() != expected.strip():
        problems.append("Generated inventory is stale; run with --write")
    problems += [f"Phantom registry entry (no file on disk): {n}.py"
                 for n in phantoms(head + tail, {t["name"] for t in tools})]
    print(json.dumps({"ok": not problems, "tools_on_disk": len(tools), "problems": problems}, indent=2))
    raise SystemExit(0 if not problems else 1)


if __name__ == "__main__":
    main()
