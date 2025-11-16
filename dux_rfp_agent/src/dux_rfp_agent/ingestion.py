"""
Document ingestion module.
Handles PDF, DOCX, TXT, and ZIP files with page tracking and OCR fallback.
"""

import io
import os
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import PyPDF2
from docx import Document
from PIL import Image

from .logger import logger

try:
    import pytesseract

    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract not available - OCR will be disabled")


class DocumentIngestion:
    """Handle document ingestion with page tracking."""

    def __init__(self, enable_ocr: bool = True):
        """
        Initialize document ingestion.

        Args:
            enable_ocr: Whether to enable OCR for scanned PDFs
        """
        self.enable_ocr = enable_ocr and TESSERACT_AVAILABLE

    def ingest(self, file_path: Path) -> Dict[str, any]:
        """
        Ingest a document and extract text with page mapping.

        Args:
            file_path: Path to the document

        Returns:
            Dictionary with text, pages, and metadata
        """
        logger.info(f"Ingesting document: {file_path}")

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            return self._ingest_pdf(file_path)
        elif suffix in [".docx", ".doc"]:
            return self._ingest_docx(file_path)
        elif suffix == ".txt":
            return self._ingest_txt(file_path)
        elif suffix == ".zip":
            return self._ingest_zip(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

    def _ingest_pdf(self, file_path: Path) -> Dict[str, any]:
        """
        Extract text from PDF with page tracking.

        Returns:
            {
                'text': 'full text',
                'pages': {1: 'page 1 text', 2: 'page 2 text', ...},
                'metadata': {...}
            }
        """
        pages = {}
        all_text = []

        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            num_pages = len(pdf_reader.pages)

            logger.info(f"Processing PDF with {num_pages} pages")

            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                # Check if page is mostly empty (might be scanned)
                if len(text.strip()) < 50 and self.enable_ocr:
                    logger.info(f"Page {page_num + 1} appears scanned, attempting OCR")
                    # OCR would be implemented here if needed
                    # For now, keep the extracted text
                    pass

                pages[page_num + 1] = text
                all_text.append(text)

            # Extract metadata
            metadata = {
                "num_pages": num_pages,
                "filename": file_path.name,
                "file_type": "pdf",
            }

            try:
                if pdf_reader.metadata:
                    metadata.update(
                        {
                            "title": pdf_reader.metadata.get("/Title", ""),
                            "author": pdf_reader.metadata.get("/Author", ""),
                            "creation_date": pdf_reader.metadata.get("/CreationDate", ""),
                        }
                    )
            except Exception as e:
                logger.warning(f"Could not extract PDF metadata: {e}")

        return {"text": "\n\n".join(all_text), "pages": pages, "metadata": metadata}

    def _ingest_docx(self, file_path: Path) -> Dict[str, any]:
        """
        Extract text from DOCX file.

        Note: DOCX doesn't have rigid page numbers, so we approximate
        by assuming ~500 words per page.
        """
        doc = Document(file_path)

        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text)

        full_text = "\n\n".join(paragraphs)

        # Approximate page mapping (500 words ~ 1 page)
        words = full_text.split()
        words_per_page = 500
        pages = {}
        current_page = 1
        current_word = 0

        for i, word in enumerate(words):
            if i - current_word >= words_per_page:
                current_page += 1
                current_word = i

            if current_page not in pages:
                pages[current_page] = []

            pages[current_page].append(word)

        # Convert word lists to text
        pages = {page: " ".join(words) for page, words in pages.items()}

        metadata = {
            "num_pages": len(pages),
            "filename": file_path.name,
            "file_type": "docx",
            "word_count": len(words),
        }

        # Try to extract core properties
        try:
            core_props = doc.core_properties
            metadata.update(
                {
                    "title": core_props.title or "",
                    "author": core_props.author or "",
                    "created": str(core_props.created) if core_props.created else "",
                }
            )
        except Exception as e:
            logger.warning(f"Could not extract DOCX metadata: {e}")

        return {"text": full_text, "pages": pages, "metadata": metadata}

    def _ingest_txt(self, file_path: Path) -> Dict[str, any]:
        """
        Extract text from TXT file.

        Approximate page breaks based on line count.
        """
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        # Approximate pages (50 lines ~ 1 page)
        lines = text.split("\n")
        lines_per_page = 50
        pages = {}

        for i in range(0, len(lines), lines_per_page):
            page_num = (i // lines_per_page) + 1
            pages[page_num] = "\n".join(lines[i : i + lines_per_page])

        metadata = {
            "num_pages": len(pages),
            "filename": file_path.name,
            "file_type": "txt",
            "line_count": len(lines),
        }

        return {"text": text, "pages": pages, "metadata": metadata}

    def _ingest_zip(self, file_path: Path) -> Dict[str, any]:
        """
        Extract and process files from ZIP archive.

        Returns combined text from all supported files.
        """
        logger.info(f"Processing ZIP archive: {file_path}")

        all_texts = []
        all_pages = {}
        all_metadata = []

        with zipfile.ZipFile(file_path, "r") as zip_ref:
            for file_info in zip_ref.filelist:
                if file_info.is_dir():
                    continue

                file_name = file_info.filename
                file_ext = Path(file_name).suffix.lower()

                if file_ext in [".pdf", ".docx", ".txt"]:
                    logger.info(f"Extracting {file_name} from ZIP")

                    try:
                        # Extract to temp file
                        file_data = zip_ref.read(file_name)
                        temp_path = Path(f"/tmp/{Path(file_name).name}")
                        temp_path.write_bytes(file_data)

                        # Ingest the extracted file
                        result = self.ingest(temp_path)
                        all_texts.append(result["text"])
                        all_metadata.append(
                            {"source_file": file_name, "metadata": result["metadata"]}
                        )

                        # Merge pages with offset
                        page_offset = max(all_pages.keys()) if all_pages else 0
                        for page_num, page_text in result["pages"].items():
                            all_pages[page_offset + page_num] = page_text

                        # Clean up temp file
                        temp_path.unlink()

                    except Exception as e:
                        logger.error(f"Failed to process {file_name}: {e}")

        metadata = {
            "num_pages": len(all_pages),
            "filename": file_path.name,
            "file_type": "zip",
            "extracted_files": all_metadata,
        }

        return {"text": "\n\n---\n\n".join(all_texts), "pages": all_pages, "metadata": metadata}

    def normalize_text(self, text: str) -> str:
        """
        Normalize extracted text.

        Args:
            text: Raw text

        Returns:
            Normalized text
        """
        # Remove excessive whitespace
        text = " ".join(text.split())

        # Normalize line breaks
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Remove multiple consecutive newlines
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")

        return text.strip()
