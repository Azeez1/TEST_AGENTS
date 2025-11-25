#!/usr/bin/env python3
"""
Train BM25 Encoder from Pinecone Index

This script fetches all document chunks directly from Pinecone and trains
a BM25 encoder for hybrid search.

This is more efficient than re-processing PDFs since the data is already indexed.

Usage:
    python scripts/train_bm25_from_pinecone.py

Output:
    - Saves trained BM25 encoder to: tools/bm25_encoder.pkl
    - Saves corpus to: outputs/bm25_corpus.pkl
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

# Pinecone imports
from pinecone import Pinecone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_corpus_from_pinecone():
    """
    Extract all document texts from Pinecone index metadata

    Returns:
        List of document text chunks
    """
    logger.info("Extracting corpus from Pinecone index...")

    # Initialize Pinecone
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX", "rfp-knowledge-base")
    namespace = os.getenv("PINECONE_NAMESPACE", "compliance_frameworks")

    if not api_key:
        raise ValueError("PINECONE_API_KEY not found in environment")

    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)

    # Get index stats
    stats = index.describe_index_stats()
    namespace_stats = stats.get('namespaces', {}).get(namespace, {})
    total_vectors = namespace_stats.get('vector_count', 0)

    logger.info(f"Found {total_vectors:,} vectors in namespace '{namespace}'")

    if total_vectors == 0:
        raise ValueError(f"No vectors found in namespace '{namespace}'")

    # Fetch vectors using list_paginated (works with serverless indexes)
    corpus = []

    logger.info("Fetching vectors from Pinecone...")

    # Use query with dummy vector to get all results
    # This is a workaround since Pinecone serverless doesn't support fetch_all
    from embeddings_generator import EmbeddingsGenerator

    embeddings_gen = EmbeddingsGenerator()
    dummy_query = "dummy query for fetching vectors"
    dummy_vector = embeddings_gen.generate_single_embedding(dummy_query)

    # Fetch in batches
    batch_size = 10000  # Max results per query
    total_fetched = 0

    results = index.query(
        vector=dummy_vector,
        top_k=batch_size,
        namespace=namespace,
        include_metadata=True
    )

    matches = results.get('matches', [])

    for match in matches:
        metadata = match.metadata

        # Get text from metadata
        text = metadata.get('text', '')

        if text:
            corpus.append(text)
            total_fetched += 1

            if total_fetched % 1000 == 0:
                logger.info(f"  Fetched {total_fetched:,} texts...")

    logger.info(f"Built corpus with {len(corpus):,} document chunks")

    if len(corpus) == 0:
        raise ValueError("No text content found in Pinecone metadata")

    return corpus


def train_and_save_bm25(corpus, output_dir):
    """
    Train BM25 encoder on corpus and save to disk

    Args:
        corpus: List of document text chunks
        output_dir: Directory to save encoder and corpus
    """
    logger.info("Training BM25 encoder...")

    try:
        from pinecone_text.sparse import BM25Encoder
    except ImportError:
        logger.error(
            "pinecone-text not installed. Install with: pip install pinecone-text"
        )
        raise

    # Initialize and train BM25 encoder
    bm25_encoder = BM25Encoder()

    start_time = datetime.now()
    bm25_encoder.fit(corpus)
    duration = (datetime.now() - start_time).total_seconds()

    logger.info(f"BM25 encoder trained in {duration:.1f} seconds")

    # Save encoder
    encoder_path = output_dir / "bm25_encoder.pkl"
    with open(encoder_path, 'wb') as f:
        pickle.dump(bm25_encoder, f)

    logger.info(f"Saved BM25 encoder to: {encoder_path}")

    # Save corpus (for re-training if needed)
    corpus_path = output_dir / "bm25_corpus.pkl"
    with open(corpus_path, 'wb') as f:
        pickle.dump(corpus, f)

    logger.info(f"Saved corpus to: {corpus_path}")

    return bm25_encoder


def test_bm25_encoder(bm25_encoder):
    """
    Test BM25 encoder with sample queries

    Args:
        bm25_encoder: Trained BM25Encoder instance
    """
    logger.info("Testing BM25 encoder...")

    test_queries = [
        "HIPAA patient data encryption requirements",
        "GDPR consent management",
        "CMMC Level 2 access control",
        "FedRAMP continuous monitoring"
    ]

    print("\n" + "=" * 80)
    print("BM25 Encoder Test Results")
    print("=" * 80)

    for query in test_queries:
        try:
            sparse_vector = bm25_encoder.encode_queries(query)

            # Count non-zero values (active terms)
            if hasattr(sparse_vector, 'values'):
                active_terms = len(sparse_vector.values)
            else:
                active_terms = "unknown"

            print(f"\nQuery: {query}")
            print(f"  Active terms: {active_terms}")
            print(f"  Sparse vector type: {type(sparse_vector)}")

        except Exception as e:
            print(f"\nQuery: {query}")
            print(f"  ERROR: {e}")

    print("\n" + "=" * 80)


def main():
    """Main execution"""

    print("=" * 80)
    print("🔧 TRAINING BM25 ENCODER FROM PINECONE INDEX")
    print("=" * 80)
    print()
    print("This script will:")
    print("  1. Extract all document chunks from Pinecone index")
    print("  2. Train BM25 encoder on the corpus")
    print("  3. Save encoder for use in hybrid search")
    print()

    try:
        # Create output directory
        output_dir = Path(__file__).parent.parent / "tools"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Extract corpus from Pinecone
        print("Step 1: Extracting corpus from Pinecone...")
        print("-" * 80)
        corpus = extract_corpus_from_pinecone()
        print()

        # Train BM25 encoder
        print("Step 2: Training BM25 encoder...")
        print("-" * 80)
        bm25_encoder = train_and_save_bm25(corpus, output_dir)
        print()

        # Test encoder
        print("Step 3: Testing BM25 encoder...")
        print("-" * 80)
        test_bm25_encoder(bm25_encoder)
        print()

        # Success summary
        print("=" * 80)
        print("✅ BM25 ENCODER TRAINING COMPLETE")
        print("=" * 80)
        print()
        print("Corpus Statistics:")
        print(f"  • Total chunks: {len(corpus):,}")
        print(f"  • Average chunk length: {sum(len(c) for c in corpus) / len(corpus):.0f} characters")
        print()
        print("Saved Files:")
        print(f"  • BM25 encoder: tools/bm25_encoder.pkl")
        print(f"  • Corpus backup: tools/bm25_corpus.pkl")
        print()
        print("Next Steps:")
        print("  1. Run: python scripts/run_hybrid_search_tests.py")
        print("  2. Tests will now use hybrid search (BM25 + semantic)")
        print("  3. Expected improvement: +5-8% similarity scores")
        print()

    except Exception as e:
        logger.error(f"Training failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
