#!/usr/bin/env python3
"""
Generate EYE-POPPING, attention-grabbing flow diagrams from Mermaid code.

This enhanced script creates stunning, LinkedIn-ready diagrams with multiple visual styles:
- Glassmorphism (modern, premium look)
- Neon/Cyberpunk (bold, attention-grabbing)
- Hand-drawn/Sketch (friendly, approachable)
- Classic (original professional style)

Usage:
    python generate_diagram.py <mermaid_file> [options]

Options:
    --output, -o      Output file path (default: diagram.html)
    --title, -t       Diagram title (default: Flow Diagram)
    --style, -s       Visual style: glassmorphism, neon, hand-drawn, classic (default: glassmorphism)
    --theme           Mermaid theme (for classic style only)
    --background, -b  Background color (for classic style only)

Examples:
    python generate_diagram.py architecture.mmd --style glassmorphism
    python generate_diagram.py flow.mmd -t "User Flow" --style neon
    python generate_diagram.py process.mmd --style hand-drawn -o process.html
    python generate_diagram.py system.mmd --style classic --theme dark
"""

import argparse
import sys
from pathlib import Path


def read_template(skill_dir: Path, style: str = "glassmorphism") -> str:
    """Read the HTML template from assets directory based on style."""

    # Map style names to template files
    style_templates = {
        "glassmorphism": "glassmorphism-template.html",
        "neon": "neon-template.html",
        "hand-drawn": "hand-drawn-template.html",
        "classic": "interactive-diagram-template.html"
    }

    template_file = style_templates.get(style, "glassmorphism-template.html")
    template_path = skill_dir / "assets" / template_file

    if not template_path.exists():
        print(f"Error: Template not found at {template_path}", file=sys.stderr)
        print(f"Available styles: {', '.join(style_templates.keys())}", file=sys.stderr)
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
    background: str = "#f5f5f5",
    style: str = "glassmorphism"
) -> str:
    """Generate HTML by replacing placeholders in template."""

    # For classic style, validate theme
    if style == "classic":
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


def save_html(html: str, output_file: str, style: str) -> None:
    """Save generated HTML to file."""
    output_path = Path(output_file)

    # Create parent directories if they don't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(html, encoding='utf-8')

    style_emojis = {
        "glassmorphism": "✨",
        "neon": "⚡",
        "hand-drawn": "✏️",
        "classic": "📊"
    }
    emoji = style_emojis.get(style, "🎨")

    try:
        print(f"\n{emoji} STUNNING DIAGRAM GENERATED!")
        print(f"   Style: {style.upper()}")
        print(f"   File: {output_path.absolute()}")
        print(f"\n💡 Open in browser to:")
        print(f"   • View your eye-catching diagram")
        print(f"   • Pan/zoom interactively")
        print(f"   • Export to high-quality PNG/SVG")
        print(f"\n🚀 Ready for LinkedIn, Twitter, or any social media!")
        print()
    except UnicodeEncodeError:
        # Fallback for Windows console encoding issues
        print(f"\nSTUNNING DIAGRAM GENERATED!")
        print(f"   Style: {style.upper()}")
        print(f"   File: {output_path.absolute()}")
        print(f"\nOpen in browser to:")
        print(f"   - View your eye-catching diagram")
        print(f"   - Pan/zoom interactively")
        print(f"   - Export to high-quality PNG/SVG")
        print(f"\nReady for LinkedIn, Twitter, or any social media!")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Generate EYE-POPPING, LinkedIn-ready flow diagrams from Mermaid code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_diagram.py architecture.mmd --style glassmorphism
  python generate_diagram.py flow.mmd -t "User Flow" --style neon
  python generate_diagram.py process.mmd --style hand-drawn -o process.html
  python generate_diagram.py system.mmd --style classic --theme dark
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
        "-s", "--style",
        default="glassmorphism",
        choices=["glassmorphism", "neon", "hand-drawn", "classic"],
        help="Visual style (default: glassmorphism)"
    )

    parser.add_argument(
        "--theme",
        default="default",
        choices=["default", "forest", "dark", "neutral", "base"],
        help="Mermaid theme (for classic style only, default: default)"
    )

    parser.add_argument(
        "-b", "--background",
        default="#f5f5f5",
        help="Background color (for classic style only, default: #f5f5f5)"
    )

    args = parser.parse_args()

    # Find skill directory (script is in skills/flow-diagram/scripts/)
    skill_dir = Path(__file__).parent.parent

    # Read template and mermaid code
    template = read_template(skill_dir, args.style)
    mermaid_code = read_mermaid_code(args.mermaid_file)

    # Generate HTML
    html = generate_html(
        template,
        mermaid_code,
        title=args.title,
        theme=args.theme,
        background=args.background,
        style=args.style
    )

    # Save to file
    save_html(html, args.output, args.style)


if __name__ == "__main__":
    main()
