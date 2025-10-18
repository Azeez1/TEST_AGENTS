import os
import pickle
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']

def get_drive_service():
    creds = None
    script_dir = os.path.dirname(os.path.abspath(__file__))
    marketing_dir = os.path.dirname(script_dir)
    token_path = os.path.join(marketing_dir, 'token.pickle')

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if creds and creds.valid:
        return build('drive', 'v3', credentials=creds)
    return None

def upload_md_to_drive(file_path, title):
    service = get_drive_service()
    if not service:
        print("Authentication needed")
        return None

    file_metadata = {'name': title, 'mimeType': 'text/plain'}
    media = MediaFileUpload(file_path, mimetype='text/markdown', resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id, name, webViewLink, mimeType').execute()
    return file

if __name__ == '__main__':
    result = upload_md_to_drive(
        r'c:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS\MARKETING_TEAM\outputs\presentations\agent_flow_design_philosophy.md',
        'Agent Flow Design Philosophy'
    )
    if result:
        print(f"Uploaded: {result['name']}")
        print(f"View Link: {result['webViewLink']}")
