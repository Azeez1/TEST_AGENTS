#!/usr/bin/env python3
"""
Generate LinkedIn-optimized carousel slides from flow diagrams.

LinkedIn carousels have 45.85% engagement rate - the HIGHEST of any content type!
This script creates multiple slides from your diagram, perfect for LinkedIn posts.

Usage:
    python generate_carousel.py <mermaid_file> [options]

Options:
    --slides, -n       Number of slides to generate (default: 5)
    --style, -s        Visual style: glassmorphism, neon, hand-drawn (default: glassmorphism)
    --output-dir, -o   Output directory for slides (default: carousel_slides/)
    --title, -t        Carousel title (default: Flow Diagram)
    --size             Slide size: linkedin (1080x1080), linkedin-wide (1200x628) (default: linkedin)

Examples:
    python generate_carousel.py architecture.mmd --slides 8 --style neon
    python generate_carousel.py process.mmd -n 10 --style glassmorphism -t "Our Process"
    python generate_carousel.py flow.mmd --style hand-drawn --size linkedin-wide
"""

import argparse
import sys
from pathlib import Path
import subprocess
import tempfile
import shutil


def parse_mermaid_for_carousel(mermaid_code: str, num_slides: int):
    """
    Parse Mermaid code and split it into slides.
    Each slide focuses on a portion of the diagram for progressive revelation.
    """
    lines = mermaid_code.strip().split('\n')

    # Find all node definitions and connections
    nodes = []
    connections = []
    diagram_type = lines[0].strip() if lines else "graph TD"

    for line in lines[1:]:
        line = line.strip()
        if not line or line.startswith('%%'):
            continue

        # Check if it's a connection (contains --> or --- etc)
        if '-->' in line or '---' in line or '--' in line or '-..' in line:
            connections.append(line)
        elif line and not line.startswith('style') and not line.startswith('class'):
            nodes.append(line)

    # Create progressive slides
    slides = []

    # Slide 1: Title slide with first few nodes
    initial_nodes = min(3, len(nodes))
    slide_1 = [diagram_type] + nodes[:initial_nodes]
    slides.append({
        'title': 'Introduction',
        'code': '\n'.join(slide_1),
        'description': 'Overview of the system'
    })

    # Progressive revelation: add more nodes and connections
    if num_slides > 1:
        items_per_slide = max(1, (len(nodes) + len(connections)) // (num_slides - 1))

        current_nodes = nodes[:initial_nodes]
        current_connections = []
        remaining_nodes = nodes[initial_nodes:]
        remaining_connections = connections.copy()

        for i in range(num_slides - 1):
            # Add more elements
            add_count = min(items_per_slide, len(remaining_nodes) + len(remaining_connections))

            # Prioritize connections that reference existing nodes
            new_connections = []
            # Ensure connection quota is at least 1 to avoid isolating nodes
            connection_quota = max(1, items_per_slide // 2)
            for conn in remaining_connections[:]:
                # Simple check if connection references existing nodes
                should_add = any(node.split('[')[0].strip() in conn for node in current_nodes if '[' in node)
                if should_add and len(new_connections) < connection_quota:
                    new_connections.append(conn)
                    remaining_connections.remove(conn)

            # Add remaining nodes
            nodes_to_add = min(items_per_slide - len(new_connections), len(remaining_nodes))
            new_nodes = remaining_nodes[:nodes_to_add]
            remaining_nodes = remaining_nodes[nodes_to_add:]

            current_nodes.extend(new_nodes)
            current_connections.extend(new_connections)

            slide_code = [diagram_type] + current_nodes + current_connections
            slides.append({
                'title': f'Step {i + 1}',
                'code': '\n'.join(slide_code),
                'description': f'Building the complete picture'
            })

    return slides


def create_title_slide(title: str, style: str, output_path: Path, size_preset: str):
    """Create an attractive title slide for the carousel."""

    width, height = get_size_dimensions(size_preset)

    # Style-specific colors and designs
    style_configs = {
        'glassmorphism': {
            'bg': 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
            'title_color': '#ffffff',
            'font': 'Inter'
        },
        'neon': {
            'bg': '#0a0a0a',
            'title_color': '#00ff41',
            'font': 'Orbitron'
        },
        'hand-drawn': {
            'bg': '#fafaf8',
            'title_color': '#1f1f1f',
            'font': 'Caveat'
        }
    }

    config = style_configs.get(style, style_configs['glassmorphism'])

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@700;900&family=Orbitron:wght@900&family=Caveat:wght@700&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
            width: {width}px;
            height: {height}px;
            background: {config['bg']};
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: '{config['font']}', sans-serif;
        }}
        .title {{
            font-size: 72px;
            font-weight: 900;
            color: {config['title_color']};
            text-align: center;
            padding: 60px;
            max-width: 900px;
            {'text-shadow: 0 0 20px ' + config['title_color'] + ', 0 0 40px ' + config['title_color'] + ';' if style == 'neon' else ''}
        }}
        .subtitle {{
            font-size: 32px;
            margin-top: 30px;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="title">
        {title}
        <div class="subtitle">Swipe to explore →</div>
    </div>
</body>
</html>"""

    # Save title slide HTML
    title_html = output_path.parent / "title_slide.html"
    title_html.write_text(html_content, encoding='utf-8')

    print(f"   Created title slide")


def get_size_dimensions(size_preset: str):
    """Get dimensions for different size presets."""
    sizes = {
        'linkedin': (1080, 1080),
        'linkedin-wide': (1200, 628),
        'instagram': (1080, 1080),
        'twitter': (1200, 675)
    }
    return sizes.get(size_preset, (1080, 1080))


def generate_slide_html(slide_data: dict, style: str, skill_dir: Path, slide_num: int, total_slides: int):
    """Generate HTML for a single carousel slide."""

    # Read the appropriate template
    from generate_diagram import read_template, generate_html

    template = read_template(skill_dir, style)

    # Add slide progress indicator to title
    title = f"{slide_data['title']} ({slide_num}/{total_slides})"

    html = generate_html(
        template,
        slide_data['code'],
        title=title,
        style=style
    )

    return html


def main():
    parser = argparse.ArgumentParser(
        description="Generate LinkedIn carousel slides from flow diagrams (45.85% engagement rate!)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_carousel.py architecture.mmd --slides 8 --style neon
  python generate_carousel.py process.mmd -n 10 --style glassmorphism
  python generate_carousel.py flow.mmd --style hand-drawn
        """
    )

    parser.add_argument(
        "mermaid_file",
        help="Path to Mermaid diagram file (.mmd or .txt)"
    )

    parser.add_argument(
        "-n", "--slides",
        type=int,
        default=5,
        help="Number of slides to generate (default: 5, recommended: 6-10 for LinkedIn)"
    )

    parser.add_argument(
        "-s", "--style",
        default="glassmorphism",
        choices=["glassmorphism", "neon", "hand-drawn"],
        help="Visual style (default: glassmorphism)"
    )

    parser.add_argument(
        "-o", "--output-dir",
        default="carousel_slides",
        help="Output directory for slides (default: carousel_slides/)"
    )

    parser.add_argument(
        "-t", "--title",
        default="Flow Diagram",
        help="Carousel title (default: Flow Diagram)"
    )

    parser.add_argument(
        "--size",
        default="linkedin",
        choices=["linkedin", "linkedin-wide", "instagram", "twitter"],
        help="Slide size preset (default: linkedin - 1080x1080)"
    )

    args = parser.parse_args()

    print(f"\n🎨 LINKEDIN CAROUSEL GENERATOR")
    print(f"   Style: {args.style}")
    print(f"   Slides: {args.slides}")
    print(f"   Size: {args.size}")
    print()

    # Find skill directory
    skill_dir = Path(__file__).parent.parent

    # Read mermaid code
    mermaid_path = Path(args.mermaid_file)
    if not mermaid_path.exists():
        print(f"Error: File not found: {args.mermaid_file}", file=sys.stderr)
        sys.exit(1)

    mermaid_code = mermaid_path.read_text(encoding='utf-8').strip()

    # Remove code block markers if present
    if mermaid_code.startswith("```mermaid") or mermaid_code.startswith("```"):
        lines = mermaid_code.split("\n")
        mermaid_code = "\n".join(lines[1:-1]) if len(lines) > 2 else mermaid_code

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create title slide
    print("📄 Generating slides...")
    create_title_slide(args.title, args.style, output_dir / "slide_0.html", args.size)

    # Parse and create slides
    slides = parse_mermaid_for_carousel(mermaid_code, args.slides)

    # Generate HTML for each slide
    for i, slide_data in enumerate(slides, 1):
        slide_html = generate_slide_html(slide_data, args.style, skill_dir, i, len(slides))

        # Save slide HTML
        slide_path = output_dir / f"slide_{i}.html"
        slide_path.write_text(slide_html, encoding='utf-8')

        print(f"   ✓ Slide {i}: {slide_data['title']}")

    print(f"\n✨ SUCCESS! Generated {len(slides) + 1} carousel slides")
    print(f"   Location: {output_dir.absolute()}")
    print(f"\n📱 Next steps:")
    print(f"   1. Open each slide_*.html in your browser")
    print(f"   2. Use browser tools or screenshot tool to capture as PNG")
    print(f"   3. Upload to LinkedIn as a carousel post")
    print(f"\n💡 LinkedIn Pro Tips:")
    print(f"   • Use 6-10 slides for best engagement")
    print(f"   • Keep text minimal (under 50 words per slide)")
    print(f"   • End with a call-to-action slide")
    print(f"   • Post during business hours for B2B content")
    print(f"\n🚀 Carousels have 45.85% engagement rate - the HIGHEST on LinkedIn!")
    print()


if __name__ == "__main__":
    main()
