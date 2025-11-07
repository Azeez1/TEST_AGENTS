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

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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
        'primary_color': '#1e293b',
        'secondary_color': '#475569',
        'accent_color': '#3b82f6',
        'background': '#f1f5f9',
        'card_background': '#ffffff',
        'card_shadow': '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
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
        'primary_color': '#1a202c',
        'secondary_color': '#4a5568',
        'accent_color': '#9f7aea',
        'background': '#f7fafc',
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

    def generate_metrics_html(self) -> str:
        """Generate HTML for metrics cards from data"""
        if not self.data or self.infographic_type != 'statistical':
            return ""

        # Handle dict data (get the list)
        data_list = self.data if isinstance(self.data, list) else []

        metrics_html = []
        for index, row in enumerate(data_list):
            # Extract data from row
            label = row.get('metric', 'Metric')
            value = row.get('value', '0')
            change = row.get('change', '')

            # Determine if change is positive or negative
            change_num = 0
            try:
                change_num = float(change.replace('%', '').replace('+', ''))
            except:
                pass

            change_class = 'positive' if change_num >= 0 else 'negative'
            change_arrow = '↑' if change_num >= 0 else '↓'

            # Generate card HTML
            card_html = f'''
            <div class="metric-card" data-metric-index="{index}">
                <div class="metric-value" data-target="{value}">{value}</div>
                <div class="metric-label">{label}</div>'''

            if change:
                card_html += f'''
                <div class="metric-change {change_class}">
                    {change_arrow} {change}%
                </div>'''

            card_html += '''
            </div>'''

            metrics_html.append(card_html)

        return '\n'.join(metrics_html)

    def generate_charts_html(self) -> str:
        """Generate HTML for charts section"""
        # For Phase 1, return empty - charts will be added in Phase 2
        return ""

    def generate_timeline_html(self) -> str:
        """Generate HTML for timeline events from data"""
        if not self.data or self.infographic_type != 'timeline':
            return ""

        # Handle dict data (get the list)
        data_list = self.data if isinstance(self.data, list) else []

        timeline_html = []
        for index, row in enumerate(data_list):
            # Extract data from row
            date = row.get('quarter', row.get('date', ''))
            title = row.get('milestone', row.get('title', row.get('event', '')))
            description = row.get('description', '')
            status = row.get('status', '')

            # Generate timeline item HTML
            item_html = f'''
            <div class="timeline-item" data-event-index="{index}">
                <!-- Node (circle on axis) -->
                <div class="timeline-node {status}"></div>

                <!-- Content card -->
                <div class="timeline-content">
                    <div class="timeline-date">{date}</div>
                    <h3 class="timeline-title">{title}</h3>'''

            if description:
                item_html += f'''
                    <p class="timeline-description">{description}</p>'''

            if status:
                item_html += f'''
                    <span class="timeline-status {status}">{status}</span>'''

            item_html += '''
                </div>
            </div>'''

            timeline_html.append(item_html)

        return '\n'.join(timeline_html)

    def generate_comparison_html(self) -> str:
        """Generate HTML for comparison columns from data"""
        if not self.data or self.infographic_type != 'comparison':
            return ""

        # Handle JSON data with 'comparisons' array
        if isinstance(self.data, dict) and 'comparisons' in self.data:
            comparisons = self.data['comparisons']
        else:
            comparisons = self.data if isinstance(self.data, list) else []

        if not comparisons:
            return ""

        # Generate two columns: "Us" (Dux Machina) and "Them" (Competitors)
        us_features = []
        them_features = []

        for comp in comparisons:
            feature_name = comp.get('feature', '')
            us_value = comp.get('us', '')
            competitor_value = comp.get('competitor', '')
            advantage = comp.get('advantage', '')

            us_features.append({
                'text': f"{feature_name}: {us_value}",
                'included': True,
                'highlight': advantage
            })

            them_features.append({
                'text': f"{feature_name}: {competitor_value}",
                'included': True,
                'highlight': False
            })

        # Generate HTML for both columns
        comparison_html = []

        # Column 1: Dux Machina (Us)
        us_html = '''
            <div class="comparison-column">
                <div class="column-header">
                    <div class="recommended-badge">Recommended</div>
                    <div class="column-name">Dux Machina</div>
                    <div class="column-tagline">37 AI Agents, Maximum Power</div>
                </div>
                <div class="features-list">'''

        for feature in us_features:
            us_html += f'''
                    <div class="feature-item">
                        <span class="feature-icon yes">✓</span>
                        <span class="feature-text">{feature['text']}</span>
                    </div>'''

        us_html += '''
                </div>
            </div>'''

        # Column 2: Competitors (Them)
        them_html = '''
            <div class="comparison-column">
                <div class="column-header">
                    <div class="column-name">Competitors</div>
                    <div class="column-tagline">Traditional Approach</div>
                </div>
                <div class="features-list">'''

        for feature in them_features:
            them_html += f'''
                    <div class="feature-item">
                        <span class="feature-icon no">✗</span>
                        <span class="feature-text disabled">{feature['text']}</span>
                    </div>'''

        them_html += '''
                </div>
            </div>'''

        # Add VS divider between columns
        vs_divider = '''
            <div class="vs-divider">VS</div>'''

        comparison_html = [us_html, vs_divider, them_html]

        return '\n'.join(comparison_html)

    def generate_process_html(self) -> str:
        """Generate HTML for process steps from data"""
        if not self.data or self.infographic_type != 'process':
            return ""

        data_list = self.data if isinstance(self.data, list) else []

        process_html = []
        for index, row in enumerate(data_list):
            step_num = row.get('step', index + 1)
            title = row.get('title', f'Step {step_num}')
            description = row.get('description', '')
            icon = row.get('icon', '')
            agent = row.get('agent', '')

            # Add agent info to description if present
            if agent and agent not in description:
                description = f"{description} (Agent: {agent})"

            step_html = f'''
            <div class="step" data-step-index="{index}">
                <div class="step-number">{step_num}</div>
                <div class="step-content">'''

            if icon:
                step_html += f'''
                    <div class="step-icon">{icon}</div>'''

            step_html += f'''
                    <h3 class="step-title">{title}</h3>
                    <p class="step-description">{description}</p>
                </div>
            </div>'''

            # Add arrow between steps (except after last step)
            if index < len(data_list) - 1:
                step_html += '''
            <div class="arrow"></div>'''

            process_html.append(step_html)

        return '\n'.join(process_html)

    def generate_list_html(self) -> str:
        """Generate HTML for list items from data"""
        if not self.data or self.infographic_type != 'list':
            return ""

        # Handle both direct list and nested structure
        if isinstance(self.data, dict) and 'items' in self.data:
            items_list = self.data['items']
        else:
            items_list = self.data if isinstance(self.data, list) else []

        list_html = []
        for index, item in enumerate(items_list):
            rank = item.get('rank', index + 1)
            title = item.get('title', f'Item {rank}')
            description = item.get('description', '')
            icon = item.get('icon', '')

            item_html = f'''
            <div class="list-item" data-item-index="{index}">
                <div class="item-rank">{rank}</div>
                <div class="item-content">'''

            if icon:
                item_html += f'''
                    <div class="item-icon">{icon}</div>'''

            item_html += f'''
                    <h3 class="item-title">{title}</h3>
                    <p class="item-description">{description}</p>
                </div>
            </div>'''

            list_html.append(item_html)

        return '\n'.join(list_html)

    def generate_hierarchical_html(self) -> str:
        """Generate HTML for hierarchical pyramid levels from data"""
        if not self.data or self.infographic_type != 'hierarchical':
            return ""

        # Handle both direct list and nested structure
        if isinstance(self.data, dict) and 'levels' in self.data:
            levels_list = self.data['levels']
        else:
            levels_list = self.data if isinstance(self.data, list) else []

        hierarchy_html = []
        for index, level in enumerate(levels_list):
            level_num = level.get('level', index + 1)
            title = level.get('title', f'Level {level_num}')
            description = level.get('description', '')
            count = level.get('count', '')
            color = level.get('color', '#6366f1')

            level_html = f'''
            <div class="pyramid-level level-{level_num}" data-level-index="{index}" style="background: {color};">
                <div class="level-content">
                    <h3 class="level-title">{title}</h3>'''

            if count:
                level_html += f'''
                    <div class="level-count">{count} agent{"s" if count != 1 else ""}</div>'''

            if description:
                level_html += f'''
                    <p class="level-description">{description}</p>'''

            level_html += '''
                </div>
            </div>'''

            hierarchy_html.append(level_html)

        return '\n'.join(hierarchy_html)

    def generate_geographic_html(self) -> str:
        """Generate HTML for geographic regions as stat cards matching template structure"""
        if not self.data or self.infographic_type != 'geographic':
            return ""

        # Handle both direct list and nested structure
        if isinstance(self.data, dict) and 'regions' in self.data:
            regions_list = self.data['regions']
        else:
            regions_list = self.data if isinstance(self.data, list) else []

        geographic_html = []
        for index, region in enumerate(regions_list):
            name = region.get('name', f'Region {index + 1}')
            metric = region.get('metric', '')
            value = region.get('value', 0)
            description = region.get('description', '')
            color = region.get('color', '#6366f1')
            icon = region.get('icon', '📍')

            # Create stat-card structure matching geographic-template.html
            # Force opacity: 1 to override template's opacity: 0 (since anime.js may not load properly)
            region_html = f'''
        <div class="stat-card" data-region-index="{index}" style="border-top: 4px solid {color}; opacity: 1 !important;">
            <div style="font-size: 32px; margin-bottom: 10px;">{icon}</div>
            <div class="stat-label" style="font-size: 18px; font-weight: bold; color: {color}; margin-bottom: 8px;">{name}</div>
            <div class="stat-value">{metric}</div>'''

            if value:
                region_html += f'''
            <div style="font-size: 14px; color: #64748b; margin-top: 8px;">{value:,} customers</div>'''

            if description:
                region_html += f'''
            <p style="font-size: 13px; color: #64748b; margin-top: 12px; line-height: 1.5;">{description}</p>'''

            region_html += '''
        </div>'''

            geographic_html.append(region_html)

        return '\n'.join(geographic_html)

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
            'NUM_ITEMS': 2,  # For comparison: 2 columns (us vs them)

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
            'DATA': self.data,

            # Metrics sizing (for statistical infographics)
            'METRIC_VALUE_SIZE': 48,
            'METRIC_LABEL_SIZE': 16,
            'METRIC_CHANGE_SIZE': 14,

            # Timeline sizing (for timeline infographics)
            'DATE_SIZE': 20,
            'EVENT_TITLE_SIZE': 24,
            'EVENT_DESC_SIZE': 16,

            # Canvas background (use style background)
            'CANVAS_BACKGROUND': colors.get('background', self.style['background']),

            # Charts section
            'CHARTS_SECTION_TITLE': 'Performance Overview',
            'CHARTS_DATA': json.dumps([]),  # Empty for Phase 1

            # Comparison column colors (high contrast for visibility)
            'COLOR_1_START': '#10b981',  # Emerald green (recommended column)
            'COLOR_1_END': '#059669',    # Darker emerald
            'COLOR_2_START': '#6b7280',  # Neutral gray (competitor column)
            'COLOR_2_END': '#4b5563',    # Darker gray
            'COLOR_3_START': colors.get('primary', self.style['primary_color']),
            'COLOR_3_END': colors.get('secondary', self.style['secondary_color']),

            # Geographic (prevent {{#if STATS}} block from being removed)
            'STATS': 'true' if self.infographic_type == 'geographic' else '',
            'MAP_DATA': '"https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"',  # TopoJSON world map
            'MARKERS': self._generate_markers() if self.infographic_type == 'geographic' else '[]'
        }

        return variables

    def _generate_markers(self) -> str:
        """Generate map markers from geographic region data"""
        if not self.data or self.infographic_type != 'geographic':
            return '[]'

        # Handle both direct list and nested structure
        if isinstance(self.data, dict) and 'regions' in self.data:
            regions_list = self.data['regions']
        else:
            regions_list = self.data if isinstance(self.data, list) else []

        # Approximate coordinates for common regions
        region_coords = {
            'north america': [-100, 40],
            'europe': [10, 50],
            'asia-pacific': [130, 30],
            'asia pacific': [130, 30],
            'south america': [-60, -10],
            'africa': [25, 0],
            'middle east': [45, 25],
            'africa & middle east': [30, 10]
        }

        markers = []
        for region in regions_list:
            name = region.get('name', '').lower()
            metric = region.get('metric', '')

            # Find matching coordinates
            coords = None
            for key, coord in region_coords.items():
                if key in name:
                    coords = coord
                    break

            if coords:
                markers.append({
                    'name': region.get('name', ''),
                    'coords': coords,
                    'value': metric,
                    'color': region.get('color', '#6366f1')
                })

        return json.dumps(markers)

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

        # Generate dynamic HTML sections based on infographic type
        metrics_html = self.generate_metrics_html()
        charts_html = self.generate_charts_html()
        timeline_html = self.generate_timeline_html()
        comparison_html = self.generate_comparison_html()
        process_html = self.generate_process_html()
        list_html = self.generate_list_html()
        hierarchical_html = self.generate_hierarchical_html()
        geographic_html = self.generate_geographic_html()

        # Replace Handlebars-style blocks with generated HTML
        import re

        # Replace {{#each METRICS}}...{{/each}} with actual metrics HTML
        metrics_pattern = r'\{\{#each METRICS\}\}.*?\{\{/each\}\}'
        html = re.sub(metrics_pattern, metrics_html, template_html, flags=re.DOTALL)

        # Replace {{#each TIMELINE_EVENTS}}...{{/each}} with actual timeline HTML
        timeline_pattern = r'\{\{#each TIMELINE_EVENTS\}\}.*?\{\{/each\}\}'
        html = re.sub(timeline_pattern, timeline_html, html, flags=re.DOTALL)

        # Replace {{#each COMPARISON_ITEMS}}...{{/each}} with actual comparison HTML
        comparison_pattern = r'\{\{#each COMPARISON_ITEMS\}\}.*?\{\{/each\}\}'
        html = re.sub(comparison_pattern, comparison_html, html, flags=re.DOTALL)

        # Replace {{#each PROCESS_STEPS}}...{{/each}} with actual process HTML
        process_pattern = r'\{\{#each PROCESS_STEPS\}\}.*?\{\{/each\}\}'
        html = re.sub(process_pattern, process_html, html, flags=re.DOTALL)

        # Replace {{#each LIST_ITEMS}}...{{/each}} with actual list HTML
        list_pattern = r'\{\{#each LIST_ITEMS\}\}.*?\{\{/each\}\}'
        html = re.sub(list_pattern, list_html, html, flags=re.DOTALL)

        # Replace {{#each HIERARCHY_LEVELS}}...{{/each}} with actual hierarchical HTML
        hierarchy_pattern = r'\{\{#each HIERARCHY_LEVELS\}\}.*?\{\{/each\}\}'
        html = re.sub(hierarchy_pattern, hierarchical_html, html, flags=re.DOTALL)

        # Replace entire {{#if STATS}}...{{/if}} block with stats-grid for geographic
        if self.infographic_type == 'geographic' and geographic_html:
            stats_block_html = f'''
        <div class="stats-grid">
{geographic_html}
        </div>'''
            stats_block_pattern = r'\{\{#if STATS\}\}.*?\{\{/if\}\}'
            html = re.sub(stats_block_pattern, stats_block_html, html, flags=re.DOTALL)

        # Replace {{#if CHARTS}}...{{/if}} with charts HTML (empty for Phase 1)
        charts_pattern = r'\{\{#if CHARTS\}\}.*?\{\{/if\}\}'
        html = re.sub(charts_pattern, charts_html, html, flags=re.DOTALL)

        # Replace {{#if LOGO_PATH}}...{{/if}} blocks
        logo_path = self.brand_kit.get('logo')
        if logo_path:
            logo_html = f'<img src="{logo_path}" alt="Logo" class="logo">'
            logo_pattern = r'\{\{#if LOGO_PATH\}\}.*?\{\{/if\}\}'
            html = re.sub(logo_pattern, logo_html, html, flags=re.DOTALL)
        else:
            # Remove logo block entirely if no logo
            logo_pattern = r'\{\{#if LOGO_PATH\}\}.*?\{\{/if\}\}'
            html = re.sub(logo_pattern, '', html, flags=re.DOTALL)

        # Replace {{#if SUBTITLE}}...{{/if}} blocks
        subtitle = self.args.subtitle or ''
        if subtitle:
            subtitle_html = f'<p class="subtitle">{subtitle}</p>'
            subtitle_pattern = r'\{\{#if SUBTITLE\}\}.*?\{\{/if\}\}'
            html = re.sub(subtitle_pattern, subtitle_html, html, flags=re.DOTALL)
        else:
            subtitle_pattern = r'\{\{#if SUBTITLE\}\}.*?\{\{/if\}\}'
            html = re.sub(subtitle_pattern, '', html, flags=re.DOTALL)

        # Replace {{#if WATERMARK_TEXT}}...{{/if}} blocks
        watermark = self.brand_kit.get('watermark')
        if watermark:
            watermark_html = f'<div class="watermark">{watermark}</div>'
            watermark_pattern = r'\{\{#if WATERMARK_TEXT\}\}.*?\{\{/if\}\}'
            html = re.sub(watermark_pattern, watermark_html, html, flags=re.DOTALL)
        else:
            watermark_pattern = r'\{\{#if WATERMARK_TEXT\}\}.*?\{\{/if\}\}'
            html = re.sub(watermark_pattern, '', html, flags=re.DOTALL)

        # Get template variables for simple replacements
        variables = self.prepare_template_variables()

        # Simple template variable replacement
        for key, value in variables.items():
            placeholder = '{{' + key + '}}'
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            elif isinstance(value, bool):
                # Convert Python boolean to JavaScript boolean (lowercase)
                value = 'true' if value else 'false'
            elif value is None:
                value = ''
            else:
                value = str(value)
            html = html.replace(placeholder, value)

        # Final cleanup: Remove any remaining Handlebars blocks we haven't explicitly handled
        # This catches unused sections like pricing, CTAs, icons, etc.
        # Multiple passes to handle nested blocks
        for _ in range(3):  # Run multiple times to catch nested structures
            # Remove {{#if ...}}...{{/if}} blocks (including nested ones like @last, ../showVS)
            html = re.sub(r'\{\{#if\s+[@\.\w/]+\}\}.*?\{\{/if\}\}', '', html, flags=re.DOTALL)
            # Remove {{#unless ...}}...{{/unless}} blocks
            html = re.sub(r'\{\{#unless\s+[@\.\w/]+\}\}.*?\{\{/unless\}\}', '', html, flags=re.DOTALL)
            # Remove {{#each ...}}...{{/each}} blocks (nested loops not handled)
            html = re.sub(r'\{\{#each\s+[@\.\w/]+\}\}.*?\{\{/each\}\}', '', html, flags=re.DOTALL)

        # Remove {{else}} statements
        html = re.sub(r'\{\{else\}\}', '', html)
        # Remove any remaining {{variable}} placeholders
        html = re.sub(r'\{\{[\w\./@]+\}\}', '', html)
        # Remove closing tags that might be orphaned
        html = re.sub(r'\{\{/if\}\}', '', html)
        html = re.sub(r'\{\{/each\}\}', '', html)
        html = re.sub(r'\{\{/unless\}\}', '', html)

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

        with open(headlines_file, 'w', encoding='utf-8') as f:
            f.write(f"# Generated Headlines for: {self.args.title}\n\n")
            f.write("1. Record-Breaking Results: [Your Data Here]\n")
            f.write("2. The Numbers Are In: [Key Metric] Achievement\n")
            f.write("3. Success Story: [Your Achievement] in Numbers\n")
            f.write("4. Unprecedented Growth: [Percentage] Increase\n")
            f.write("5. By the Numbers: [Your Company] Performance\n")

        with open(captions_file, 'w', encoding='utf-8') as f:
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
