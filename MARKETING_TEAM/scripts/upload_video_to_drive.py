"""
Upload AI video to Google Drive
"""

from tools.google_drive import get_drive_manager
import sys

try:
    print("Uploading video to Google Drive...")
    print()

    manager = get_drive_manager()

    file_path = "outputs/videos/ai_future_video.mp4"
    folder_type = "videos"
    description = "AI Future Video - 12 second Sora-2 generated video showcasing artificial intelligence transformation"

    drive_url = manager.upload_file(file_path, folder_type, description)

    print("=" * 70)
    print("[SUCCESS] Video uploaded to Google Drive!")
    print("=" * 70)
    print()
    print(f"Shareable Link: {drive_url}")
    print()
    print("Anyone with this link can view the video.")
    print()

except FileNotFoundError as e:
    print("[ERROR] credentials.json not found")
    print()
    print("To upload to Google Drive, you need:")
    print("1. Create a Google Cloud project")
    print("2. Enable Google Drive API")
    print("3. Download credentials.json")
    print("4. Place it in MARKETING_TEAM folder")
    print()
    print("See: MARKETING_TEAM/docs/getting-started/api-setup.md")
    print()

except Exception as e:
    print(f"[ERROR] Upload failed: {str(e)}")
    print()
