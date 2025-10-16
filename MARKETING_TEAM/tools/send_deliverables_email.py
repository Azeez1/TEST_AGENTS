"""
Email Marketing Deliverables Tool
Always sends to default recipients: sabaazeez12@gmail.com and aoseni@duxvitaecapital.com
"""

import os
import json
from pathlib import Path

# Load default recipients from memory
def get_default_recipients():
    """Load default email recipients from memory"""
    memory_file = Path("memory/default_email_recipients.json")
    if memory_file.exists():
        with open(memory_file) as f:
            data = json.load(f)
            return data.get("default_recipients", [])
    return ["sabaazeez12@gmail.com", "aoseni@duxvitaecapital.com"]


def send_landing_page_email():
    """Send landing page deliverable email to default recipients"""

    recipients = get_default_recipients()

    subject = "AI Investment Landing Page - Ready to Deploy"

    body = """Hi!

Your AI Investment Intelligence landing page is complete and ready to deploy.

## What's Included:

**Landing Page File:**
- Location: MARKETING_TEAM/outputs/landing_pages/ai_investment_platform.html
- Type: Production-ready HTML (fully self-contained)
- Size: ~25KB

## Key Features:

1. **Hero Section** - Grabs attention with AI stock performance stats:
   - NVDA: +120% YTD
   - QUBT: +3,200% explosive growth
   - PLTR: +311% returns

2. **6 Feature Cards** - Highlights platform capabilities:
   - Early AI stock detection
   - Real-time analysis
   - Smart alerts
   - Portfolio tracking
   - AI trend analysis
   - Expert research

3. **Stock Showcase** - Top 6 AI stocks with performance data

4. **Social Proof** - 3 testimonials from investors

5. **Lead Capture Form** - Email signup with clear CTA

6. **Fully Responsive** - Mobile, tablet, desktop optimized

## Technical Details:

- Modern gradient design (blue/cyan color scheme)
- CSS Grid/Flexbox responsive layout
- No external dependencies
- Accessibility compliant (ARIA labels, semantic HTML)
- Fast loading (embedded CSS, no external resources)

## How to Use:

1. **Preview:** Open the HTML file in any browser
2. **Deploy:** Upload to your web hosting or use with landing page builder
3. **Customize:** Update form action to connect to your email service
4. **Rebrand:** Modify CSS variables at top of file for colors/spacing

## Also Created Today:

**AI Future Video (12 seconds)**
- Google Drive: https://drive.google.com/file/d/1__OUsk0w-etUObBOFSRNGQP224xUb0cb/view?usp=drivesdk
- Local: MARKETING_TEAM/outputs/videos/ai_future_video.mp4
- Cost: $1.20 (Sora-2)

Both deliverables are based on the AI stocks research showing NVDA, QUBT, PLTR, and other top performers.

Ready to launch!

Best,
AI Marketing Team"""

    print("=" * 70)
    print("Sending Deliverables Email")
    print("=" * 70)
    print()
    print(f"To: {', '.join(recipients)}")
    print(f"Subject: {subject}")
    print()
    print("NOTE: To actually send emails, you need to:")
    print("1. Set up Google Workspace MCP (already configured)")
    print("2. Restart Claude Code to load MCP servers")
    print("3. Use MCP Gmail tools to send")
    print()
    print("Email body preview:")
    print("-" * 70)
    print(body)
    print("-" * 70)
    print()
    print("Email would be sent to:")
    for email in recipients:
        print(f"  - {email}")
    print()


if __name__ == "__main__":
    send_landing_page_email()
