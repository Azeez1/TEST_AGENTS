"""
Tests for document ingestion module.
"""

import pytest
from pathlib import Path
from dux_rfp_agent.ingestion import DocumentIngestion


class TestDocumentIngestion:
    """Test document ingestion functionality."""

    def test_ingestion_init(self):
        """Test ingestion initialization."""
        ingestion = DocumentIngestion()
        assert ingestion is not None

    def test_normalize_text(self):
        """Test text normalization."""
        ingestion = DocumentIngestion()

        # Test whitespace normalization
        text = "This  is   a    test"
        normalized = ingestion.normalize_text(text)
        assert normalized == "This is a test"

        # Test line break normalization
        text = "Line 1\r\nLine 2\rLine 3\nLine 4"
        normalized = ingestion.normalize_text(text)
        assert "\r" not in normalized

    def test_ingest_txt(self, tmp_path):
        """Test TXT file ingestion."""
        ingestion = DocumentIngestion()

        # Create test file
        test_file = tmp_path / "test.txt"
        test_content = "This is a test document.\n" * 100  # 100 lines
        test_file.write_text(test_content)

        # Ingest
        result = ingestion.ingest(test_file)

        assert "text" in result
        assert "pages" in result
        assert "metadata" in result
        assert len(result["pages"]) >= 2  # Should have multiple pages
        assert result["metadata"]["file_type"] == "txt"

    def test_ingest_nonexistent_file(self):
        """Test ingestion of nonexistent file."""
        ingestion = DocumentIngestion()

        with pytest.raises(FileNotFoundError):
            ingestion.ingest(Path("/nonexistent/file.pdf"))

    def test_ingest_unsupported_format(self, tmp_path):
        """Test ingestion of unsupported file format."""
        ingestion = DocumentIngestion()

        test_file = tmp_path / "test.xyz"
        test_file.write_text("test")

        with pytest.raises(ValueError, match="Unsupported file type"):
            ingestion.ingest(test_file)
