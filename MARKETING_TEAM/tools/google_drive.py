"""
Google Drive Storage Tool
Automatically uploads files to organized folder structure
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from claude_agent_sdk import tool
import json
import os
import pickle
from pathlib import Path

# OAuth 2.0 scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class GoogleDriveManager:
    """Manage Google Drive uploads"""

    def __init__(self):
        self.service = None
        self.folder_ids = self.load_folder_config()
        self.authenticate()

    def authenticate(self):
        """Authenticate with Google Drive"""
        creds = None

        # Check for existing token
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('drive', 'v3', credentials=creds)

    def load_folder_config(self):
        """Load Google Drive folder structure"""
        config_path = "memory/google_drive_config.json"

        if os.path.exists(config_path):
            with open(config_path) as f:
                return json.load(f)
        else:
            return {
                "root_folder_id": None,
                "folders": {
                    "blog_posts": None,
                    "social_posts": None,
                    "images": None,
                    "videos": None,
                    "pdfs": None,
                    "presentations": None,
                    "emails": None
                }
            }

    def create_folder_structure(self):
        """Create folder structure in Google Drive"""
        # Create root folder
        if not self.folder_ids["root_folder_id"]:
            root_metadata = {
                'name': 'Marketing Content - AI Generated',
                'mimeType': 'application/vnd.google-apps.folder'
            }
            root = self.service.files().create(body=root_metadata, fields='id').execute()
            self.folder_ids["root_folder_id"] = root['id']

        # Create subfolders
        root_id = self.folder_ids["root_folder_id"]

        for folder_name, folder_id in self.folder_ids["folders"].items():
            if not folder_id:
                folder_metadata = {
                    'name': folder_name.replace('_', ' ').title(),
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [root_id]
                }
                folder = self.service.files().create(body=folder_metadata, fields='id').execute()
                self.folder_ids["folders"][folder_name] = folder['id']

        # Save config
        Path("memory").mkdir(exist_ok=True)
        with open("memory/google_drive_config.json", "w") as f:
            json.dump(self.folder_ids, f, indent=2)

    def upload_file(self, file_path: str, folder_type: str, description: str = "") -> str:
        """Upload file to Google Drive"""
        # Ensure folders exist
        if not self.folder_ids["folders"].get(folder_type):
            self.create_folder_structure()

        folder_id = self.folder_ids["folders"][folder_type]

        # File metadata
        file_name = Path(file_path).name
        file_metadata = {
            'name': file_name,
            'parents': [folder_id],
            'description': description
        }

        # Upload
        media = MediaFileUpload(file_path, resumable=True)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        # Make shareable
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        self.service.permissions().create(
            fileId=file['id'],
            body=permission
        ).execute()

        return file['webViewLink']


# Global instance
drive_manager = None


def get_drive_manager():
    """Get or create drive manager instance"""
    global drive_manager
    if drive_manager is None:
        drive_manager = GoogleDriveManager()
    return drive_manager


@tool(
    "upload_to_google_drive",
    "Upload file to Google Drive and get shareable link",
    {
        "file_path": str,
        "folder_type": str,  # blog_posts, images, videos, etc.
        "description": str
    }
)
async def upload_file_to_drive(args):
    """Upload file to organized Google Drive structure"""

    file_path = args["file_path"]
    folder_type = args["folder_type"]
    description = args.get("description", "")

    try:
        manager = get_drive_manager()
        drive_url = manager.upload_file(file_path, folder_type, description)

        result = {
            "status": "success",
            "file_path": file_path,
            "google_drive_url": drive_url,
            "folder_type": folder_type,
            "shareable": True
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
                "text": f"Error uploading to Google Drive: {str(e)}\n\nMake sure credentials.json exists and you've authenticated."
            }]
        }
