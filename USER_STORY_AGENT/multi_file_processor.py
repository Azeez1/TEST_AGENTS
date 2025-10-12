"""
Multi-File Processor Module
Handles processing of multiple input files simultaneously
"""

import os
from typing import List, Dict, Tuple
from note_parser import extract_notes, extract_notes_from_multiple_files


class MultiFileProcessor:
    """Process multiple files for story generation"""

    def __init__(self):
        """Initialize multi-file processor"""
        self.supported_extensions = {
            '.pdf', '.txt', '.md', '.docx', '.xlsx', '.xls',
            '.json', '.csv', '.html', '.htm', '.xml',
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'
        }

    def process_files(self, file_paths: List[str]) -> Dict[str, any]:
        """
        Process multiple files and combine their content

        Args:
            file_paths: List of file paths

        Returns:
            Dictionary with combined content and metadata
        """
        result = {
            "success": True,
            "files_processed": [],
            "files_failed": [],
            "combined_content": "",
            "total_files": len(file_paths),
            "file_types": {}
        }

        # Validate files
        valid_files = []
        for file_path in file_paths:
            if not os.path.exists(file_path):
                result["files_failed"].append({
                    "file": file_path,
                    "reason": "File not found"
                })
                continue

            ext = os.path.splitext(file_path)[1].lower()
            if ext not in self.supported_extensions:
                result["files_failed"].append({
                    "file": file_path,
                    "reason": f"Unsupported file type: {ext}"
                })
                continue

            valid_files.append(file_path)

            # Track file types
            result["file_types"][ext] = result["file_types"].get(ext, 0) + 1

        # Process valid files
        if not valid_files:
            result["success"] = False
            result["combined_content"] = "No valid files to process"
            return result

        try:
            # Use multi-file extraction
            combined_content = extract_notes_from_multiple_files(valid_files)
            result["combined_content"] = combined_content

            # Mark files as processed
            for file_path in valid_files:
                result["files_processed"].append({
                    "file": os.path.basename(file_path),
                    "path": file_path,
                    "type": os.path.splitext(file_path)[1]
                })

        except Exception as e:
            result["success"] = False
            result["combined_content"] = f"Error processing files: {str(e)}"

        return result

    def group_files_by_type(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Group files by their type

        Args:
            file_paths: List of file paths

        Returns:
            Dictionary mapping file types to file lists
        """
        groups = {}

        for file_path in file_paths:
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in groups:
                groups[ext] = []
            groups[ext].append(file_path)

        return groups

    def get_processing_strategy(self, file_paths: List[str]) -> str:
        """
        Determine best processing strategy based on file types

        Args:
            file_paths: List of file paths

        Returns:
            Strategy name
        """
        groups = self.group_files_by_type(file_paths)

        # If all files are the same type
        if len(groups) == 1:
            ext = list(groups.keys())[0]
            if ext in ['.xlsx', '.xls']:
                return "excel_merge"
            elif ext in ['.pdf', '.docx']:
                return "document_concatenate"
            else:
                return "standard_concatenate"

        # Mixed file types
        return "mixed_processing"

    def create_file_summary(self, file_paths: List[str]) -> str:
        """
        Create a summary of files being processed

        Args:
            file_paths: List of file paths

        Returns:
            Summary string
        """
        groups = self.group_files_by_type(file_paths)

        summary_parts = [
            f"Processing {len(file_paths)} files:",
            ""
        ]

        for ext, files in groups.items():
            file_type = self._get_file_type_name(ext)
            summary_parts.append(f"- {len(files)} {file_type} file(s)")

        return "\n".join(summary_parts)

    def _get_file_type_name(self, ext: str) -> str:
        """Get friendly name for file extension"""
        names = {
            '.pdf': 'PDF',
            '.txt': 'Text',
            '.md': 'Markdown',
            '.docx': 'Word',
            '.xlsx': 'Excel',
            '.xls': 'Excel',
            '.json': 'JSON',
            '.csv': 'CSV',
            '.html': 'HTML',
            '.htm': 'HTML',
            '.xml': 'XML',
            '.png': 'PNG Image',
            '.jpg': 'JPEG Image',
            '.jpeg': 'JPEG Image',
            '.gif': 'GIF Image',
            '.bmp': 'BMP Image',
            '.tiff': 'TIFF Image',
            '.webp': 'WebP Image'
        }
        return names.get(ext.lower(), ext.upper())


def process_multiple_files(file_paths: List[str]) -> Tuple[bool, str, Dict]:
    """
    Process multiple files and return combined content

    Args:
        file_paths: List of file paths

    Returns:
        Tuple of (success, combined_content, metadata)
    """
    processor = MultiFileProcessor()
    result = processor.process_files(file_paths)

    return (
        result["success"],
        result["combined_content"],
        {
            "files_processed": result["files_processed"],
            "files_failed": result["files_failed"],
            "file_types": result["file_types"]
        }
    )


def create_multi_file_summary(file_paths: List[str]) -> str:
    """
    Create a summary of files to be processed

    Args:
        file_paths: List of file paths

    Returns:
        Summary string
    """
    processor = MultiFileProcessor()
    return processor.create_file_summary(file_paths)
