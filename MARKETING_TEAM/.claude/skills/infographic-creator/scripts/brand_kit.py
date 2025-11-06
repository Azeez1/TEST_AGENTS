#!/usr/bin/env python3
"""
Brand Kit Management
Save and apply brand kits to infographics
"""

import json
import argparse
from pathlib import Path

class BrandKitManager:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.skill_dir = self.script_dir.parent
        self.brand_kits_file = self.skill_dir / 'brand_kits.json'
        self.load_kits()

    def load_kits(self):
        if self.brand_kits_file.exists():
            with open(self.brand_kits_file, 'r') as f:
                self.kits = json.load(f)
        else:
            self.kits = {}

    def save_kits(self):
        with open(self.brand_kits_file, 'w') as f:
            json.dump(self.kits, f, indent=2)

    def create_kit(self, name, primary_color, secondary_color, accent_color,
                   headline_font='Inter', body_font='Inter', logo_path=None, watermark=None):
        kit = {
            'colors': {
                'primary': primary_color,
                'secondary': secondary_color,
                'accent': accent_color
            },
            'fonts': {
                'headline': headline_font,
                'body': body_font
            },
            'logo': logo_path,
            'watermark': watermark
        }
        self.kits[name] = kit
        self.save_kits()
        print(f"✓ Brand kit '{name}' created successfully!")

    def list_kits(self):
        if not self.kits:
            print("No brand kits found.")
            return

        print("\n📦 Saved Brand Kits:\n")
        for name, kit in self.kits.items():
            print(f"  • {name}")
            print(f"    Primary: {kit['colors']['primary']}")
            print(f"    Fonts: {kit['fonts']['headline']}, {kit['fonts']['body']}")
            print()

    def delete_kit(self, name):
        if name in self.kits:
            del self.kits[name]
            self.save_kits()
            print(f"✓ Brand kit '{name}' deleted.")
        else:
            print(f"Error: Brand kit '{name}' not found.")

def main():
    parser = argparse.ArgumentParser(description='Manage brand kits')
    subparsers = parser.add_subparsers(dest='command')

    # Create command
    create_parser = subparsers.add_parser('create', help='Create new brand kit')
    create_parser.add_argument('name', help='Brand kit name')
    create_parser.add_argument('--primary', required=True, help='Primary color (hex)')
    create_parser.add_argument('--secondary', required=True, help='Secondary color (hex)')
    create_parser.add_argument('--accent', required=True, help='Accent color (hex)')
    create_parser.add_argument('--headline-font', default='Inter', help='Headline font')
    create_parser.add_argument('--body-font', default='Inter', help='Body font')
    create_parser.add_argument('--logo', help='Path to logo image')
    create_parser.add_argument('--watermark', help='Watermark text')

    # List command
    subparsers.add_parser('list', help='List all brand kits')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete brand kit')
    delete_parser.add_argument('name', help='Brand kit name')

    args = parser.parse_args()

    manager = BrandKitManager()

    if args.command == 'create':
        manager.create_kit(
            args.name, args.primary, args.secondary, args.accent,
            args.headline_font, args.body_font, args.logo, args.watermark
        )
    elif args.command == 'list':
        manager.list_kits()
    elif args.command == 'delete':
        manager.delete_kit(args.name)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
