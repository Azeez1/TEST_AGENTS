"""
File Handlers Module
Handles multiple file formats for input processing
"""

import os
import json
import csv
from typing import Union, List, Dict
from io import StringIO
import pandas as pd
from bs4 import BeautifulSoup


class FileHandler:
    """Base class for file handlers"""

    @staticmethod
    def detect_file_type(file_path: str) -> str:
        """Detect file type from extension"""
        _, ext = os.path.splitext(file_path)
        return ext.lower()

    @staticmethod
    def read_file(file_path: str) -> str:
        """Read file and return text content"""
        ext = FileHandler.detect_file_type(file_path)

        handlers = {
            '.json': JSONHandler.read,
            '.csv': CSVHandler.read,
            '.html': HTMLHandler.read,
            '.htm': HTMLHandler.read,
            '.xml': XMLHandler.read,
            # Images handled by ocr_handler
            '.png': lambda f: None,
            '.jpg': lambda f: None,
            '.jpeg': lambda f: None,
        }

        if ext in handlers:
            return handlers[ext](file_path)
        else:
            # Default: read as text
            return TextHandler.read(file_path)


class TextHandler:
    """Handle plain text files"""

    @staticmethod
    def read(file_path: str) -> str:
        """Read plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()


class JSONHandler:
    """Handle JSON files"""

    @staticmethod
    def read(file_path: str) -> str:
        """Read and format JSON data"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert JSON to readable text format
        return JSONHandler.format_json(data)

    @staticmethod
    def format_json(data: Union[dict, list], indent: int = 0) -> str:
        """Format JSON data as readable text"""
        lines = []
        prefix = "  " * indent

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{prefix}{key}:")
                    lines.append(JSONHandler.format_json(value, indent + 1))
                else:
                    lines.append(f"{prefix}{key}: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    lines.append(f"{prefix}Item {i + 1}:")
                    lines.append(JSONHandler.format_json(item, indent + 1))
                else:
                    lines.append(f"{prefix}- {item}")
        else:
            lines.append(f"{prefix}{data}")

        return "\n".join(lines)


class CSVHandler:
    """Handle CSV files"""

    @staticmethod
    def read(file_path: str) -> str:
        """Read and format CSV data"""
        try:
            # Try with pandas first (handles various CSV formats well)
            df = pd.read_csv(file_path)
            return CSVHandler.format_dataframe(df)
        except Exception:
            # Fallback to basic CSV reading
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                lines = []
                for row in reader:
                    lines.append(" | ".join(row))
                return "\n".join(lines)

    @staticmethod
    def format_dataframe(df: pd.DataFrame) -> str:
        """Format DataFrame as readable text"""
        lines = []
        lines.append(f"Data with {len(df)} rows and {len(df.columns)} columns:\n")

        # Add column headers
        lines.append(" | ".join(df.columns))
        lines.append("-" * 80)

        # Add rows (limit to first 100 rows to avoid overwhelming)
        for idx, row in df.head(100).iterrows():
            lines.append(" | ".join(str(val) for val in row.values))

        if len(df) > 100:
            lines.append(f"\n... and {len(df) - 100} more rows")

        return "\n".join(lines)


class HTMLHandler:
    """Handle HTML files"""

    @staticmethod
    def read(file_path: str) -> str:
        """Read and extract text from HTML"""
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'lxml')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text


class XMLHandler:
    """Handle XML files"""

    @staticmethod
    def read(file_path: str) -> str:
        """Read and extract text from XML"""
        with open(file_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()

        soup = BeautifulSoup(xml_content, 'xml')

        # Get text content
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        text = '\n'.join(line for line in lines if line)

        return text


def read_any_file(file_path: str) -> str:
    """
    Read any supported file format and return text content

    Args:
        file_path: Path to the file

    Returns:
        Text content of the file
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    return FileHandler.read_file(file_path)


def read_multiple_files(file_paths: List[str]) -> str:
    """
    Read multiple files and combine their content

    Args:
        file_paths: List of file paths

    Returns:
        Combined text content with file separators
    """
    combined_content = []

    for file_path in file_paths:
        filename = os.path.basename(file_path)
        combined_content.append(f"\n{'='*80}\n")
        combined_content.append(f"FILE: {filename}\n")
        combined_content.append(f"{'='*80}\n")

        try:
            content = read_any_file(file_path)
            combined_content.append(content)
        except Exception as e:
            combined_content.append(f"Error reading file: {str(e)}")

    return "\n".join(combined_content)
