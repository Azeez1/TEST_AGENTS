"""
Swap broken diagnosis PDFs in Drive with fixed versions.

For each of the 10 fixed PDFs:
  1. Upload the new local PDF to the diagnoses Drive folder
  2. Move the old Drive file (by ID) to trash (recoverable for 30 days)
  3. Record the new file ID

Reads mapping from tmp/pdf_swap_mapping.json (stem -> {row, firm, old_file_id}).
Writes results to tmp/pdf_swap_results.json (stem -> {row, new_file_id, old_file_id}).
"""
import json
import sys
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = REPO_ROOT / "MARKETING_TEAM" / "outputs" / "reports"
MAPPING_PATH = REPO_ROOT / "tmp" / "pdf_swap_mapping.json"
RESULTS_PATH = REPO_ROOT / "tmp" / "pdf_swap_results.json"
DRIVE_FOLDER_ID = "1QkAUOP9v4u3DugZjVcYUnaiT7pitN3sv"

# upload_to_drive's get_drive_service() looks for credentials.json + token.pickle
# in the CWD. Switch to MARKETING_TEAM so it finds them.
os.chdir(REPO_ROOT / "MARKETING_TEAM")
sys.path.insert(0, str(REPO_ROOT / "MARKETING_TEAM" / "tools"))
from upload_to_drive import upload_to_drive, get_drive_service


def trash_drive_file(service, file_id: str) -> bool:
    """Move file to Drive trash (soft-delete, recoverable for 30 days)."""
    try:
        service.files().update(fileId=file_id, body={"trashed": True}).execute()
        return True
    except Exception as e:
        print(f"    trash failed for {file_id}: {e}")
        return False


def main():
    with open(MAPPING_PATH, encoding="utf-8") as f:
        mapping = json.load(f)

    service = get_drive_service()
    results = {}

    for stem, info in mapping.items():
        pdf_path = REPORTS_DIR / f"{stem}_diagnosis.pdf"
        if not pdf_path.exists():
            print(f"[{stem}] SKIP — PDF not found")
            continue

        print(f"\n[{stem}] row={info['row']}")
        print(f"  Uploading {pdf_path.name} ({pdf_path.stat().st_size // 1024} KB)...")
        try:
            new = upload_to_drive(
                file_path=str(pdf_path),
                file_name=pdf_path.name,
                folder_id=DRIVE_FOLDER_ID,
            )
            new_id = new["file_id"]
            print(f"  Uploaded -> new file_id: {new_id}")
        except Exception as e:
            print(f"  UPLOAD FAILED: {e}")
            results[stem] = {"row": info["row"], "error": str(e)}
            continue

        old_id = info.get("old_file_id", "")
        if old_id and old_id != new_id:
            print(f"  Trashing old file_id: {old_id}")
            trashed = trash_drive_file(service, old_id)
            print(f"  {'Old file trashed' if trashed else 'Trash failed (left in place)'}")
        else:
            trashed = False

        results[stem] = {
            "row": info["row"],
            "firm": info["firm"],
            "new_file_id": new_id,
            "old_file_id": old_id,
            "old_trashed": trashed,
        }

    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n{'=' * 70}")
    print(f"Results saved to {RESULTS_PATH}")
    print(f"{sum(1 for r in results.values() if 'new_file_id' in r)}/{len(mapping)} uploads succeeded")


if __name__ == "__main__":
    main()
