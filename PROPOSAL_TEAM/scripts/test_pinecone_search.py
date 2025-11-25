#!/usr/bin/env python3
"""
Test Pinecone Search Quality
Query the compliance knowledge base with sample RFP requirements
"""

import os
import sys
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

# Import embeddings generator
import importlib.util
emb_spec = importlib.util.spec_from_file_location(
    "embeddings_generator",
    Path(__file__).parent.parent / "tools" / "embeddings_generator.py"
)
emb_module = importlib.util.module_from_spec(emb_spec)
emb_spec.loader.exec_module(emb_module)
EmbeddingsGenerator = emb_module.EmbeddingsGenerator


class PineconeSearchTester:
    """Test Pinecone search with compliance queries"""

    def __init__(self):
        """Initialize Pinecone and embeddings"""
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

        # Get index stats
        stats = self.index.describe_index_stats()
        namespace_stats = stats.get('namespaces', {}).get(self.namespace, {})

        print(f"✅ Connected to Pinecone")
        print(f"   Index: {self.index_name}")
        print(f"   Namespace: {self.namespace}")
        print(f"   Total vectors: {namespace_stats.get('vector_count', 0):,}")

    def search(self, query: str, framework_filter: str = None, top_k: int = 5):
        """
        Search Pinecone for relevant compliance content.

        Args:
            query: The search query (RFP requirement)
            framework_filter: Optional framework ID to filter (e.g., "cmmc", "fedramp")
            top_k: Number of results to return
        """
        print(f"\n{'='*80}")
        print(f"🔍 Query: {query}")
        if framework_filter:
            print(f"🏷️  Filter: {framework_filter.upper()}")
        print(f"{'='*80}")

        # Generate query embedding
        query_embedding = self.embeddings_gen.generate_single_embedding(query)

        # Build metadata filter
        metadata_filter = {}
        if framework_filter:
            metadata_filter = {"framework_id": framework_filter}

        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace=self.namespace,
            filter=metadata_filter if metadata_filter else None
        )

        # Display results
        if not results.matches:
            print("❌ No results found")
            return []

        print(f"\n📊 Found {len(results.matches)} results:\n")

        for i, match in enumerate(results.matches, 1):
            metadata = match.metadata
            score = match.score

            print(f"{'─'*80}")
            print(f"Result #{i} - Score: {score:.4f} (Similarity: {score*100:.2f}%)")
            print(f"{'─'*80}")
            print(f"📄 Document: {metadata.get('file_name', 'Unknown')}")
            print(f"🏷️  Framework: {metadata.get('framework_name', 'Unknown')} ({metadata.get('framework_id', '')})")
            print(f"📍 Chunk: {metadata.get('chunk_index', 0)} ({metadata.get('char_count', 0)} chars)")
            print(f"\n💬 Content Preview:")
            print(f"{metadata.get('text', 'No preview available')[:500]}...")
            print()

        return results.matches

    def run_test_queries(self):
        """Run a set of test queries covering different frameworks"""

        print("\n" + "="*80)
        print("🧪 PINECONE SEARCH QUALITY TEST")
        print("="*80)

        test_queries = [
            # General compliance
            {
                "query": "What are the requirements for multi-factor authentication?",
                "framework": None,
                "description": "General MFA requirements across all frameworks"
            },
            # CMMC specific
            {
                "query": "CMMC Level 2 access control requirements for defense contractors",
                "framework": "cmmc",
                "description": "DoD contractor access control"
            },
            # FedRAMP specific
            {
                "query": "FedRAMP continuous monitoring and incident response requirements",
                "framework": "fedramp",
                "description": "Federal cloud security monitoring"
            },
            # NIST 800-171
            {
                "query": "How to protect Controlled Unclassified Information (CUI) at rest and in transit?",
                "framework": "nist_800_171",
                "description": "CUI protection requirements"
            },
            # HIPAA
            {
                "query": "HIPAA requirements for patient data encryption and access controls",
                "framework": "hipaa",
                "description": "Healthcare data protection"
            },
            # PCI-DSS
            {
                "query": "PCI-DSS requirements for storing and transmitting credit card data",
                "framework": "pci_dss",
                "description": "Payment card data security"
            },
            # GDPR
            {
                "query": "GDPR data subject rights and consent management requirements",
                "framework": "gdpr",
                "description": "EU data privacy compliance"
            },
            # Cross-framework
            {
                "query": "What certifications are required for cloud service providers?",
                "framework": None,
                "description": "Cloud provider certifications (cross-framework)"
            },
        ]

        results_summary = []

        for test in test_queries:
            print(f"\n\n{'#'*80}")
            print(f"TEST: {test['description']}")
            print(f"{'#'*80}")

            matches = self.search(
                query=test['query'],
                framework_filter=test.get('framework'),
                top_k=3  # Show top 3 results
            )

            results_summary.append({
                "description": test['description'],
                "query": test['query'],
                "framework": test.get('framework', 'all'),
                "num_results": len(matches),
                "avg_score": sum(m.score for m in matches) / len(matches) if matches else 0,
                "top_score": matches[0].score if matches else 0
            })

            # Pause for readability (commented out for automated testing)
            # input("\n⏸️  Press Enter to continue to next test...")
            print("\n⏸️  Continuing to next test...")

        # Print summary
        self.print_summary(results_summary)

    def print_summary(self, results_summary):
        """Print test results summary"""

        print("\n\n" + "="*80)
        print("📊 TEST RESULTS SUMMARY")
        print("="*80)

        print(f"\n{'Test Description':<50} {'Framework':<15} {'Results':<10} {'Top Score':<12} {'Avg Score'}")
        print(f"{'-'*50} {'-'*15} {'-'*10} {'-'*12} {'-'*10}")

        for result in results_summary:
            desc = result['description'][:47] + "..." if len(result['description']) > 50 else result['description']
            framework = result['framework'].upper()[:12]
            num_results = result['num_results']
            top_score = f"{result['top_score']:.4f}" if result['top_score'] > 0 else "N/A"
            avg_score = f"{result['avg_score']:.4f}" if result['avg_score'] > 0 else "N/A"

            print(f"{desc:<50} {framework:<15} {num_results:<10} {top_score:<12} {avg_score}")

        # Overall statistics
        total_tests = len(results_summary)
        successful_tests = sum(1 for r in results_summary if r['num_results'] > 0)
        avg_top_score = sum(r['top_score'] for r in results_summary) / total_tests

        print(f"\n{'='*80}")
        print(f"Overall Statistics:")
        print(f"  Total tests: {total_tests}")
        print(f"  Successful queries: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
        print(f"  Average top score: {avg_top_score:.4f} ({avg_top_score*100:.2f}% similarity)")
        print(f"{'='*80}")

        # Quality assessment
        if avg_top_score >= 0.80:
            print("\n✅ EXCELLENT: High-quality semantic search! (80%+ similarity)")
        elif avg_top_score >= 0.70:
            print("\n✅ GOOD: Solid search quality (70-80% similarity)")
        elif avg_top_score >= 0.60:
            print("\n⚠️  FAIR: Acceptable but could be improved (60-70% similarity)")
        else:
            print("\n❌ NEEDS IMPROVEMENT: Low similarity scores (<60%)")


def main():
    """Main execution"""

    tester = PineconeSearchTester()

    # Check if running interactively or in automated mode
    import sys
    if sys.stdin.isatty():
        print("\n" + "="*80)
        print("Choose test mode:")
        print("  1. Run full test suite (8 queries)")
        print("  2. Custom single query")
        print("="*80)

        choice = input("\nEnter choice (1 or 2): ").strip()

        if choice == "1":
            tester.run_test_queries()
        elif choice == "2":
            query = input("\nEnter your query: ").strip()
            framework = input("Filter by framework (cmmc/fedramp/nist_800_171/hipaa/pci_dss/gdpr or press Enter for all): ").strip()
            framework = framework if framework else None
            tester.search(query, framework, top_k=5)
        else:
            print("Invalid choice. Running full test suite...")
            tester.run_test_queries()
    else:
        # Automated mode - run full test suite
        print("\n" + "="*80)
        print("Running in automated mode - Full test suite")
        print("="*80)
        tester.run_test_queries()


if __name__ == "__main__":
    main()
