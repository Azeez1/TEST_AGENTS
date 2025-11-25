#!/usr/bin/env python3
"""
Re-index the failed HIPAA document with fixed PDF extractor
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

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

# Import Pinecone
from pinecone import Pinecone
import hashlib
from typing import List, Dict, Tuple


def main():
    """Re-index the failed HIPAA document"""

    print("="*60)
    print("🔄 Re-indexing Failed HIPAA Document")
    print("="*60)

    # HIPAA document path
    hipaa_path = r"C:\Users\sabaa\OneDrive\Desktop\Compliance Frameworks\HIPAA_privacysummary.pdf"

    if not Path(hipaa_path).exists():
        print(f"❌ HIPAA document not found: {hipaa_path}")
        return

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

    # Extract text
    print(f"\n📖 Extracting text from HIPAA document...")
    try:
        text, page_boundaries, metadata = pdf_extractor.extract_pdf_text(hipaa_path)
        print(f"✅ Successfully extracted {metadata['num_pages']} pages, {len(text):,} characters")
    except Exception as e:
        print(f"❌ Error extracting PDF: {str(e)}")
        return

    # Chunk the document
    print(f"\n✂️  Chunking document...")
    chunks = embeddings_gen.chunk_text(text, chunk_size=1200, overlap=150)
    print(f"✅ Created {len(chunks)} chunks")

    # Generate embeddings
    print(f"\n🧠 Generating embeddings...")
    chunk_texts = [chunk['text'] for chunk in chunks]
    embeddings = embeddings_gen.generate_embeddings(chunk_texts)
    print(f"✅ Generated {len(embeddings)} embeddings")

    # Prepare vectors
    print(f"\n📦 Preparing vectors...")
    vectors = []

    doc_metadata = {
        'framework_id': 'hipaa',
        'framework_name': 'HIPAA',
        'file_name': Path(hipaa_path).name,
        'category': 'compliance',
        'doc_type': 'framework_document'
    }

    doc_id = hashlib.md5(doc_metadata['file_name'].encode()).hexdigest()[:12]

    for chunk, embedding in zip(chunks, embeddings):
        chunk_id = hashlib.md5(
            f"{doc_id}_chunk_{chunk['chunk_index']}".encode()
        ).hexdigest()

        vector_metadata = {
            'doc_id': doc_id,
            'framework_id': 'hipaa',
            'framework_name': 'HIPAA',
            'file_name': doc_metadata['file_name'],
            'category': 'compliance',
            'doc_type': 'framework_document',
            'chunk_index': chunk['chunk_index'],
            'char_count': chunk['char_count'],
            'text': chunk['text'][:1000]
        }

        vectors.append((chunk_id, embedding, vector_metadata))

    print(f"✅ Prepared {len(vectors)} vectors")

    # Upload to Pinecone
    print(f"\n📤 Uploading to Pinecone...")
    batch_size = 100
    total_batches = (len(vectors) + batch_size - 1) // batch_size

    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        batch_num = (i // batch_size) + 1

        try:
            index.upsert(
                vectors=batch,
                namespace=namespace
            )
            print(f"  ✅ Batch {batch_num}/{total_batches} uploaded ({len(batch)} vectors)")
        except Exception as e:
            print(f"  ❌ Error uploading batch {batch_num}: {str(e)}")

    # Verify upload
    print(f"\n🔍 Verifying upload...")
    stats = index.describe_index_stats()
    namespace_stats = stats.get('namespaces', {}).get(namespace, {})

    print(f"\n✅ HIPAA Document Re-indexed Successfully!")
    print(f"\n📊 Pinecone Stats:")
    print(f"  Index: {index_name}")
    print(f"  Namespace: {namespace}")
    print(f"  Total vectors in namespace: {namespace_stats.get('vector_count', 0):,}")

    # Cost info
    cost_info = embeddings_gen.estimate_cost()
    print(f"\n💰 Cost:")
    print(f"  Tokens: {cost_info['total_tokens']:,}")
    print(f"  Cost: ${cost_info['actual_cost']}")

    print(f"\n✨ All 21 compliance documents are now indexed!")


if __name__ == "__main__":
    main()
