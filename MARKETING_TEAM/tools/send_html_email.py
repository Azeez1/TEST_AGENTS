"""
Send HTML Gmail without attachment using Google Workspace API
"""
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

def send_html_email(to_email, subject, body, cc=None, bcc=None):
    """Send HTML email without attachment

    Args:
        to_email: Recipient email address (required)
        subject: Email subject (required)
        body: Email body text (will be converted to HTML)
        cc: Optional CC email address(es) - single string or list
        bcc: Optional BCC email address(es) - single string or list

    Returns:
        str: Message ID of sent email

    Raises:
        Exception: If email sending fails
    """
    if not all([to_email, subject, body]):
        raise ValueError("to_email, subject, and body are required")

    service = get_gmail_service()

    # Create message container
    message = MIMEMultipart('alternative')
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

    # Attach plaintext version first (lower priority)
    message.attach(MIMEText(body, 'plain', 'utf-8'))

    # Attach HTML version second (higher priority - email clients will show this)
    message.attach(MIMEText(html_email, 'html', 'utf-8'))

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
    import sys
    if len(sys.argv) < 4:
        print("Usage: python send_html_email.py <to_email> <subject> <body> [cc]")
        sys.exit(1)

    to = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]
    cc = sys.argv[4] if len(sys.argv) > 4 else None

    send_html_email(to, subject, body, cc=cc)
