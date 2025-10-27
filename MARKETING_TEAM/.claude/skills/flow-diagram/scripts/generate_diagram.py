#!/usr/bin/env python3
"""
Generate interactive flow diagrams from Mermaid code.

This script creates beautiful, interactive HTML diagrams with pan/zoom capabilities
and export options (PNG, SVG).

Usage:
    python generate_diagram.py <mermaid_file> [options]

Options:
    --output, -o      Output file path (default: diagram.html)
    --title, -t       Diagram title (default: Flow Diagram)
    --theme           Theme: default, forest, dark, neutral, base (default: default)
    --background, -b  Background color (default: #f5f5f5)

Examples:
    python generate_diagram.py architecture.mmd -o system-arch.html
    python generate_diagram.py flow.mmd -t "User Flow" --theme dark
"""

import argparse
import sys
from pathlib import Path


def read_template(skill_dir: Path) -> str:
    """Read the HTML template from assets directory."""
    template_path = skill_dir / "assets" / "interactive-diagram-template.html"

    if not template_path.exists():
        print(f"Error: Template not found at {template_path}", file=sys.stderr)
        sys.exit(1)

    return template_path.read_text(encoding='utf-8')


def read_mermaid_code(mermaid_file: str) -> str:
    """Read Mermaid code from file."""
    mermaid_path = Path(mermaid_file)

    if not mermaid_path.exists():
        print(f"Error: Mermaid file not found: {mermaid_file}", file=sys.stderr)
        sys.exit(1)

    content = mermaid_path.read_text(encoding='utf-8').strip()

    # If content is wrapped in code blocks, extract the mermaid code
    if content.startswith("```mermaid") or content.startswith("```"):
        lines = content.split("\n")
        # Remove first and last lines (``` markers)
        content = "\n".join(lines[1:-1]) if len(lines) > 2 else content

    return content


def generate_html(
    template: str,
    mermaid_code: str,
    title: str = "Flow Diagram",
    theme: str = "default",
    background: str = "#f5f5f5"
) -> str:
    """Generate HTML by replacing placeholders in template."""

    # Validate theme
    valid_themes = ["default", "forest", "dark", "neutral", "base"]
    if theme not in valid_themes:
        print(f"Warning: Unknown theme '{theme}'. Using 'default'.", file=sys.stderr)
        theme = "default"

    # Replace placeholders
    html = template.replace("{{DIAGRAM_TITLE}}", title)
    html = html.replace("{{THEME}}", theme)
    html = html.replace("{{BACKGROUND_COLOR}}", background)
    html = html.replace("{{MERMAID_CODE}}", mermaid_code)

    return html


def save_html(html: str, output_file: str) -> None:
    """Save generated HTML to file."""
    output_path = Path(output_file)

    # Create parent directories if they don't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(html, encoding='utf-8')
    print(f"[OK] Interactive diagram generated: {output_path.absolute()}")
    print(f"[OK] Open in browser to view, pan/zoom, and export to PNG/SVG")


def main():
    parser = argparse.ArgumentParser(
        description="Generate interactive flow diagrams from Mermaid code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_diagram.py architecture.mmd
  python generate_diagram.py flow.mmd -o user-flow.html -t "User Journey"
  python generate_diagram.py system.mmd --theme dark --background "#1a1a1a"
        """
    )

    parser.add_argument(
        "mermaid_file",
        help="Path to Mermaid diagram file (.mmd or .txt)"
    )

    parser.add_argument(
        "-o", "--output",
        default="diagram.html",
        help="Output HTML file path (default: diagram.html)"
    )

    parser.add_argument(
        "-t", "--title",
        default="Flow Diagram",
        help="Diagram title (default: Flow Diagram)"
    )

    parser.add_argument(
        "--theme",
        default="default",
        choices=["default", "forest", "dark", "neutral", "base"],
        help="Mermaid theme (default: default)"
    )

    parser.add_argument(
        "-b", "--background",
        default="#f5f5f5",
        help="Background color (default: #f5f5f5)"
    )

    args = parser.parse_args()

    # Find skill directory (script is in skills/flow-diagram/scripts/)
    skill_dir = Path(__file__).parent.parent

    # Read template and mermaid code
    template = read_template(skill_dir)
    mermaid_code = read_mermaid_code(args.mermaid_file)

    # Generate HTML
    html = generate_html(
        template,
        mermaid_code,
        title=args.title,
        theme=args.theme,
        background=args.background
    )

    # Save to file
    save_html(html, args.output)


if __name__ == "__main__":
    main()
