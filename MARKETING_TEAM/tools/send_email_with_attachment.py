"""
Send Gmail with attachment using Google Workspace API
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

    # Delete old token to force re-auth with new scopes
    if os.path.exists(token_path):
        os.remove(token_path)
        print("Removed old token to re-authenticate with proper scopes...")

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
    subject = "AI Investment Platform Landing Page"
    body = """Hi,

Here's the AI Investment Platform landing page we created today.

LANDING PAGE OVERVIEW

Platform: AI InvestIQ
Purpose: AI-powered investment intelligence for stock investors
Target Audience: Investors looking for high-growth AI stocks

KEY FEATURES

The landing page includes:

• Hero section with 3,200% QUBT return headline and compelling stats
• 6 feature cards explaining platform benefits (early detection, real-time analysis, smart alerts, portfolio tracking, AI trend analysis, expert research)
• Top 6 AI stocks being tracked (NVDA, QUBT, AVGO, PLTR, GOOGL, TSM) with performance data
• Social proof with 3 investor testimonials
• Lead capture form for email signups
• Professional blue/cyan gradient design theme
• Fully responsive mobile-friendly layout

DEPLOYMENT

The HTML file is attached and ready to deploy. It's a single self-contained file with all CSS embedded - just upload to your hosting provider or open directly in a browser to view.

File: ai_investment_platform.html
Size: 20 KB

Best regards"""

    attachment_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'outputs',
        'landing_pages',
        'ai_investment_platform.html'
    )

    # Send email
    send_email_with_attachment(to_email, subject, body, attachment_path)
