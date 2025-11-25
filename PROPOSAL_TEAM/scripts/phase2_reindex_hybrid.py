#!/usr/bin/env python3
"""
Phase 2: Re-index Pinecone with Hybrid Search Support

This script:
1. Deletes existing index (cosine metric)
2. Creates new index (dotproduct metric for hybrid search)
3. Triggers full re-indexing via index_compliance_frameworks.py

Then you can run run_hybrid_search_tests.py to test the improvement.

Usage:
    python scripts/phase2_reindex_hybrid.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import time

# Fix Windows encoding
import io
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
env_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(env_path)


def main():
    """Main execution"""

    print("=" * 80)
    print("🔄 PHASE 2: RE-INDEXING WITH HYBRID SEARCH SUPPORT")
    print("=" * 80)
    print()
    print("This script will:")
    print("  1. Delete existing index (cosine metric - no hybrid search)")
    print("  2. Create new index (dotproduct metric - hybrid search enabled)")
    print("  3. Tell you to run: python scripts/index_compliance_frameworks.py")
    print()
    print("⚠️  WARNING: This will delete all existing vectors!")
    print("   The index will be recreated with proper hybrid search support.")
    print()

    # Confirm
    response = input("Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Aborted by user")
        sys.exit(0)

    print()

    # Get configuration
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX", "rfp-knowledge-base")

    if not api_key:
        raise ValueError("PINECONE_API_KEY not found in environment")

    # Initialize Pinecone
    print("🔄 Initializing Pinecone client...")
    pc = Pinecone(api_key=api_key)

    # Step 1: Delete existing index
    print()
    print("Step 1: Deleting existing index...")
    print("-" * 80)

    existing_indexes = pc.list_indexes().names()

    if index_name in existing_indexes:
        print(f"⚠️  Found existing index: {index_name}")
        print("   Deleting to recreate with dotproduct metric...")

        pc.delete_index(index_name)

        # Wait for deletion
        while index_name in pc.list_indexes().names():
            print("   Waiting for deletion to complete...")
            time.sleep(2)

        print("✅ Index deleted successfully")
    else:
        print(f"ℹ️  Index '{index_name}' does not exist (nothing to delete)")

    print()

    # Step 2: Create new index with dotproduct metric
    print("Step 2: Creating new index with hybrid search support...")
    print("-" * 80)

    print(f"Creating index: {index_name}")
    print(f"  Dimension: 1024 (OpenAI text-embedding-3-large)")
    print(f"  Metric: dotproduct (✅ ENABLES HYBRID SEARCH)")
    print(f"  Cloud: AWS")
    print(f"  Region: us-east-1")

    pc.create_index(
        name=index_name,
        dimension=1024,
        metric="dotproduct",  # ✅ Enables sparse vectors (BM25)
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

    # Wait for index to be ready
    while not pc.describe_index(index_name).status['ready']:
        print("   Waiting for index to be ready...")
        time.sleep(2)

    print("✅ Index created successfully with dotproduct metric")
    print()

    # Success
    print("=" * 80)
    print("✅ INDEX RECREATION COMPLETE")
    print("=" * 80)
    print()
    print("Next Steps:")
    print()
    print("1. Run the indexing script to upload all documents:")
    print("   cd PROPOSAL_TEAM")
    print("   python scripts/index_compliance_frameworks.py")
    print()
    print("   This will index all compliance PDFs (~5-10 minutes)")
    print()
    print("2. After indexing completes, test hybrid search:")
    print("   python scripts/run_hybrid_search_tests.py")
    print()
    print("3. Expected results:")
    print("   • Average: 73-76% (+8-11% from baseline 65.33%)")
    print("   • HIPAA: 68-73%")
    print("   • GDPR: 66-70%")
    print("   • All frameworks >60%, most >70%")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
