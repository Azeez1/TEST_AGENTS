"""Package only the portable ELI5 sources, installer, and documentation."""
from __future__ import annotations
import argparse
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
ALLOWED = {".md", ".py", ".yaml", ".css", ".js", ".html", ".svg"}


def package(output: Path) -> int:
    files = []
    for relative in (".claude/skills/eli5", "CODEX_TEAM/skills/eli5"):
        folder = ROOT / relative
        if not (folder / "SKILL.md").is_file():
            raise FileNotFoundError(f"Incomplete package: {relative}")
        files.extend(p for p in folder.rglob("*") if p.is_file()
                     and p.suffix in ALLOWED and "__pycache__" not in p.parts)
    files.extend(ROOT / name for name in (
        "CODEX_TEAM/skills/install_eli5.py", "CODEX_TEAM/skills/package_eli5.py",
        "CODEX_TEAM/skills/ELI5_INSTALL.md",
        "CODEX_TEAM/docs/eli5.md", "CODEX_TEAM/examples/eli5-builder-walkthrough.md",
        "CODEX_TEAM/examples/builder-walkthrough.source.html"))
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, path.relative_to(ROOT).as_posix())
    return len(files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(f"Packaged {package(args.output)} files into {args.output}")
