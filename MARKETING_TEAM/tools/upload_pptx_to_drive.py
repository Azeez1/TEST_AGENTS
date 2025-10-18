"""
Upload PowerPoint to Google Drive and convert to Google Slides
"""
import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

# Scopes for Google Drive
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive'
]

def get_drive_service(user_email='sabaazeez12@gmail.com'):
    """Authenticate and return Drive service"""
    creds = None
    # Use paths relative to MARKETING_TEAM folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    marketing_dir = os.path.dirname(script_dir)
    token_path = os.path.join(marketing_dir, 'token.pickle')
    credentials_path = os.path.join(marketing_dir, 'credentials.json')

    # Load existing credentials
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

def upload_pptx_to_slides(file_path, title):
    """Upload PowerPoint and convert to Google Slides"""

    service = get_drive_service()

    # File metadata - specify Google Slides MIME type for conversion
    file_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.presentation'
    }

    # Upload with conversion
    media = MediaFileUpload(
        file_path,
        mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation',
        resumable=True
    )

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, webViewLink, mimeType'
    ).execute()

    return file

if __name__ == '__main__':
    import sys
    # File to upload
    if len(sys.argv) > 1:
        pptx_path = sys.argv[1]
        title = sys.argv[2] if len(sys.argv) > 2 else 'Marketing Agents Presentation'
    else:
        pptx_path = r'c:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS\MARKETING_TEAM\outputs\presentations\AI_Marketing_Agents.pptx'
        title = 'AI Marketing Agents Presentation'

    print(f"Uploading {pptx_path} to Google Drive...")

    result = upload_pptx_to_slides(pptx_path, title)

    print(f"\nSuccessfully uploaded to Google Slides!")
    print(f"File ID: {result['id']}")
    print(f"File Name: {result['name']}")
    print(f"View/Edit Link: {result['webViewLink']}")
    print(f"MIME Type: {result['mimeType']}")
