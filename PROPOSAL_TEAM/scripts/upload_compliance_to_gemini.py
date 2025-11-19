#!/usr/bin/env python3
"""
Script to upload compliance framework PDFs to Gemini File Search (backup RAG system).

This script provides a backup/alternative to Pinecone by uploading documents to
Google's fully managed RAG system. Gemini handles chunking, embedding, and indexing
automatically.

Usage:
    python scripts/upload_compliance_to_gemini.py [--verify-only] [--framework FRAMEWORK_ID]
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.legacy.gemini_file_search import GeminiFileSearch, GEMINI_AVAILABLE
from tools.legacy.config import config

# Compliance documents folder
COMPLIANCE_FOLDER = Path(r"C:\Users\sabaa\OneDrive\Desktop\Compliance Frameworks")

# Alternative paths to check (cross-platform)
ALT_PATHS = [
    Path(__file__).parent.parent / "kb" / "compliance",
    Path.home() / "Documents" / "Compliance Frameworks",
    Path("/home/user/TEST_AGENTS/PROPOSAL_TEAM/kb/compliance"),
]

# Framework document mappings
FRAMEWORK_DOCUMENTS = {
    "cmmc": {
        "name": "CMMC (Cybersecurity Maturity Model Certification)",
        "files": [
            "CMMC_32 CFR 170 (CMMC Program Rule).pdf",
            "CMMC_AssessmentGuideL1v2.pdf",
            "CMMC_AssessmentGuideL2v2.pdf",
            "CMMC_ModelOverview.pdf",
            "CMMC_ScopingGuideL1v2.pdf",
            "CMMC_ScopingGuideL2v2.pdf",
        ],
        "sector": "government",
        "keywords": ["DoD", "defense", "cybersecurity", "maturity"],
    },
    "fedramp": {
        "name": "FedRAMP (Federal Risk and Authorization Management Program)",
        "files": [
            "FEDRAMP_Agency_Authorization_Playbook.pdf",
            "FEDRAMP_CSP_Authorization_Playbook.pdf",
            "FEDRAMP_CSP_Continuous_Monitoring_Performance_Management_Guide.pdf",
        ],
        "sector": "government",
        "keywords": ["cloud", "federal", "authorization", "security"],
    },
    "nist_800_171": {
        "name": "NIST SP 800-171 (Protecting CUI)",
        "files": [
            "NIST.SP.800-171r3.pdf",
            "NIST.SP.800-171Ar3.pdf",
        ],
        "sector": "government",
        "keywords": ["CUI", "controlled information", "NIST", "security"],
    },
    "nist_800_53": {
        "name": "NIST SP 800-53 (Security and Privacy Controls)",
        "files": [
            "NIST.SP.800-53r5.pdf",
            "NIST.SP.800-53Ar5.pdf",
            "NIST.SP.800-53B.pdf",
        ],
        "sector": "government",
        "keywords": ["security controls", "privacy", "NIST", "RMF"],
    },
    "hipaa": {
        "name": "HIPAA (Health Insurance Portability and Accountability Act)",
        "files": [
            "HIPAA_privacysummary.pdf",
            "HIPAA_security101.pdf",
        ],
        "sector": "healthcare",
        "keywords": ["healthcare", "PHI", "privacy", "medical"],
    },
    "pci_dss": {
        "name": "PCI DSS (Payment Card Industry Data Security Standard)",
        "files": [
            "PCI-DSS-v4_0_1.pdf",
        ],
        "sector": "financial",
        "keywords": ["payment", "credit card", "PCI", "financial"],
    },
    "gdpr": {
        "name": "GDPR (General Data Protection Regulation)",
        "files": [
            "GDPR_CELEX_32016R0679_EN_TXT.pdf",
        ],
        "sector": "privacy",
        "keywords": ["privacy", "EU", "data protection", "GDPR"],
    },
    "glba": {
        "name": "GLBA (Gramm-Leach-Bliley Act)",
        "files": [
            "GLBA_16 CFR Part 314.pdf",
            "GLBA_Privacy_viii-1.1.pdf",
        ],
        "sector": "financial",
        "keywords": ["financial", "privacy", "banking", "security"],
    },
    "dfars": {
        "name": "DFARS (Defense Federal Acquisition Regulation Supplement)",
        "files": [
            "CMMC_DFARS 2019-D041 (Cybersecurity Requirements).pdf",
        ],
        "sector": "government",
        "keywords": ["DoD", "acquisition", "cybersecurity", "defense"],
    },
}


def find_compliance_folder() -> Optional[Path]:
    """Find the compliance documents folder."""
    # Check primary path
    if COMPLIANCE_FOLDER.exists():
        return COMPLIANCE_FOLDER

    # Check alternative paths
    for path in ALT_PATHS:
        if path.exists():
            return path

    return None


def get_file_metadata(framework_id: str, file_name: str) -> Dict:
    """Generate metadata for a compliance document."""
    framework = FRAMEWORK_DOCUMENTS[framework_id]

    return {
        "framework_id": framework_id,
        "framework_name": framework["name"],
        "document_name": file_name,
        "document_type": "compliance_framework",
        "sector": framework["sector"],
        "category": "official_documentation",
        "keywords": ", ".join(framework["keywords"]),
    }


def verify_documents(compliance_folder: Path) -> tuple[List, List]:
    """
    Verify which documents exist and which are missing.

    Returns:
        (found_files, missing_files) tuple
    """
    print("=" * 80)
    print("VERIFYING COMPLIANCE DOCUMENTS")
    print("=" * 80)
    print(f"Compliance folder: {compliance_folder}")
    print()

    found_files = []
    missing_files = []

    for fw_id, fw_data in FRAMEWORK_DOCUMENTS.items():
        print(f"\n{fw_data['name']} ({fw_id}):")
        print("-" * 60)

        for file_name in fw_data["files"]:
            file_path = compliance_folder / file_name

            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"  ✓ {file_name} ({size_mb:.1f} MB)")
                found_files.append((fw_id, file_path))
            else:
                print(f"  ✗ {file_name} - NOT FOUND")
                missing_files.append((fw_id, file_name))

    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    total = len(found_files) + len(missing_files)
    print(f"Total documents expected: {total}")
    print(f"Documents found:          {len(found_files)}")
    print(f"Documents missing:        {len(missing_files)}")

    if missing_files:
        print("\n⚠️  Missing documents:")
        for fw_id, file_name in missing_files:
            print(f"   - {fw_id}: {file_name}")

    return found_files, missing_files


def upload_to_gemini(
    found_files: List,
    framework_filter: Optional[str] = None,
    dry_run: bool = False,
):
    """
    Upload documents to Gemini File Search.

    Args:
        found_files: List of (framework_id, file_path) tuples
        framework_filter: Optional framework ID to upload only that framework
        dry_run: If True, only show what would be uploaded
    """
    if not GEMINI_AVAILABLE:
        print("\n❌ ERROR: Gemini API not available")
        print("Install with: pip install google-genai")
        return

    if not config.gemini.api_key:
        print("\n❌ ERROR: GEMINI_API_KEY not set")
        print("Set your API key in .env file")
        print("Get your key from: https://aistudio.google.com/app/apikey")
        return

    # Filter by framework if specified
    if framework_filter:
        found_files = [
            (fw_id, path)
            for fw_id, path in found_files
            if fw_id == framework_filter
        ]

        if not found_files:
            print(f"\n❌ No files found for framework: {framework_filter}")
            return

    print("\n" + "=" * 80)
    print("UPLOADING TO GEMINI FILE SEARCH")
    print("=" * 80)
    print(f"Files to upload: {len(found_files)}")

    if dry_run:
        print("\n🔍 DRY RUN - No files will be uploaded")
        for fw_id, file_path in found_files:
            metadata = get_file_metadata(fw_id, file_path.name)
            print(f"\nWould upload: {file_path.name}")
            print(f"  Framework: {metadata['framework_name']}")
            print(f"  Sector: {metadata['sector']}")
        return

    # Initialize Gemini client
    try:
        print("\n🔗 Connecting to Gemini File Search...")
        gemini = GeminiFileSearch()

        # Get or create file search store
        store_name = gemini.get_or_create_store()
        print(f"✓ Using store: {store_name}")

    except Exception as e:
        print(f"\n❌ Failed to initialize Gemini: {e}")
        return

    # Upload files
    uploaded_count = 0
    failed_count = 0

    for fw_id, file_path in found_files:
        metadata = get_file_metadata(fw_id, file_path.name)

        print(f"\n📤 Uploading: {file_path.name}")
        print(f"   Framework: {metadata['framework_name']}")
        print(f"   Sector: {metadata['sector']}")

        try:
            file_name = gemini.upload_file(file_path, metadata)
            print(f"   ✓ Uploaded: {file_name}")
            uploaded_count += 1

        except Exception as e:
            print(f"   ✗ Failed: {e}")
            failed_count += 1

    # Final summary
    print("\n" + "=" * 80)
    print("UPLOAD SUMMARY")
    print("=" * 80)
    print(f"Total files processed: {len(found_files)}")
    print(f"Successfully uploaded: {uploaded_count}")
    print(f"Failed:                {failed_count}")

    # Show store statistics
    try:
        stats = gemini.get_store_stats()
        print("\n📊 Store Statistics:")
        print(f"   Store name:   {stats['display_name']}")
        print(f"   Total files:  {stats['total_files']}")
        print(f"   Model:        {stats['model']}")
    except Exception as e:
        print(f"\n⚠️  Could not get store stats: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Upload compliance documents to Gemini File Search"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify documents, don't upload",
    )
    parser.add_argument(
        "--framework",
        type=str,
        help="Upload only this framework (e.g., 'cmmc', 'fedramp')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be uploaded without uploading",
    )
    parser.add_argument(
        "--list-frameworks",
        action="store_true",
        help="List available frameworks and exit",
    )

    args = parser.parse_args()

    # List frameworks
    if args.list_frameworks:
        print("Available frameworks:")
        for fw_id, fw_data in FRAMEWORK_DOCUMENTS.items():
            print(f"  {fw_id:15s} - {fw_data['name']}")
        return

    # Find compliance folder
    compliance_folder = find_compliance_folder()
    if not compliance_folder:
        print("❌ ERROR: Compliance documents folder not found")
        print("\nSearched paths:")
        print(f"  - {COMPLIANCE_FOLDER}")
        for path in ALT_PATHS:
            print(f"  - {path}")
        print("\nPlease update COMPLIANCE_FOLDER in the script or place documents in one of the above paths.")
        sys.exit(1)

    # Verify documents
    found_files, missing_files = verify_documents(compliance_folder)

    if not found_files:
        print("\n❌ No documents found to upload")
        sys.exit(1)

    # Upload if not verify-only
    if not args.verify_only:
        upload_to_gemini(
            found_files,
            framework_filter=args.framework,
            dry_run=args.dry_run,
        )
    else:
        print("\n✓ Verification complete (use without --verify-only to upload)")


if __name__ == "__main__":
    main()
