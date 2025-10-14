"""
Gmail API Tool
Sends emails, creates drafts, manages email campaigns
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from claude_agent_sdk import tool
import json
import os
import pickle
import base64
import time
from pathlib import Path

# OAuth 2.0 scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose'
]

# Rate limiting constants
MAX_EMAILS_PER_DAY = 500
CAMPAIGN_DELAY_SECONDS = 7  # 5-10 seconds between emails


class GmailManager:
    """Manage Gmail operations"""

    def __init__(self):
        self.service = None
        self.sent_count = self.load_sent_count()
        self.authenticate()

    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Check for existing token
        if os.path.exists('gmail_token.pickle'):
            with open('gmail_token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'gmail_credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials
            with open('gmail_token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)

    def load_sent_count(self):
        """Load daily sent count"""
        count_file = "memory/gmail_sent_count.json"

        if os.path.exists(count_file):
            with open(count_file) as f:
                data = json.load(f)
                # Reset count if new day
                from datetime import date
                if data.get("date") != str(date.today()):
                    return 0
                return data.get("count", 0)
        return 0

    def save_sent_count(self):
        """Save daily sent count"""
        Path("memory").mkdir(exist_ok=True)
        from datetime import date
        with open("memory/gmail_sent_count.json", "w") as f:
            json.dump({
                "date": str(date.today()),
                "count": self.sent_count
            }, f)

    def create_message(self, to: str, subject: str, body: str,
                      attachments: list = None, is_html: bool = True):
        """Create email message"""
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject

        # Add body
        mime_type = 'html' if is_html else 'plain'
        message.attach(MIMEText(body, mime_type))

        # Add attachments
        if attachments:
            for file_path in attachments:
                if not os.path.exists(file_path):
                    continue

                attachment = MIMEBase('application', 'octet-stream')
                with open(file_path, 'rb') as f:
                    attachment.set_payload(f.read())

                encoders.encode_base64(attachment)
                filename = Path(file_path).name
                attachment.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}'
                )
                message.attach(attachment)

        # Encode message
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw}

    def send_message(self, to: str, subject: str, body: str,
                    attachments: list = None, is_html: bool = True):
        """Send email message"""
        # Check rate limit
        if self.sent_count >= MAX_EMAILS_PER_DAY:
            raise Exception(f"Daily email limit reached ({MAX_EMAILS_PER_DAY})")

        try:
            message = self.create_message(to, subject, body, attachments, is_html)
            sent = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()

            # Update count
            self.sent_count += 1
            self.save_sent_count()

            return sent['id']
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")

    def create_draft(self, to: str, subject: str, body: str,
                    attachments: list = None, is_html: bool = True):
        """Create email draft"""
        try:
            message = self.create_message(to, subject, body, attachments, is_html)
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': message}
            ).execute()

            draft_id = draft['id']
            draft_url = f"https://mail.google.com/mail/u/0/#drafts/{draft_id}"
            return draft_url
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")

    def send_campaign(self, recipients: list, subject: str, body: str,
                     attachments: list = None, is_html: bool = True):
        """Send email campaign with rate limiting"""
        results = []

        for i, recipient in enumerate(recipients):
            # Check limit
            if self.sent_count >= MAX_EMAILS_PER_DAY:
                results.append({
                    "to": recipient,
                    "status": "skipped",
                    "reason": "Daily limit reached"
                })
                continue

            try:
                # Send email
                message_id = self.send_message(
                    recipient, subject, body, attachments, is_html
                )
                results.append({
                    "to": recipient,
                    "status": "sent",
                    "message_id": message_id
                })

                # Delay between emails (except last one)
                if i < len(recipients) - 1:
                    time.sleep(CAMPAIGN_DELAY_SECONDS)

            except Exception as e:
                results.append({
                    "to": recipient,
                    "status": "failed",
                    "error": str(e)
                })

        return results


# Global instance
gmail_manager = None


def get_gmail_manager():
    """Get or create Gmail manager instance"""
    global gmail_manager
    if gmail_manager is None:
        gmail_manager = GmailManager()
    return gmail_manager


@tool(
    "send_gmail",
    "Send email via Gmail with optional attachments",
    {
        "to": str,
        "subject": str,
        "body": str,
        "attachments": list,  # Optional list of file paths
        "is_html": bool  # Default True
    }
)
async def send_gmail(args):
    """Send individual email via Gmail"""

    to = args["to"]
    subject = args["subject"]
    body = args["body"]
    attachments = args.get("attachments", [])
    is_html = args.get("is_html", True)

    try:
        manager = get_gmail_manager()
        message_id = manager.send_message(to, subject, body, attachments, is_html)

        result = {
            "status": "sent",
            "to": to,
            "subject": subject,
            "message_id": message_id,
            "sent_today": manager.sent_count,
            "limit_remaining": MAX_EMAILS_PER_DAY - manager.sent_count
        }

        return {
            "content": [{
                "type": "text",
                "text": json.dumps(result, indent=2)
            }]
        }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error sending email: {str(e)}\n\nMake sure gmail_credentials.json exists and you've authenticated."
            }]
        }


@tool(
    "create_gmail_draft",
    "Create email draft in Gmail for review",
    {
        "to": str,
        "subject": str,
        "body": str,
        "attachments": list,  # Optional list of file paths
        "is_html": bool  # Default True
    }
)
async def create_gmail_draft(args):
    """Create email draft for review"""

    to = args["to"]
    subject = args["subject"]
    body = args["body"]
    attachments = args.get("attachments", [])
    is_html = args.get("is_html", True)

    try:
        manager = get_gmail_manager()
        draft_url = manager.create_draft(to, subject, body, attachments, is_html)

        result = {
            "status": "draft_created",
            "to": to,
            "subject": subject,
            "draft_url": draft_url,
            "message": "Draft created. Review and send from Gmail."
        }

        return {
            "content": [{
                "type": "text",
                "text": json.dumps(result, indent=2)
            }]
        }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error creating draft: {str(e)}\n\nMake sure gmail_credentials.json exists and you've authenticated."
            }]
        }


@tool(
    "send_email_campaign",
    "Send email campaign to multiple recipients (rate limited: 7s delay between emails)",
    {
        "recipients": list,  # List of email addresses
        "subject": str,
        "body": str,
        "attachments": list,  # Optional list of file paths
        "is_html": bool  # Default True
    }
)
async def send_email_campaign(args):
    """Send email campaign with rate limiting"""

    recipients = args["recipients"]
    subject = args["subject"]
    body = args["body"]
    attachments = args.get("attachments", [])
    is_html = args.get("is_html", True)

    # Validate recipient count
    if len(recipients) > MAX_EMAILS_PER_DAY:
        return {
            "content": [{
                "type": "text",
                "text": f"Error: Campaign exceeds daily limit. Max {MAX_EMAILS_PER_DAY} emails/day."
            }]
        }

    try:
        manager = get_gmail_manager()
        results = manager.send_campaign(recipients, subject, body, attachments, is_html)

        # Summarize results
        sent = sum(1 for r in results if r["status"] == "sent")
        failed = sum(1 for r in results if r["status"] == "failed")
        skipped = sum(1 for r in results if r["status"] == "skipped")

        summary = {
            "status": "campaign_completed",
            "total_recipients": len(recipients),
            "sent": sent,
            "failed": failed,
            "skipped": skipped,
            "sent_today": manager.sent_count,
            "limit_remaining": MAX_EMAILS_PER_DAY - manager.sent_count,
            "detailed_results": results
        }

        return {
            "content": [{
                "type": "text",
                "text": json.dumps(summary, indent=2)
            }]
        }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error sending campaign: {str(e)}\n\nMake sure gmail_credentials.json exists and you've authenticated."
            }]
        }
