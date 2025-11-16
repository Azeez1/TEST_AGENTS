"""
QA agent for validating proposal coverage and quality.
"""

import json
import re
from typing import Dict, List

from .config import config
from .llm_client import LLMClient
from .logger import logger


class QAAgent:
    """Validate proposal completeness and compliance."""

    def __init__(self):
        """Initialize QA agent."""
        self.llm = LLMClient()

        # Load prompt template
        self.prompt_template = config.get_prompt("qa_coverage")

    def validate_proposal(
        self,
        requirements: List[Dict],
        proposal_sections: Dict[str, str],
        compliance_data: Dict,
    ) -> Dict[str, any]:
        """
        Validate proposal coverage and quality.

        Args:
            requirements: List of requirements
            proposal_sections: Dictionary of section content
            compliance_data: Compliance matrix

        Returns:
            QA report with issues and recommendations
        """
        logger.info("Running QA validation")

        # Run automated checks first
        auto_issues = self._run_automated_checks(
            requirements, proposal_sections, compliance_data
        )

        # Run LLM-based validation
        llm_report = self._run_llm_validation(requirements, proposal_sections, compliance_data)

        # Merge results
        report = llm_report
        report["issues"].extend(auto_issues)

        # Recalculate summary
        report["total_issues"] = len(report["issues"])
        report["critical_issues"] = len([i for i in report["issues"] if i["severity"] == "CRITICAL"])

        logger.info(
            f"QA validation complete: {report['status']}, "
            f"{report['total_issues']} issues ({report['critical_issues']} critical)"
        )

        return report

    def _run_automated_checks(
        self, requirements: List[Dict], proposal_sections: Dict[str, str], compliance_data: Dict
    ) -> List[Dict]:
        """Run automated validation checks."""
        issues = []

        # Check for placeholders
        placeholders = self._check_placeholders(proposal_sections)
        issues.extend(placeholders)

        # Check citation integrity
        citation_issues = self._check_citations(requirements, proposal_sections)
        issues.extend(citation_issues)

        # Check word counts
        word_count_issues = self._check_word_counts(proposal_sections)
        issues.extend(word_count_issues)

        return issues

    def _check_placeholders(self, sections: Dict[str, str]) -> List[Dict]:
        """Check for placeholder text."""
        placeholder_patterns = [
            r"\[TBD\]",
            r"\[TODO\]",
            r"\[PLACEHOLDER\]",
            r"\{\{[^}]+\}\}",
            r"XXX",
            r"FIXME",
        ]

        issues = []

        for section_name, content in sections.items():
            for pattern in placeholder_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    issues.append(
                        {
                            "severity": "CRITICAL",
                            "category": "placeholder",
                            "description": f"Found {len(matches)} placeholder(s) in {section_name}: {matches[0]}",
                            "location": section_name,
                            "recommendation": "Replace all placeholders with actual content",
                        }
                    )

        return issues

    def _check_citations(self, requirements: List[Dict], sections: Dict[str, str]) -> List[Dict]:
        """Check citation integrity."""
        issues = []

        # Build set of valid requirement IDs
        valid_req_ids = {req["id"] for req in requirements}

        # Check all sections for citations
        for section_name, content in sections.items():
            # Find all requirement citations [Requirement R-XXX]
            req_citations = re.findall(r"\[Requirement (R-\d{3,})\]", content)

            for cited_id in req_citations:
                if cited_id not in valid_req_ids:
                    issues.append(
                        {
                            "severity": "WARNING",
                            "category": "broken_citation",
                            "description": f"Citation to non-existent requirement {cited_id} in {section_name}",
                            "location": section_name,
                            "recommendation": f"Verify or remove citation to {cited_id}",
                        }
                    )

        return issues

    def _check_word_counts(self, sections: Dict[str, str]) -> List[Dict]:
        """Check section word counts."""
        issues = []

        # Expected ranges
        ranges = {
            "executive_summary": (500, 800),
        }

        for section_name, content in sections.items():
            if section_name in ranges:
                word_count = len(content.split())
                min_words, max_words = ranges[section_name]

                if word_count < min_words:
                    issues.append(
                        {
                            "severity": "WARNING",
                            "category": "quality",
                            "description": f"{section_name} is too short: {word_count} words (min: {min_words})",
                            "location": section_name,
                            "recommendation": f"Expand {section_name} to at least {min_words} words",
                        }
                    )
                elif word_count > max_words:
                    issues.append(
                        {
                            "severity": "INFO",
                            "category": "quality",
                            "description": f"{section_name} is too long: {word_count} words (max: {max_words})",
                            "location": section_name,
                            "recommendation": f"Consider condensing {section_name} to under {max_words} words",
                        }
                    )

        return issues

    def _run_llm_validation(
        self, requirements: List[Dict], sections: Dict[str, str], compliance_data: Dict
    ) -> Dict:
        """Run LLM-based validation."""
        # Format inputs
        requirements_json = json.dumps(requirements, indent=2)
        proposal_text = "\n\n---\n\n".join(
            [f"## {name}\n\n{content}" for name, content in sections.items()]
        )
        compliance_json = json.dumps(compliance_data, indent=2)

        # Format prompt
        prompt = self.prompt_template.format(
            requirements_json=requirements_json,
            proposal_sections=proposal_text,
            compliance_matrix=compliance_json,
        )

        try:
            # Get LLM response
            response = self.llm.complete_json(
                prompt=prompt, model=config.llm.model_small, temperature=0.0, max_tokens=4000
            )

            return response

        except Exception as e:
            logger.error(f"LLM validation failed: {e}")

            # Return basic report
            return {
                "status": "WARNING",
                "coverage_percentage": 0.0,
                "issues": [
                    {
                        "severity": "WARNING",
                        "category": "system",
                        "description": f"LLM validation failed: {e}",
                        "location": "QA System",
                        "recommendation": "Review proposal manually",
                    }
                ],
                "must_requirements_covered": 0,
                "must_requirements_total": len(
                    [r for r in requirements if r["priority"] in ["MUST", "SHALL"]]
                ),
                "summary": "Automated QA validation encountered errors. Manual review required.",
            }
