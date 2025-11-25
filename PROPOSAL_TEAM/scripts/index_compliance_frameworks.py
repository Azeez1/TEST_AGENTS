#!/usr/bin/env python3
"""
Index Compliance Framework Documents to Pinecone
Processes 21 compliance PDFs and uploads to vector database with framework-aware chunking
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple
from dotenv import load_dotenv
from pinecone import Pinecone
import time
from datetime import datetime
import hashlib

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


class ComplianceIndexer:
    """Index compliance documents to Pinecone with intelligent chunking"""

    def __init__(self):
        """Initialize indexer with Pinecone and OpenAI"""
        # Get configuration
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX", "rfp-knowledge-base")
        self.namespace = os.getenv("PINECONE_NAMESPACE", "compliance_frameworks")

        # Initialize clients
        print("🔄 Initializing Pinecone client...")
        self.pc = Pinecone(api_key=self.api_key)
        self.index = self.pc.Index(self.index_name)

        print("🔄 Initializing embeddings generator...")
        self.embeddings_gen = EmbeddingsGenerator()

        print("🔄 Initializing PDF extractor...")
        self.pdf_extractor = PDFExtractor()

        # Load BM25 encoder for hybrid search
        print("🔄 Loading BM25 encoder for hybrid search...")
        encoder_path = Path(__file__).parent.parent / "tools" / "bm25_encoder.pkl"
        if encoder_path.exists():
            import pickle
            with open(encoder_path, 'rb') as f:
                self.bm25_encoder = pickle.load(f)
            print("✅ BM25 encoder loaded - hybrid search enabled")
        else:
            self.bm25_encoder = None
            print("⚠️  BM25 encoder not found - semantic-only indexing")

        # Framework-specific chunk sizes (OPTIMIZED v2 - Better overlap & HIPAA/GDPR fixes)
        self.chunk_config = {
            'cmmc': {'size': 2000, 'overlap': 500},           # Increased overlap: 300 → 500
            'fedramp': {'size': 1800, 'overlap': 450},        # Increased overlap: 250 → 450
            'nist_800_171': {'size': 1500, 'overlap': 400},   # Increased overlap: 200 → 400
            'nist_800_53': {'size': 1500, 'overlap': 400},    # Increased overlap: 200 → 400
            'hipaa': {'size': 1800, 'overlap': 450},          # Increased size: 1200 → 1800, overlap: 150 → 450
            'pci_dss': {'size': 1500, 'overlap': 400},        # Increased overlap: 200 → 400
            'gdpr': {'size': 1800, 'overlap': 450},           # Increased size: 1000 → 1800, overlap: 150 → 450
            'glba': {'size': 1500, 'overlap': 400},           # Increased size: 1200 → 1500, overlap: 150 → 400
            'dfars': {'size': 1500, 'overlap': 400},          # Increased overlap: 200 → 400
            'default': {'size': 1500, 'overlap': 400}         # Increased overlap: 200 → 400
        }

        # Track progress
        self.stats = {
            'total_docs': 0,
            'total_chunks': 0,
            'total_tokens': 0,
            'total_vectors': 0,
            'errors': []
        }

    def load_compliance_manifest(self) -> Dict:
        """Load the compliance document manifest"""
        manifest_path = Path(__file__).parent.parent / "config" / "compliance_manifest.json"

        if not manifest_path.exists():
            raise FileNotFoundError(f"Compliance manifest not found: {manifest_path}")

        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        print(f"📋 Loaded manifest: {len(manifest.get('documents', []))} documents")
        return manifest

    def get_framework_id(self, doc_metadata: Dict) -> str:
        """Extract framework ID from document metadata"""
        # First try to get framework_id directly from manifest
        if 'framework_id' in doc_metadata:
            return doc_metadata['framework_id']

        # Fallback: map framework name to ID
        framework_map = {
            'CMMC 2.0': 'cmmc',
            'CMMC': 'cmmc',
            'FedRAMP': 'fedramp',
            'NIST 800-171': 'nist_800_171',
            'NIST 800-53': 'nist_800_53',
            'HIPAA': 'hipaa',
            'PCI-DSS': 'pci_dss',
            'GDPR': 'gdpr',
            'GLBA': 'glba',
            'DFARS': 'dfars'
        }

        framework_name = doc_metadata.get('framework_name', '')
        return framework_map.get(framework_name, 'unknown')

    def chunk_document(
        self,
        text: str,
        framework_id: str,
        metadata: Dict
    ) -> List[Dict]:
        """Chunk document with framework-specific settings"""

        # Get chunk configuration for this framework
        config = self.chunk_config.get(framework_id, self.chunk_config['default'])

        # Use embeddings generator's chunking method
        chunks = self.embeddings_gen.chunk_text(
            text,
            chunk_size=config['size'],
            overlap=config['overlap']
        )

        # Enhance chunks with metadata
        for chunk in chunks:
            chunk['framework_id'] = framework_id
            chunk['framework_name'] = metadata.get('framework_name', '')
            chunk['doc_id'] = metadata.get('doc_id', '')
            chunk['file_name'] = metadata.get('file_name', '')
            chunk['category'] = metadata.get('category', '')

        return chunks

    def prepare_vectors(
        self,
        chunks: List[Dict],
        embeddings: List[List[float]],
        doc_metadata: Dict
    ) -> List[Dict]:
        """Prepare vectors for Pinecone upload with hybrid search support"""

        vectors = []

        for chunk, embedding in zip(chunks, embeddings):
            # Generate unique ID for this chunk using file name and chunk index
            doc_id = doc_metadata.get('doc_id') or hashlib.md5(
                doc_metadata.get('file_name', 'unknown').encode()
            ).hexdigest()[:12]

            chunk_id = hashlib.md5(
                f"{doc_id}_chunk_{chunk['chunk_index']}".encode()
            ).hexdigest()

            # Prepare metadata (Pinecone has metadata size limits)
            vector_metadata = {
                'doc_id': doc_id,
                'framework_id': chunk.get('framework_id', ''),
                'framework_name': chunk.get('framework_name', ''),
                'file_name': chunk.get('file_name', ''),
                'category': doc_metadata.get('category', 'compliance'),
                'doc_type': doc_metadata.get('doc_type', 'framework_document'),
                'chunk_index': chunk['chunk_index'],
                'char_count': chunk['char_count'],
                'chunk_size': chunk.get('char_count', 0),  # For compatibility
                'chunk_number': chunk['chunk_index'],  # For compatibility
                'text': chunk['text'][:1000]  # Truncate text to 1000 chars for metadata
            }

            # Build vector dict
            vector_dict = {
                'id': chunk_id,
                'values': embedding,
                'metadata': vector_metadata
            }

            # Add sparse vector if BM25 encoder available
            if self.bm25_encoder:
                try:
                    sparse_vector = self.bm25_encoder.encode_documents(chunk['text'])
                    vector_dict['sparse_values'] = sparse_vector
                except Exception as e:
                    # If BM25 encoding fails, continue with dense-only
                    pass

            vectors.append(vector_dict)

        return vectors

    def upload_vectors(
        self,
        vectors: List[Dict],
        batch_size: int = 100
    ):
        """Upload vectors to Pinecone in batches (with hybrid search support)"""

        total_batches = (len(vectors) + batch_size - 1) // batch_size

        print(f"📤 Uploading {len(vectors)} vectors in {total_batches} batches...")
        if self.bm25_encoder:
            print("   ✅ Hybrid search enabled (dense + sparse vectors)")
        else:
            print("   ℹ️  Semantic-only (dense vectors only)")

        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            batch_num = (i // batch_size) + 1

            try:
                self.index.upsert(
                    vectors=batch,
                    namespace=self.namespace
                )

                print(f"  ✅ Batch {batch_num}/{total_batches} uploaded ({len(batch)} vectors)")

                # Small delay to avoid rate limits
                if batch_num < total_batches:
                    time.sleep(0.2)

            except Exception as e:
                print(f"  ❌ Error uploading batch {batch_num}: {str(e)}")
                self.stats['errors'].append({
                    'batch': batch_num,
                    'error': str(e)
                })

    def index_document(self, doc_info: Dict) -> bool:
        """Index a single compliance document"""

        file_path = Path(doc_info['file_path'])

        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False

        print(f"\n{'='*60}")
        print(f"📄 Processing: {doc_info['framework_name']} - {file_path.name}")
        print(f"{'='*60}")

        try:
            # Step 1: Extract text from PDF
            print("📖 Extracting text from PDF...")
            text, page_boundaries, pdf_metadata = self.pdf_extractor.extract_pdf_text(str(file_path))

            # Step 2: Chunk the document
            framework_id = self.get_framework_id(doc_info)
            print(f"✂️  Chunking document (framework: {framework_id})...")
            chunks = self.chunk_document(text, framework_id, doc_info)

            print(f"  Created {len(chunks)} chunks")
            print(f"  Average chunk size: {sum(c['char_count'] for c in chunks) / len(chunks):.0f} chars")

            # Step 3: Generate embeddings
            print("🧠 Generating embeddings...")
            chunk_texts = [chunk['text'] for chunk in chunks]
            embeddings = self.embeddings_gen.generate_embeddings(chunk_texts)

            # Step 4: Prepare vectors
            print("📦 Preparing vectors...")
            vectors = self.prepare_vectors(chunks, embeddings, doc_info)

            # Step 5: Upload to Pinecone
            self.upload_vectors(vectors)

            # Update stats
            self.stats['total_docs'] += 1
            self.stats['total_chunks'] += len(chunks)
            self.stats['total_vectors'] += len(vectors)

            print(f"✅ Successfully indexed {file_path.name}")
            return True

        except Exception as e:
            print(f"❌ Error indexing {file_path.name}: {str(e)}")
            self.stats['errors'].append({
                'file': str(file_path),
                'error': str(e)
            })
            return False

    def index_all_documents(self):
        """Index all compliance documents from manifest"""

        # Load manifest
        manifest = self.load_compliance_manifest()
        documents = manifest.get('documents', [])

        if not documents:
            print("❌ No documents found in manifest")
            return

        print(f"\n🚀 Starting indexing of {len(documents)} compliance documents")
        print(f"Target namespace: {self.namespace}")
        print(f"Embedding model: {self.embeddings_gen.model}")
        print(f"Embedding dimension: {self.embeddings_gen.dimension}")

        # Estimate cost before starting
        print(f"\n💰 Cost Estimation:")
        sample_doc = documents[0]
        sample_path = Path(sample_doc['file_path'])
        if sample_path.exists():
            sample_text, _, _ = self.pdf_extractor.extract_pdf_text(str(sample_path))
            cost_estimate = self.embeddings_gen.estimate_cost([sample_text] * len(documents))
            print(f"  Estimated tokens: ~{cost_estimate['estimated_tokens']:,}")
            print(f"  Estimated cost: ~${cost_estimate['estimated_cost']}")

        # Auto-continue (skip confirmation for automated runs)
        import sys as _sys
        try:
            if _sys.stdin.isatty():
                input(f"\n⏸️  Press Enter to continue or Ctrl+C to cancel...")
            else:
                print(f"\n▶️  Auto-continuing (automated mode)...")
        except (EOFError, OSError):
            # Stdin not available or closed - auto-continue
            print(f"\n▶️  Auto-continuing (automated mode)...")

        # Start indexing
        start_time = datetime.now()

        for i, doc_info in enumerate(documents, 1):
            print(f"\n[{i}/{len(documents)}] ", end='')
            self.index_document(doc_info)

        # Calculate totals
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Get final cost
        cost_info = self.embeddings_gen.estimate_cost()

        # Print summary
        self.print_summary(duration, cost_info)

    def print_summary(self, duration: float, cost_info: Dict):
        """Print indexing summary"""

        print(f"\n{'='*60}")
        print(f"✨ INDEXING COMPLETE")
        print(f"{'='*60}")

        print(f"\n📊 Summary:")
        print(f"  Documents processed: {self.stats['total_docs']}")
        print(f"  Total chunks created: {self.stats['total_chunks']:,}")
        print(f"  Total vectors uploaded: {self.stats['total_vectors']:,}")
        print(f"  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")

        print(f"\n💰 Cost:")
        print(f"  Model: {cost_info['model']}")
        print(f"  Total tokens: {cost_info['total_tokens']:,}")
        print(f"  Actual cost: ${cost_info['actual_cost']}")

        if self.stats['errors']:
            print(f"\n⚠️  Errors: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:  # Show first 5
                print(f"  - {error}")

        # Verify index stats
        print(f"\n🔍 Verifying Pinecone index...")
        stats = self.index.describe_index_stats()
        namespace_stats = stats.get('namespaces', {}).get(self.namespace, {})

        print(f"  Index: {self.index_name}")
        print(f"  Namespace: {self.namespace}")
        print(f"  Vectors in namespace: {namespace_stats.get('vector_count', 0):,}")

        # Save report
        self.save_report(duration, cost_info)

    def save_report(self, duration: float, cost_info: Dict):
        """Save indexing report to file"""

        report = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'stats': self.stats,
            'cost': cost_info,
            'config': {
                'index_name': self.index_name,
                'namespace': self.namespace,
                'embedding_model': self.embeddings_gen.model,
                'embedding_dimension': self.embeddings_gen.dimension
            }
        }

        report_path = Path(__file__).parent.parent / "outputs" / "indexing_report.json"
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Report saved to: {report_path}")


def main():
    """Main execution"""

    print("="*60)
    print("🚀 Compliance Framework Indexing Pipeline")
    print("="*60)

    indexer = ComplianceIndexer()
    indexer.index_all_documents()


if __name__ == "__main__":
    main()