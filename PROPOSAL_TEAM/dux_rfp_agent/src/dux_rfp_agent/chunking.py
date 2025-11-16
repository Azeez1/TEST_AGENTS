"""
Semantic text chunking with page-range metadata tracking.
Chunks by document structure, not arbitrary character counts.
"""

import re
from typing import Dict, List, Tuple

from .config import config
from .logger import logger


class TextChunker:
    """Chunk text by semantic boundaries while preserving page range metadata."""

    def __init__(self, max_chunk_size: int = None, target_chunk_size: int = None):
        """
        Initialize semantic chunker.

        Args:
            max_chunk_size: Maximum chunk size (hard limit)
            target_chunk_size: Target chunk size (soft guideline)
        """
        self.max_chunk_size = max_chunk_size or config.chunk_size
        self.target_chunk_size = target_chunk_size or (config.chunk_size // 2)

    def chunk_document(self, text: str, pages: Dict[int, str]) -> List[Dict[str, any]]:
        """
        Chunk document text by semantic boundaries while tracking page ranges.

        Uses semantic boundaries in order of preference:
        1. Section headers (SECTION X:, 1., 1.1, etc.)
        2. Requirement blocks (paragraphs with MUST/SHALL/SHOULD/MAY)
        3. Paragraph boundaries
        4. Sentence boundaries (fallback)

        Args:
            text: Full document text
            pages: Dictionary mapping page numbers to page text

        Returns:
            List of chunks with metadata
        """
        logger.info(
            f"Semantic chunking: {len(text)} chars, "
            f"{len(pages)} pages, target={self.target_chunk_size}, max={self.max_chunk_size}"
        )

        # Build position-to-page mapping
        page_map = self._build_page_map(text, pages)

        # Detect semantic boundaries
        boundaries = self._detect_semantic_boundaries(text)

        # Create chunks from boundaries
        chunks = self._create_chunks_from_boundaries(text, boundaries, page_map)

        logger.info(f"Created {len(chunks)} semantic chunks")
        return chunks

    def _detect_semantic_boundaries(self, text: str) -> List[Tuple[int, str, str]]:
        """
        Detect semantic boundaries in text.

        Returns:
            List of (position, boundary_type, context) tuples
            boundary_type: 'section', 'requirement', 'paragraph', 'sentence'
        """
        boundaries = []

        # 1. Section headers (highest priority)
        # Patterns: "SECTION 1:", "1.", "1.1", "Chapter 1", etc.
        section_patterns = [
            (r'^SECTION\s+\d+[:\.].*$', 'section'),
            (r'^CHAPTER\s+\d+[:\.].*$', 'section'),
            (r'^\d+\.\s+[A-Z]', 'section'),  # "1. REQUIREMENTS"
            (r'^\d+\.\d+\s+[A-Z]', 'subsection'),  # "1.1 Technical"
            (r'^[A-Z\s]{3,}:?\s*$', 'heading'),  # "TECHNICAL REQUIREMENTS:"
        ]

        for pattern, btype in section_patterns:
            for match in re.finditer(pattern, text, re.MULTILINE):
                boundaries.append((match.start(), btype, match.group().strip()))

        # 2. Requirement blocks (high priority)
        # Look for paragraphs containing modal verbs
        requirement_keywords = r'\b(MUST|SHALL|SHOULD|MAY|REQUIRED|MANDATORY|OPTIONAL)\b'

        # Split into paragraphs
        paragraphs = text.split('\n\n')
        pos = 0
        for para in paragraphs:
            if re.search(requirement_keywords, para, re.IGNORECASE):
                boundaries.append((pos, 'requirement', para[:50]))
            pos += len(para) + 2  # +2 for \n\n

        # 3. Paragraph boundaries (medium priority)
        for match in re.finditer(r'\n\n+', text):
            boundaries.append((match.start(), 'paragraph', ''))

        # Sort by position
        boundaries.sort(key=lambda x: x[0])

        # Remove duplicates (keep highest priority at each position)
        priority_order = {'section': 0, 'subsection': 1, 'requirement': 2,
                         'heading': 3, 'paragraph': 4, 'sentence': 5}

        unique_boundaries = []
        last_pos = -1
        for pos, btype, context in boundaries:
            if pos != last_pos:
                unique_boundaries.append((pos, btype, context))
                last_pos = pos
            else:
                # Keep higher priority boundary
                if priority_order.get(btype, 99) < priority_order.get(unique_boundaries[-1][1], 99):
                    unique_boundaries[-1] = (pos, btype, context)

        logger.debug(f"Detected {len(unique_boundaries)} semantic boundaries")
        return unique_boundaries

    def _create_chunks_from_boundaries(
        self, text: str, boundaries: List[Tuple[int, str, str]], page_map: Dict[int, int]
    ) -> List[Dict]:
        """
        Create chunks from detected semantic boundaries.

        Strategy:
        - Build chunks by combining segments between boundaries
        - Respect target_chunk_size but never exceed max_chunk_size
        - Keep sections together when possible
        - Keep requirements together (never split mid-requirement)
        """
        chunks = []
        chunk_id = 0

        if not boundaries:
            # No boundaries found, fall back to simple chunking
            logger.warning("No semantic boundaries detected, using simple chunking")
            return self._fallback_chunk(text, page_map)

        # Add start and end boundaries
        all_boundaries = [(0, 'start', '')] + boundaries + [(len(text), 'end', '')]

        current_chunk_start = 0
        current_chunk_segments = []
        current_chunk_size = 0

        for i in range(len(all_boundaries) - 1):
            pos, btype, context = all_boundaries[i]
            next_pos = all_boundaries[i + 1][0]

            segment = text[pos:next_pos]
            segment_size = len(segment)

            # Decision: add to current chunk or start new chunk?
            if current_chunk_size == 0:
                # First segment, always add
                current_chunk_segments.append(segment)
                current_chunk_size += segment_size
                current_chunk_start = pos

            elif current_chunk_size + segment_size <= self.max_chunk_size:
                # Within max size, add to current chunk
                current_chunk_segments.append(segment)
                current_chunk_size += segment_size

            else:
                # Would exceed max size

                # Special case: if this is a section header or requirement,
                # keep it with next chunk (don't orphan headers)
                if btype in ['section', 'subsection', 'requirement'] and segment_size < self.max_chunk_size:
                    # Finalize current chunk
                    if current_chunk_segments:
                        chunk_text = ''.join(current_chunk_segments).strip()
                        if chunk_text:
                            chunks.append(self._create_chunk(
                                chunk_text, chunk_id, current_chunk_start,
                                current_chunk_start + current_chunk_size, page_map
                            ))
                            chunk_id += 1

                    # Start new chunk with this segment
                    current_chunk_segments = [segment]
                    current_chunk_size = segment_size
                    current_chunk_start = pos

                else:
                    # Finalize current chunk
                    if current_chunk_segments:
                        chunk_text = ''.join(current_chunk_segments).strip()
                        if chunk_text:
                            chunks.append(self._create_chunk(
                                chunk_text, chunk_id, current_chunk_start,
                                current_chunk_start + current_chunk_size, page_map
                            ))
                            chunk_id += 1

                    # If segment itself is too large, split it
                    if segment_size > self.max_chunk_size:
                        sub_chunks = self._split_large_segment(segment, pos, page_map, chunk_id)
                        chunks.extend(sub_chunks)
                        chunk_id += len(sub_chunks)
                        current_chunk_segments = []
                        current_chunk_size = 0
                        current_chunk_start = next_pos
                    else:
                        current_chunk_segments = [segment]
                        current_chunk_size = segment_size
                        current_chunk_start = pos

        # Add final chunk
        if current_chunk_segments:
            chunk_text = ''.join(current_chunk_segments).strip()
            if chunk_text:
                chunks.append(self._create_chunk(
                    chunk_text, chunk_id, current_chunk_start,
                    current_chunk_start + current_chunk_size, page_map
                ))

        return chunks

    def _create_chunk(
        self, text: str, chunk_id: int, start: int, end: int, page_map: Dict[int, int]
    ) -> Dict:
        """Create a chunk with metadata."""
        page_range = self._get_page_range(start, end, page_map)

        return {
            "text": text,
            "chunk_id": chunk_id,
            "page_range": sorted(list(set(page_range))),
            "char_start": start,
            "char_end": end,
            "char_count": len(text),
        }

    def _split_large_segment(
        self, segment: str, base_pos: int, page_map: Dict[int, int], start_id: int
    ) -> List[Dict]:
        """Split a segment that's larger than max_chunk_size."""
        sub_chunks = []
        chunk_id = start_id

        # Try to split by paragraph
        paragraphs = segment.split('\n\n')
        current_text = []
        current_size = 0
        current_start = base_pos

        for para in paragraphs:
            para_size = len(para) + 2  # +2 for \n\n

            if current_size + para_size <= self.max_chunk_size:
                current_text.append(para)
                current_size += para_size
            else:
                # Finalize current chunk
                if current_text:
                    chunk_text = '\n\n'.join(current_text)
                    sub_chunks.append(self._create_chunk(
                        chunk_text, chunk_id, current_start,
                        current_start + current_size, page_map
                    ))
                    chunk_id += 1
                    current_start += current_size

                # Start new chunk
                current_text = [para]
                current_size = para_size

        # Add final sub-chunk
        if current_text:
            chunk_text = '\n\n'.join(current_text)
            sub_chunks.append(self._create_chunk(
                chunk_text, chunk_id, current_start,
                current_start + current_size, page_map
            ))

        return sub_chunks

    def _fallback_chunk(self, text: str, page_map: Dict[int, int]) -> List[Dict]:
        """Fallback to simple paragraph-based chunking."""
        logger.info("Using fallback paragraph-based chunking")

        chunks = []
        chunk_id = 0
        paragraphs = text.split('\n\n')

        current_text = []
        current_size = 0
        current_start = 0

        for para in paragraphs:
            para_size = len(para) + 2

            if current_size + para_size <= self.max_chunk_size:
                current_text.append(para)
                current_size += para_size
            else:
                if current_text:
                    chunk_text = '\n\n'.join(current_text)
                    chunks.append(self._create_chunk(
                        chunk_text, chunk_id, current_start,
                        current_start + current_size, page_map
                    ))
                    chunk_id += 1
                    current_start += current_size

                current_text = [para]
                current_size = para_size

        if current_text:
            chunk_text = '\n\n'.join(current_text)
            chunks.append(self._create_chunk(
                chunk_text, chunk_id, current_start,
                current_start + current_size, page_map
            ))

        return chunks

    def _build_page_map(self, full_text: str, pages: Dict[int, str]) -> Dict[int, int]:
        """Build a mapping from character position to page number."""
        page_map = {}
        current_pos = 0

        sorted_pages = sorted(pages.items())

        for page_num, page_text in sorted_pages:
            page_start = full_text.find(page_text, current_pos)

            if page_start == -1:
                logger.warning(f"Could not locate page {page_num} in full text, estimating")
                continue

            page_end = page_start + len(page_text)

            for i in range(page_start, page_end):
                page_map[i] = page_num

            current_pos = page_end

        return page_map

    def _get_page_range(self, start: int, end: int, page_map: Dict[int, int]) -> List[int]:
        """Get page range for a character range."""
        pages = set()

        for i in range(start, min(end, max(page_map.keys(), default=0) + 1)):
            if i in page_map:
                pages.add(page_map[i])

        if not pages:
            # Rough estimate: 3000 chars per page
            estimated_page = (start // 3000) + 1
            pages.add(estimated_page)

        return list(pages)

    def chunk_by_pages(self, pages: Dict[int, str], pages_per_chunk: int = 3) -> List[Dict]:
        """
        Alternative chunking strategy: group by pages.
        Useful when semantic chunking is not needed.
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
                    "char_count": len(chunk_text),
                }
            )

            chunk_id += 1

        logger.info(f"Created {len(chunks)} page-based chunks")
        return chunks
