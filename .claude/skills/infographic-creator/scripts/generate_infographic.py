#!/usr/bin/env python3
"""
Infographic Generator - Main Script
Creates stunning static, animated, and interactive infographics

Usage:
    python generate_infographic.py --data metrics.csv --type statistical --output infographic.html
    python generate_infographic.py --data metrics.json --style glassmorphism --brand "Dux Machina"
    python generate_infographic.py --interactive --generate-content --export linkedin-post
"""

import argparse
import json
import csv
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

# Template configurations
TEMPLATE_CONFIGS = {
    'statistical': {
        'template': 'statistical-template.html',
        'description': 'Numbers, metrics, charts, KPIs',
        'best_for': ['metrics', 'kpi', 'dashboard', 'results', 'performance']
    },
    'timeline': {
        'template': 'timeline-template.html',
        'description': 'Chronological events, milestones',
        'best_for': ['history', 'roadmap', 'timeline', 'milestones', 'events']
    },
    'comparison': {
        'template': 'comparison-template.html',
        'description': 'Side-by-side, versus, before/after',
        'best_for': ['vs', 'versus', 'comparison', 'compare', 'difference']
    },
    'process': {
        'template': 'process-template.html',
        'description': 'Step-by-step, workflow, how-to',
        'best_for': ['steps', 'process', 'workflow', 'how-to', 'guide']
    },
    'hierarchical': {
        'template': 'hierarchical-template.html',
        'description': 'Pyramids, org charts, nested data',
        'best_for': ['hierarchy', 'pyramid', 'org', 'structure', 'levels']
    },
    'geographic': {
        'template': 'geographic-template.html',
        'description': 'Maps, locations, regional data',
        'best_for': ['map', 'geographic', 'location', 'region', 'country']
    },
    'list': {
        'template': 'list-template.html',
        'description': 'Tips, features, top 10, checklist',
        'best_for': ['list', 'tips', 'top', 'features', 'ways']
    }
}

# Visual styles (from flow-diagram)
VISUAL_STYLES = {
    'glassmorphism': {
        'primary_color': '#6366f1',
        'secondary_color': '#8b5cf6',
        'accent_color': '#ec4899',
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'card_background': 'rgba(255, 255, 255, 0.1)',
        'card_shadow': '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
        'border_radius': 16,
        'description': 'Modern, premium frosted glass effects'
    },
    'neon': {
        'primary_color': '#00ffff',
        'secondary_color': '#ff00ff',
        'accent_color': '#ffff00',
        'background': '#0a0e27',
        'card_background': 'rgba(10, 14, 39, 0.8)',
        'card_shadow': '0 0 20px rgba(0, 255, 255, 0.5)',
        'border_radius': 8,
        'description': 'Bold, cyberpunk, attention-grabbing'
    },
    'hand-drawn': {
        'primary_color': '#2d3748',
        'secondary_color': '#4a5568',
        'accent_color': '#ed8936',
        'background': '#f7fafc',
        'card_background': '#ffffff',
        'card_shadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'border_radius': 4,
        'description': 'Friendly, sketch-style, approachable'
    },
    'vibrant': {
        'primary_color': '#f56565',
        'secondary_color': '#ed64a6',
        'accent_color': '#9f7aea',
        'background': 'linear-gradient(135deg, #ff6b6b, #ee5a6f, #c06c84)',
        'card_background': '#ffffff',
        'card_shadow': '0 10px 30px rgba(0, 0, 0, 0.15)',
        'border_radius': 12,
        'description': 'Bold gradients, maximalist, eye-catching'
    },
    'corporate': {
        'primary_color': '#2c5282',
        'secondary_color': '#4a5568',
        'accent_color': '#3182ce',
        'background': '#f7fafc',
        'card_background': '#ffffff',
        'card_shadow': '0 2px 8px rgba(0, 0, 0, 0.08)',
        'border_radius': 8,
        'description': 'Clean, professional, business-appropriate'
    },
    'animated': {
        'primary_color': '#667eea',
        'secondary_color': '#764ba2',
        'accent_color': '#f093fb',
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'card_background': '#ffffff',
        'card_shadow': '0 8px 20px rgba(0, 0, 0, 0.12)',
        'border_radius': 12,
        'description': 'Dynamic particles and flowing elements'
    }
}

# Social media presets
SOCIAL_PRESETS = {
    'linkedin-post': {'width': 1200, 'height': 627, 'format': 'png'},
    'linkedin-carousel': {'width': 1080, 'height': 1080, 'format': 'png'},
    'instagram-post': {'width': 1080, 'height': 1080, 'format': 'png'},
    'instagram-story': {'width': 1080, 'height': 1920, 'format': 'png'},
    'twitter-post': {'width': 1200, 'height': 675, 'format': 'png'},
    'facebook-post': {'width': 1200, 'height': 630, 'format': 'png'},
    'pinterest-pin': {'width': 1000, 'height': 1500, 'format': 'png'}
}

# Default brand kits
BRAND_KITS = {
    'Dux Machina': {
        'colors': {
            'primary': '#B8860B',  # Precision Gold
            'secondary': '#0A0E14',  # Void Black
            'accent': '#FFFFFF',
            'background': '#F5F5F5',
            'text': '#0A0E14'
        },
        'fonts': {
            'headline': 'Inter',
            'body': 'Inter'
        },
        'logo': None,
        'watermark': '© 2025 Dux Machina'
    }
}


class InfographicGenerator:
    """Main infographic generation class"""

    def __init__(self, args):
        self.args = args
        self.script_dir = Path(__file__).parent
        self.skill_dir = self.script_dir.parent
        self.templates_dir = self.skill_dir / 'templates'
        self.data = None
        self.infographic_type = args.type or self.detect_type()
        self.style = self.load_style()
        self.brand_kit = self.load_brand_kit()

    def detect_type(self) -> str:
        """Auto-detect infographic type from data or title"""
        # Read data to analyze
        if self.args.data:
            data_content = self.read_data_file()
            if isinstance(data_content, str):
                text = data_content.lower()
            else:
                text = json.dumps(data_content).lower()
        else:
            text = (self.args.title or '').lower()

        # Score each type based on keywords
        scores = {}
        for itype, config in TEMPLATE_CONFIGS.items():
            score = sum(1 for keyword in config['best_for'] if keyword in text)
            scores[itype] = score

        # Return highest scoring type, default to statistical
        best_type = max(scores.items(), key=lambda x: x[1])
        return best_type[0] if best_type[1] > 0 else 'statistical'

    def read_data_file(self) -> Any:
        """Read data from CSV, JSON, or other formats"""
        if not self.args.data:
            return None

        data_path = Path(self.args.data)

        if not data_path.exists():
            print(f"Error: Data file not found: {self.args.data}")
            sys.exit(1)

        # CSV format
        if data_path.suffix.lower() == '.csv':
            with open(data_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)

        # JSON format
        elif data_path.suffix.lower() == '.json':
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        # Plain text (treat as description)
        else:
            with open(data_path, 'r', encoding='utf-8') as f:
                return f.read()

    def load_style(self) -> Dict[str, Any]:
        """Load visual style configuration"""
        if self.args.style and self.args.style in VISUAL_STYLES:
            return VISUAL_STYLES[self.args.style]

        # Default to glassmorphism
        return VISUAL_STYLES['glassmorphism']

    def load_brand_kit(self) -> Dict[str, Any]:
        """Load brand kit configuration"""
        if self.args.brand and self.args.brand in BRAND_KITS:
            return BRAND_KITS[self.args.brand]

        # Return empty brand kit
        return {
            'colors': {},
            'fonts': {'headline': 'Inter', 'body': 'Inter'},
            'logo': None,
            'watermark': None
        }

    def prepare_template_variables(self) -> Dict[str, Any]:
        """Prepare all template variables"""
        # Merge style colors with brand kit colors
        colors = {**self.style, **self.brand_kit.get('colors', {})}

        variables = {
            # Title and metadata
            'TITLE': self.args.title or 'Untitled Infographic',
            'SUBTITLE': self.args.subtitle or '',

            # Colors
            'PRIMARY_COLOR': colors.get('primary', self.style['primary_color']),
            'SECONDARY_COLOR': colors.get('secondary', self.style['secondary_color']),
            'ACCENT_COLOR': colors.get('accent', self.style['accent_color']),
            'BACKGROUND_COLOR': colors.get('background', self.style['background']),
            'TEXT_COLOR': colors.get('text', '#1a202c'),
            'CARD_BACKGROUND': self.style.get('card_background', '#ffffff'),
            'CARD_SHADOW': self.style.get('card_shadow', '0 4px 6px rgba(0, 0, 0, 0.1)'),

            # Typography
            'HEADLINE_FONT': self.brand_kit['fonts']['headline'],
            'BODY_FONT': self.brand_kit['fonts']['body'],
            'TITLE_SIZE': self.args.title_size or 48,
            'SUBTITLE_SIZE': self.args.subtitle_size or 20,

            # Layout
            'CANVAS_WIDTH': self.args.canvas_width or 1200,
            'PADDING': 40,
            'BORDER_RADIUS': self.style.get('border_radius', 12),

            # Logo
            'LOGO_PATH': self.brand_kit.get('logo'),
            'LOGO_POSITION': 'top-left',
            'LOGO_TOP': 20,
            'LOGO_OFFSET': 20,
            'LOGO_SIZE': 120,
            'LOGO_OPACITY': 1.0,

            # Watermark
            'WATERMARK_TEXT': self.brand_kit.get('watermark'),
            'WATERMARK_POSITION': 'bottom-right',
            'WATERMARK_BOTTOM': 20,
            'WATERMARK_OFFSET': 20,
            'WATERMARK_SIZE': 12,
            'WATERMARK_OPACITY': 0.5,

            # Animation
            'ENABLE_ANIMATIONS': not self.args.no_animation,
            'ANIMATION_DURATION': self.args.animation_duration or 2000,
            'ANIMATION_DELAY': 200,
            'ANIMATION_EASING': 'easeOutExpo',

            # Interactivity
            'ENABLE_INTERACTIVE': self.args.interactive,

            # Data (will be populated based on type)
            'DATA': self.data
        }

        return variables

    def generate_html(self) -> str:
        """Generate the complete HTML infographic"""
        # Get template
        template_name = TEMPLATE_CONFIGS[self.infographic_type]['template']
        template_path = self.templates_dir / template_name

        if not template_path.exists():
            print(f"Error: Template not found: {template_path}")
            sys.exit(1)

        # Read template
        with open(template_path, 'r', encoding='utf-8') as f:
            template_html = f.read()

        # Get template variables
        variables = self.prepare_template_variables()

        # Simple template variable replacement (for production, use Jinja2)
        html = template_html
        for key, value in variables.items():
            placeholder = '{{' + key + '}}'
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            elif value is None:
                value = ''
            html = html.replace(placeholder, str(value))

        return html

    def save_html(self, html: str):
        """Save HTML to file"""
        output_path = Path(self.args.output)

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write HTML
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✓ Infographic generated: {output_path}")
        print(f"  Type: {self.infographic_type}")
        print(f"  Style: {self.args.style or 'glassmorphism'}")
        if self.args.brand:
            print(f"  Brand: {self.args.brand}")

    def generate_content(self):
        """Generate AI-powered headlines and captions"""
        if not self.args.generate_content:
            return

        print("\n🤖 Generating content...")

        # This would integrate with Claude or another LLM
        # For now, provide placeholders
        content_dir = Path(self.args.output).parent / 'content'
        content_dir.mkdir(exist_ok=True)

        headlines_file = content_dir / 'headlines.txt'
        captions_file = content_dir / 'captions.txt'

        with open(headlines_file, 'w') as f:
            f.write(f"# Generated Headlines for: {self.args.title}\n\n")
            f.write("1. Record-Breaking Results: [Your Data Here]\n")
            f.write("2. The Numbers Are In: [Key Metric] Achievement\n")
            f.write("3. Success Story: [Your Achievement] in Numbers\n")
            f.write("4. Unprecedented Growth: [Percentage] Increase\n")
            f.write("5. By the Numbers: [Your Company] Performance\n")

        with open(captions_file, 'w') as f:
            f.write(f"# Generated Social Media Captions\n\n")
            f.write("## LinkedIn (1300-1900 chars):\n")
            f.write(f"We're excited to share our latest results! 🚀\n\n")
            f.write(f"[Your key metrics here]\n\n")
            f.write(f"Check out the full infographic below! 👇\n\n")
            f.write(f"#Data #BusinessResults #Growth\n\n")
            f.write("## Twitter/X (280 chars):\n")
            f.write(f"Our latest numbers are in! 📊\n\n[Key metric] ✅\n\n#Growth\n")

        print(f"✓ Content generated:")
        print(f"  - {headlines_file}")
        print(f"  - {captions_file}")

    def export(self):
        """Export to various formats"""
        # This would integrate with screenshot/export tools
        # For Phase 1, HTML is the primary output
        pass

    def run(self):
        """Main execution flow"""
        print(f"\n📊 Generating {self.infographic_type} infographic...")

        # Load data
        self.data = self.read_data_file()

        # Generate HTML
        html = self.generate_html()

        # Save HTML
        self.save_html(html)

        # Generate content if requested
        self.generate_content()

        # Export if requested
        if self.args.export:
            self.export()

        print("\n✓ Done!")


def main():
    parser = argparse.ArgumentParser(
        description='Generate stunning infographics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic statistical infographic
  python generate_infographic.py --data metrics.csv --title "Q4 Results"

  # With specific style and brand
  python generate_infographic.py --data metrics.csv --style neon --brand "Dux Machina"

  # LinkedIn-optimized with content generation
  python generate_infographic.py --data metrics.csv --export linkedin-post --generate-content

  # Interactive infographic
  python generate_infographic.py --data sales.json --interactive --output dashboard.html
        """
    )

    # Data input
    parser.add_argument('--data', help='Data file (CSV, JSON)')
    parser.add_argument('--type', choices=list(TEMPLATE_CONFIGS.keys()),
                       help='Infographic type (auto-detected if not specified)')

    # Content
    parser.add_argument('--title', help='Infographic title')
    parser.add_argument('--subtitle', help='Infographic subtitle')

    # Visual style
    parser.add_argument('--style', choices=list(VISUAL_STYLES.keys()),
                       help='Visual style (default: glassmorphism)')
    parser.add_argument('--brand', help='Brand kit to apply')
    parser.add_argument('--theme', help='Theme-factory theme to apply')

    # Customization
    parser.add_argument('--canvas-width', type=int, default=1200,
                       help='Canvas width in pixels (default: 1200)')
    parser.add_argument('--title-size', type=int, help='Title font size')
    parser.add_argument('--subtitle-size', type=int, help='Subtitle font size')

    # Animation
    parser.add_argument('--no-animation', action='store_true',
                       help='Disable animations')
    parser.add_argument('--animation-duration', type=int,
                       help='Animation duration in milliseconds')

    # Features
    parser.add_argument('--interactive', action='store_true',
                       help='Enable interactive features')
    parser.add_argument('--generate-content', action='store_true',
                       help='Generate AI-powered headlines and captions')

    # Output
    parser.add_argument('--output', default='infographic.html',
                       help='Output HTML file path (default: infographic.html)')
    parser.add_argument('--export', choices=list(SOCIAL_PRESETS.keys()) + ['png', 'pdf', 'gif', 'mp4'],
                       help='Export format or social media preset')

    args = parser.parse_args()

    # Validate
    if not args.data and not args.title:
        parser.error('Either --data or --title is required')

    # Generate
    generator = InfographicGenerator(args)
    generator.run()


if __name__ == '__main__':
    main()
