"""
Send Gmail with attachment using Google Workspace API

PURE UTILITY - No hardcoded content. Always called by gmail-agent with explicit parameters.

Supports branded HTML email templates (plain, branded_light, branded_dark, professional).
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
from email_template_renderer import render_email_html, get_default_template

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

def send_email_with_attachment(to_email, subject, body, attachment_path, cc=None, bcc=None, template='branded_light', cta_text=None, cta_link=None):
    """Send email with attachment using branded HTML templates

    Args:
        to_email: Recipient email address (required)
        subject: Email subject (required)
        body: Email body text (required)
        attachment_path: Path to file to attach (required)
        cc: Optional CC email address(es) - single string or list
        bcc: Optional BCC email address(es) - single string or list
        template: Email template ('plain', 'branded_light', 'branded_dark', 'professional')
                 Default: 'branded_light'
        cta_text: Optional CTA button text
        cta_link: Optional CTA button URL

    Returns:
        str: Message ID of sent email

    Raises:
        Exception: If email sending fails

    Note:
        This is a pure utility function. No hardcoded content.
        Always called by gmail-agent with explicit parameters.

    Templates:
        - plain: Enhanced minimal (safe for all clients)
        - branded_light: Professional with dark header/footer + gold CTAs
        - branded_dark: Full dark theme (elite, high-impact)
        - professional: Corporate-safe (enterprise clients)
    """
    if not all([to_email, subject, body, attachment_path]):
        raise ValueError("to_email, subject, body, and attachment_path are required")

    if not os.path.exists(attachment_path):
        raise FileNotFoundError(f"Attachment not found: {attachment_path}")

    service = get_gmail_service()

    # Create message container with mixed content (body + attachments)
    message = MIMEMultipart('mixed')
    message['to'] = to_email
    message['subject'] = subject

    # Add CC if provided
    if cc:
        if isinstance(cc, list):
            message['cc'] = ', '.join(cc)
        else:
            message['cc'] = cc

    # Add BCC if provided
    if bcc:
        if isinstance(bcc, list):
            message['bcc'] = ', '.join(bcc)
        else:
            message['bcc'] = bcc

    # Render HTML email using branded template
    html_email = render_email_html(
        body=body,
        template=template,
        cta_text=cta_text,
        cta_link=cta_link
    )

    # Create alternative part (for email clients to choose HTML or plaintext)
    msg_alternative = MIMEMultipart('alternative')

    # Attach plaintext version first (lower priority)
    msg_alternative.attach(MIMEText(body, 'plain', 'utf-8'))

    # Attach HTML version second (higher priority - email clients will show this)
    msg_alternative.attach(MIMEText(html_email, 'html', 'utf-8'))

    # Attach the alternative part to the main message
    message.attach(msg_alternative)

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
    # Pure utility - no hardcoded content
    print("=" * 70)
    print("send_email_with_attachment.py - Pure Utility Function")
    print("=" * 70)
    print()
    print("This tool should be called by gmail-agent with explicit parameters.")
    print("It contains NO hardcoded email content.")
    print()
    print("Usage from Python:")
    print("  from send_email_with_attachment import send_email_with_attachment")
    print("  message_id = send_email_with_attachment(")
    print("      to_email='recipient@example.com',")
    print("      subject='Your Subject',")
    print("      body='Your email body text',")
    print("      attachment_path='/path/to/file.pdf',")
    print("      cc='cc@example.com',  # Optional")
    print("      template='branded_dark',  # Optional (default: 'branded_light')")
    print("      cta_text='View Dashboard',  # Optional CTA button")
    print("      cta_link='https://example.com/dashboard'  # Optional CTA link")
    print("  )")
    print()
    print("Available Templates:")
    print("  - plain: Enhanced minimal (safe for all clients)")
    print("  - branded_light: Professional with dark header/footer + gold CTAs (default)")
    print("  - branded_dark: Full dark theme (elite, high-impact)")
    print("  - professional: Corporate-safe (enterprise clients)")
    print()
    print("Usage from gmail-agent:")
    print("  1. Read memory/email_config.json for default email addresses")
    print("  2. Compose email content (or delegate to email-specialist)")
    print("  3. Call this tool with explicit parameters")
    print("  4. Report message ID to user")
    print()
    print("=" * 70)
