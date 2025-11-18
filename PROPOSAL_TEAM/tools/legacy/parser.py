"""
RFP Parser - extracts structured requirements from RFP text using LLM.
"""

import json
import re
from typing import Dict, List

from jsonschema import validate

from .chunking import TextChunker
from .config import config
from .llm_client import LLMClient
from .logger import logger


class RFPParser:
    """Parse RFP documents and extract requirements."""

    def __init__(self):
        """Initialize parser."""
        self.llm = LLMClient()
        self.chunker = TextChunker()

        # Load schema for validation
        schema_path = config.schemas_dir / "requirements.schema.json"
        with open(schema_path, "r") as f:
            self.schema = json.load(f)

        # Load prompt template
        self.prompt_template = config.get_prompt("parser")

    def parse_rfp(self, text: str, pages: Dict[int, str]) -> Dict[str, any]:
        """
        Parse RFP and extract all requirements.

        Args:
            text: Full RFP text
            pages: Page mapping

        Returns:
            {
                'requirements': [...],
                'metadata': {...}
            }
        """
        logger.info("Starting RFP parsing")

        # Chunk the document
        chunks = self.chunker.chunk_document(text, pages)
        logger.info(f"Processing {len(chunks)} chunks")

        all_requirements = []

        # Process each chunk
        for i, chunk in enumerate(chunks):
            logger.info(f"Parsing chunk {i + 1}/{len(chunks)}")

            try:
                chunk_requirements = self._parse_chunk(chunk)
                all_requirements.extend(chunk_requirements)
                logger.info(f"Extracted {len(chunk_requirements)} requirements from chunk {i + 1}")

            except Exception as e:
                logger.error(f"Failed to parse chunk {i + 1}: {e}")
                continue

        # Merge and deduplicate requirements
        merged_requirements = self._merge_requirements(all_requirements)

        # Assign stable IDs
        for i, req in enumerate(merged_requirements, 1):
            req["id"] = f"R-{i:03d}"

        # Count by priority
        must_count = sum(1 for r in merged_requirements if r["priority"] in ["MUST", "SHALL"])
        shall_count = sum(1 for r in merged_requirements if r["priority"] == "SHALL")
        should_count = sum(1 for r in merged_requirements if r["priority"] == "SHOULD")

        result = {
            "requirements": merged_requirements,
            "metadata": {
                "total_requirements": len(merged_requirements),
                "must_count": must_count,
                "shall_count": shall_count,
                "should_count": should_count,
            },
        }

        # Validate against schema
        try:
            validate(instance=result, schema=self.schema)
            logger.info("Requirements validation passed")
        except Exception as e:
            logger.warning(f"Schema validation failed: {e}")

        return result

    def _parse_chunk(self, chunk: Dict[str, any]) -> List[Dict[str, any]]:
        """
        Parse a single chunk and extract requirements.

        Args:
            chunk: Chunk dictionary with text and page_range

        Returns:
            List of requirement dictionaries
        """
        # Format prompt
        page_range_str = f"Pages {min(chunk['page_range'])}-{max(chunk['page_range'])}"

        prompt = self.prompt_template.format(
            chunk_text=chunk["text"], page_range=page_range_str
        )

        # Get LLM response
        response = self.llm.complete_json(
            prompt=prompt, model=config.llm.model_small, temperature=0.1, max_tokens=4000
        )

        # Extract requirements
        requirements = response.get("requirements", [])

        # Add chunk metadata to each requirement
        for req in requirements:
            if "source_pages" not in req or not req["source_pages"]:
                req["source_pages"] = chunk["page_range"]

        return requirements

    def _merge_requirements(self, requirements: List[Dict]) -> List[Dict]:
        """
        Merge and deduplicate requirements from multiple chunks.

        Args:
            requirements: List of all requirements from all chunks

        Returns:
            Deduplicated list
        """
        logger.info(f"Merging {len(requirements)} total requirements")

        # Group by normalized text
        groups = {}

        for req in requirements:
            # Normalize text for comparison
            normalized = self._normalize_text(req["text"])

            if normalized in groups:
                # Merge: combine page numbers
                existing = groups[normalized]
                existing["source_pages"] = sorted(
                    list(set(existing["source_pages"] + req["source_pages"]))
                )

                # Keep higher priority
                priority_order = ["MUST", "SHALL", "SHOULD", "MAY", "OPTIONAL"]
                if priority_order.index(req["priority"]) < priority_order.index(
                    existing["priority"]
                ):
                    existing["priority"] = req["priority"]

            else:
                groups[normalized] = req

        merged = list(groups.values())
        logger.info(f"After deduplication: {len(merged)} unique requirements")

        return merged

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        # Remove extra whitespace
        text = " ".join(text.split())

        # Remove common variations
        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)

        return text
