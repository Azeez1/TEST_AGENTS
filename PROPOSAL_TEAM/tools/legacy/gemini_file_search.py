"""
Gemini File Search integration for RAG backup system.
Provides fully managed RAG capabilities using Google's Gemini API.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import config

logger = logging.getLogger(__name__)

# Try to import Gemini, gracefully handle if not installed
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning(
        "Gemini API not available. Install with: pip install google-genai"
    )


class GeminiFileSearch:
    """
    Gemini File Search client for backup RAG system.

    This provides a fully managed alternative to Pinecone that handles:
    - Automatic document chunking
    - Embedding generation and storage (free)
    - Vector search and retrieval (free)
    - Built-in citations and grounding

    Use this as a backup/fallback when Pinecone is unavailable or for
    comparison testing.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        store_name: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize Gemini File Search client.

        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
            store_name: Name of the file search store
            model: Gemini model to use for queries
        """
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "Gemini API not installed. Run: pip install google-genai"
            )

        self.api_key = api_key or config.gemini.api_key
        if not self.api_key:
            raise ValueError(
                "Gemini API key required. Set GEMINI_API_KEY environment variable."
            )

        self.store_name = store_name or config.gemini.file_search_store_name
        self.model = model or config.gemini.model

        # Initialize Gemini client
        self.client = genai.Client(api_key=self.api_key)
        self.file_search_store = None
        self.file_search_tool = None

        logger.info(f"Initialized Gemini File Search with model: {self.model}")

    def create_file_search_store(self, display_name: Optional[str] = None) -> str:
        """
        Create a new file search store for documents.

        Args:
            display_name: Human-readable name for the store

        Returns:
            Store resource name
        """
        try:
            display_name = display_name or self.store_name

            # Create the file search store
            self.file_search_store = self.client.files.create_corpus(
                display_name=display_name
            )

            logger.info(
                f"Created file search store: {self.file_search_store.name}"
            )
            return self.file_search_store.name

        except Exception as e:
            logger.error(f"Failed to create file search store: {e}")
            raise

    def get_or_create_store(self, display_name: Optional[str] = None) -> str:
        """
        Get existing file search store or create a new one.

        Args:
            display_name: Human-readable name for the store

        Returns:
            Store resource name
        """
        try:
            display_name = display_name or self.store_name

            # List existing corpora
            corpora = list(self.client.files.list_corpora())

            # Check if store with this name exists
            for corpus in corpora:
                if corpus.display_name == display_name:
                    self.file_search_store = corpus
                    logger.info(f"Found existing store: {corpus.name}")
                    return corpus.name

            # Create new store if not found
            return self.create_file_search_store(display_name)

        except Exception as e:
            logger.error(f"Failed to get or create store: {e}")
            raise

    def upload_file(
        self,
        file_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Upload a file to the file search store.

        Args:
            file_path: Path to the file to upload
            metadata: Optional metadata to attach to the file

        Returns:
            Uploaded file resource name
        """
        try:
            if not self.file_search_store:
                self.get_or_create_store()

            # Prepare metadata
            file_metadata = metadata or {}
            file_metadata["original_filename"] = file_path.name

            # Upload file to Gemini
            with open(file_path, "rb") as f:
                uploaded_file = self.client.files.upload(
                    file=f,
                    config=types.UploadFileConfig(
                        display_name=file_path.name,
                        mime_type=self._get_mime_type(file_path),
                    ),
                )

            # Add to corpus
            self.client.files.create_corpus_document(
                corpus=self.file_search_store.name,
                document=types.Document(
                    display_name=file_path.name,
                    custom_metadata=file_metadata,
                ),
                files=[uploaded_file],
            )

            logger.info(f"Uploaded file: {file_path.name}")
            return uploaded_file.name

        except Exception as e:
            logger.error(f"Failed to upload file {file_path}: {e}")
            raise

    def upload_files_batch(
        self,
        file_paths: List[Path],
        metadata_list: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """
        Upload multiple files to the file search store.

        Args:
            file_paths: List of file paths to upload
            metadata_list: Optional list of metadata dicts (one per file)

        Returns:
            List of uploaded file resource names
        """
        if metadata_list and len(metadata_list) != len(file_paths):
            raise ValueError("metadata_list must match length of file_paths")

        uploaded_files = []
        for i, file_path in enumerate(file_paths):
            metadata = metadata_list[i] if metadata_list else None
            try:
                file_name = self.upload_file(file_path, metadata)
                uploaded_files.append(file_name)
            except Exception as e:
                logger.error(f"Failed to upload {file_path}: {e}")
                continue

        logger.info(f"Uploaded {len(uploaded_files)}/{len(file_paths)} files")
        return uploaded_files

    def query(
        self,
        query_text: str,
        top_k: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query the file search store using Gemini.

        Args:
            query_text: The query string
            top_k: Number of results to return (not directly controllable in Gemini)
            metadata_filter: Optional metadata filters (limited support)

        Returns:
            List of search results with text, metadata, and citations
        """
        try:
            if not self.file_search_store:
                self.get_or_create_store()

            # Create file search tool if not exists
            if not self.file_search_tool:
                self.file_search_tool = types.Tool(
                    google_search=types.GoogleSearch(
                        dynamic_retrieval_config=types.DynamicRetrievalConfig(
                            mode=types.DynamicRetrievalConfig.Mode.MODE_DYNAMIC,
                            dynamic_threshold=0.3,
                        )
                    )
                )

            # Query using Gemini with file search
            response = self.client.models.generate_content(
                model=self.model,
                contents=query_text,
                config=types.GenerateContentConfig(
                    tools=[self.file_search_tool],
                    temperature=config.gemini.temperature,
                ),
            )

            # Parse response and extract grounding metadata
            results = self._parse_search_results(response)

            logger.info(f"Query returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise

    def query_with_context(
        self,
        query_text: str,
        top_k: int = 10,
    ) -> Dict[str, Any]:
        """
        Query and return both the AI response and retrieved context.

        Args:
            query_text: The query string
            top_k: Number of results to return

        Returns:
            Dict with 'response' (AI answer) and 'sources' (retrieved docs)
        """
        try:
            if not self.file_search_store:
                self.get_or_create_store()

            # Create file search tool
            file_search_tool = types.Tool(
                google_search=types.GoogleSearch()
            )

            # Generate response with grounding
            response = self.client.models.generate_content(
                model=self.model,
                contents=query_text,
                config=types.GenerateContentConfig(
                    tools=[file_search_tool],
                    temperature=config.gemini.temperature,
                ),
            )

            # Extract response text and sources
            result = {
                "response": response.text if response.text else "",
                "sources": self._extract_sources(response),
                "grounding_metadata": self._extract_grounding_metadata(response),
            }

            return result

        except Exception as e:
            logger.error(f"Query with context failed: {e}")
            raise

    def delete_file(self, file_name: str) -> bool:
        """
        Delete a file from the file search store.

        Args:
            file_name: Resource name of the file to delete

        Returns:
            True if successful
        """
        try:
            self.client.files.delete(name=file_name)
            logger.info(f"Deleted file: {file_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file {file_name}: {e}")
            return False

    def list_files(self) -> List[Dict[str, Any]]:
        """
        List all files in the file search store.

        Returns:
            List of file metadata dicts
        """
        try:
            if not self.file_search_store:
                self.get_or_create_store()

            documents = list(
                self.client.files.list_corpus_documents(
                    corpus=self.file_search_store.name
                )
            )

            files = []
            for doc in documents:
                files.append({
                    "name": doc.name,
                    "display_name": doc.display_name,
                    "metadata": doc.custom_metadata,
                })

            logger.info(f"Found {len(files)} files in store")
            return files

        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []

    def get_store_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the file search store.

        Returns:
            Dict with store statistics
        """
        try:
            if not self.file_search_store:
                self.get_or_create_store()

            files = self.list_files()

            return {
                "store_name": self.file_search_store.name,
                "display_name": self.file_search_store.display_name,
                "total_files": len(files),
                "model": self.model,
            }

        except Exception as e:
            logger.error(f"Failed to get store stats: {e}")
            return {}

    # Helper methods

    def _get_mime_type(self, file_path: Path) -> str:
        """Determine MIME type from file extension."""
        extension = file_path.suffix.lower()
        mime_types = {
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".doc": "application/msword",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".csv": "text/csv",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".html": "text/html",
        }
        return mime_types.get(extension, "application/octet-stream")

    def _parse_search_results(self, response: Any) -> List[Dict[str, Any]]:
        """Parse Gemini response into search results."""
        results = []

        # Extract grounding chunks if available
        if hasattr(response, "grounding_metadata"):
            for chunk in response.grounding_metadata.grounding_chunks:
                results.append({
                    "text": chunk.content if hasattr(chunk, "content") else "",
                    "score": 1.0,  # Gemini doesn't return scores
                    "metadata": {},
                })

        return results

    def _extract_sources(self, response: Any) -> List[Dict[str, Any]]:
        """Extract source citations from response."""
        sources = []

        if hasattr(response, "grounding_metadata"):
            for support in response.grounding_metadata.grounding_supports:
                sources.append({
                    "segment": support.segment.text if hasattr(support, "segment") else "",
                    "grounding_chunk_indices": support.grounding_chunk_indices,
                })

        return sources

    def _extract_grounding_metadata(self, response: Any) -> Dict[str, Any]:
        """Extract grounding metadata from response."""
        if hasattr(response, "grounding_metadata"):
            return {
                "web_search_queries": getattr(
                    response.grounding_metadata, "web_search_queries", []
                ),
                "search_entry_point": getattr(
                    response.grounding_metadata, "search_entry_point", None
                ),
            }
        return {}
