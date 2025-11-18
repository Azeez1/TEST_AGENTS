#!/usr/bin/env python3
"""
Script to upload compliance framework PDFs to Pinecone vector database.
This will index your 10 priority frameworks for RAG retrieval.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict
import hashlib

# Add the tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from tools.priority_frameworks import (
    PRIORITY_FRAMEWORKS,
    get_framework_summary
)

# Compliance documents folder
COMPLIANCE_FOLDER = Path(r"C:\Users\sabaa\OneDrive\Desktop\Compliance Frameworks")

def get_document_metadata(framework_id: str, pdf_file: str) -> Dict:
    """Create metadata for a compliance document."""
    fw = PRIORITY_FRAMEWORKS.get(framework_id)
    if not fw:
        return {}

    file_path = COMPLIANCE_FOLDER / pdf_file

    # Create a unique ID for this document
    doc_id = hashlib.md5(f"{framework_id}_{pdf_file}".encode()).hexdigest()[:12]

    metadata = {
        "doc_id": doc_id,
        "framework_id": framework_id,
        "framework_name": fw.name,
        "framework_short": fw.short_name,
        "document_name": pdf_file,
        "document_type": "compliance_framework",
        "category": "official_documentation",
        "file_path": str(file_path),
        "keywords": ", ".join(fw.keywords),
        "description": fw.description
    }

    # Add category information
    if framework_id in ["cmmc", "fedramp", "nist_800_171", "nist_800_53", "dfars"]:
        metadata["sector"] = "government"
    elif framework_id == "hipaa":
        metadata["sector"] = "healthcare"
    elif framework_id in ["pci_dss", "glba", "soc2"]:
        metadata["sector"] = "financial"
    elif framework_id == "gdpr":
        metadata["sector"] = "privacy"
    elif framework_id == "iso_27001":
        metadata["sector"] = "security"

    return metadata

def verify_documents():
    """Verify all priority framework documents exist."""
    print("=" * 80)
    print("VERIFYING COMPLIANCE DOCUMENTS")
    print("=" * 80)

    total_docs = 0
    missing_docs = []
    found_docs = []

    for fw_id, fw in PRIORITY_FRAMEWORKS.items():
        print(f"\n{fw.short_name} ({fw_id}):")
        print("-" * 40)

        if not fw.pdf_files:
            print("  [INFO] No PDF documents (proprietary framework)")
            continue

        for pdf_file in fw.pdf_files:
            file_path = COMPLIANCE_FOLDER / pdf_file
            total_docs += 1

            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"  ✓ {pdf_file} ({size_mb:.1f} MB)")
                found_docs.append((fw_id, pdf_file))
            else:
                print(f"  ✗ {pdf_file} - NOT FOUND")
                missing_docs.append((fw_id, pdf_file))

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total documents expected: {total_docs}")
    print(f"Documents found: {len(found_docs)}")
    print(f"Documents missing: {len(missing_docs)}")

    if missing_docs:
        print("\nMissing documents:")
        for fw_id, pdf_file in missing_docs:
            print(f"  - {PRIORITY_FRAMEWORKS[fw_id].short_name}: {pdf_file}")

    return found_docs

def prepare_upload_manifest(found_docs: List):
    """Prepare upload manifest for Pinecone."""
    print("\n" + "=" * 80)
    print("PREPARING UPLOAD MANIFEST")
    print("=" * 80)

    manifest = []

    for fw_id, pdf_file in found_docs:
        metadata = get_document_metadata(fw_id, pdf_file)
        manifest.append(metadata)
        print(f"\n{metadata['framework_short']}: {pdf_file}")
        print(f"  ID: {metadata['doc_id']}")
        print(f"  Sector: {metadata.get('sector', 'N/A')}")

    print(f"\nTotal documents to upload: {len(manifest)}")
    return manifest

def create_pinecone_config():
    """Create Pinecone configuration for upload."""
    config = {
        "api_key": "pcsk_YwCSZ_SSsaxk2HxiZM5uRsQ1uCV2KsoNsgGdPmdpNZ99aiZLSaewmCmVEthUi97uENvjH",
        "environment": "us-east-1",
        "index_name": "rfp-knowledge-base",
        "dimension": 1536,  # OpenAI embeddings dimension
        "metric": "cosine",
        "namespace": "compliance_frameworks"
    }

    print("\n" + "=" * 80)
    print("PINECONE CONFIGURATION")
    print("=" * 80)
    print(f"Index: {config['index_name']}")
    print(f"Namespace: {config['namespace']}")
    print(f"Dimension: {config['dimension']}")
    print(f"Metric: {config['metric']}")

    return config

def main():
    """Main execution."""
    print("\n" + "=" * 80)
    print("COMPLIANCE FRAMEWORK UPLOAD PREPARATION")
    print("=" * 80)

    # Show framework summary
    print("\n" + get_framework_summary())

    # Verify documents exist
    found_docs = verify_documents()

    if not found_docs:
        print("\n[ERROR] No documents found to upload!")
        return

    # Prepare upload manifest
    manifest = prepare_upload_manifest(found_docs)

    # Create Pinecone config
    config = create_pinecone_config()

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("""
To complete the upload to Pinecone:

1. Install required packages:
   pip install pinecone-client pypdf2 openai tiktoken

2. Run the actual upload script:
   python upload_to_pinecone_actual.py

3. The script will:
   - Extract text from PDFs
   - Create embeddings using OpenAI
   - Upload to Pinecone with metadata
   - Enable RAG retrieval for proposals

Your 10 priority frameworks will be fully indexed and searchable.
""")

    # Save manifest for next step
    import json
    with open('upload_manifest.json', 'w') as f:
        json.dump({
            "config": config,
            "documents": manifest
        }, f, indent=2)

    print(f"Manifest saved to: upload_manifest.json")

if __name__ == "__main__":
    main()