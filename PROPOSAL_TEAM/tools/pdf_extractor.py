#!/usr/bin/env python3
"""
PDF Text Extractor for Compliance Documents
Extracts text from PDF files with page tracking and metadata preservation
"""

import os
import sys
from pathlib import Path
from typing import Tuple, List, Dict, Optional
import PyPDF2
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFExtractor:
    """Extract text from PDF files with intelligent section detection"""

    def __init__(self):
        """Initialize PDF extractor"""
        self.section_patterns = {
            'chapter': re.compile(r'^(Chapter|CHAPTER|Section|SECTION)\s+\d+', re.MULTILINE),
            'heading': re.compile(r'^[A-Z][A-Z\s]{3,}$', re.MULTILINE),
            'numbered': re.compile(r'^\d+\.\s+[A-Z]', re.MULTILINE),
            'appendix': re.compile(r'^(Appendix|APPENDIX)\s+[A-Z]', re.MULTILINE),
        }

    def extract_pdf_text(self, pdf_path: str) -> Tuple[str, List[int], Dict]:
        """
        Extract text from PDF with page tracking and metadata.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Tuple of (full_text, page_boundaries, metadata)
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        logger.info(f"Extracting text from: {pdf_path.name}")

        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)

                # Extract metadata
                metadata = self._extract_metadata(reader, pdf_path)

                # Extract text with page tracking
                full_text = ""
                page_boundaries = [0]  # Start at character 0
                page_texts = []

                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()

                    # Clean up text
                    page_text = self._clean_text(page_text)

                    # Add page marker for reference
                    page_marker = f"\n\n[PAGE {page_num + 1}]\n"
                    full_text += page_marker + page_text

                    # Track page boundary
                    page_boundaries.append(len(full_text))
                    page_texts.append(page_text)

                # Detect sections
                sections = self._detect_sections(full_text)
                metadata['sections'] = sections
                metadata['page_texts'] = page_texts

                logger.info(f"Successfully extracted {len(reader.pages)} pages, {len(full_text):,} characters")
                logger.info(f"Detected {len(sections)} sections")

                return full_text, page_boundaries, metadata

        except Exception as e:
            logger.error(f"Error extracting PDF: {str(e)}")
            raise

    def _extract_metadata(self, reader: PyPDF2.PdfReader, pdf_path: Path) -> Dict:
        """Extract PDF metadata with graceful error handling"""
        metadata = {
            'filename': pdf_path.name,
            'path': str(pdf_path),
            'num_pages': len(reader.pages),
            'file_size': pdf_path.stat().st_size,
            'file_size_mb': round(pdf_path.stat().st_size / (1024 * 1024), 2)
        }

        # Try to extract PDF metadata - handle each field individually
        if reader.metadata:
            # Extract title
            try:
                if hasattr(reader.metadata, 'title') and reader.metadata.title:
                    metadata['title'] = reader.metadata.title
            except Exception as e:
                logger.warning(f"Could not extract title: {e}")

            # Extract author
            try:
                if hasattr(reader.metadata, 'author') and reader.metadata.author:
                    metadata['author'] = reader.metadata.author
            except Exception as e:
                logger.warning(f"Could not extract author: {e}")

            # Extract subject
            try:
                if hasattr(reader.metadata, 'subject') and reader.metadata.subject:
                    metadata['subject'] = reader.metadata.subject
            except Exception as e:
                logger.warning(f"Could not extract subject: {e}")

            # Extract creation date (commonly malformed in older PDFs)
            try:
                if hasattr(reader.metadata, 'creation_date') and reader.metadata.creation_date:
                    metadata['creation_date'] = str(reader.metadata.creation_date)
            except Exception as e:
                logger.warning(f"Could not extract creation_date (malformed metadata): {e}")
                # Continue without this field - not critical for indexing

        return metadata

    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Fix common OCR issues
        text = text.replace('  ', ' ')
        text = text.replace('\n \n', '\n\n')

        # Remove page headers/footers if they're repetitive
        # This is a simple heuristic - can be improved
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            # Skip lines that are likely page numbers
            if re.match(r'^\d{1,4}$', line.strip()):
                continue
            # Skip lines that are likely headers/footers
            if len(line.strip()) < 5 and line.strip().isdigit():
                continue
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _detect_sections(self, text: str) -> List[Dict]:
        """Detect sections in the text"""
        sections = []

        for pattern_name, pattern in self.section_patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                sections.append({
                    'type': pattern_name,
                    'title': match.group(0).strip(),
                    'start': match.start(),
                    'end': match.end()
                })

        # Sort sections by position
        sections.sort(key=lambda x: x['start'])

        # Add section content
        for i, section in enumerate(sections):
            if i < len(sections) - 1:
                section['content_end'] = sections[i + 1]['start']
            else:
                section['content_end'] = len(text)

        return sections

    def extract_multiple_pdfs(self, pdf_paths: List[str]) -> List[Tuple[str, List[int], Dict]]:
        """
        Extract text from multiple PDFs.

        Args:
            pdf_paths: List of PDF file paths

        Returns:
            List of (full_text, page_boundaries, metadata) tuples
        """
        results = []

        for pdf_path in pdf_paths:
            try:
                result = self.extract_pdf_text(pdf_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to extract {pdf_path}: {str(e)}")
                continue

        logger.info(f"Successfully extracted {len(results)}/{len(pdf_paths)} PDFs")
        return results

    def get_page_for_character(self, char_position: int, page_boundaries: List[int]) -> int:
        """
        Get the page number for a given character position.

        Args:
            char_position: Character position in the full text
            page_boundaries: List of page boundary positions

        Returns:
            Page number (1-indexed)
        """
        for i, boundary in enumerate(page_boundaries[1:], 1):
            if char_position < boundary:
                return i
        return len(page_boundaries) - 1


def main():
    """Test the PDF extractor"""
    import json

    # Test path
    test_pdf = r"C:\Users\sabaa\OneDrive\Desktop\Compliance Frameworks\CMMC\CMMC_ModelOverview.pdf"

    if not Path(test_pdf).exists():
        print(f"Test PDF not found: {test_pdf}")
        print("Please update the test path to a valid PDF file")
        return

    extractor = PDFExtractor()

    print("Testing PDF extraction...")
    text, boundaries, metadata = extractor.extract_pdf_text(test_pdf)

    print(f"\n=== Extraction Results ===")
    print(f"File: {metadata['filename']}")
    print(f"Pages: {metadata['num_pages']}")
    print(f"Size: {metadata['file_size_mb']} MB")
    print(f"Text length: {len(text):,} characters")
    print(f"Sections found: {len(metadata.get('sections', []))}")

    # Show first 500 characters
    print(f"\n=== First 500 characters ===")
    print(text[:500])

    # Show detected sections
    if metadata.get('sections'):
        print(f"\n=== Detected Sections ===")
        for section in metadata['sections'][:10]:  # Show first 10
            print(f"- {section['type']}: {section['title']}")

    # Test page detection
    test_position = 1000
    page = extractor.get_page_for_character(test_position, boundaries)
    print(f"\nCharacter position {test_position} is on page {page}")


if __name__ == "__main__":
    main()