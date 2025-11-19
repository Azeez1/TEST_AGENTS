"""
Gemini File Search integration for RAG backup system.
Provides fully managed RAG capabilities using Google's Gemini API.
"""

import logging
import time
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

            # Create the file search store (CORRECT API)
            self.file_search_store = self.client.file_search_stores.create(
                config={'display_name': display_name}
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

            # List existing stores (CORRECT API)
            for store in self.client.file_search_stores.list():
                if store.display_name == display_name:
                    self.file_search_store = store
                    logger.info(f"Found existing store: {store.name}")
                    return store.name

            # Create new store if not found
            return self.create_file_search_store(display_name)

        except Exception as e:
            logger.error(f"Failed to get or create store: {e}")
            raise

    def upload_file(
        self,
        file_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
        wait_for_completion: bool = True,
        timeout: int = 300,
    ) -> str:
        """
        Upload a file to the file search store.

        Args:
            file_path: Path to the file to upload
            metadata: Optional metadata (stored in display_name for now)
            wait_for_completion: Wait for async upload to complete
            timeout: Max seconds to wait for upload completion

        Returns:
            Uploaded file resource name
        """
        try:
            if not self.file_search_store:
                self.get_or_create_store()

            # Prepare display name (can include metadata)
            display_name = file_path.name
            if metadata and "framework_id" in metadata:
                display_name = f"{metadata['framework_id']}_{file_path.name}"

            # Upload file to Gemini (CORRECT API)
            operation = self.client.file_search_stores.upload_to_file_search_store(
                file=str(file_path),
                file_search_store_name=self.file_search_store.name,
                config={'display_name': display_name}
            )

            logger.info(f"Uploading file: {file_path.name}")

            # Wait for upload to complete (async operation)
            if wait_for_completion:
                start_time = time.time()
                while not operation.done:
                    if time.time() - start_time > timeout:
                        raise TimeoutError(
                            f"Upload timed out after {timeout} seconds"
                        )
                    time.sleep(5)
                    operation = self.client.operations.get(operation)

                logger.info(f"✓ Upload complete: {file_path.name}")

            return operation.name

        except Exception as e:
            logger.error(f"Failed to upload file {file_path}: {e}")
            raise

    def upload_files_batch(
        self,
        file_paths: List[Path],
        metadata_list: Optional[List[Dict[str, Any]]] = None,
        wait_for_completion: bool = True,
    ) -> List[str]:
        """
        Upload multiple files to the file search store.

        Args:
            file_paths: List of file paths to upload
            metadata_list: Optional list of metadata dicts (one per file)
            wait_for_completion: Wait for each upload to complete

        Returns:
            List of uploaded operation names
        """
        if metadata_list and len(metadata_list) != len(file_paths):
            raise ValueError("metadata_list must match length of file_paths")

        uploaded_operations = []
        for i, file_path in enumerate(file_paths):
            metadata = metadata_list[i] if metadata_list else None
            try:
                operation_name = self.upload_file(
                    file_path, metadata, wait_for_completion
                )
                uploaded_operations.append(operation_name)
            except Exception as e:
                logger.error(f"Failed to upload {file_path}: {e}")
                continue

        logger.info(
            f"Uploaded {len(uploaded_operations)}/{len(file_paths)} files"
        )
        return uploaded_operations

    def query(
        self,
        query_text: str,
        top_k: int = 10,
    ) -> str:
        """
        Query the file search store using Gemini.

        Note: Gemini File Search doesn't directly return chunks like Pinecone.
        It uses the file search tool to ground responses automatically.

        Args:
            query_text: The query string
            top_k: Not directly controllable in Gemini

        Returns:
            AI-generated response grounded in your documents
        """
        try:
            if not self.file_search_store:
                self.get_or_create_store()

            # Query using Gemini with file search tool (CORRECT API)
            response = self.client.models.generate_content(
                model=self.model,
                contents=query_text,
                config=types.GenerateContentConfig(
                    tools=[
                        types.Tool(
                            file_search=types.FileSearch(
                                file_search_store_names=[self.file_search_store.name]
                            )
                        )
                    ],
                    temperature=config.gemini.temperature,
                ),
            )

            logger.info(f"Query completed successfully")
            return response.text if response.text else ""

        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise

    def query_with_context(
        self,
        query_text: str,
        top_k: int = 10,
    ) -> Dict[str, Any]:
        """
        Query and return both the AI response and grounding metadata.

        Args:
            query_text: The query string
            top_k: Number of results (not directly controllable)

        Returns:
            Dict with 'response' (AI answer) and 'grounding_metadata'
        """
        try:
            if not self.file_search_store:
                self.get_or_create_store()

            # Generate response with grounding (CORRECT API)
            response = self.client.models.generate_content(
                model=self.model,
                contents=query_text,
                config=types.GenerateContentConfig(
                    tools=[
                        types.Tool(
                            file_search=types.FileSearch(
                                file_search_store_names=[self.file_search_store.name]
                            )
                        )
                    ],
                    temperature=config.gemini.temperature,
                ),
            )

            # Extract response and grounding metadata
            result = {
                "response": response.text if response.text else "",
                "grounding_metadata": self._extract_grounding_metadata(response),
                "grounding_chunks": self._extract_grounding_chunks(response),
            }

            return result

        except Exception as e:
            logger.error(f"Query with context failed: {e}")
            raise

    def delete_store(self, store_name: Optional[str] = None, force: bool = True) -> bool:
        """
        Delete a file search store.

        Args:
            store_name: Resource name of the store to delete
            force: If True, delete all documents in store too

        Returns:
            True if successful
        """
        try:
            name = store_name or (
                self.file_search_store.name if self.file_search_store else None
            )
            if not name:
                raise ValueError("No store name provided")

            # Delete store (CORRECT API)
            self.client.file_search_stores.delete(
                name=name,
                config={'force': force}
            )

            logger.info(f"Deleted file search store: {name}")
            if name == self.file_search_store.name:
                self.file_search_store = None

            return True

        except Exception as e:
            logger.error(f"Failed to delete store: {e}")
            return False

    def list_stores(self) -> List[Dict[str, Any]]:
        """
        List all file search stores.

        Returns:
            List of store metadata dicts
        """
        try:
            stores = []

            # List stores (CORRECT API)
            for store in self.client.file_search_stores.list():
                stores.append({
                    "name": store.name,
                    "display_name": store.display_name,
                    "create_time": getattr(store, "create_time", None),
                    "update_time": getattr(store, "update_time", None),
                })

            logger.info(f"Found {len(stores)} file search stores")
            return stores

        except Exception as e:
            logger.error(f"Failed to list stores: {e}")
            return []

    def get_store(self, store_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific file search store by name.

        Args:
            store_name: Resource name of the store

        Returns:
            Store metadata dict or None
        """
        try:
            # Get specific store (CORRECT API)
            store = self.client.file_search_stores.get(name=store_name)

            return {
                "name": store.name,
                "display_name": store.display_name,
                "create_time": getattr(store, "create_time", None),
                "update_time": getattr(store, "update_time", None),
            }

        except Exception as e:
            logger.error(f"Failed to get store {store_name}: {e}")
            return None

    def get_store_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current file search store.

        Returns:
            Dict with store statistics
        """
        try:
            if not self.file_search_store:
                self.get_or_create_store()

            return {
                "store_name": self.file_search_store.name,
                "display_name": self.file_search_store.display_name,
                "model": self.model,
                "create_time": getattr(self.file_search_store, "create_time", None),
                "update_time": getattr(self.file_search_store, "update_time", None),
            }

        except Exception as e:
            logger.error(f"Failed to get store stats: {e}")
            return {}

    # Helper methods

    def _extract_grounding_chunks(self, response: Any) -> List[Dict[str, Any]]:
        """Extract grounding chunks from file search response."""
        chunks = []

        if hasattr(response, "candidates"):
            for candidate in response.candidates:
                if hasattr(candidate, "grounding_metadata"):
                    gm = candidate.grounding_metadata
                    if hasattr(gm, "grounding_chunks"):
                        for chunk in gm.grounding_chunks:
                            # For file search, chunks have retrieved_context
                            if hasattr(chunk, "retrieved_context"):
                                rc = chunk.retrieved_context
                                chunks.append({
                                    "title": getattr(rc, "title", ""),
                                    "text": getattr(rc, "text", ""),
                                    "uri": getattr(rc, "uri", ""),
                                })
                            # Fallback for web search grounding (has web attribute)
                            elif hasattr(chunk, "web"):
                                chunks.append({
                                    "title": getattr(chunk.web, "title", ""),
                                    "text": "",
                                    "uri": getattr(chunk.web, "uri", ""),
                                })

        return chunks

    def _extract_grounding_metadata(self, response: Any) -> Dict[str, Any]:
        """Extract grounding metadata from file search response."""
        metadata = {
            "grounding_chunks": [],
            "grounding_supports": [],
            "web_search_queries": [],
        }

        if hasattr(response, "candidates"):
            for candidate in response.candidates:
                if hasattr(candidate, "grounding_metadata"):
                    gm = candidate.grounding_metadata

                    # Extract grounding chunks (for file search)
                    if hasattr(gm, "grounding_chunks"):
                        chunks = []
                        for chunk in gm.grounding_chunks:
                            if hasattr(chunk, "retrieved_context"):
                                rc = chunk.retrieved_context
                                chunks.append({
                                    "title": getattr(rc, "title", ""),
                                    "text": getattr(rc, "text", ""),
                                    "uri": getattr(rc, "uri", ""),
                                })
                        metadata["grounding_chunks"] = chunks

                    # Extract grounding supports (maps text segments to chunks)
                    if hasattr(gm, "grounding_supports"):
                        supports = []
                        for support in gm.grounding_supports:
                            support_data = {
                                "grounding_chunk_indices": getattr(
                                    support, "grounding_chunk_indices", []
                                ),
                            }

                            # Extract segment information
                            if hasattr(support, "segment"):
                                seg = support.segment
                                support_data["segment"] = {
                                    "text": getattr(seg, "text", ""),
                                    "start_index": getattr(seg, "start_index", 0),
                                    "end_index": getattr(seg, "end_index", 0),
                                }

                            # Extract confidence scores if available
                            if hasattr(support, "confidence_scores"):
                                support_data["confidence_scores"] = list(
                                    support.confidence_scores
                                )

                            supports.append(support_data)

                        metadata["grounding_supports"] = supports

                    # Extract web search queries (if using web grounding)
                    if hasattr(gm, "web_search_queries"):
                        metadata["web_search_queries"] = list(gm.web_search_queries)

        return metadata
