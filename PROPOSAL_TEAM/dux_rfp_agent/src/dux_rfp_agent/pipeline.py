"""
Main RFP processing pipeline orchestrator.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from .compliance import ComplianceMatrixBuilder
from .config import config
from .export import Exporter
from .ingestion import DocumentIngestion
from .logger import logger
from .parser import RFPParser
from .qa_agent import QAAgent
from .retrieval import KnowledgeBaseRetrieval
from .writer import ProposalWriter


class RFPPipeline:
    """Orchestrate the end-to-end RFP processing pipeline."""

    def __init__(self, enable_kb: bool = True):
        """
        Initialize pipeline.

        Args:
            enable_kb: Whether to enable knowledge base retrieval
        """
        self.ingestion = DocumentIngestion()
        self.parser = RFPParser()
        self.kb = KnowledgeBaseRetrieval(enabled=enable_kb)
        self.compliance_builder = ComplianceMatrixBuilder()
        self.writer = ProposalWriter()
        self.qa = QAAgent()
        self.exporter = Exporter()

        logger.info("RFP Pipeline initialized")

    def process_rfp(
        self,
        rfp_path: Path,
        output_dir: Path,
        sector: str = "government",
        rfp_title: Optional[str] = None,
        company_name: Optional[str] = None,
    ) -> Dict[str, any]:
        """
        Process RFP end-to-end.

        Args:
            rfp_path: Path to RFP document
            output_dir: Output directory for deliverables
            sector: Industry sector (government, healthcare, etc.)
            rfp_title: RFP title (auto-detected if not provided)
            company_name: Company name for proposal

        Returns:
            Dictionary with processing results and paths
        """
        logger.info(f"=" * 80)
        logger.info(f"Starting RFP processing pipeline")
        logger.info(f"RFP: {rfp_path}")
        logger.info(f"Output: {output_dir}")
        logger.info(f"=" * 80)

        start_time = datetime.now()

        # Stage 1: Ingestion
        logger.info("\n[STAGE 1/7] Document Ingestion")
        logger.info("-" * 40)
        doc_data = self.ingestion.ingest(rfp_path)
        logger.info(
            f"Ingested {doc_data['metadata']['num_pages']} pages, "
            f"{len(doc_data['text'])} characters"
        )

        # Normalize text
        doc_data["text"] = self.ingestion.normalize_text(doc_data["text"])

        # Auto-detect title if not provided
        if not rfp_title:
            rfp_title = doc_data["metadata"].get("title") or rfp_path.stem
        if not company_name:
            company_name = "Your Company"

        # Stage 2: Parsing
        logger.info("\n[STAGE 2/7] Requirements Parsing")
        logger.info("-" * 40)
        requirements_data = self.parser.parse_rfp(doc_data["text"], doc_data["pages"])
        logger.info(
            f"Extracted {requirements_data['metadata']['total_requirements']} requirements "
            f"({requirements_data['metadata']['must_count']} MUST/SHALL)"
        )

        # Stage 3: Knowledge Base Retrieval
        logger.info("\n[STAGE 3/7] Knowledge Base Retrieval")
        logger.info("-" * 40)
        if self.kb.enabled:
            kb_evidence = self.kb.query_requirements(requirements_data["requirements"])
            logger.info(f"Retrieved KB evidence for {len(kb_evidence)} requirements")
        else:
            kb_evidence = {}
            logger.info("KB retrieval disabled, skipping")

        # Stage 4: Compliance Matrix
        logger.info("\n[STAGE 4/7] Compliance Matrix Generation")
        logger.info("-" * 40)
        compliance_data = self.compliance_builder.build_matrix(
            requirements_data["requirements"], kb_evidence
        )
        logger.info(f"Generated {len(compliance_data['compliance_items'])} compliance entries")

        # Stage 5: Proposal Writing
        logger.info("\n[STAGE 5/7] Proposal Section Writing")
        logger.info("-" * 40)

        # Build requirements summary for executive summary
        must_reqs = [
            r for r in requirements_data["requirements"] if r["priority"] in ["MUST", "SHALL"]
        ]
        req_summary = f"{len(must_reqs)} critical requirements across {len(set(r['category'] for r in requirements_data['requirements']))} categories"

        # Get KB evidence for writers
        all_kb_docs = []
        for docs in kb_evidence.values():
            all_kb_docs.extend(docs[:2])  # Top 2 per requirement

        # Write sections
        logger.info("Writing executive summary...")
        executive_summary = self.writer.write_executive_summary(
            rfp_title=rfp_title,
            sector=sector,
            requirements_summary=req_summary,
            kb_evidence=all_kb_docs[:10],
        )

        logger.info("Writing technical approach...")
        technical_approach = self.writer.write_technical_approach(
            rfp_title=rfp_title,
            sector=sector,
            requirements=requirements_data["requirements"],
            compliance_data=compliance_data,
            kb_evidence=all_kb_docs[:15],
        )

        logger.info("Writing management approach...")
        management_approach = self.writer.write_management_approach(
            rfp_title=rfp_title,
            sector=sector,
            requirements=requirements_data["requirements"],
            compliance_data=compliance_data,
            kb_evidence=all_kb_docs[:10],
        )

        # Assemble proposal
        sections = {
            "rfp_title": rfp_title,
            "client_name": "Client Name",
            "company_name": company_name,
            "submission_date": datetime.now().strftime("%Y-%m-%d"),
            "proposal_id": f"PROP-{datetime.now().strftime('%Y%m%d')}",
            "executive_summary": executive_summary,
            "technical_approach": technical_approach,
            "management_approach": management_approach,
            "staffing_plan": "To be developed based on specific staffing requirements.",
            "past_performance": "To be developed with specific project examples.",
            "quality_assurance": "To be developed with QA processes and standards.",
            "pricing_section": "To be developed by finance team.",
            "compliance_matrix": "See compliance_matrix.csv for detailed matrix.",
            "appendices": "Supporting documents to be attached.",
        }

        logger.info("Assembling final proposal...")
        proposal_md = self.writer.assemble_proposal(sections)

        # Stage 6: QA Validation
        logger.info("\n[STAGE 6/7] QA Validation")
        logger.info("-" * 40)
        qa_sections = {
            "executive_summary": executive_summary,
            "technical_approach": technical_approach,
            "management_approach": management_approach,
        }
        qa_report = self.qa.validate_proposal(
            requirements_data["requirements"], qa_sections, compliance_data
        )
        logger.info(
            f"QA Status: {qa_report['status']}, "
            f"Coverage: {qa_report.get('coverage_percentage', 0):.1f}%, "
            f"Issues: {len(qa_report.get('issues', []))}"
        )

        # Stage 7: Export
        logger.info("\n[STAGE 7/7] Export Deliverables")
        logger.info("-" * 40)
        self.exporter.export_bundle(
            output_dir=output_dir,
            proposal_md=proposal_md,
            requirements_data=requirements_data,
            compliance_data=compliance_data,
            qa_report=qa_report,
            sections=sections,
        )

        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()

        logger.info("\n" + "=" * 80)
        logger.info(f"Pipeline completed in {duration:.1f} seconds")
        logger.info(f"Output directory: {output_dir}")
        logger.info("=" * 80 + "\n")

        return {
            "success": True,
            "output_dir": str(output_dir),
            "duration_seconds": duration,
            "requirements_count": requirements_data["metadata"]["total_requirements"],
            "must_requirements": requirements_data["metadata"]["must_count"],
            "compliance_items": len(compliance_data["compliance_items"]),
            "qa_status": qa_report["status"],
            "qa_issues": len(qa_report.get("issues", [])),
            "files": {
                "proposal": str(output_dir / "proposal_draft.md"),
                "requirements": str(output_dir / "requirements.json"),
                "compliance_csv": str(output_dir / "compliance_matrix.csv"),
                "qa_report": str(output_dir / "qa_report.json"),
            },
        }
