"""
Text chunking with page-range metadata tracking.
"""

from typing import Dict, List, Tuple

from .config import config
from .logger import logger


class TextChunker:
    """Chunk text while preserving page range metadata."""

    def __init__(self, chunk_size: int = None, overlap: int = None):
        """
        Initialize chunker.

        Args:
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size or config.chunk_size
        self.overlap = overlap or config.chunk_overlap

    def chunk_document(self, text: str, pages: Dict[int, str]) -> List[Dict[str, any]]:
        """
        Chunk document text while tracking page ranges.

        Args:
            text: Full document text
            pages: Dictionary mapping page numbers to page text

        Returns:
            List of chunks with metadata:
            [
                {
                    'text': 'chunk text',
                    'chunk_id': 0,
                    'page_range': [1, 2, 3],
                    'char_start': 0,
                    'char_end': 6000
                },
                ...
            ]
        """
        logger.info(
            f"Chunking document: {len(text)} chars, "
            f"{len(pages)} pages, chunk_size={self.chunk_size}, overlap={self.overlap}"
        )

        # Build position-to-page mapping
        page_map = self._build_page_map(text, pages)

        chunks = []
        start = 0
        chunk_id = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))

            # Try to break at sentence or paragraph boundary
            chunk_text = text[start:end]

            # If not at the end, try to find a good break point
            if end < len(text):
                # Look for paragraph break first
                last_para = chunk_text.rfind("\n\n")
                if last_para > self.chunk_size * 0.7:  # At least 70% through chunk
                    end = start + last_para + 2
                else:
                    # Look for sentence break
                    last_period = max(
                        chunk_text.rfind(". "), chunk_text.rfind(".\n"), chunk_text.rfind("! ")
                    )
                    if last_period > self.chunk_size * 0.7:
                        end = start + last_period + 2

            chunk_text = text[start:end].strip()

            # Determine page range for this chunk
            page_range = self._get_page_range(start, end, page_map)

            chunks.append(
                {
                    "text": chunk_text,
                    "chunk_id": chunk_id,
                    "page_range": sorted(list(set(page_range))),
                    "char_start": start,
                    "char_end": end,
                }
            )

            # Move to next chunk with overlap
            start = end - self.overlap
            chunk_id += 1

        logger.info(f"Created {len(chunks)} chunks")
        return chunks

    def _build_page_map(self, full_text: str, pages: Dict[int, str]) -> Dict[int, int]:
        """
        Build a mapping from character position to page number.

        Args:
            full_text: Full document text
            pages: Page number to text mapping

        Returns:
            Dictionary mapping character index to page number
        """
        page_map = {}
        current_pos = 0

        # Sort pages by number
        sorted_pages = sorted(pages.items())

        for page_num, page_text in sorted_pages:
            # Find where this page text appears in the full text
            page_start = full_text.find(page_text, current_pos)

            if page_start == -1:
                # Fallback: estimate based on position
                logger.warning(f"Could not locate page {page_num} in full text, estimating")
                continue

            page_end = page_start + len(page_text)

            # Map all characters in this page
            for i in range(page_start, page_end):
                page_map[i] = page_num

            current_pos = page_end

        return page_map

    def _get_page_range(self, start: int, end: int, page_map: Dict[int, int]) -> List[int]:
        """
        Get page range for a character range.

        Args:
            start: Start character position
            end: End character position
            page_map: Character to page mapping

        Returns:
            List of page numbers
        """
        pages = set()

        for i in range(start, end):
            if i in page_map:
                pages.add(page_map[i])

        # If no pages found, estimate
        if not pages:
            # Rough estimate: 3000 chars per page
            estimated_page = (start // 3000) + 1
            pages.add(estimated_page)

        return list(pages)

    def chunk_by_pages(self, pages: Dict[int, str], pages_per_chunk: int = 3) -> List[Dict]:
        """
        Alternative chunking strategy: group by pages.

        Args:
            pages: Dictionary mapping page numbers to text
            pages_per_chunk: Number of pages per chunk

        Returns:
            List of chunks
        """
        logger.info(f"Chunking by pages: {len(pages)} pages, {pages_per_chunk} per chunk")

        chunks = []
        sorted_pages = sorted(pages.items())
        chunk_id = 0

        for i in range(0, len(sorted_pages), pages_per_chunk):
            page_batch = sorted_pages[i : i + pages_per_chunk]
            page_numbers = [p[0] for p in page_batch]
            chunk_text = "\n\n".join([p[1] for p in page_batch])

            chunks.append(
                {
                    "text": chunk_text,
                    "chunk_id": chunk_id,
                    "page_range": page_numbers,
                    "pages": page_numbers,
                }
            )

            chunk_id += 1

        logger.info(f"Created {len(chunks)} page-based chunks")
        return chunks
