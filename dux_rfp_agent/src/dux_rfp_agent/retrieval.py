"""
Knowledge base retrieval using Pinecone.
"""

from typing import Any, Dict, List, Optional

from .config import config
from .logger import logger

try:
    from pinecone import Pinecone, ServerlessSpec

    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    logger.warning("Pinecone not available - KB retrieval will be disabled")

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class KnowledgeBaseRetrieval:
    """Handle knowledge base retrieval from Pinecone."""

    def __init__(self, enabled: bool = True):
        """
        Initialize KB retrieval.

        Args:
            enabled: Whether KB retrieval is enabled
        """
        self.enabled = enabled and PINECONE_AVAILABLE and config.pinecone.api_key

        if not self.enabled:
            logger.warning("Knowledge base retrieval is disabled")
            self.index = None
            return

        # Initialize Pinecone
        try:
            self.pc = Pinecone(api_key=config.pinecone.api_key)

            # Connect to index
            self.index = self.pc.Index(config.pinecone.index_name)
            logger.info(f"Connected to Pinecone index: {config.pinecone.index_name}")

        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            self.enabled = False
            self.index = None

        # Initialize embedding client
        if config.embedding.provider == "openai" and OPENAI_AVAILABLE:
            self.embed_client = openai.OpenAI(api_key=config.llm.api_key)
        else:
            self.embed_client = None

    def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding for text.

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        if not self.embed_client:
            raise RuntimeError("Embedding client not available")

        try:
            response = self.embed_client.embeddings.create(
                input=text, model=config.embedding.model
            )
            return response.data[0].embedding

        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            raise

    def query(
        self,
        query_text: str,
        top_k: int = 10,
        filter_metadata: Optional[Dict] = None,
        namespace: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query knowledge base for relevant documents.

        Args:
            query_text: Query text
            top_k: Number of results to return
            filter_metadata: Metadata filter (e.g., {'doc_type': 'resume'})
            namespace: Pinecone namespace

        Returns:
            List of matching documents with scores and metadata
        """
        if not self.enabled or not self.index:
            logger.warning("KB retrieval not available, returning empty results")
            return []

        namespace = namespace or config.pinecone.namespace

        try:
            # Create embedding for query
            query_embedding = self.create_embedding(query_text)

            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                namespace=namespace,
                filter=filter_metadata,
            )

            # Format results
            documents = []
            for match in results.matches:
                documents.append(
                    {
                        "id": match.id,
                        "score": match.score,
                        "metadata": match.metadata,
                        "text": match.metadata.get("text", ""),
                    }
                )

            logger.info(f"Retrieved {len(documents)} documents for query")
            return documents

        except Exception as e:
            logger.error(f"KB query failed: {e}")
            return []

    def upsert(
        self,
        documents: List[Dict[str, Any]],
        namespace: Optional[str] = None,
        batch_size: int = 100,
    ) -> int:
        """
        Upsert documents to knowledge base.

        Args:
            documents: List of documents with 'id', 'text', and 'metadata'
            namespace: Pinecone namespace
            batch_size: Batch size for upserts

        Returns:
            Number of documents upserted
        """
        if not self.enabled or not self.index:
            logger.warning("KB retrieval not available, cannot upsert")
            return 0

        namespace = namespace or config.pinecone.namespace

        try:
            vectors = []

            for doc in documents:
                # Create embedding
                embedding = self.create_embedding(doc["text"])

                # Prepare vector
                metadata = doc.get("metadata", {})
                metadata["text"] = doc["text"]  # Store text in metadata

                vectors.append(
                    {
                        "id": doc["id"],
                        "values": embedding,
                        "metadata": metadata,
                    }
                )

            # Upsert in batches
            total_upserted = 0
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i : i + batch_size]
                self.index.upsert(vectors=batch, namespace=namespace)
                total_upserted += len(batch)
                logger.info(f"Upserted batch {i // batch_size + 1}: {len(batch)} vectors")

            logger.info(f"Successfully upserted {total_upserted} documents")
            return total_upserted

        except Exception as e:
            logger.error(f"KB upsert failed: {e}")
            raise

    def query_requirements(self, requirements: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Query KB for each requirement.

        Args:
            requirements: List of requirement dictionaries

        Returns:
            Dictionary mapping requirement ID to retrieved documents
        """
        if not self.enabled:
            return {}

        results = {}

        for req in requirements:
            req_id = req["id"]
            req_text = req["text"]

            # Build query from requirement text and keywords
            query = req_text
            if "keywords" in req and req["keywords"]:
                query += " " + " ".join(req["keywords"])

            # Query KB
            docs = self.query(query, top_k=5)
            results[req_id] = docs

            logger.debug(f"Retrieved {len(docs)} docs for {req_id}")

        return results
