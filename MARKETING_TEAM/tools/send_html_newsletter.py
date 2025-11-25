"""
Send HTML Newsletter via Gmail API

Pure utility for sending HTML newsletters without attachments.
Always called by gmail-agent with explicit parameters.
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

def send_html_newsletter(to_email, subject, html_content, cc=None, bcc=None):
    """Send HTML newsletter email

    Args:
        to_email: Recipient email address (required)
        subject: Email subject (required)
        html_content: HTML content as string or path to HTML file (required)
        cc: Optional CC email address(es) - single string or list
        bcc: Optional BCC email address(es) - single string or list

    Returns:
        str: Message ID of sent email

    Raises:
        Exception: If email sending fails
    """
    if not all([to_email, subject, html_content]):
        raise ValueError("to_email, subject, and html_content are required")

    # Check if html_content is a file path
    if isinstance(html_content, str) and os.path.exists(html_content):
        with open(html_content, 'r', encoding='utf-8') as f:
            html_body = f.read()
    else:
        html_body = html_content

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

    # Create plain text version (fallback)
    plain_text = "This email is best viewed in an HTML-compatible email client."

    # Attach both versions
    message.attach(MIMEText(plain_text, 'plain', 'utf-8'))
    message.attach(MIMEText(html_body, 'html', 'utf-8'))

    # Encode and send
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    try:
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()

        print(f"[SUCCESS] Newsletter sent successfully!")
        print(f"  To: {to_email}")
        if cc:
            print(f"  CC: {cc}")
        print(f"  Subject: {subject}")
        print(f"  Message ID: {sent_message['id']}")
        return sent_message['id']

    except Exception as e:
        print(f"[ERROR] Error sending newsletter: {str(e)}")
        raise

if __name__ == "__main__":
    print("=" * 70)
    print("send_html_newsletter.py - HTML Newsletter Utility")
    print("=" * 70)
    print()
    print("Usage:")
    print("  from send_html_newsletter import send_html_newsletter")
    print("  message_id = send_html_newsletter(")
    print("      to_email='recipient@example.com',")
    print("      subject='Newsletter Subject',")
    print("      html_content='/path/to/newsletter.html',  # or HTML string")
    print("      cc='cc@example.com'  # Optional")
    print("  )")
    print()
