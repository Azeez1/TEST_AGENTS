"""
Upload HTML file to Google Drive
"""
import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes for Google Drive
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive'
]

def get_drive_service():
    """Authenticate and return Drive service"""
    creds = None
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

def upload_html_to_drive(file_path, title):
    """Upload HTML file to Google Drive"""
    service = get_drive_service()

    # File metadata
    file_metadata = {
        'name': title,
        'mimeType': 'text/html'
    }

    # Upload file
    media = MediaFileUpload(
        file_path,
        mimetype='text/html',
        resumable=True
    )

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, webViewLink, mimeType'
    ).execute()

    return file

if __name__ == '__main__':
    # File to upload
    html_path = r'c:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS\MARKETING_TEAM\outputs\presentations\agent_flow_interactive.html'
    title = 'Marketing Agents Intelligence Network - Interactive'

    print(f"Uploading {html_path} to Google Drive...")

    result = upload_html_to_drive(html_path, title)

    print(f"\nSuccessfully uploaded to Google Drive!")
    print(f"File ID: {result['id']}")
    print(f"File Name: {result['name']}")
    print(f"View Link: {result['webViewLink']}")
    print(f"MIME Type: {result['mimeType']}")
    print(f"\nNote: Download the HTML file from Drive and open locally for full interactivity.")
    print(f"Google Drive's HTML preview may have limited functionality.")
