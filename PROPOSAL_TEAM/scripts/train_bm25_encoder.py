#!/usr/bin/env python3
"""
Train BM25 Encoder on Compliance Document Corpus

This script loads all compliance document chunks and trains a BM25 encoder
for hybrid search (semantic + keyword matching).

The BM25 encoder learns vocabulary and IDF statistics from the corpus,
enabling effective keyword-based search alongside semantic search.

Run this ONCE after indexing documents to enable hybrid search.

Usage:
    python scripts/train_bm25_encoder.py

Output:
    - Saves trained BM25 encoder to: tools/bm25_encoder.pkl
    - Saves corpus to: outputs/bm25_corpus.pkl (for re-training if needed)
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
from pinecone_knowledge_base import PineconeKnowledgeBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_corpus_from_index():
    """
    Extract all document texts by re-processing PDFs

    Returns:
        List of document text chunks
    """
    logger.info("Extracting corpus from compliance PDFs...")

    # Load from indexing process
    from pdf_extractor import PDFExtractor
    from pinecone_knowledge_base import FrameworkAwareChunker

    # Get list of PDF files
    kb_dir = Path(__file__).parent.parent / "kb"
    pdf_files = list(kb_dir.glob("**/*.pdf"))

    if not pdf_files:
        raise ValueError(f"No PDF files found in {kb_dir}")

    logger.info(f"Found {len(pdf_files)} PDF files to process")

    # Initialize extractors
    extractor = PDFExtractor()
    chunker = FrameworkAwareChunker()
    corpus = []

    # Framework detection helper
    def detect_framework(filename: str) -> str:
        """Detect framework from filename"""
        filename_lower = filename.lower()

        if 'cmmc' in filename_lower:
            return 'cmmc'
        elif 'fedramp' in filename_lower:
            return 'fedramp'
        elif 'nist' in filename_lower and '800-171' in filename_lower:
            return 'nist_800_171'
        elif 'nist' in filename_lower and '800-53' in filename_lower:
            return 'nist_800_53'
        elif 'hipaa' in filename_lower:
            return 'hipaa'
        elif 'pci' in filename_lower or 'dss' in filename_lower:
            return 'pci_dss'
        elif 'gdpr' in filename_lower:
            return 'gdpr'
        elif 'glba' in filename_lower:
            return 'glba'
        elif 'dfars' in filename_lower:
            return 'dfars'
        else:
            return 'general'

    # Process each PDF
    for pdf_file in pdf_files:
        try:
            logger.info(f"Processing: {pdf_file.name}")

            # Extract text
            text, metadata = extractor.extract_from_pdf(str(pdf_file))

            if not text:
                logger.warning(f"No text extracted from {pdf_file.name}")
                continue

            # Detect framework
            framework_id = detect_framework(pdf_file.name)

            # Chunk document
            chunks = chunker.chunk_document(
                text=text,
                framework_id=framework_id,
                document_id=f"doc_{len(corpus)}",
                file_name=pdf_file.name
            )

            # Add chunk texts to corpus
            for chunk in chunks:
                if hasattr(chunk, 'chunk_text'):
                    corpus.append(chunk.chunk_text)
                elif hasattr(chunk, 'text'):
                    corpus.append(chunk.text)
                else:
                    # Fallback: chunk might be a dict or string
                    if isinstance(chunk, str):
                        corpus.append(chunk)

            logger.info(f"  Added {len(chunks)} chunks from {pdf_file.name}")

        except Exception as e:
            logger.error(f"Error processing {pdf_file.name}: {e}")
            import traceback
            traceback.print_exc()
            continue

    logger.info(f"Built corpus with {len(corpus):,} document chunks")

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
    print("🔧 TRAINING BM25 ENCODER FOR HYBRID SEARCH")
    print("=" * 80)
    print()
    print("This script will:")
    print("  1. Extract all document chunks from compliance PDFs")
    print("  2. Train BM25 encoder on the corpus")
    print("  3. Save encoder for use in hybrid search")
    print()

    try:
        # Create output directory
        output_dir = Path(__file__).parent.parent / "tools"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Extract corpus from index
        print("Step 1: Extracting corpus...")
        print("-" * 80)
        corpus = extract_corpus_from_index()
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
        print("  1. Run: python scripts/run_search_tests.py")
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
