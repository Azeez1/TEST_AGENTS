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
from .compliance_frameworks import (
    detect_applicable_frameworks,
    generate_compliance_section,
    generate_compliance_matrix_table,
    ComplianceFramework
)


class ComplianceMatrixBuilder:
    """Build compliance matrix from requirements and KB evidence."""

    def __init__(self, sector: Optional[str] = None):
        """
        Initialize compliance matrix builder.

        Args:
            sector: Optional sector hint for compliance detection
        """
        self.llm = LLMClient()
        self.sector = sector
        self.detected_frameworks: List[ComplianceFramework] = []

        # Load schema
        schema_path = config.schemas_dir / "compliance.schema.json"
        with open(schema_path, "r") as f:
            self.schema = json.load(f)

        # Load prompt template
        self.prompt_template = config.get_prompt("compliance_matrix")

    def detect_frameworks(self, rfp_text: str) -> List[ComplianceFramework]:
        """
        Detect applicable compliance frameworks from RFP text.

        Args:
            rfp_text: Full RFP text

        Returns:
            List of detected compliance frameworks
        """
        logger.info(f"Detecting compliance frameworks (sector: {self.sector})")
        self.detected_frameworks = detect_applicable_frameworks(rfp_text, self.sector)

        if self.detected_frameworks:
            framework_names = [fw.name for fw in self.detected_frameworks]
            logger.info(f"Detected {len(self.detected_frameworks)} frameworks: {', '.join(framework_names[:5])}")
        else:
            logger.warning("No compliance frameworks auto-detected")

        return self.detected_frameworks

    def build_matrix(
        self, requirements: List[Dict], kb_evidence: Optional[Dict[str, List[Dict]]] = None,
        rfp_text: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Build compliance matrix for all requirements.

        Args:
            requirements: List of requirements
            kb_evidence: Optional KB evidence mapping (req_id -> docs)
            rfp_text: Optional full RFP text for framework detection

        Returns:
            {
                'compliance_items': [...],
                'detected_frameworks': [...],
                'compliance_summary': str,
                'metadata': {...}
            }
        """
        logger.info(f"Building compliance matrix for {len(requirements)} requirements")

        # Detect frameworks if RFP text provided
        if rfp_text and not self.detected_frameworks:
            self.detect_frameworks(rfp_text)

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

        result = {
            "compliance_items": all_items,
            "detected_frameworks": [
                {
                    "id": fw.id,
                    "name": fw.name,
                    "category": fw.category,
                    "description": fw.description
                }
                for fw in self.detected_frameworks
            ]
        }

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
        context_parts = []

        # Add detected frameworks context
        if self.detected_frameworks:
            context_parts.append("\n### APPLICABLE COMPLIANCE FRAMEWORKS:\n")
            for fw in self.detected_frameworks[:5]:  # Top 5
                context_parts.append(f"\n**{fw.name}** ({fw.category}):")
                context_parts.append(f"\n{fw.description}")
                if fw.requirements:
                    context_parts.append("\nKey requirements:")
                    for req in fw.requirements[:5]:  # Top 5 requirements
                        context_parts.append(f"  - {req}")
                context_parts.append("\n")

        # Add KB evidence
        if not kb_evidence:
            context_parts.append("\nNo knowledge base evidence available.")
            return "".join(context_parts)

        context_parts.append("\n### KNOWLEDGE BASE EVIDENCE:\n")

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

        return "".join(context_parts)

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

    def generate_compliance_narrative(self, company_name: str = "Our Company") -> str:
        """
        Generate compliance narrative section for proposal.

        Args:
            company_name: Company name for proposal

        Returns:
            Formatted compliance narrative text
        """
        if not self.detected_frameworks:
            return ""

        logger.info(f"Generating compliance narrative for {len(self.detected_frameworks)} frameworks")
        return generate_compliance_section(self.detected_frameworks, company_name)

    def generate_framework_matrix_table(self) -> str:
        """
        Generate compliance framework summary table.

        Returns:
            Markdown table of frameworks
        """
        if not self.detected_frameworks:
            return ""

        return generate_compliance_matrix_table(self.detected_frameworks)
