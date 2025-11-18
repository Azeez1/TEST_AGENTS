"""
Adaptive Proposal Writer
Generates proposals that adapt to RFP format and compliance requirements.
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import re

# Import supporting modules
from .rfp_parser import ParsedRFP, RFPFormat, RFPSection
from .compliance_engine import ComplianceAnalysis, FrameworkEvidence, ComplianceConfidence
from .user_priority_frameworks import FRAMEWORK_BY_ID

class ProposalSection(Enum):
    """Standard proposal sections."""
    EXECUTIVE_SUMMARY = "executive_summary"
    TECHNICAL_APPROACH = "technical_approach"
    COMPLIANCE_MATRIX = "compliance_matrix"
    PAST_PERFORMANCE = "past_performance"
    MANAGEMENT_APPROACH = "management_approach"
    PRICING = "pricing"
    QUALIFICATIONS = "qualifications"
    IMPLEMENTATION = "implementation"
    RISK_MANAGEMENT = "risk_management"
    APPENDICES = "appendices"

@dataclass
class ProposalContent:
    """Content for a proposal section."""
    section: ProposalSection
    title: str
    content: str
    subsections: List['ProposalContent'] = field(default_factory=list)
    compliance_refs: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    page_count_estimate: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AdaptiveProposal:
    """Complete adaptive proposal."""
    rfp_format: RFPFormat
    solicitation_number: str
    title: str
    executive_summary: str
    sections: List[ProposalContent]
    compliance_frameworks: List[str]
    total_pages_estimate: int
    win_themes: List[str]
    differentiators: List[str]
    metadata: Dict[str, Any]

class FormatAdapter:
    """Adapts proposal structure to RFP format requirements."""

    def __init__(self):
        # Format-specific section mappings
        self.format_templates = {
            RFPFormat.FAR_SECTION_L_M: self._get_far_template(),
            RFPFormat.SLED: self._get_sled_template(),
            RFPFormat.COMMERCIAL: self._get_commercial_template(),
            RFPFormat.INTERNATIONAL: self._get_international_template(),
            RFPFormat.UNKNOWN: self._get_generic_template()
        }

    def _get_far_template(self) -> List[Tuple[str, ProposalSection]]:
        """Template for FAR Section L/M format."""
        return [
            ("Volume I - Technical Proposal", ProposalSection.TECHNICAL_APPROACH),
            ("Volume II - Management Proposal", ProposalSection.MANAGEMENT_APPROACH),
            ("Volume III - Past Performance", ProposalSection.PAST_PERFORMANCE),
            ("Volume IV - Price Proposal", ProposalSection.PRICING),
            ("Compliance Matrix", ProposalSection.COMPLIANCE_MATRIX),
            ("Risk Management Plan", ProposalSection.RISK_MANAGEMENT)
        ]

    def _get_sled_template(self) -> List[Tuple[str, ProposalSection]]:
        """Template for State/Local/Education format."""
        return [
            ("Executive Summary", ProposalSection.EXECUTIVE_SUMMARY),
            ("Technical Response", ProposalSection.TECHNICAL_APPROACH),
            ("Qualifications and Experience", ProposalSection.QUALIFICATIONS),
            ("Implementation Plan", ProposalSection.IMPLEMENTATION),
            ("Cost Proposal", ProposalSection.PRICING),
            ("References", ProposalSection.PAST_PERFORMANCE)
        ]

    def _get_commercial_template(self) -> List[Tuple[str, ProposalSection]]:
        """Template for commercial RFP format."""
        return [
            ("Executive Summary", ProposalSection.EXECUTIVE_SUMMARY),
            ("Solution Overview", ProposalSection.TECHNICAL_APPROACH),
            ("Implementation Approach", ProposalSection.IMPLEMENTATION),
            ("Company Qualifications", ProposalSection.QUALIFICATIONS),
            ("Pricing Model", ProposalSection.PRICING),
            ("Case Studies", ProposalSection.PAST_PERFORMANCE)
        ]

    def _get_international_template(self) -> List[Tuple[str, ProposalSection]]:
        """Template for international organization format."""
        return [
            ("Executive Summary", ProposalSection.EXECUTIVE_SUMMARY),
            ("Technical Proposal", ProposalSection.TECHNICAL_APPROACH),
            ("Methodology and Approach", ProposalSection.MANAGEMENT_APPROACH),
            ("Team Composition", ProposalSection.QUALIFICATIONS),
            ("Financial Proposal", ProposalSection.PRICING),
            ("Previous Experience", ProposalSection.PAST_PERFORMANCE)
        ]

    def _get_generic_template(self) -> List[Tuple[str, ProposalSection]]:
        """Generic template for unknown formats."""
        return [
            ("Executive Summary", ProposalSection.EXECUTIVE_SUMMARY),
            ("Technical Approach", ProposalSection.TECHNICAL_APPROACH),
            ("Qualifications", ProposalSection.QUALIFICATIONS),
            ("Pricing", ProposalSection.PRICING),
            ("Past Performance", ProposalSection.PAST_PERFORMANCE)
        ]

    def get_template(self, rfp_format: RFPFormat) -> List[Tuple[str, ProposalSection]]:
        """Get proposal template for RFP format."""
        return self.format_templates.get(rfp_format, self._get_generic_template())

class ComplianceWriter:
    """Writes compliance-focused proposal content."""

    def __init__(self):
        self.framework_templates = self._load_framework_templates()

    def _load_framework_templates(self) -> Dict[str, str]:
        """Load compliance statement templates."""
        return {
            "cmmc": """
Our solution maintains {level} compliance with CMMC 2.0 requirements through:
• Comprehensive implementation of all {control_count} required practices
• Continuous monitoring and assessment capabilities
• Third-party C3PAO assessment readiness
• Documented policies, procedures, and evidence artifacts
• Automated compliance tracking and reporting
            """,
            "fedramp": """
Our cloud solution holds {level} FedRAMP authorization, demonstrating:
• Implementation of {control_count} NIST 800-53 security controls
• Continuous monitoring (ConMon) capabilities
• Annual 3PAO assessments
• Monthly POA&M updates and vulnerability scanning
• Incident response within required timeframes
            """,
            "nist_800_171": """
We fully implement NIST SP 800-171 Rev 3 requirements:
• All 110+ security requirements implemented and documented
• Organization-Defined Parameters (ODPs) configured
• CUI protection across all system boundaries
• SPRS score of {score} demonstrating maturity
• External Service Provider requirements addressed
            """,
            "nist_800_53": """
Our implementation aligns with NIST 800-53 Rev 5:
• {level} baseline controls fully implemented
• All 20 control families addressed
• Privacy controls integrated
• Supply chain risk management controls
• Continuous control monitoring and assessment
            """,
            "hipaa": """
We ensure HIPAA compliance through:
• Administrative safeguards including workforce training
• Physical safeguards for facilities and devices
• Technical safeguards including encryption and access controls
• Executed Business Associate Agreements (BAAs)
• Breach notification procedures within 60 days
• Annual risk assessments and security reviews
            """,
            "pci_dss": """
Our PCI-DSS v4.0 compliance includes:
• All 12 requirements fully implemented
• Quarterly vulnerability scans by Approved Scanning Vendor (ASV)
• Annual penetration testing
• Customized approach for specific environments
• Network segmentation to reduce scope
• Tokenization to protect cardholder data
            """,
            "gdpr": """
We ensure GDPR compliance through:
• Lawful basis established for all processing
• Data subject rights fully supported (access, erasure, portability)
• Privacy by design and default
• Data Protection Officer (DPO) appointed
• 72-hour breach notification capability
• Data Protection Impact Assessments (DPIAs) conducted
            """,
            "soc2": """
Our SOC 2 Type II certification demonstrates:
• Security criteria (Common Criteria) fully met
• {additional_criteria} criteria addressed
• Annual independent auditor assessment
• Continuous monitoring of controls
• Vendor management procedures
• Incident response and recovery capabilities
            """,
            "iso_27001": """
Our ISO 27001:2022 certification includes:
• Certified Information Security Management System (ISMS)
• All 114 Annex A controls implemented as applicable
• Annual surveillance audits
• Risk assessment and treatment methodology
• Management review and internal audits
• Continuous improvement processes
            """,
            "glba": """
We maintain GLBA compliance through:
• Written Information Security Program
• Qualified Individual designated
• Annual risk assessments
• Safeguards for customer information
• Employee training programs
• Service provider oversight procedures
• Board-level reporting and oversight
            """,
            "dfars": """
We meet DFARS 252.204-7012 requirements:
• NIST 800-171 fully implemented
• 72-hour cyber incident reporting capability
• 90-day forensic image preservation
• Cloud computing security requirements met
• Supply chain flow-down to subcontractors
• Covered Defense Information (CDI) protection
            """
        }

    def write_compliance_section(self, analysis: ComplianceAnalysis) -> ProposalContent:
        """Write comprehensive compliance section."""
        content_parts = []

        # Opening statement
        content_parts.append("""
## Compliance and Security Framework

Our solution provides comprehensive compliance with all identified regulatory and security frameworks,
ensuring your organization meets all mandatory requirements while maintaining the highest standards
of data protection and operational security.
        """.strip())

        # Primary frameworks
        if analysis.primary_frameworks:
            content_parts.append("\n### Primary Compliance Frameworks\n")
            for fw_id in analysis.primary_frameworks:
                fw_evidence = next(
                    (e for e in analysis.detected_frameworks if e.framework_id == fw_id),
                    None
                )
                if fw_evidence:
                    content_parts.append(self._write_framework_compliance(fw_evidence))

        # Compliance matrix summary
        content_parts.append("\n### Compliance Coverage Analysis\n")
        content_parts.append(self._write_compliance_matrix_summary(analysis))

        # Integration approach
        if analysis.integration_points:
            content_parts.append("\n### Integrated Compliance Approach\n")
            content_parts.append(self._write_integration_approach(analysis))

        # Risk mitigation
        if analysis.risk_areas:
            content_parts.append("\n### Risk Mitigation Strategy\n")
            content_parts.append(self._write_risk_mitigation(analysis))

        return ProposalContent(
            section=ProposalSection.COMPLIANCE_MATRIX,
            title="Compliance and Security Framework",
            content="\n".join(content_parts),
            compliance_refs=[fw.framework_id for fw in analysis.detected_frameworks],
            metadata={"frameworks_count": len(analysis.detected_frameworks)}
        )

    def _write_framework_compliance(self, evidence: FrameworkEvidence) -> str:
        """Write compliance statement for a specific framework."""
        template = self.framework_templates.get(evidence.framework_id, "")

        if not template:
            return f"**{evidence.framework_name}**: Full compliance demonstrated.\n"

        # Customize template based on evidence
        customized = template.strip()

        # Add confidence indicator
        if evidence.confidence == ComplianceConfidence.HIGH:
            prefix = f"**{evidence.framework_name}** ✓ [High Confidence]"
        elif evidence.confidence == ComplianceConfidence.MEDIUM:
            prefix = f"**{evidence.framework_name}** [Medium Confidence]"
        else:
            prefix = f"**{evidence.framework_name}** [Developing]"

        return f"{prefix}\n{customized}\n"

    def _write_compliance_matrix_summary(self, analysis: ComplianceAnalysis) -> str:
        """Write compliance matrix summary."""
        lines = []

        lines.append("| Framework | Coverage | Status | Key Requirements |")
        lines.append("|-----------|----------|--------|------------------|")

        for fw_id, matrix in analysis.compliance_matrix.items():
            fw_name = FRAMEWORK_BY_ID.get(fw_id, type('', (), {'name': fw_id})).name
            coverage = matrix.get("coverage_percentage", 0)
            status = "✓ Compliant" if coverage > 75 else "⚡ In Progress"
            key_reqs = len(matrix.get("mapped_controls", []))

            lines.append(f"| {fw_name} | {coverage:.0f}% | {status} | {key_reqs} controls mapped |")

        return "\n".join(lines)

    def _write_integration_approach(self, analysis: ComplianceAnalysis) -> str:
        """Write integration approach section."""
        lines = []

        lines.append("""
Our integrated compliance approach leverages synergies between frameworks to:
- Reduce implementation complexity
- Eliminate redundant controls
- Streamline audit and assessment processes
- Provide unified reporting and dashboards
        """.strip())

        if analysis.integration_points:
            lines.append("\n**Framework Integration Points:**")
            for point in analysis.integration_points[:5]:
                lines.append(f"- {point['framework_1']} + {point['framework_2']}: {point['benefit']}")

        return "\n".join(lines)

    def _write_risk_mitigation(self, analysis: ComplianceAnalysis) -> str:
        """Write risk mitigation section."""
        lines = []

        # Group risks by level
        high_risks = [r for r in analysis.risk_areas if r.get("risk_level") == "HIGH"]
        medium_risks = [r for r in analysis.risk_areas if r.get("risk_level") == "MEDIUM"]

        if high_risks:
            lines.append("**Critical Risk Mitigation:**")
            for risk in high_risks[:3]:
                lines.append(f"- {risk['issue']}: {risk['recommendation']}")

        if medium_risks:
            lines.append("\n**Additional Risk Management:**")
            for risk in medium_risks[:3]:
                lines.append(f"- {risk['issue']}: {risk['recommendation']}")

        return "\n".join(lines)

class WinThemeGenerator:
    """Generates win themes and differentiators."""

    def generate_themes(self, parsed_rfp: ParsedRFP,
                       analysis: ComplianceAnalysis) -> Tuple[List[str], List[str]]:
        """
        Generate win themes and differentiators.

        Returns:
            Tuple of (win_themes, differentiators)
        """
        win_themes = []
        differentiators = []

        # Compliance-based themes
        if len(analysis.primary_frameworks) >= 3:
            win_themes.append("Comprehensive Multi-Framework Compliance")
            differentiators.append("Pre-certified across all major compliance frameworks")

        # Format-specific themes
        if parsed_rfp.format_type == RFPFormat.FAR_SECTION_L_M:
            win_themes.append("Proven Federal Contractor with Exceptional CPARS Ratings")
            differentiators.append("10+ years of federal contract performance excellence")
        elif parsed_rfp.format_type == RFPFormat.SLED:
            win_themes.append("Local Presence with Global Capabilities")
            differentiators.append("Dedicated state/local government practice")
        elif parsed_rfp.format_type == RFPFormat.COMMERCIAL:
            win_themes.append("Rapid ROI through Accelerated Implementation")
            differentiators.append("Proprietary fast-track deployment methodology")
        elif parsed_rfp.format_type == RFPFormat.INTERNATIONAL:
            win_themes.append("Global Delivery with Local Expertise")
            differentiators.append("Presence in 50+ countries with local partners")

        # Framework-specific themes
        frameworks = [e.framework_id for e in analysis.detected_frameworks
                     if e.confidence_score > 0.7]

        if "cmmc" in frameworks or "dfars" in frameworks:
            win_themes.append("Defense-Grade Security Architecture")
            differentiators.append("CMMC Level 2 certified with C3PAO assessment")

        if "fedramp" in frameworks:
            win_themes.append("FedRAMP Authorized Cloud Solution")
            differentiators.append("Continuous ATO with no POA&Ms")

        if "hipaa" in frameworks:
            win_themes.append("Healthcare Compliance Excellence")
            differentiators.append("Zero HIPAA breaches in 10-year history")

        # Innovation themes
        win_themes.append("Innovation through Automation and AI")
        differentiators.append("AI-powered compliance monitoring and reporting")

        return win_themes[:5], differentiators[:5]  # Limit to top 5 each

class AdaptiveProposalWriter:
    """
    Main adaptive proposal writer that orchestrates all components.
    """

    def __init__(self):
        self.format_adapter = FormatAdapter()
        self.compliance_writer = ComplianceWriter()
        self.theme_generator = WinThemeGenerator()

    def write_proposal(self, parsed_rfp: ParsedRFP,
                      analysis: ComplianceAnalysis,
                      company_info: Dict[str, str] = None) -> AdaptiveProposal:
        """
        Write complete adaptive proposal.

        Args:
            parsed_rfp: Parsed RFP document
            analysis: Compliance analysis results
            company_info: Optional company information

        Returns:
            Complete AdaptiveProposal object
        """
        # Get format-specific template
        template = self.format_adapter.get_template(parsed_rfp.format_type)

        # Generate win themes
        win_themes, differentiators = self.theme_generator.generate_themes(
            parsed_rfp, analysis
        )

        # Write executive summary
        executive_summary = self._write_executive_summary(
            parsed_rfp, analysis, win_themes, company_info
        )

        # Create proposal sections
        sections = []
        for section_title, section_type in template:
            if section_type == ProposalSection.COMPLIANCE_MATRIX:
                # Use specialized compliance writer
                content = self.compliance_writer.write_compliance_section(analysis)
            else:
                # Generate section content
                content = self._write_section(
                    section_type, section_title, parsed_rfp, analysis
                )
            sections.append(content)

        # Calculate total pages
        total_pages = sum(s.page_count_estimate for s in sections) + 2  # +2 for cover/TOC

        # Extract compliance frameworks
        compliance_frameworks = [
            fw.framework_name for fw in analysis.detected_frameworks
            if fw.confidence_score > 0.5
        ]

        return AdaptiveProposal(
            rfp_format=parsed_rfp.format_type,
            solicitation_number=parsed_rfp.solicitation_number,
            title=self._generate_proposal_title(parsed_rfp, company_info),
            executive_summary=executive_summary,
            sections=sections,
            compliance_frameworks=compliance_frameworks,
            total_pages_estimate=total_pages,
            win_themes=win_themes,
            differentiators=differentiators,
            metadata={
                "rfp_title": parsed_rfp.title,
                "issuing_agency": parsed_rfp.issuing_agency,
                "due_date": parsed_rfp.due_date,
                "frameworks_addressed": len(compliance_frameworks),
                "confidence_score": self._calculate_proposal_confidence(analysis)
            }
        )

    def _write_executive_summary(self, parsed_rfp: ParsedRFP,
                                analysis: ComplianceAnalysis,
                                win_themes: List[str],
                                company_info: Dict[str, str] = None) -> str:
        """Write executive summary."""
        company_name = company_info.get("name", "Dux Machina") if company_info else "Dux Machina"

        summary = f"""
# Executive Summary

{company_name} is pleased to submit this proposal in response to {parsed_rfp.issuing_agency}'s
solicitation {parsed_rfp.solicitation_number}. Our solution directly addresses all stated requirements
while providing proven compliance with {len(analysis.primary_frameworks)} critical regulatory frameworks.

## Why {company_name}?

Our selection as your partner ensures:
        """.strip()

        # Add win themes
        for theme in win_themes:
            summary += f"\n• {theme}"

        summary += "\n\n## Compliance Assurance\n\n"
        summary += "We bring pre-existing compliance certifications and authorizations including:\n"

        for fw_id in analysis.primary_frameworks[:5]:
            fw_name = FRAMEWORK_BY_ID.get(fw_id, type('', (), {'name': fw_id})).name
            summary += f"• {fw_name}\n"

        summary += f"""

## Our Commitment

We commit to delivering a solution that not only meets but exceeds your requirements, with:
• Full compliance with all {len(analysis.detected_frameworks)} identified frameworks
• Implementation within required timeframes
• Proven methodologies and experienced team
• Continuous support and optimization

We look forward to partnering with {parsed_rfp.issuing_agency} to deliver exceptional value
and ensure mission success.
        """

        return summary.strip()

    def _write_section(self, section_type: ProposalSection, title: str,
                      parsed_rfp: ParsedRFP, analysis: ComplianceAnalysis) -> ProposalContent:
        """Write a proposal section."""
        content = ""

        if section_type == ProposalSection.TECHNICAL_APPROACH:
            content = self._write_technical_approach(parsed_rfp, analysis)
        elif section_type == ProposalSection.MANAGEMENT_APPROACH:
            content = self._write_management_approach(parsed_rfp)
        elif section_type == ProposalSection.PAST_PERFORMANCE:
            content = self._write_past_performance(parsed_rfp)
        elif section_type == ProposalSection.PRICING:
            content = self._write_pricing(parsed_rfp)
        elif section_type == ProposalSection.QUALIFICATIONS:
            content = self._write_qualifications(analysis)
        elif section_type == ProposalSection.IMPLEMENTATION:
            content = self._write_implementation(parsed_rfp)
        elif section_type == ProposalSection.RISK_MANAGEMENT:
            content = self._write_risk_management(analysis)
        else:
            content = f"[{title} content to be developed]"

        # Estimate page count based on content length
        page_estimate = max(1, len(content) // 3000)  # ~3000 chars per page

        return ProposalContent(
            section=section_type,
            title=title,
            content=content,
            page_count_estimate=page_estimate
        )

    def _write_technical_approach(self, parsed_rfp: ParsedRFP,
                                 analysis: ComplianceAnalysis) -> str:
        """Write technical approach section."""
        return f"""
## Technical Approach

### Solution Overview

Our comprehensive technical solution addresses all requirements through a proven,
compliance-focused architecture that ensures:

• Scalability to meet current and future needs
• Security aligned with {len(analysis.primary_frameworks)} compliance frameworks
• Reliability with 99.99% uptime SLA
• Performance optimized for your operational requirements

### Architecture

Our solution architecture incorporates:

**Core Components:**
- Multi-tier architecture with segregated security zones
- Encrypted data at rest and in transit
- Redundant systems with automatic failover
- Continuous monitoring and alerting
- Automated compliance validation

**Security Architecture:**
- Defense-in-depth strategy
- Zero-trust network architecture
- Identity and access management (IAM)
- Security information and event management (SIEM)
- Vulnerability management and patching

### Technical Requirements Compliance

We address all {len(parsed_rfp.technical_requirements)} identified technical requirements through:
- Proven COTS products and integrations
- Custom development where needed
- Automated testing and validation
- Comprehensive documentation

### Innovation and Future-Proofing

Our solution incorporates cutting-edge technologies:
- AI/ML for predictive analytics
- Automation for operational efficiency
- Cloud-native architecture for scalability
- API-first design for integration
        """.strip()

    def _write_management_approach(self, parsed_rfp: ParsedRFP) -> str:
        """Write management approach section."""
        return """
## Management Approach

### Program Management

Our proven program management approach ensures successful delivery through:

• PMP-certified Program Manager with federal experience
• Agile/Scrum methodology with 2-week sprints
• Weekly status reports and monthly reviews
• Risk management and mitigation strategies
• Quality assurance at every phase

### Team Structure

**Key Personnel:**
- Program Manager: Overall delivery accountability
- Technical Lead: Architecture and implementation
- Compliance Manager: Framework compliance oversight
- Security Lead: Security controls and monitoring
- Quality Assurance Lead: Testing and validation

### Communication Plan

We maintain transparent communication through:
- Weekly status meetings
- Monthly executive briefings
- 24/7 issue tracking portal
- Quarterly business reviews
- Annual strategic planning sessions

### Performance Metrics

We measure success through:
- On-time delivery milestones
- Quality metrics and defect rates
- Compliance audit scores
- Customer satisfaction surveys
- SLA achievement rates
        """.strip()

    def _write_past_performance(self, parsed_rfp: ParsedRFP) -> str:
        """Write past performance section."""
        return """
## Past Performance

### Relevant Contract Experience

We bring extensive experience delivering similar solutions:

**Contract 1: Federal Agency Cloud Migration**
- Customer: [Agency Name]
- Value: $15M
- Period: 2020-2023
- Relevance: FedRAMP cloud migration with CMMC compliance
- Result: On-time, on-budget delivery with exceptional CPARS ratings

**Contract 2: State Healthcare System Implementation**
- Customer: [State Name]
- Value: $8M
- Period: 2021-2024
- Relevance: HIPAA-compliant system implementation
- Result: Zero security incidents, 100% uptime achieved

**Contract 3: Financial Services Platform**
- Customer: [Company Name]
- Value: $12M
- Period: 2019-2023
- Relevance: PCI-DSS and SOC 2 compliant platform
- Result: Successful certification achieved in 6 months

### Performance Metrics

Across all contracts:
- 100% on-time delivery
- 98% customer satisfaction
- Zero security breaches
- 15% average cost savings
- 99.99% system availability
        """.strip()

    def _write_pricing(self, parsed_rfp: ParsedRFP) -> str:
        """Write pricing section."""
        return """
## Pricing Proposal

### Pricing Strategy

Our competitive pricing delivers exceptional value through:
- Transparent, itemized pricing structure
- No hidden fees or surprise costs
- Volume discounts available
- Flexible payment terms
- Best value determination focus

### Cost Summary

| Category | Year 1 | Year 2 | Year 3 | Total |
|----------|--------|--------|--------|-------|
| Implementation | $X | $0 | $0 | $X |
| Licensing | $X | $X | $X | $3X |
| Operations | $X | $X | $X | $3X |
| Maintenance | $X | $X | $X | $3X |
| **Total** | **$X** | **$X** | **$X** | **$X** |

### Value Proposition

Our pricing provides:
- Lower TCO than competitors
- Included compliance certifications
- No additional fees for updates
- Bundled training and support
- ROI within 18 months
        """.strip()

    def _write_qualifications(self, analysis: ComplianceAnalysis) -> str:
        """Write qualifications section."""
        frameworks_text = ", ".join([
            FRAMEWORK_BY_ID[fw].name for fw in analysis.primary_frameworks[:3]
        ])

        return f"""
## Corporate Qualifications

### Company Overview

Dux Machina brings:
- 15+ years in compliant solution delivery
- 500+ successful implementations
- Expertise across {len(analysis.primary_frameworks)} compliance frameworks
- Industry-leading customer retention (95%)

### Certifications and Credentials

**Corporate Certifications:**
- ISO 9001:2015 (Quality Management)
- ISO 27001:2022 (Information Security)
- CMMC Level 2 Certified
- FedRAMP Authorized CSP

**Compliance Authorizations:**
- {frameworks_text}
- Additional frameworks as required

### Industry Recognition

- Gartner Magic Quadrant Leader (2023)
- Federal Computer Week Top 100 (2022-2024)
- CRN Solution Provider 500 (2021-2024)

### Financial Stability

- Annual Revenue: $XXM
- D&B Rating: XX
- Bonding Capacity: $XXM
- No litigation or bankruptcy history
        """.strip()

    def _write_implementation(self, parsed_rfp: ParsedRFP) -> str:
        """Write implementation section."""
        return """
## Implementation Plan

### Phased Approach

**Phase 1: Foundation (Months 1-2)**
- Requirements validation
- Environment setup
- Security baseline configuration
- Initial compliance assessment

**Phase 2: Core Implementation (Months 3-4)**
- System deployment
- Integration development
- Security controls implementation
- Initial testing

**Phase 3: Compliance & Validation (Months 5-6)**
- Compliance validation
- Security testing
- Performance optimization
- Documentation completion

**Phase 4: Transition (Month 7)**
- User training
- Operational handover
- Go-live support
- Post-implementation review

### Critical Success Factors

- Executive sponsorship
- Dedicated project team
- Regular communication
- Phased rollout approach
- Comprehensive testing
        """.strip()

    def _write_risk_management(self, analysis: ComplianceAnalysis) -> str:
        """Write risk management section."""
        return """
## Risk Management

### Risk Mitigation Strategy

Our comprehensive risk management approach addresses:

**Technical Risks:**
- Mitigation: Proven architecture patterns
- Contingency: Redundant systems and rollback procedures

**Compliance Risks:**
- Mitigation: Pre-validated compliance controls
- Contingency: Rapid remediation processes

**Schedule Risks:**
- Mitigation: Agile methodology with buffer time
- Contingency: Additional resources available

**Security Risks:**
- Mitigation: Defense-in-depth architecture
- Contingency: Incident response team on standby

### Risk Monitoring

Continuous risk assessment through:
- Weekly risk reviews
- Automated compliance monitoring
- Security scanning and alerts
- Performance metrics tracking
- Stakeholder feedback loops

### Issue Resolution

Rapid issue resolution via:
- 24/7 support desk
- Tiered escalation process
- Root cause analysis
- Corrective action tracking
- Lessons learned documentation
        """.strip()

    def _generate_proposal_title(self, parsed_rfp: ParsedRFP,
                                company_info: Dict[str, str] = None) -> str:
        """Generate proposal title."""
        company_name = company_info.get("name", "Dux Machina") if company_info else "Dux Machina"

        if parsed_rfp.solicitation_number:
            return f"{company_name} Response to {parsed_rfp.solicitation_number}"
        else:
            return f"{company_name} Technical and Cost Proposal"

    def _calculate_proposal_confidence(self, analysis: ComplianceAnalysis) -> float:
        """Calculate overall proposal confidence score."""
        scores = []

        # Factor in framework confidence
        for fw in analysis.detected_frameworks:
            scores.append(fw.confidence_score)

        # Factor in coverage
        for matrix in analysis.compliance_matrix.values():
            coverage = matrix.get("coverage_percentage", 0) / 100
            scores.append(coverage)

        if scores:
            return sum(scores) / len(scores)
        return 0.5

    def export_proposal(self, proposal: AdaptiveProposal, output_dir: str):
        """Export proposal to files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Export as JSON for processing
        json_file = output_path / "proposal_data.json"
        with open(json_file, 'w') as f:
            # Convert to serializable format
            proposal_dict = {
                "rfp_format": proposal.rfp_format.value,
                "solicitation_number": proposal.solicitation_number,
                "title": proposal.title,
                "executive_summary": proposal.executive_summary,
                "sections": [
                    {
                        "section": s.section.value,
                        "title": s.title,
                        "content": s.content,
                        "page_count": s.page_count_estimate
                    } for s in proposal.sections
                ],
                "compliance_frameworks": proposal.compliance_frameworks,
                "total_pages": proposal.total_pages_estimate,
                "win_themes": proposal.win_themes,
                "differentiators": proposal.differentiators,
                "metadata": proposal.metadata
            }
            json.dump(proposal_dict, f, indent=2)

        # Export as markdown for review
        md_file = output_path / "proposal_draft.md"
        with open(md_file, 'w') as f:
            f.write(f"# {proposal.title}\n\n")
            f.write(f"**Solicitation:** {proposal.solicitation_number}\n")
            f.write(f"**Format:** {proposal.rfp_format.value}\n")
            f.write(f"**Estimated Pages:** {proposal.total_pages_estimate}\n\n")

            f.write("## Win Themes\n")
            for theme in proposal.win_themes:
                f.write(f"- {theme}\n")

            f.write("\n## Differentiators\n")
            for diff in proposal.differentiators:
                f.write(f"- {diff}\n")

            f.write("\n---\n\n")
            f.write(proposal.executive_summary)
            f.write("\n\n---\n\n")

            for section in proposal.sections:
                f.write(f"# {section.title}\n\n")
                f.write(section.content)
                f.write("\n\n---\n\n")

        print(f"Proposal exported to: {output_path}")
        print(f"  - Data: {json_file}")
        print(f"  - Draft: {md_file}")

# Export main classes
__all__ = [
    'AdaptiveProposalWriter',
    'AdaptiveProposal',
    'ProposalContent',
    'ProposalSection'
]