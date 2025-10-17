"""
Send DUX MACHINA OS Marketing Team documentation via email
"""
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://mail.google.com/'
]

def get_gmail_service():
    """Authenticate and return Gmail service"""
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), '..', 'token.pickle')
    creds_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')

    # Load existing credentials
    if os.path.exists(token_path):
        import pickle
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials
        import pickle
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def send_email_with_attachment(to_email, subject, body, attachment_path):
    """Send email with attachment"""
    service = get_gmail_service()

    # Create message
    message = MIMEMultipart()
    message['to'] = to_email
    message['subject'] = subject

    # Add body
    message.attach(MIMEText(body, 'plain'))

    # Add attachment
    filename = os.path.basename(attachment_path)
    with open(attachment_path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())

    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
    message.attach(part)

    # Encode and send
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    try:
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()

        print(f"Email sent successfully!")
        print(f"Message ID: {sent_message['id']}")
        return sent_message['id']

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise

if __name__ == "__main__":
    # Email details
    to_email = "sabaazeez12@gmail.com"
    subject = "DUX MACHINA OS - Marketing Team Documentation"
    body = """Hi,

Here is the comprehensive documentation for the DUX MACHINA OS Marketing Team.

OVERVIEW

This document provides a complete reference guide to your AI marketing automation system featuring 15 specialized agents powered by Claude Agent SDK.

WHAT'S INCLUDED

The attached HTML page documents all 15 marketing agents with:

• Role and description for each agent
• Core capabilities and responsibilities
• Tools and APIs each agent uses
• MCP server infrastructure details
• Model information (Claude Opus 4 and Sonnet 4)
• How to invoke each agent with examples

MARKETING TEAM CAPABILITIES

Router Agent - Campaign orchestration and intent classification
Content Strategist - Multi-agent coordination and quality oversight
Research Agent - Deep research with Perplexity AI and citations
Copywriter - Blog posts and long-form content (2000+ words)
Editor - Content review and QA for all materials
Social Media Manager - Twitter/X and LinkedIn platform optimization
Visual Designer - GPT-4o image generation with brand compliance
Video Producer - Sora video creation (720p, $0.10/second)
SEO Specialist - Keyword research and competitive analysis
Email Specialist - High-converting email campaigns
Gmail Agent - Email automation with rate limiting (500/day)
Landing Page Specialist - Conversion-optimized pages with code
PDF Specialist - Whitepapers, lead magnets, reports
Presentation Designer - PowerPoint decks with GPT-4o images
Analyst - Campaign performance and ROI analysis

MCP INFRASTRUCTURE

The system leverages 5 MCP servers:

• Perplexity MCP - Real-time web research with citations
• OpenAI MCP - GPT-4o images and Sora videos
• Playwright MCP - Browser automation for visual analysis
• Google Workspace MCP - Gmail, Drive, Docs, Sheets, Calendar
• Marketing Tools MCP - Brand voice and platform formatters

USAGE

All agents are invoked through natural conversation with Claude Code. The HTML page includes example commands and a complete campaign workflow demonstration.

FILE DETAILS

Filename: DUX_MACHINA_OS_Marketing_Team.html
Type: HTML (viewable in any browser)
Size: ~60 KB
Purpose: Business partner presentation and reference guide

VIEWING THE DOCUMENT

Simply open the attached HTML file in any web browser (Chrome, Firefox, Edge, Safari) to view the complete documentation. The page is fully responsive and includes:

• Modern dark theme design
• Agent cards with all technical details
• MCP server infrastructure guide
• Example campaign workflow
• Mobile-friendly layout

This document is perfect for sharing with business partners to showcase the capabilities of your AI marketing automation system.

Best regards</body>"""

    attachment_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'outputs',
        'DUX_MACHINA_OS_Marketing_Team.html'
    )

    # Send email
    send_email_with_attachment(to_email, subject, body, attachment_path)
