#!/usr/bin/env python3
"""
Run Hybrid Search Tests - Phase 1 Optimization

Combines:
1. Query Expansion (framework-specific synonyms)
2. Hybrid Search (BM25 + semantic)

Expected improvement: +5-11% similarity scores
Target: 70%+ average similarity (currently 65.33%)
"""

import os
import sys
import pickle
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone

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

# Import modules
from embeddings_generator import EmbeddingsGenerator
from query_expander import QueryExpander
from hybrid_search import HybridSearcher


class HybridSearchTester:
    """Test Pinecone with hybrid search and query expansion"""

    def __init__(self):
        """Initialize with hybrid search capabilities"""

        print("=" * 80)
        print("🚀 HYBRID SEARCH TESTER - Phase 1 Optimizations")
        print("=" * 80)
        print()

        # Get configuration
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX", "rfp-knowledge-base")
        self.namespace = os.getenv("PINECONE_NAMESPACE", "compliance_frameworks")

        # Initialize Pinecone
        print("🔄 Initializing Pinecone client...")
        self.pc = Pinecone(api_key=self.api_key)
        self.index = self.pc.Index(self.index_name)

        # Initialize embeddings generator
        print("🔄 Initializing embeddings generator...")
        self.embeddings_gen = EmbeddingsGenerator()

        # Initialize query expander
        print("🔄 Initializing query expander...")
        self.query_expander = QueryExpander()

        # Initialize hybrid searcher
        print("🔄 Initializing hybrid searcher...")
        self.hybrid_searcher = HybridSearcher(
            self.index,
            self.embeddings_gen,
            self.namespace
        )

        # Load BM25 encoder if available
        self._load_bm25_encoder()

        # Get index stats
        stats = self.index.describe_index_stats()
        namespace_stats = stats.get('namespaces', {}).get(self.namespace, {})

        print(f"✅ Connected to Pinecone")
        print(f"   Index: {self.index_name}")
        print(f"   Namespace: {self.namespace}")
        print(f"   Total vectors: {namespace_stats.get('vector_count', 0):,}")
        print()

    def _load_bm25_encoder(self):
        """Load BM25 encoder if available"""

        encoder_path = Path(__file__).parent.parent / "tools" / "bm25_encoder.pkl"

        if encoder_path.exists():
            try:
                print(f"📂 Loading BM25 encoder from: {encoder_path}")

                with open(encoder_path, 'rb') as f:
                    bm25_encoder = pickle.load(f)

                self.hybrid_searcher.bm25_encoder = bm25_encoder
                self.hybrid_searcher._is_fitted = True

                print("✅ BM25 encoder loaded successfully")
                print("   Hybrid search enabled (BM25 + semantic)")

            except Exception as e:
                print(f"⚠️  Error loading BM25 encoder: {e}")
                print("   Falling back to semantic-only search")

        else:
            print("⚠️  BM25 encoder not found")
            print(f"   Run: python scripts/train_bm25_encoder.py")
            print("   Falling back to semantic-only search")

    def hybrid_search(
        self,
        query: str,
        framework_filter: str = None,
        top_k: int = 3,
        expand_query: bool = True
    ):
        """
        Perform hybrid search with query expansion

        Args:
            query: Search query
            framework_filter: Framework to filter by
            top_k: Number of results
            expand_query: Whether to expand query with synonyms
        """

        print(f"\n{'='*80}")
        print(f"🔍 Query: {query}")
        if framework_filter:
            print(f"🏷️  Filter: {framework_filter.upper()}")
        print(f"{'='*80}")

        # Query expansion
        if expand_query and framework_filter:
            expanded = self.query_expander.expand_query(
                query,
                framework_id=framework_filter,
                max_synonyms=2
            )

            if expanded != query:
                print(f"\n✨ Expanded Query:")
                print(f"   {expanded}")
                query = expanded

        # Hybrid search with framework-optimized alpha
        results = self.hybrid_searcher.optimized_search(
            query=query,
            framework_filter=framework_filter,
            top_k=top_k
        )

        # Display results
        if not results:
            print("\n❌ No results found")
            return []

        print(f"\n📊 Found {len(results)} results:")

        for i, match in enumerate(results, 1):
            score = match.score
            metadata = match.metadata

            print(f"\n{'─' * 80}")
            print(f"Result #{i} - Score: {score:.4f} (Similarity: {score*100:.2f}%)")
            print(f"{'─' * 80}")
            print(f"📄 Document: {metadata.get('file_name', 'Unknown')}")
            print(f"🏷️  Framework: {metadata.get('framework_name', 'Unknown')} ({metadata.get('framework_id', 'N/A')})")
            print(f"📍 Chunk: {metadata.get('chunk_number', 'N/A')} ({metadata.get('chunk_size', 'N/A')} chars)")
            print()
            print(f"💬 Content Preview:")

            text = metadata.get('text', '')
            preview = text[:500] + "..." if len(text) > 500 else text
            print(preview)

        return results

    def run_test_suite(self):
        """Run complete test suite"""

        # Test queries
        test_queries = [
            {
                "description": "General MFA requirements across all frameworks",
                "query": "What are the requirements for multi-factor authentication?",
                "framework": None
            },
            {
                "description": "DoD contractor access control",
                "query": "CMMC Level 2 access control requirements for defense contractors",
                "framework": "cmmc"
            },
            {
                "description": "Federal cloud security monitoring",
                "query": "FedRAMP continuous monitoring and incident response requirements",
                "framework": "fedramp"
            },
            {
                "description": "CUI protection requirements",
                "query": "How to protect Controlled Unclassified Information (CUI) at rest and in transit?",
                "framework": "nist_800_171"
            },
            {
                "description": "Healthcare data protection",
                "query": "HIPAA requirements for patient data encryption and access controls",
                "framework": "hipaa"
            },
            {
                "description": "Payment card data security",
                "query": "PCI-DSS requirements for storing and transmitting credit card data",
                "framework": "pci_dss"
            },
            {
                "description": "EU data privacy compliance",
                "query": "GDPR data subject rights and consent management requirements",
                "framework": "gdpr"
            },
            {
                "description": "Cloud provider certifications (cross-framework)",
                "query": "What certifications are required for cloud service providers?",
                "framework": None
            }
        ]

        print("\n\n" + "=" * 80)
        print("🧪 HYBRID SEARCH QUALITY TEST SUITE")
        print("=" * 80)
        print()

        results_summary = []

        for i, test in enumerate(test_queries, 1):
            print("\n\n" + "#" * 80)
            print(f"TEST: {test['description']}")
            print("#" * 80)

            matches = self.hybrid_search(
                query=test['query'],
                framework_filter=test.get('framework'),
                top_k=3,
                expand_query=True
            )

            # Calculate metrics
            avg_score = sum(m.score for m in matches) / len(matches) if matches else 0
            top_score = matches[0].score if matches else 0

            results_summary.append({
                "description": test['description'],
                "query": test['query'],
                "framework": test.get('framework', 'all'),
                "num_results": len(matches),
                "avg_score": avg_score,
                "top_score": top_score
            })

            print("\n⏸️  Continuing to next test...")

        # Print summary
        self.print_summary(results_summary)

    def print_summary(self, results_summary):
        """Print test results summary"""

        print("\n\n" + "=" * 80)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 80)

        print(f"\n{'Test Description':<50} {'Framework':<15} {'Results':<10} {'Top Score':<12} {'Avg Score'}")
        print(f"{'-'*50} {'-'*15} {'-'*10} {'-'*12} {'-'*10}")

        for result in results_summary:
            desc = result['description'][:47] + "..." if len(result['description']) > 50 else result['description']
            framework = (result['framework'] or 'all').upper()[:12]
            num_results = result['num_results']
            top_score = f"{result['top_score']:.4f}" if result['top_score'] > 0 else "N/A"
            avg_score = f"{result['avg_score']:.4f}" if result['avg_score'] > 0 else "N/A"

            print(f"{desc:<50} {framework:<15} {num_results:<10} {top_score:<12} {avg_score}")

        # Overall statistics
        total_tests = len(results_summary)
        successful = sum(1 for r in results_summary if r['num_results'] > 0)
        avg_top_score = sum(r['top_score'] for r in results_summary) / total_tests if total_tests > 0 else 0

        print("\n" + "=" * 80)
        print(f"Overall Statistics:")
        print(f"  Total tests: {total_tests}")
        print(f"  Successful queries: {successful}/{total_tests} ({successful/total_tests*100:.1f}%)")
        print(f"  Average top score: {avg_top_score:.4f} ({avg_top_score*100:.2f}% similarity)")
        print("=" * 80)

        # Quality rating
        if avg_top_score >= 0.80:
            print("\n✅ EXCELLENT: Very high similarity scores (>80%)")
        elif avg_top_score >= 0.75:
            print("\n✅ VERY GOOD: High similarity scores (75-80%)")
        elif avg_top_score >= 0.70:
            print("\n✅ GOOD: Production-ready similarity scores (70-75%)")
        elif avg_top_score >= 0.60:
            print("\n⚠️  FAIR: Acceptable but could be improved (60-70% similarity)")
        else:
            print("\n❌ NEEDS IMPROVEMENT: Low similarity scores (<60%)")


def main():
    """Main execution"""

    tester = HybridSearchTester()
    tester.run_test_suite()


if __name__ == "__main__":
    main()
