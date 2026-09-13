"""Bundle trusted ELI5 lesson source and local assets into portable HTML."""
from __future__ import annotations

import argparse
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]


def build(source: Path, output: Path, *, force: bool = False) -> Path:
    """Embed the toolkit; refuse accidental overwrite and unresolved markers."""
    source, output = source.resolve(), output.resolve()
    if source == output:
        raise ValueError("Choose an output different from the source.")
    html = source.read_text(encoding="utf-8")
    assets = {
        "<!-- ELI5:STYLE -->": ("style", SKILL_ROOT / "assets/lesson.css"),
        "<!-- ELI5:SCRIPT -->": ("script", SKILL_ROOT / "assets/lesson.js"),
    }
    for marker, (tag, path) in assets.items():
        if html.count(marker) != 1:
            raise ValueError(f"Expected exactly one {marker}")
        html = html.replace(marker, f"<{tag}>\n{path.read_text(encoding='utf-8')}\n</{tag}>")
    if "<!-- ELI5:" in html:
        raise ValueError("Unresolved ELI5 build marker.")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w" if force else "x", encoding="utf-8", newline="\n") as handle:
        handle.write(html)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        print(build(args.source, args.output, force=args.force))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Build failed: {exc}\n")


if __name__ == "__main__":
    main()
