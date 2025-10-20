"""
Send Gmail with attachment using Google Workspace API

PURE UTILITY - No hardcoded content. Always called by gmail-agent with explicit parameters.
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

def send_email_with_attachment(to_email, subject, body, attachment_path, cc=None, bcc=None):
    """Send email with attachment

    Args:
        to_email: Recipient email address (required)
        subject: Email subject (required)
        body: Email body text (required)
        attachment_path: Path to file to attach (required)
        cc: Optional CC email address(es) - single string or list
        bcc: Optional BCC email address(es) - single string or list

    Returns:
        str: Message ID of sent email

    Raises:
        Exception: If email sending fails

    Note:
        This is a pure utility function. No hardcoded content.
        Always called by gmail-agent with explicit parameters.
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

    # Convert plaintext to HTML with proper formatting
    # Step 1: Process line by line to detect UPPERCASE headers and make them bold
    lines = body.split('\n')
    processed_lines = []

    for line in lines:
        stripped = line.strip()
        # Auto-detect UPPERCASE headers (line is all uppercase letters/spaces and not empty)
        if stripped and stripped.isupper() and any(c.isalpha() for c in stripped):
            # Make UPPERCASE headers bold
            processed_lines.append(f'<strong>{line}</strong>')
        else:
            processed_lines.append(line)

    # Rejoin lines
    html_body = '\n'.join(processed_lines)

    # Step 2: Replace line breaks with HTML breaks
    html_body = html_body.replace('\n\n', '<PARAGRAPH_BREAK>')  # Temporary marker for paragraphs
    html_body = html_body.replace('\n', '<br>')  # Single line breaks
    html_body = html_body.replace('<PARAGRAPH_BREAK>', '<br><br>')  # Double line breaks (paragraphs)

    # Step 3: Wrap in basic HTML structure for better rendering
    html_email = f"""
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: Arial, Calibri, sans-serif; font-size: 11pt; line-height: 1.5; color: #333333;">
        {html_body}
    </body>
    </html>
    """

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
    print("      cc='cc@example.com'  # Optional")
    print("  )")
    print()
    print("Usage from gmail-agent:")
    print("  1. Read memory/email_config.json for default email addresses")
    print("  2. Compose email content (or delegate to email-specialist)")
    print("  3. Call this tool with explicit parameters")
    print("  4. Report message ID to user")
    print()
    print("=" * 70)
