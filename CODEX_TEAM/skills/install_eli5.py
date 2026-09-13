"""Install the portable ELI5 package without network calls or dependencies."""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]


def install(home: Path, runtime: str) -> list[Path]:
    """Preflight destinations, then copy requested complete skill folders."""
    pairs = {
        "claude": (ROOT / ".claude/skills/eli5", home / ".claude/skills/eli5"),
        "codex": (ROOT / "CODEX_TEAM/skills/eli5", home / ".codex/skills/eli5"),
    }
    selected = list(pairs.values()) if runtime == "both" else [pairs[runtime]]
    for source, target in selected:
        if not (source / "SKILL.md").is_file():
            raise FileNotFoundError(f"Incomplete package: {source}")
        if target.exists() or target.is_symlink():
            raise FileExistsError(f"Existing installation preserved: {target}. Back it up before replacing it.")
    installed = []
    for source, target in selected:
        shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
        installed.append(target)
    return installed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", choices=["claude", "codex", "both"], default="both")
    parser.add_argument("--home", type=Path, default=Path.home(), help="User home directory; override for a test installation.")
    args = parser.parse_args()
    try:
        for path in install(args.home.resolve(), args.runtime):
            print(f"Installed: {path}")
    except OSError as exc:
        parser.exit(1, f"Installation stopped: {exc}\n")


if __name__ == "__main__":
    main()
