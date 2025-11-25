#!/usr/bin/env python3
"""
Re-index CMMC Documents with Correct framework_id
Fixes the CMMC framework filter issue by re-indexing with proper metadata
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone
import hashlib
from typing import List, Dict, Tuple

# Fix Windows encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)
tools_dir = str(Path(__file__).parent.parent / "tools")
sys.path.insert(0, tools_dir)

# Load environment variables
env_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(env_path)

# Import our tools directly
import importlib.util

# Import PDF extractor
pdf_spec = importlib.util.spec_from_file_location(
    "pdf_extractor",
    Path(__file__).parent.parent / "tools" / "pdf_extractor.py"
)
pdf_module = importlib.util.module_from_spec(pdf_spec)
pdf_spec.loader.exec_module(pdf_module)
PDFExtractor = pdf_module.PDFExtractor

# Import embeddings generator
emb_spec = importlib.util.spec_from_file_location(
    "embeddings_generator",
    Path(__file__).parent.parent / "tools" / "embeddings_generator.py"
)
emb_module = importlib.util.module_from_spec(emb_spec)
emb_spec.loader.exec_module(emb_module)
EmbeddingsGenerator = emb_module.EmbeddingsGenerator


def main():
    """Re-index CMMC documents with correct framework_id"""

    print("="*80)
    print("🔧 Fixing CMMC Framework ID in Pinecone")
    print("="*80)

    # Load manifest
    manifest_path = Path(__file__).parent.parent / "config" / "compliance_manifest.json"
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    # Filter CMMC documents
    cmmc_docs = [doc for doc in manifest['documents'] if doc['framework_id'] == 'cmmc']

    print(f"\n📋 Found {len(cmmc_docs)} CMMC documents to re-index:")
    for doc in cmmc_docs:
        print(f"  - {doc['file_name']}")

    # Initialize components
    print("\n🔄 Initializing components...")
    pdf_extractor = PDFExtractor()
    embeddings_gen = EmbeddingsGenerator()

    # Initialize Pinecone
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX", "rfp-knowledge-base")
    namespace = os.getenv("PINECONE_NAMESPACE", "compliance_frameworks")

    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)

    # Chunk configuration for CMMC
    chunk_size = 2000
    overlap = 300

    total_vectors = 0

    for i, doc_info in enumerate(cmmc_docs, 1):
        file_path = Path(doc_info['file_path'])

        if not file_path.exists():
            print(f"\n❌ [{i}/{len(cmmc_docs)}] File not found: {file_path.name}")
            continue

        print(f"\n{'='*80}")
        print(f"📄 [{i}/{len(cmmc_docs)}] Processing: {file_path.name}")
        print(f"{'='*80}")

        try:
            # Extract text
            print("📖 Extracting text...")
            text, page_boundaries, pdf_metadata = pdf_extractor.extract_pdf_text(str(file_path))
            print(f"  ✅ Extracted {pdf_metadata['num_pages']} pages, {len(text):,} characters")

            # Chunk document
            print(f"✂️  Chunking document (size: {chunk_size}, overlap: {overlap})...")
            chunks = embeddings_gen.chunk_text(text, chunk_size=chunk_size, overlap=overlap)
            print(f"  ✅ Created {len(chunks)} chunks")

            # Generate embeddings
            print("🧠 Generating embeddings...")
            chunk_texts = [chunk['text'] for chunk in chunks]
            embeddings = embeddings_gen.generate_embeddings(chunk_texts)
            print(f"  ✅ Generated {len(embeddings)} embeddings")

            # Prepare vectors with CORRECT framework_id
            print("📦 Preparing vectors with framework_id='cmmc'...")
            vectors = []

            doc_id = hashlib.md5(doc_info['file_name'].encode()).hexdigest()[:12]

            for chunk, embedding in zip(chunks, embeddings):
                chunk_id = hashlib.md5(
                    f"{doc_id}_chunk_{chunk['chunk_index']}".encode()
                ).hexdigest()

                vector_metadata = {
                    'doc_id': doc_id,
                    'framework_id': 'cmmc',  # FIXED: Now correctly set to 'cmmc'
                    'framework_name': 'CMMC 2.0',
                    'file_name': doc_info['file_name'],
                    'category': 'compliance',
                    'doc_type': 'framework_document',
                    'chunk_index': chunk['chunk_index'],
                    'char_count': chunk['char_count'],
                    'text': chunk['text'][:1000]
                }

                vectors.append((chunk_id, embedding, vector_metadata))

            print(f"  ✅ Prepared {len(vectors)} vectors")

            # Upload to Pinecone (will overwrite existing vectors with same IDs)
            print("📤 Uploading to Pinecone...")
            batch_size = 100
            total_batches = (len(vectors) + batch_size - 1) // batch_size

            for j in range(0, len(vectors), batch_size):
                batch = vectors[j:j + batch_size]
                batch_num = (j // batch_size) + 1

                try:
                    index.upsert(
                        vectors=batch,
                        namespace=namespace
                    )
                    print(f"  ✅ Batch {batch_num}/{total_batches} uploaded ({len(batch)} vectors)")
                except Exception as e:
                    print(f"  ❌ Error uploading batch {batch_num}: {str(e)}")

            total_vectors += len(vectors)
            print(f"✅ Successfully re-indexed {file_path.name}")

        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {str(e)}")
            continue

    # Verify results
    print(f"\n{'='*80}")
    print("✅ CMMC RE-INDEXING COMPLETE")
    print(f"{'='*80}")
    print(f"\n📊 Summary:")
    print(f"  Documents processed: {len(cmmc_docs)}")
    print(f"  Total vectors uploaded: {total_vectors:,}")

    # Get final cost
    cost_info = embeddings_gen.estimate_cost()
    print(f"\n💰 Cost:")
    print(f"  Tokens: {cost_info['total_tokens']:,}")
    print(f"  Cost: ${cost_info['actual_cost']}")

    # Verify index stats
    print(f"\n🔍 Verifying Pinecone index...")
    stats = index.describe_index_stats()
    namespace_stats = stats.get('namespaces', {}).get(namespace, {})
    print(f"  Total vectors in namespace: {namespace_stats.get('vector_count', 0):,}")

    print("\n✨ CMMC documents now have framework_id='cmmc' and will work with filters!")


if __name__ == "__main__":
    main()
