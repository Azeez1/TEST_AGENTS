"""
Tests for text chunking module.
"""

import pytest
from dux_rfp_agent.chunking import TextChunker


class TestTextChunker:
    """Test text chunking functionality."""

    def test_chunker_init(self):
        """Test chunker initialization."""
        chunker = TextChunker(chunk_size=1000, overlap=100)
        assert chunker.chunk_size == 1000
        assert chunker.overlap == 100

    def test_chunk_document(self):
        """Test document chunking."""
        chunker = TextChunker(chunk_size=500, overlap=50)

        # Create test text
        text = "This is a test sentence. " * 100  # ~2500 chars
        pages = {1: text[:1000], 2: text[1000:]}

        chunks = chunker.chunk_document(text, pages)

        assert len(chunks) > 0
        assert all("text" in chunk for chunk in chunks)
        assert all("page_range" in chunk for chunk in chunks)
        assert all("chunk_id" in chunk for chunk in chunks)

        # Check overlap
        if len(chunks) > 1:
            assert chunks[1]["char_start"] < chunks[0]["char_end"]

    def test_chunk_by_pages(self):
        """Test page-based chunking."""
        chunker = TextChunker()

        pages = {
            1: "Page 1 content",
            2: "Page 2 content",
            3: "Page 3 content",
            4: "Page 4 content",
        }

        chunks = chunker.chunk_by_pages(pages, pages_per_chunk=2)

        assert len(chunks) == 2
        assert chunks[0]["page_range"] == [1, 2]
        assert chunks[1]["page_range"] == [3, 4]
