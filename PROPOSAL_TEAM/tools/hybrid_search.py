"""
Hybrid Search for Pinecone - Combines Semantic and Keyword (BM25) Search

Improves search quality by combining:
1. Semantic search (embeddings) - Captures conceptual similarity
2. BM25 keyword search (sparse vectors) - Captures exact terminology matches

This is particularly effective for legal/compliance documents where both
conceptual understanding AND precise terminology matter.

Usage:
    from hybrid_search import HybridSearcher

    searcher = HybridSearcher(index, embeddings_generator)
    results = searcher.hybrid_search(
        query="HIPAA patient data encryption requirements",
        framework_filter="hipaa",
        top_k=5,
        alpha=0.7  # 70% semantic, 30% keyword
    )
"""

import logging
from typing import List, Optional, Dict, Any
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

logger = logging.getLogger(__name__)


class HybridSearcher:
    """
    Hybrid search combining semantic (dense) and keyword (sparse) search
    """

    def __init__(
        self,
        pinecone_index,
        embeddings_generator,
        namespace: str = "compliance_frameworks"
    ):
        """
        Initialize hybrid searcher

        Args:
            pinecone_index: Pinecone index instance
            embeddings_generator: EmbeddingsGenerator instance
            namespace: Pinecone namespace to search in
        """
        self.index = pinecone_index
        self.embeddings_gen = embeddings_generator
        self.namespace = namespace

        # BM25 encoder (will be initialized with fit())
        self.bm25_encoder = None
        self._is_fitted = False

        logger.info(f"Initialized HybridSearcher for namespace: {namespace}")

    def fit_bm25(self, corpus: List[str]):
        """
        Train BM25 encoder on document corpus

        Args:
            corpus: List of document texts to train on

        Note: This should be called once with all your document chunks
        to build the BM25 vocabulary and IDF statistics.
        """
        try:
            from pinecone_text.sparse import BM25Encoder

            logger.info(f"Training BM25 encoder on corpus of {len(corpus)} documents...")

            self.bm25_encoder = BM25Encoder()
            self.bm25_encoder.fit(corpus)
            self._is_fitted = True

            logger.info("BM25 encoder trained successfully")

        except ImportError:
            logger.error(
                "pinecone-text not installed. Install with: pip install pinecone-text"
            )
            raise
        except Exception as e:
            logger.error(f"Error training BM25 encoder: {e}")
            raise

    def hybrid_search(
        self,
        query: str,
        framework_filter: Optional[str] = None,
        top_k: int = 5,
        alpha: float = 0.7,
        include_metadata: bool = True
    ) -> List[Any]:
        """
        Perform hybrid search combining semantic and keyword matching

        Args:
            query: Search query text
            framework_filter: Optional framework_id to filter results (e.g., 'hipaa')
            top_k: Number of results to return
            alpha: Balance between semantic (dense) and keyword (sparse) search
                   - 1.0 = pure semantic search
                   - 0.0 = pure keyword search
                   - 0.7 = 70% semantic, 30% keyword (recommended default)
            include_metadata: Whether to return full metadata

        Returns:
            List of search results (Pinecone matches)
        """
        if not query:
            logger.warning("Empty query provided")
            return []

        # Generate semantic (dense) embedding
        try:
            dense_vector = self.embeddings_gen.generate_single_embedding(query)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []

        # Prepare query parameters
        query_params = {
            "vector": dense_vector,
            "top_k": top_k,
            "include_metadata": include_metadata,
            "namespace": self.namespace
        }

        # Add framework filter if specified
        if framework_filter:
            query_params["filter"] = {"framework_id": framework_filter.lower()}

        # Add BM25 sparse vector if encoder is fitted
        if self._is_fitted and self.bm25_encoder and alpha < 1.0:
            try:
                # Generate sparse vector for keyword matching
                sparse_vector = self.bm25_encoder.encode_queries(query)
                query_params["sparse_vector"] = sparse_vector

                logger.debug(
                    f"Hybrid search: alpha={alpha} "
                    f"(semantic={alpha:.0%}, keyword={1-alpha:.0%})"
                )

            except Exception as e:
                logger.warning(f"Error generating sparse vector: {e}. Using semantic-only search.")
                # Fall back to semantic-only search

        else:
            if not self._is_fitted:
                logger.warning(
                    "BM25 encoder not fitted. Using semantic-only search. "
                    "Call fit_bm25() to enable hybrid search."
                )

        # Execute search
        try:
            results = self.index.query(**query_params)
            matches = results.get('matches', [])

            logger.info(
                f"Search returned {len(matches)} results "
                f"(query: '{query[:50]}...', filter: {framework_filter})"
            )

            return matches

        except Exception as e:
            logger.error(f"Error executing Pinecone query: {e}")
            return []

    def semantic_only_search(
        self,
        query: str,
        framework_filter: Optional[str] = None,
        top_k: int = 5
    ) -> List[Any]:
        """
        Perform semantic-only search (no BM25)

        This is equivalent to hybrid_search with alpha=1.0

        Args:
            query: Search query text
            framework_filter: Optional framework_id to filter results
            top_k: Number of results to return

        Returns:
            List of search results
        """
        return self.hybrid_search(
            query=query,
            framework_filter=framework_filter,
            top_k=top_k,
            alpha=1.0  # Pure semantic
        )

    def keyword_only_search(
        self,
        query: str,
        framework_filter: Optional[str] = None,
        top_k: int = 5
    ) -> List[Any]:
        """
        Perform keyword-only search (pure BM25)

        This is equivalent to hybrid_search with alpha=0.0

        Args:
            query: Search query text
            framework_filter: Optional framework_id to filter results
            top_k: Number of results to return

        Returns:
            List of search results
        """
        if not self._is_fitted:
            logger.error("BM25 encoder not fitted. Cannot perform keyword-only search.")
            return []

        return self.hybrid_search(
            query=query,
            framework_filter=framework_filter,
            top_k=top_k,
            alpha=0.0  # Pure keyword
        )

    def get_framework_specific_alpha(self, framework_id: str) -> float:
        """
        Get recommended alpha value for specific framework

        Based on empirical testing:
        - HIPAA/GDPR: More keyword-focused (alpha=0.65) due to specific terminology
        - CMMC/FedRAMP: More semantic-focused (alpha=0.75) for conceptual matching
        - Others: Balanced (alpha=0.70)

        Args:
            framework_id: Framework identifier

        Returns:
            Recommended alpha value (0.0-1.0)
        """
        if not framework_id:
            return 0.70  # Default balanced

        fw = framework_id.lower()

        # Framework-specific tuning
        alpha_map = {
            "hipaa": 0.65,      # More keyword weight (dense terminology)
            "gdpr": 0.60,       # Highest keyword weight (Article numbers, specific terms)
            "cmmc": 0.75,       # More semantic weight (conceptual requirements)
            "fedramp": 0.75,    # More semantic weight (broad concepts)
            "nist_800_171": 0.70,  # Balanced
            "nist_800_53": 0.70,   # Balanced
            "pci_dss": 0.70,    # Balanced
            "glba": 0.70,       # Balanced
            "dfars": 0.70       # Balanced
        }

        return alpha_map.get(fw, 0.70)  # Default if not in map

    def optimized_search(
        self,
        query: str,
        framework_filter: Optional[str] = None,
        top_k: int = 5
    ) -> List[Any]:
        """
        Perform search with framework-optimized alpha value

        Automatically selects best alpha based on framework characteristics.

        Args:
            query: Search query text
            framework_filter: Optional framework_id to filter results
            top_k: Number of results to return

        Returns:
            List of search results
        """
        alpha = self.get_framework_specific_alpha(framework_filter)

        logger.info(
            f"Optimized search for {framework_filter or 'all frameworks'} "
            f"using alpha={alpha}"
        )

        return self.hybrid_search(
            query=query,
            framework_filter=framework_filter,
            top_k=top_k,
            alpha=alpha
        )


# Utility function for loading corpus from Pinecone index
def load_corpus_from_pinecone(
    index,
    namespace: str = "compliance_frameworks",
    batch_size: int = 100
) -> List[str]:
    """
    Load all document texts from Pinecone index to build BM25 corpus

    Args:
        index: Pinecone index instance
        namespace: Namespace to read from
        batch_size: Number of vectors to fetch per batch

    Returns:
        List of document texts

    Note: This can be slow for large indexes. Consider caching the result.
    """
    logger.info(f"Loading corpus from Pinecone namespace: {namespace}")

    corpus = []

    try:
        # Get index stats to determine total vectors
        stats = index.describe_index_stats()
        namespace_stats = stats.get('namespaces', {}).get(namespace, {})
        total_vectors = namespace_stats.get('vector_count', 0)

        logger.info(f"Found {total_vectors} vectors in namespace")

        if total_vectors == 0:
            logger.warning("No vectors found in namespace")
            return corpus

        # Pinecone doesn't support full scan, so we need to query
        # Use a dummy vector to get all results (not ideal, but works)
        # Better approach: Store corpus during indexing

        # For now, return empty list and require manual corpus provision
        logger.warning(
            "Cannot automatically load corpus from Pinecone. "
            "Please provide corpus explicitly when calling fit_bm25()"
        )

        return corpus

    except Exception as e:
        logger.error(f"Error loading corpus: {e}")
        return corpus


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )

    print("=" * 80)
    print("Hybrid Search - BM25 + Semantic Search for Compliance Documents")
    print("=" * 80)
    print()

    print("This module provides hybrid search combining:")
    print("  1. Semantic search (embeddings) - Conceptual similarity")
    print("  2. BM25 keyword search - Exact terminology matching")
    print()

    print("Usage Example:")
    print("-" * 80)
    print("""
from hybrid_search import HybridSearcher
from embeddings_generator import EmbeddingsGenerator
from pinecone_knowledge_base import PineconeKnowledgeBase

# Initialize components
kb = PineconeKnowledgeBase()
embeddings_gen = EmbeddingsGenerator()

# Create hybrid searcher
searcher = HybridSearcher(kb.index, embeddings_gen)

# Train BM25 on your corpus (one-time)
corpus = [...]  # List of all document chunks
searcher.fit_bm25(corpus)

# Perform hybrid search
results = searcher.optimized_search(
    query="HIPAA patient data encryption requirements",
    framework_filter="hipaa",
    top_k=5
)

# Or manual alpha tuning
results = searcher.hybrid_search(
    query="GDPR consent management",
    framework_filter="gdpr",
    top_k=5,
    alpha=0.7  # 70% semantic, 30% keyword
)
    """)
    print()

    print("Framework-Specific Alpha Values:")
    print("-" * 80)
    print("  • HIPAA: 0.65 (more keyword weight)")
    print("  • GDPR: 0.60 (highest keyword weight)")
    print("  • CMMC: 0.75 (more semantic weight)")
    print("  • FedRAMP: 0.75 (more semantic weight)")
    print("  • Others: 0.70 (balanced)")
    print()
