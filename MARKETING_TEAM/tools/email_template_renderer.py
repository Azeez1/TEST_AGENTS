"""
Email Template Renderer for Branded HTML Emails

Provides branded HTML email templates for gmail-agent and email sending tools.
Converts plaintext email bodies to styled HTML using Dux Machina brand templates.

Templates available:
- plain: Enhanced minimal styling (safe for all clients)
- branded_light: Professional with dark header/footer + gold CTAs
- branded_dark: Full dark theme (elite, high-impact)
- professional: Corporate-safe (enterprise clients)
"""

import json
import os
from typing import Optional, Dict

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'memory')
TEMPLATES_PATH = os.path.join(MEMORY_DIR, 'email_templates.json')


def load_templates() -> Dict:
    """
    Load email templates from memory/email_templates.json

    Returns:
        Dict containing templates, default_template, and cta_templates
    """
    try:
        with open(TEMPLATES_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Email templates not found at {TEMPLATES_PATH}. "
            "Please ensure memory/email_templates.json exists."
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in email templates file: {e}")


def get_template(template_name: str = 'branded_light') -> str:
    """
    Get a specific email template by name

    Args:
        template_name: Name of template ('plain', 'branded_light', 'branded_dark', 'professional')

    Returns:
        HTML template string

    Raises:
        ValueError: If template name not found
    """
    templates_data = load_templates()
    templates = templates_data.get('templates', {})

    if template_name not in templates:
        available = ', '.join(templates.keys())
        raise ValueError(
            f"Template '{template_name}' not found. "
            f"Available templates: {available}"
        )

    return templates[template_name]['html_template']


def convert_plaintext_to_html(body: str) -> str:
    """
    Convert plaintext email body to HTML with formatting

    Converts:
    - UPPERCASE headers → <strong> tags
    - Line breaks (\n) → <br> tags
    - Double line breaks (\n\n) → <br><br> (paragraph breaks)

    Args:
        body: Plaintext email body

    Returns:
        HTML-formatted body content
    """
    lines = body.split('\n')
    processed_lines = []

    for line in lines:
        stripped = line.strip()

        # If line is all UPPERCASE letters/spaces (and has letters), make it bold
        if stripped and stripped.isupper() and any(c.isalpha() for c in stripped):
            processed_lines.append(f'<strong>{line}</strong>')
        else:
            processed_lines.append(line)

    html_body = '\n'.join(processed_lines)

    # Convert line breaks to HTML
    html_body = html_body.replace('\n\n', '<PARAGRAPH_BREAK>')
    html_body = html_body.replace('\n', '<br>')
    html_body = html_body.replace('<PARAGRAPH_BREAK>', '<br><br>')

    return html_body


def render_email_html(
    body: str,
    template: str = 'branded_light',
    cta_text: Optional[str] = None,
    cta_link: Optional[str] = None
) -> str:
    """
    Render complete branded HTML email

    Args:
        body: Plaintext email body
        template: Template name ('plain', 'branded_light', 'branded_dark', 'professional')
        cta_text: Optional CTA button text
        cta_link: Optional CTA button URL

    Returns:
        Complete HTML email ready to send

    Example:
        >>> html = render_email_html(
        ...     body="Hi there,\\n\\nThis is a test email.\\n\\nThanks!",
        ...     template='branded_dark',
        ...     cta_text='View Dashboard',
        ...     cta_link='https://example.com/dashboard'
        ... )
    """
    # Load templates
    templates_data = load_templates()

    # Get template HTML
    template_html = get_template(template)

    # Convert plaintext body to HTML
    html_body = convert_plaintext_to_html(body)

    # Handle CTA button
    cta_section = ''
    if cta_text and cta_link:
        cta_templates = templates_data.get('cta_templates', {})

        # Use template-specific CTA if available, otherwise skip
        if template in cta_templates:
            cta_section = cta_templates[template]
            cta_section = cta_section.replace('{{CTA_TEXT}}', cta_text)
            cta_section = cta_section.replace('{{CTA_LINK}}', cta_link)

    # Insert content into template
    final_html = template_html.replace('{{BODY_CONTENT}}', html_body)
    final_html = final_html.replace('{{CTA_SECTION}}', cta_section)

    return final_html


def get_default_template() -> str:
    """
    Get the default template name from configuration

    Returns:
        Default template name (e.g., 'branded_light')
    """
    templates_data = load_templates()
    return templates_data.get('default_template', 'branded_light')


def list_templates() -> Dict[str, Dict]:
    """
    List all available templates with metadata

    Returns:
        Dict mapping template names to their metadata (name, description, use_cases)
    """
    templates_data = load_templates()
    templates = templates_data.get('templates', {})

    return {
        name: {
            'name': info['name'],
            'description': info['description'],
            'use_cases': info['use_cases']
        }
        for name, info in templates.items()
    }


def select_template_for_context(
    email_type: str = 'general',
    recipient_type: str = 'general'
) -> str:
    """
    Automatically select template based on email context

    Args:
        email_type: Type of email ('announcement', 'deliverable', 'proposal', 'update', etc.)
        recipient_type: Type of recipient ('enterprise', 'partner', 'client', 'internal', etc.)

    Returns:
        Recommended template name

    Examples:
        >>> select_template_for_context('announcement', 'general')
        'branded_dark'

        >>> select_template_for_context('deliverable', 'enterprise')
        'professional'

        >>> select_template_for_context('update', 'client')
        'branded_light'
    """
    # Strategic/High-Impact → Dark
    if email_type in ['announcement', 'thought_leadership', 'strategic']:
        return 'branded_dark'

    # Enterprise/Formal → Professional
    if recipient_type in ['enterprise', 'partner', 'formal']:
        return 'professional'

    # Client Work → Branded Light
    if email_type in ['deliverable', 'proposal', 'client_update']:
        return 'branded_light'

    # Internal/Quick → Plain
    if email_type in ['internal', 'transactional', 'quick_update']:
        return 'plain'

    # Default → Branded Light
    return 'branded_light'


if __name__ == '__main__':
    # Test the renderer
    print("Email Template Renderer Test")
    print("=" * 60)

    # List available templates
    print("\nAvailable Templates:")
    templates = list_templates()
    for name, info in templates.items():
        print(f"  - {name}: {info['name']}")
        print(f"    {info['description']}")
        print(f"    Use cases: {', '.join(info['use_cases'])}")

    # Test rendering
    print("\n" + "=" * 60)
    print("Test Rendering (branded_dark template):")
    print("=" * 60)

    test_body = """Hi there,

EXCITING NEWS

We've just launched 4 new branded email templates for your marketing communications.

WHAT'S INCLUDED

• Plain - Enhanced minimal styling
• Branded Light - Professional with dark header/footer
• Branded Dark - Full dark theme (elite, high-impact)
• Professional - Corporate-safe for enterprise clients

These templates use your Dux Machina brand colors and maintain consistent visual identity across all emails.

Ready to elevate your email game?

Best regards,
Your Marketing Team"""

    html = render_email_html(
        body=test_body,
        template='branded_dark',
        cta_text='View Templates',
        cta_link='https://example.com/templates'
    )

    print("\n[HTML output generated - use in email client to view]")
    print(f"Length: {len(html)} characters")
    print("\nFirst 500 characters:")
    print(html[:500] + "...")
