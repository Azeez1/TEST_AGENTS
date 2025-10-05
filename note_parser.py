"""
Note Parser Module
Handles parsing of raw meeting notes from various formats (PDF, text, docx)
"""

import PyPDF2
import os
from typing import Dict, List, Optional


class NoteParser:
    """Parse raw meeting notes into structured data"""

    def __init__(self):
        self.supported_formats = ['.pdf', '.txt', '.md']

    def parse_file(self, file_path: str) -> str:
        """
        Parse a file and return its content as text

        Args:
            file_path: Path to the notes file

        Returns:
            Raw text content from the file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.pdf':
            return self._parse_pdf(file_path)
        elif file_ext in ['.txt', '.md']:
            return self._parse_text(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}. Supported: {self.supported_formats}")

    def _parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")

        return text.strip()

    def _parse_text(self, file_path: str) -> str:
        """Read plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            raise Exception(f"Error reading text file: {str(e)}")

    def parse_text(self, text: str) -> str:
        """
        Parse raw text input (for interactive mode)

        Args:
            text: Raw text notes

        Returns:
            Cleaned text
        """
        return text.strip()


def extract_notes(input_source: str) -> str:
    """
    Main entry point for note extraction

    Args:
        input_source: File path or raw text

    Returns:
        Extracted text content
    """
    parser = NoteParser()

    # Check if input is a file path
    if os.path.exists(input_source):
        return parser.parse_file(input_source)
    else:
        # Treat as raw text
        return parser.parse_text(input_source)
