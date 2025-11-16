"""
Compliance matrix builder.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Optional

from jsonschema import validate

from .config import config
from .llm_client import LLMClient
from .logger import logger


class ComplianceMatrixBuilder:
    """Build compliance matrix from requirements and KB evidence."""

    def __init__(self):
        """Initialize compliance matrix builder."""
        self.llm = LLMClient()

        # Load schema
        schema_path = config.schemas_dir / "compliance.schema.json"
        with open(schema_path, "r") as f:
            self.schema = json.load(f)

        # Load prompt template
        self.prompt_template = config.get_prompt("compliance_matrix")

    def build_matrix(
        self, requirements: List[Dict], kb_evidence: Optional[Dict[str, List[Dict]]] = None
    ) -> Dict[str, any]:
        """
        Build compliance matrix for all requirements.

        Args:
            requirements: List of requirements
            kb_evidence: Optional KB evidence mapping (req_id -> docs)

        Returns:
            {
                'compliance_items': [...],
                'metadata': {...}
            }
        """
        logger.info(f"Building compliance matrix for {len(requirements)} requirements")

        kb_evidence = kb_evidence or {}

        # Process in batches
        batch_size = config.agents.get("compliance_builder", {}).get("batch_size", 25)
        all_items = []

        for i in range(0, len(requirements), batch_size):
            batch = requirements[i : i + batch_size]
            logger.info(f"Processing compliance batch {i // batch_size + 1}")

            try:
                batch_items = self._process_batch(batch, kb_evidence)
                all_items.extend(batch_items)

            except Exception as e:
                logger.error(f"Failed to process batch: {e}")
                # Create fallback entries
                for req in batch:
                    all_items.append(self._create_fallback_entry(req))

        result = {"compliance_items": all_items}

        # Validate
        try:
            validate(instance=result, schema=self.schema)
            logger.info("Compliance matrix validation passed")
        except Exception as e:
            logger.warning(f"Schema validation failed: {e}")

        return result

    def _process_batch(
        self, requirements: List[Dict], kb_evidence: Dict[str, List[Dict]]
    ) -> List[Dict]:
        """
        Process a batch of requirements.

        Args:
            requirements: Batch of requirements
            kb_evidence: KB evidence mapping

        Returns:
            List of compliance items
        """
        # Format requirements for prompt
        requirements_json = json.dumps(requirements, indent=2)

        # Build KB context
        kb_context = self._format_kb_context(requirements, kb_evidence)

        # Format prompt
        prompt = self.prompt_template.format(
            requirements_json=requirements_json, kb_context=kb_context
        )

        # Get LLM response
        response = self.llm.complete_json(
            prompt=prompt, model=config.llm.model_strong, temperature=0.3, max_tokens=6000
        )

        return response.get("compliance_items", [])

    def _format_kb_context(
        self, requirements: List[Dict], kb_evidence: Dict[str, List[Dict]]
    ) -> str:
        """
        Format KB evidence for inclusion in prompt.

        Args:
            requirements: Requirements being processed
            kb_evidence: KB evidence mapping

        Returns:
            Formatted KB context string
        """
        if not kb_evidence:
            return "No knowledge base evidence available."

        context_parts = []

        for req in requirements:
            req_id = req["id"]
            if req_id in kb_evidence and kb_evidence[req_id]:
                docs = kb_evidence[req_id][:3]  # Top 3 docs
                context_parts.append(f"\n### Evidence for {req_id}:\n")

                for i, doc in enumerate(docs, 1):
                    doc_id = doc.get("id", "unknown")
                    doc_text = doc.get("text", "")[:500]  # First 500 chars
                    score = doc.get("score", 0)

                    context_parts.append(
                        f"{i}. [KB: {doc_id}] (score: {score:.3f})\n{doc_text}\n"
                    )

        return "".join(context_parts) if context_parts else "No knowledge base evidence available."

    def _create_fallback_entry(self, requirement: Dict) -> Dict:
        """
        Create a fallback compliance entry.

        Args:
            requirement: Requirement dictionary

        Returns:
            Basic compliance entry
        """
        return {
            "requirement_id": requirement["id"],
            "requirement_text": requirement["text"],
            "priority": requirement["priority"],
            "approach": f"We will address this {requirement['priority']} requirement through our established processes and methodologies. Detailed approach to be developed.",
            "risk_level": "MEDIUM",
            "owner": self._assign_owner(requirement["category"]),
            "evidence_sources": [],
            "completion_criteria": "To be defined based on detailed technical analysis.",
        }

    def _assign_owner(self, category: str) -> str:
        """Assign owner based on category."""
        owner_map = {
            "technical": "Engineering Team",
            "management": "Program Management Office",
            "staffing": "HR/Recruiting",
            "pricing": "Finance/Contracts",
            "past_performance": "Business Development",
            "quality": "QA Team",
            "security": "Security Team",
            "compliance": "Legal/Compliance",
        }
        return owner_map.get(category, "Project Team")

    def export_csv(self, compliance_data: Dict, output_path: Path):
        """
        Export compliance matrix to CSV.

        Args:
            compliance_data: Compliance matrix data
            output_path: Output CSV file path
        """
        logger.info(f"Exporting compliance matrix to CSV: {output_path}")

        items = compliance_data.get("compliance_items", [])

        if not items:
            logger.warning("No compliance items to export")
            return

        # Define CSV columns
        fieldnames = [
            "Requirement ID",
            "Priority",
            "Requirement Text",
            "Our Approach",
            "Risk Level",
            "Owner",
            "Evidence Sources",
            "Completion Criteria",
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for item in items:
                writer.writerow(
                    {
                        "Requirement ID": item.get("requirement_id", ""),
                        "Priority": item.get("priority", ""),
                        "Requirement Text": item.get("requirement_text", ""),
                        "Our Approach": item.get("approach", ""),
                        "Risk Level": item.get("risk_level", ""),
                        "Owner": item.get("owner", ""),
                        "Evidence Sources": ", ".join(item.get("evidence_sources", [])),
                        "Completion Criteria": item.get("completion_criteria", ""),
                    }
                )

        logger.info(f"Exported {len(items)} compliance items to CSV")
