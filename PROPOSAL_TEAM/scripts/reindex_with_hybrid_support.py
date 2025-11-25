#!/usr/bin/env python3
"""
Re-index Pinecone with Hybrid Search Support

This script recreates the Pinecone index with dotproduct metric to enable
hybrid search (BM25 + semantic).

Steps:
1. Delete existing index (if exists)
2. Create new index with metric="dotproduct"
3. Re-index all documents with dense + sparse vectors
4. Verify hybrid search works

Usage:
    python scripts/reindex_with_hybrid_support.py
"""

import os
import sys
import pickle
from pathlib import Path
from datetime import datetime
import logging

# Fix Windows encoding
import io
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)
tools_dir = str(Path(__file__).parent.parent / "tools")
sys.path.insert(0, tools_dir)

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(env_path)

# Imports
from pinecone import Pinecone, ServerlessSpec
from embeddings_generator import EmbeddingsGenerator
from pinecone_text.sparse import BM25Encoder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main execution"""

    print("=" * 80)
    print("🔄 RE-INDEXING PINECONE WITH HYBRID SEARCH SUPPORT")
    print("=" * 80)
    print()
    print("This script will:")
    print("  1. Delete existing index (cosine metric)")
    print("  2. Create new index (dotproduct metric)")
    print("  3. Re-index all 7,782 chunks with dense + sparse vectors")
    print("  4. Verify hybrid search functionality")
    print()

    # Get configuration
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX", "rfp-knowledge-base")
    namespace = os.getenv("PINECONE_NAMESPACE", "compliance_frameworks")

    if not api_key:
        raise ValueError("PINECONE_API_KEY not found in environment")

    # Initialize Pinecone
    pc = Pinecone(api_key=api_key)

    # Step 1: Delete existing index
    print("Step 1: Deleting existing index...")
    print("-" * 80)

    existing_indexes = pc.list_indexes().names()

    if index_name in existing_indexes:
        print(f"⚠️  Found existing index: {index_name}")
        print("   Deleting to recreate with dotproduct metric...")

        pc.delete_index(index_name)

        # Wait for deletion
        import time
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
    print(f"  Metric: dotproduct (REQUIRED for hybrid search)")
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
    import time
    while not pc.describe_index(index_name).status['ready']:
        print("   Waiting for index to be ready...")
        time.sleep(2)

    print("✅ Index created successfully with dotproduct metric")
    print()

    # Step 3: Re-index all documents
    print("Step 3: Re-indexing all documents with hybrid vectors...")
    print("-" * 80)

    # Load BM25 encoder
    encoder_path = Path(__file__).parent.parent / "tools" / "bm25_encoder.pkl"

    if not encoder_path.exists():
        raise FileNotFoundError(
            f"BM25 encoder not found at {encoder_path}. "
            "Run: python scripts/train_bm25_from_pinecone.py first"
        )

    print(f"📂 Loading BM25 encoder from: {encoder_path}")
    with open(encoder_path, 'rb') as f:
        bm25_encoder = pickle.load(f)

    print("✅ BM25 encoder loaded")

    # Load corpus
    corpus_path = Path(__file__).parent.parent / "tools" / "bm25_corpus.pkl"

    if not corpus_path.exists():
        raise FileNotFoundError(
            f"Corpus not found at {corpus_path}. "
            "Run: python scripts/train_bm25_from_pinecone.py first"
        )

    print(f"📂 Loading corpus from: {corpus_path}")
    with open(corpus_path, 'rb') as f:
        corpus = pickle.load(f)

    print(f"✅ Corpus loaded: {len(corpus):,} chunks")

    # Initialize embeddings generator
    print("🔄 Initializing embeddings generator...")
    embeddings_gen = EmbeddingsGenerator()

    # Get index
    index = pc.Index(index_name)

    # Re-index with hybrid vectors
    print(f"\n🔄 Re-indexing {len(corpus):,} chunks...")
    print("   This will take ~5-10 minutes...")
    print()

    batch_size = 100
    total_batches = (len(corpus) + batch_size - 1) // batch_size

    for batch_idx in range(0, len(corpus), batch_size):
        batch_texts = corpus[batch_idx:batch_idx + batch_size]
        batch_num = (batch_idx // batch_size) + 1

        print(f"Processing batch {batch_num}/{total_batches} ({len(batch_texts)} chunks)...")

        # Generate dense embeddings
        dense_embeddings = embeddings_gen.generate_embeddings(batch_texts)

        # Generate sparse vectors
        vectors_to_upsert = []

        for i, text in enumerate(batch_texts):
            vector_id = f"chunk_{batch_idx + i}"

            # Dense vector
            dense_vector = dense_embeddings[i]

            # Sparse vector (BM25)
            sparse_vector = bm25_encoder.encode_documents(text)

            # Create vector with both dense and sparse
            vectors_to_upsert.append({
                "id": vector_id,
                "values": dense_vector,
                "sparse_values": sparse_vector,
                "metadata": {
                    "text": text[:1000],  # Store preview for testing
                    "chunk_number": batch_idx + i,
                    "framework_id": "unknown"  # Will be updated with actual metadata
                }
            })

        # Upsert batch
        index.upsert(
            vectors=vectors_to_upsert,
            namespace=namespace
        )

        if batch_num % 10 == 0:
            print(f"   Progress: {batch_num}/{total_batches} batches ({batch_num * batch_size:,} chunks)")

    print()
    print(f"✅ Re-indexing complete: {len(corpus):,} chunks indexed")
    print()

    # Step 4: Verify hybrid search
    print("Step 4: Verifying hybrid search functionality...")
    print("-" * 80)

    # Test query
    test_query = "HIPAA patient data encryption requirements"

    print(f"Test query: {test_query}")
    print()

    # Generate query vectors
    query_dense = embeddings_gen.generate_single_embedding(test_query)
    query_sparse = bm25_encoder.encode_queries(test_query)

    # Try hybrid search
    try:
        results = index.query(
            vector=query_dense,
            sparse_vector=query_sparse,
            top_k=3,
            namespace=namespace,
            include_metadata=True
        )

        matches = results.get('matches', [])

        if matches:
            print("✅ HYBRID SEARCH WORKING!")
            print(f"   Found {len(matches)} results")
            print()

            for i, match in enumerate(matches, 1):
                print(f"Result {i}:")
                print(f"  Score: {match.score:.4f}")
                print(f"  Text preview: {match.metadata.get('text', '')[:100]}...")
                print()
        else:
            print("⚠️  Hybrid search executed but returned no results")
            print("   This may be normal if corpus doesn't contain relevant content")

    except Exception as e:
        print(f"❌ Hybrid search failed: {e}")
        raise

    # Success summary
    print("=" * 80)
    print("✅ RE-INDEXING COMPLETE - HYBRID SEARCH ENABLED")
    print("=" * 80)
    print()
    print("Index Configuration:")
    print(f"  • Name: {index_name}")
    print(f"  • Metric: dotproduct (hybrid search supported)")
    print(f"  • Dimension: 1024")
    print(f"  • Namespace: {namespace}")
    print(f"  • Total vectors: {len(corpus):,}")
    print()
    print("Next Steps:")
    print("  1. Run: python scripts/run_hybrid_search_tests.py")
    print("  2. Verify 70%+ average similarity achieved")
    print("  3. Expected: 73-76% average (HIPAA: 68-73%, GDPR: 66-70%)")
    print()
    print("⚠️  NOTE: Framework metadata (framework_id, file_name, etc.) needs to be")
    print("   updated separately. Current index has placeholder metadata.")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Re-indexing failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
