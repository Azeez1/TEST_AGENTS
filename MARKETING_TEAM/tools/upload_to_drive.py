#!/usr/bin/env python3
"""
Reusable Google Drive upload tool for binary files.

Fills the gap in google-workspace MCP which can't handle local binary file uploads.
Supports all file types: PowerPoint, PDF, Excel, Word, images, videos, etc.

Usage:
    from tools.upload_to_drive import upload_to_drive

    result = upload_to_drive(
        file_path="outputs/presentations/deck.pptx",
        file_name="My Presentation.pptx",
        folder_id="1QkAUOP9v4u3DugZjVcYUnaiT7pitN3sv"
    )
"""

import os
import pickle
from typing import Dict, Optional
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes for Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Common MIME types
MIME_TYPES = {
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.pdf': 'application/pdf',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.mp4': 'video/mp4',
    '.txt': 'text/plain',
    '.md': 'text/markdown',
    '.csv': 'text/csv',
}


def get_drive_service():
    """Authenticate and return Google Drive service."""
    creds = None
    token_path = 'token.pickle'

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
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)


def detect_mime_type(file_path: str) -> str:
    """Detect MIME type from file extension."""
    ext = Path(file_path).suffix.lower()
    return MIME_TYPES.get(ext, 'application/octet-stream')


def upload_to_drive(
    file_path: str,
    file_name: str,
    folder_id: str,
    mime_type: Optional[str] = None
) -> Dict[str, str]:
    """
    Upload a local file to Google Drive.

    Args:
        file_path: Path to the local file to upload
        file_name: Name for the file in Google Drive
        folder_id: Google Drive folder ID (use config from memory/google_drive_config.json)
        mime_type: Optional MIME type (auto-detected if not provided)

    Returns:
        Dict with file_id, file_name, and web_view_link

    Raises:
        FileNotFoundError: If file_path doesn't exist
        Exception: If upload fails
    """
    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Auto-detect MIME type if not provided
    if not mime_type:
        mime_type = detect_mime_type(file_path)

    # Get Drive service
    service = get_drive_service()

    # Prepare file metadata
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    # Create media upload
    media = MediaFileUpload(
        file_path,
        mimetype=mime_type,
        resumable=True
    )

    # Upload file
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, webViewLink'
    ).execute()

    return {
        'file_id': file.get('id'),
        'file_name': file.get('name'),
        'web_view_link': file.get('webViewLink')
    }


def main():
    """CLI interface for testing."""
    import sys

    if len(sys.argv) < 4:
        print("Usage: python upload_to_drive.py <file_path> <file_name> <folder_id>")
        sys.exit(1)

    file_path = sys.argv[1]
    file_name = sys.argv[2]
    folder_id = sys.argv[3]

    try:
        result = upload_to_drive(file_path, file_name, folder_id)
        print("File uploaded successfully!")
        print(f"File ID: {result['file_id']}")
        print(f"File Name: {result['file_name']}")
        print(f"View Link: {result['web_view_link']}")
    except Exception as e:
        print(f"Upload failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
