"""
Proposal section writers using LLM.
"""

from typing import Dict, List, Optional

from jinja2 import Template

from .config import config
from .llm_client import LLMClient
from .logger import logger


class ProposalWriter:
    """Generate proposal sections using LLM."""

    def __init__(self):
        """Initialize proposal writer."""
        self.llm = LLMClient()

    def write_executive_summary(
        self,
        rfp_title: str,
        sector: str,
        requirements_summary: str,
        kb_evidence: Optional[List[Dict]] = None,
    ) -> str:
        """
        Write executive summary section.

        Args:
            rfp_title: RFP title
            sector: Industry sector
            requirements_summary: Summary of key requirements
            kb_evidence: Optional KB evidence

        Returns:
            Executive summary markdown
        """
        logger.info("Writing executive summary")

        # Load prompt template
        prompt_template = config.get_prompt("writer_executive_summary")

        # Format KB excerpts
        kb_excerpts = self._format_kb_excerpts(kb_evidence) if kb_evidence else "Not available"

        # Format prompt
        prompt = prompt_template.format(
            rfp_title=rfp_title,
            sector=sector,
            company_name="[Your Company Name]",
            key_requirements_summary=requirements_summary,
            kb_excerpts=kb_excerpts,
        )

        # Get LLM response
        response = self.llm.complete(
            prompt=prompt, model=config.llm.model_strong, temperature=0.4, max_tokens=3000
        )

        return response

    def write_technical_approach(
        self,
        rfp_title: str,
        sector: str,
        requirements: List[Dict],
        compliance_data: Dict,
        kb_evidence: Optional[List[Dict]] = None,
    ) -> str:
        """
        Write technical approach section.

        Args:
            rfp_title: RFP title
            sector: Industry sector
            requirements: Technical requirements
            compliance_data: Compliance matrix
            kb_evidence: Optional KB evidence

        Returns:
            Technical approach markdown
        """
        logger.info("Writing technical approach")

        # Filter technical requirements
        tech_reqs = [r for r in requirements if r.get("category") == "technical"]

        # Load prompt template
        prompt_template = config.get_prompt("writer_technical_approach")

        # Format inputs
        requirements_list = "\n".join([f"- [{r['id']}] {r['text']}" for r in tech_reqs])

        kb_technical = self._format_kb_excerpts(kb_evidence) if kb_evidence else "Not available"

        compliance_summary = self._format_compliance_summary(compliance_data, tech_reqs)

        # Format prompt
        prompt = prompt_template.format(
            rfp_title=rfp_title,
            sector=sector,
            technical_requirements=", ".join([r["id"] for r in tech_reqs]),
            requirements_list=requirements_list,
            kb_technical=kb_technical,
            compliance_matrix=compliance_summary,
            compliance_data=compliance_summary,
        )

        # Get LLM response
        response = self.llm.complete(
            prompt=prompt, model=config.llm.model_strong, temperature=0.3, max_tokens=8000
        )

        return response

    def write_management_approach(
        self,
        rfp_title: str,
        sector: str,
        requirements: List[Dict],
        compliance_data: Dict,
        kb_evidence: Optional[List[Dict]] = None,
    ) -> str:
        """
        Write management approach section.

        Args:
            rfp_title: RFP title
            sector: Industry sector
            requirements: Management requirements
            compliance_data: Compliance matrix
            kb_evidence: Optional KB evidence

        Returns:
            Management approach markdown
        """
        logger.info("Writing management approach")

        # Filter management requirements
        mgmt_reqs = [r for r in requirements if r.get("category") == "management"]

        # Load prompt template
        prompt_template = config.get_prompt("writer_management_approach")

        # Format inputs
        requirements_list = "\n".join([f"- [{r['id']}] {r['text']}" for r in mgmt_reqs])

        kb_management = self._format_kb_excerpts(kb_evidence) if kb_evidence else "Not available"

        compliance_summary = self._format_compliance_summary(compliance_data, mgmt_reqs)

        # Format prompt
        prompt = prompt_template.format(
            rfp_title=rfp_title,
            sector=sector,
            management_requirements=", ".join([r["id"] for r in mgmt_reqs]),
            requirements_list=requirements_list,
            kb_management=kb_management,
            compliance_matrix=compliance_summary,
            compliance_data=compliance_summary,
        )

        # Get LLM response
        response = self.llm.complete(
            prompt=prompt, model=config.llm.model_strong, temperature=0.3, max_tokens=6000
        )

        return response

    def assemble_proposal(
        self, sections: Dict[str, str], template_name: str = "proposal_template"
    ) -> str:
        """
        Assemble final proposal from sections using template.

        Args:
            sections: Dictionary of section name -> content
            template_name: Template file name

        Returns:
            Complete proposal markdown
        """
        logger.info("Assembling final proposal")

        # Load template
        template_content = config.get_template(template_name)
        template = Template(template_content)

        # Render template
        proposal = template.render(**sections)

        return proposal

    def _format_kb_excerpts(self, kb_docs: List[Dict]) -> str:
        """Format KB documents for inclusion in prompt."""
        if not kb_docs:
            return "No KB evidence available."

        excerpts = []
        for i, doc in enumerate(kb_docs[:5], 1):  # Top 5
            doc_id = doc.get("id", "unknown")
            text = doc.get("text", "")[:300]  # First 300 chars
            excerpts.append(f"{i}. [KB: {doc_id}]\n{text}\n")

        return "\n".join(excerpts)

    def _format_compliance_summary(self, compliance_data: Dict, requirements: List[Dict]) -> str:
        """Format compliance matrix summary for prompt."""
        items = compliance_data.get("compliance_items", [])

        # Filter to relevant requirements
        req_ids = {r["id"] for r in requirements}
        relevant_items = [item for item in items if item.get("requirement_id") in req_ids]

        if not relevant_items:
            return "No compliance data available."

        summary_parts = []
        for item in relevant_items:
            summary_parts.append(
                f"- [{item['requirement_id']}] {item['approach'][:200]}... "
                f"(Risk: {item['risk_level']}, Owner: {item['owner']})"
            )

        return "\n".join(summary_parts)
