"""
6-Block Universal Compliance Engine
Processes RFPs against the 10 priority compliance frameworks with equal optimization.
"""

import re
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

# Import user's priority frameworks
try:
    from .user_priority_frameworks import (
        USER_PRIORITY_FRAMEWORKS,
        FRAMEWORK_BY_ID,
        detect_user_frameworks,
        UserFramework
    )
except ImportError:
    from user_priority_frameworks import (
        USER_PRIORITY_FRAMEWORKS,
        FRAMEWORK_BY_ID,
        detect_user_frameworks,
        UserFramework
    )

class ComplianceConfidence(Enum):
    """Confidence levels for compliance detection."""
    HIGH = "high"          # 90-100% - Multiple strong indicators
    MEDIUM = "medium"      # 70-89% - Clear indicators present
    LOW = "low"           # 50-69% - Some indicators found
    MINIMAL = "minimal"    # 30-49% - Weak indicators only
    NONE = "none"         # <30% - No meaningful indicators

@dataclass
class FrameworkEvidence:
    """Evidence of a framework's presence in an RFP."""
    framework_id: str
    framework_name: str
    confidence: ComplianceConfidence
    confidence_score: float  # 0.0 to 1.0
    keyword_matches: List[str]
    section_references: List[str]  # Section IDs where found
    requirement_count: int
    specific_clauses: List[str]  # Specific clause references (e.g., "FAR 52.204-21")
    evidence_snippets: List[str]  # Text snippets showing evidence

@dataclass
class ComplianceAnalysis:
    """Complete compliance analysis for an RFP."""
    detected_frameworks: List[FrameworkEvidence]
    primary_frameworks: List[str]  # Top 3-5 framework IDs
    compliance_matrix: Dict[str, Dict[str, Any]]  # Framework ID -> requirements mapping
    risk_areas: List[Dict[str, str]]  # Areas needing special attention
    integration_points: List[Dict[str, str]]  # Where frameworks overlap
    recommendations: List[str]
    metadata: Dict[str, Any]

class Block1_FrameworkDetector:
    """
    Block 1: Framework Detection Engine
    Identifies which of the 10 priority frameworks apply to an RFP.
    """

    def __init__(self):
        # Enhanced keyword patterns for each framework
        self.enhanced_patterns = self._build_enhanced_patterns()

        # Clause reference patterns
        self.clause_patterns = {
            "cmmc": [r"32\s+CFR\s+(?:Part\s+)?170", r"CMMC\s+Level\s+[123]", r"NIST\s+800-171"],
            "fedramp": [r"FedRAMP\s+(?:Low|Moderate|High)", r"ATO", r"3PAO", r"ConMon"],
            "nist_800_171": [r"NIST\s+(?:SP\s+)?800-171(?:\s+Rev(?:ision)?\s+3)?", r"CUI", r"SPRS"],
            "nist_800_53": [r"NIST\s+(?:SP\s+)?800-53(?:\s+Rev(?:ision)?\s+5)?", r"Control\s+Families"],
            "hipaa": [r"45\s+CFR\s+(?:Part\s+)?16[024]", r"Privacy\s+Rule", r"Security\s+Rule"],
            "pci_dss": [r"PCI[- ]DSS\s+v?4\.0", r"Payment\s+Card", r"Cardholder\s+Data"],
            "gdpr": [r"(?:EU\s+)?2016/679", r"Article\s+\d+", r"GDPR"],
            "soc2": [r"SOC\s*2\s+Type\s+[III]+", r"Trust\s+Service(?:s)?\s+Criteria", r"AICPA"],
            "iso_27001": [r"ISO/IEC\s+27001(?::20\d{2})?", r"ISMS", r"Annex\s+A"],
            "glba": [r"16\s+CFR\s+(?:Part\s+)?314", r"Gramm[- ]Leach[- ]Bliley", r"Safeguards\s+Rule"],
            "dfars": [r"DFARS\s+252\.204-7012", r"252\.204-7019", r"252\.204-7020", r"72[- ]hour"]
        }

    def _build_enhanced_patterns(self) -> Dict[str, Set[str]]:
        """Build enhanced keyword patterns for better detection."""
        patterns = {}

        for fw in USER_PRIORITY_FRAMEWORKS:
            # Start with base keywords
            base_keywords = fw.keywords.copy()

            # Add framework-specific enhancements
            if fw.id == "cmmc":
                base_keywords.update({
                    "cybersecurity maturity model", "cmmc level", "c3pao assessment",
                    "nist 800-171 compliance", "controlled unclassified information",
                    "32 cfr 170", "cmmc 2.0 level", "dod contractor", "dibcac"
                })
            elif fw.id == "fedramp":
                base_keywords.update({
                    "federal risk authorization", "cloud security", "authority to operate",
                    "continuous monitoring", "3pao assessment", "jab authorization",
                    "agency ato", "fedramp marketplace", "security assessment report"
                })
            elif fw.id == "nist_800_171":
                base_keywords.update({
                    "controlled unclassified information", "cui protection",
                    "security requirements", "nonfederal systems", "sprs score",
                    "110 requirements", "14 families", "800-171 rev 3", "odp"
                })
            elif fw.id == "nist_800_53":
                base_keywords.update({
                    "security controls", "privacy controls", "control families",
                    "control baselines", "low baseline", "moderate baseline", "high baseline",
                    "supply chain", "800-53 rev 5", "control catalog"
                })
            elif fw.id == "hipaa":
                base_keywords.update({
                    "protected health information", "phi", "ephi", "covered entity",
                    "business associate", "baa", "privacy rule", "security rule",
                    "breach notification", "administrative safeguards", "physical safeguards",
                    "technical safeguards", "45 cfr 160", "45 cfr 164"
                })
            elif fw.id == "pci_dss":
                base_keywords.update({
                    "payment card industry", "cardholder data", "credit card",
                    "pci compliance", "pci dss 4.0", "saq", "roc", "aoc",
                    "qsa", "card data environment", "cde", "tokenization"
                })
            elif fw.id == "gdpr":
                base_keywords.update({
                    "general data protection", "eu privacy", "data subject rights",
                    "right to be forgotten", "data controller", "data processor",
                    "lawful basis", "consent", "data protection officer", "dpo",
                    "privacy by design", "data portability", "2016/679"
                })
            elif fw.id == "soc2":
                base_keywords.update({
                    "service organization control", "trust services criteria",
                    "type i", "type ii", "aicpa", "security criteria",
                    "availability criteria", "processing integrity", "confidentiality criteria",
                    "privacy criteria", "service auditor", "management assertion"
                })
            elif fw.id == "iso_27001":
                base_keywords.update({
                    "information security management", "isms", "iso 27001",
                    "annex a controls", "statement of applicability", "soa",
                    "risk assessment", "risk treatment", "internal audit",
                    "management review", "certification", "27001:2022"
                })
            elif fw.id == "glba":
                base_keywords.update({
                    "gramm leach bliley", "financial privacy", "safeguards rule",
                    "privacy rule", "pretexting", "financial institution",
                    "customer information", "nonpublic personal information", "npi",
                    "16 cfr 314", "risk assessment", "information security program"
                })
            elif fw.id == "dfars":
                base_keywords.update({
                    "defense federal acquisition", "cyber incident reporting",
                    "72 hour reporting", "covered defense information", "cdi",
                    "252.204-7012", "252.204-7019", "252.204-7020",
                    "cloud computing", "external service provider", "forensic analysis"
                })

            patterns[fw.id] = base_keywords

        return patterns

    def detect(self, rfp_text: str, sections: List[Any] = None) -> List[FrameworkEvidence]:
        """
        Detect frameworks in RFP text with confidence scoring.

        Args:
            rfp_text: Full RFP text
            sections: Optional parsed sections for targeted analysis

        Returns:
            List of FrameworkEvidence objects sorted by confidence
        """
        text_lower = rfp_text.lower()
        evidence_list = []

        for fw_id, fw in FRAMEWORK_BY_ID.items():
            evidence = self._analyze_framework(fw_id, fw, text_lower, rfp_text, sections)
            if evidence.confidence_score > 0.3:  # Minimum threshold
                evidence_list.append(evidence)

        # Sort by confidence score descending
        evidence_list.sort(key=lambda x: x.confidence_score, reverse=True)

        return evidence_list

    def _analyze_framework(self, fw_id: str, fw: UserFramework, text_lower: str,
                          original_text: str, sections: List[Any]) -> FrameworkEvidence:
        """Analyze presence of a specific framework."""
        keyword_matches = []
        evidence_snippets = []
        section_refs = []
        specific_clauses = []

        # Check enhanced keywords
        keywords_found = set()
        for keyword in self.enhanced_patterns.get(fw_id, fw.keywords):
            if keyword in text_lower:
                keywords_found.add(keyword)
                # Find snippet
                snippet = self._extract_snippet(original_text, keyword)
                if snippet:
                    evidence_snippets.append(snippet)

        keyword_matches = list(keywords_found)

        # Check clause patterns
        if fw_id in self.clause_patterns:
            for pattern in self.clause_patterns[fw_id]:
                matches = re.findall(pattern, original_text, re.IGNORECASE)
                if matches:
                    specific_clauses.extend(matches[:3])  # Limit to first 3

        # Check sections if provided
        if sections:
            for section in sections:
                section_text = getattr(section, 'content', str(section)).lower()
                for keyword in keywords_found:
                    if keyword in section_text:
                        section_id = getattr(section, 'section_id', 'unknown')
                        if section_id not in section_refs:
                            section_refs.append(section_id)

        # Calculate confidence score
        confidence_score = self._calculate_confidence(
            keyword_matches, specific_clauses, section_refs, fw
        )

        # Determine confidence level
        confidence = self._score_to_level(confidence_score)

        # Count requirements mentioned
        req_count = len(re.findall(r"(?:requirement|control|safeguard|criteria)",
                                   text_lower)) if keyword_matches else 0

        return FrameworkEvidence(
            framework_id=fw_id,
            framework_name=fw.name,
            confidence=confidence,
            confidence_score=confidence_score,
            keyword_matches=keyword_matches[:10],  # Limit to top 10
            section_references=section_refs[:5],    # Limit to top 5
            requirement_count=req_count,
            specific_clauses=specific_clauses[:5],  # Limit to top 5
            evidence_snippets=evidence_snippets[:3] # Limit to top 3
        )

    def _extract_snippet(self, text: str, keyword: str, context_chars: int = 100) -> str:
        """Extract text snippet around keyword."""
        try:
            index = text.lower().index(keyword)
            start = max(0, index - context_chars)
            end = min(len(text), index + len(keyword) + context_chars)
            snippet = text[start:end].strip()

            # Clean up snippet
            if start > 0:
                snippet = "..." + snippet
            if end < len(text):
                snippet = snippet + "..."

            return snippet
        except ValueError:
            return ""

    def _calculate_confidence(self, keywords: List[str], clauses: List[str],
                             sections: List[str], framework: UserFramework) -> float:
        """Calculate confidence score (0.0 to 1.0)."""
        score = 0.0

        # Keyword scoring (40% weight)
        keyword_score = min(len(keywords) / 5, 1.0) * 0.4
        score += keyword_score

        # Clause scoring (30% weight)
        clause_score = min(len(clauses) / 2, 1.0) * 0.3
        score += clause_score

        # Section reference scoring (20% weight)
        section_score = min(len(sections) / 3, 1.0) * 0.2
        score += section_score

        # Framework name exact match (10% weight)
        # This is already handled in keyword matching
        if framework.name.lower() in keywords or framework.id in keywords:
            score += 0.1

        return min(score, 1.0)

    def _score_to_level(self, score: float) -> ComplianceConfidence:
        """Convert numeric score to confidence level."""
        if score >= 0.9:
            return ComplianceConfidence.HIGH
        elif score >= 0.7:
            return ComplianceConfidence.MEDIUM
        elif score >= 0.5:
            return ComplianceConfidence.LOW
        elif score >= 0.3:
            return ComplianceConfidence.MINIMAL
        else:
            return ComplianceConfidence.NONE

class Block2_RequirementsMapper:
    """
    Block 2: Requirements Mapping Engine
    Maps RFP requirements to framework controls.
    """

    def __init__(self):
        # Framework requirement mappings
        self.requirement_mappings = self._load_requirement_mappings()

    def _load_requirement_mappings(self) -> Dict[str, List[str]]:
        """Load requirement mappings for each framework."""
        return {
            "cmmc": [
                "Access Control (AC)", "Awareness and Training (AT)",
                "Audit and Accountability (AU)", "Configuration Management (CM)",
                "Identification and Authentication (IA)", "Incident Response (IR)",
                "Maintenance (MA)", "Media Protection (MP)", "Personnel Security (PS)",
                "Physical Protection (PE)", "Risk Assessment (RA)", "Security Assessment (CA)",
                "System Communications Protection (SC)", "System Information Integrity (SI)"
            ],
            "fedramp": [
                "Access Control", "Audit and Accountability", "Security Assessment",
                "Configuration Management", "Contingency Planning", "Identification and Authentication",
                "Incident Response", "Maintenance", "Media Protection", "Physical Protection",
                "Personnel Security", "Risk Assessment", "System Acquisition",
                "System Protection", "System Integrity", "Supply Chain"
            ],
            "nist_800_171": [
                "Access Control", "Awareness and Training", "Audit and Accountability",
                "Configuration Management", "Identification and Authentication",
                "Incident Response", "Maintenance", "Media Protection", "Personnel Security",
                "Physical Protection", "Risk Assessment", "Security Assessment",
                "System and Communications Protection", "System and Information Integrity"
            ],
            "nist_800_53": [
                "Access Control (AC)", "Awareness and Training (AT)", "Audit and Accountability (AU)",
                "Security Assessment and Authorization (CA)", "Configuration Management (CM)",
                "Contingency Planning (CP)", "Identification and Authentication (IA)",
                "Incident Response (IR)", "Maintenance (MA)", "Media Protection (MP)",
                "Physical and Environmental Protection (PE)", "Planning (PL)",
                "Program Management (PM)", "Personnel Security (PS)", "PII Processing (PT)",
                "Risk Assessment (RA)", "System and Services Acquisition (SA)",
                "System and Communications Protection (SC)", "System and Information Integrity (SI)",
                "Supply Chain Risk Management (SR)"
            ],
            "hipaa": [
                "Administrative Safeguards - Security Officer", "Administrative Safeguards - Workforce Training",
                "Administrative Safeguards - Access Management", "Administrative Safeguards - Security Incident Procedures",
                "Physical Safeguards - Facility Access", "Physical Safeguards - Workstation Use",
                "Physical Safeguards - Device Controls", "Technical Safeguards - Access Control",
                "Technical Safeguards - Audit Controls", "Technical Safeguards - Integrity Controls",
                "Technical Safeguards - Transmission Security", "Organizational Requirements - Business Associate Agreements"
            ],
            "pci_dss": [
                "Build and Maintain Secure Networks", "Protect Cardholder Data",
                "Maintain Vulnerability Management", "Implement Strong Access Control",
                "Regularly Monitor Networks", "Maintain Information Security Policy",
                "Network Segmentation", "Encryption Requirements", "Key Management",
                "Logging and Monitoring", "Security Testing", "Incident Response"
            ],
            "gdpr": [
                "Lawfulness of Processing", "Consent Requirements", "Data Subject Rights",
                "Right to Access", "Right to Rectification", "Right to Erasure",
                "Right to Data Portability", "Privacy by Design", "Data Protection Officer",
                "Data Protection Impact Assessment", "Records of Processing", "Security Measures",
                "Breach Notification", "International Transfers", "Processor Requirements"
            ],
            "soc2": [
                "Security - Common Criteria", "Availability Criteria", "Processing Integrity",
                "Confidentiality Criteria", "Privacy Criteria", "Risk Assessment",
                "Logical Access", "System Operations", "Change Management",
                "Risk Mitigation", "Monitoring Activities", "Vendor Management"
            ],
            "iso_27001": [
                "Information Security Policies", "Organization of Information Security",
                "Human Resource Security", "Asset Management", "Access Control",
                "Cryptography", "Physical Security", "Operations Security",
                "Communications Security", "System Acquisition", "Supplier Relationships",
                "Incident Management", "Business Continuity", "Compliance"
            ],
            "glba": [
                "Risk Assessment", "Access Controls", "Employee Training",
                "Information Systems", "Incident Response", "Service Provider Oversight",
                "Customer Information Security", "Safeguards Testing", "Board Oversight",
                "Written Information Security Program", "Qualified Individual", "Encryption"
            ],
            "dfars": [
                "Incident Reporting (72 hours)", "Media Preservation", "Malicious Code Protection",
                "NIST 800-171 Implementation", "Supply Chain Risk", "Cloud Security",
                "External Service Providers", "Forensic Analysis", "Damage Assessment",
                "Cyber Threat Indicators", "Subcontractor Flow-down", "Security Controls"
            ]
        }

    def map_requirements(self, rfp_requirements: List[str],
                        detected_frameworks: List[FrameworkEvidence]) -> Dict[str, Dict[str, Any]]:
        """
        Map RFP requirements to framework controls.

        Returns:
            Dictionary mapping framework_id to requirement mappings
        """
        mappings = {}

        for evidence in detected_frameworks:
            if evidence.confidence_score < 0.5:  # Skip low confidence
                continue

            fw_id = evidence.framework_id
            fw_requirements = self.requirement_mappings.get(fw_id, [])

            mapped = {
                "framework": evidence.framework_name,
                "confidence": evidence.confidence.value,
                "mapped_controls": [],
                "unmapped_requirements": [],
                "coverage_percentage": 0.0
            }

            # Map each RFP requirement to framework controls
            for rfp_req in rfp_requirements:
                req_lower = rfp_req.lower()
                matched = False

                for fw_req in fw_requirements:
                    if self._requirement_matches(req_lower, fw_req.lower()):
                        mapped["mapped_controls"].append({
                            "rfp_requirement": rfp_req[:200],  # Truncate long requirements
                            "framework_control": fw_req
                        })
                        matched = True
                        break

                if not matched:
                    mapped["unmapped_requirements"].append(rfp_req[:200])

            # Calculate coverage
            total_reqs = len(rfp_requirements) if rfp_requirements else 1
            mapped_count = len(mapped["mapped_controls"])
            mapped["coverage_percentage"] = (mapped_count / total_reqs) * 100

            mappings[fw_id] = mapped

        return mappings

    def _requirement_matches(self, rfp_req: str, fw_control: str) -> bool:
        """Check if RFP requirement matches framework control."""
        # Extract key terms from framework control
        control_terms = set(fw_control.split())

        # Check for matching terms
        matches = 0
        for term in control_terms:
            if len(term) > 3 and term in rfp_req:  # Skip short words
                matches += 1

        # Consider it a match if 30% of control terms are present
        return matches >= len(control_terms) * 0.3

class Block3_GapAnalyzer:
    """
    Block 3: Gap Analysis Engine
    Identifies gaps between RFP requirements and framework compliance.
    """

    def analyze_gaps(self, compliance_matrix: Dict[str, Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Analyze gaps in compliance coverage.

        Returns:
            List of identified risk areas
        """
        risk_areas = []

        for fw_id, mapping in compliance_matrix.items():
            coverage = mapping.get("coverage_percentage", 0)

            if coverage < 50:
                risk_areas.append({
                    "framework": mapping.get("framework", fw_id),
                    "risk_level": "HIGH",
                    "issue": f"Low coverage ({coverage:.1f}%)",
                    "recommendation": f"Significant gaps in {mapping['framework']} compliance. Review unmapped requirements and consider additional controls."
                })
            elif coverage < 75:
                risk_areas.append({
                    "framework": mapping.get("framework", fw_id),
                    "risk_level": "MEDIUM",
                    "issue": f"Moderate coverage ({coverage:.1f}%)",
                    "recommendation": f"Some gaps in {mapping['framework']} compliance. Address unmapped requirements to improve coverage."
                })

            # Check for specific unmapped critical areas
            unmapped = mapping.get("unmapped_requirements", [])
            critical_terms = ["incident", "breach", "encryption", "audit", "assessment", "monitoring"]

            for req in unmapped:
                req_lower = req.lower()
                for term in critical_terms:
                    if term in req_lower:
                        risk_areas.append({
                            "framework": mapping.get("framework", fw_id),
                            "risk_level": "HIGH",
                            "issue": f"Critical requirement unmapped: {term}",
                            "recommendation": f"Critical {term} requirement not mapped to {mapping['framework']} controls. Requires immediate attention."
                        })
                        break

        return risk_areas

class Block4_EvidenceRetriever:
    """
    Block 4: Evidence Retrieval Engine
    Retrieves relevant compliance evidence from Pinecone.
    """

    def __init__(self, pinecone_client=None):
        self.pinecone_client = pinecone_client
        # This would integrate with Pinecone in production

    def retrieve_evidence(self, frameworks: List[FrameworkEvidence],
                         requirements: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieve relevant evidence from knowledge base.

        Returns:
            Dictionary mapping framework_id to evidence documents
        """
        evidence_map = {}

        for fw_evidence in frameworks:
            if fw_evidence.confidence_score < 0.5:
                continue

            fw_id = fw_evidence.framework_id

            # In production, this would query Pinecone
            # For now, return structured placeholders
            evidence_map[fw_id] = [
                {
                    "source": f"{fw_evidence.framework_name} Compliance Guide",
                    "relevance_score": 0.95,
                    "content": f"Evidence for {fw_evidence.framework_name} compliance...",
                    "document_id": f"doc_{fw_id}_001"
                }
            ]

        return evidence_map

class Block5_ComplianceWriter:
    """
    Block 5: Compliance Response Generator
    Generates compliant proposal responses.
    """

    def generate_response(self, framework: str, requirement: str,
                         evidence: List[Dict[str, Any]]) -> str:
        """
        Generate compliant response for a requirement.

        Args:
            framework: Framework ID
            requirement: RFP requirement text
            evidence: Retrieved evidence documents

        Returns:
            Generated compliance response
        """
        # In production, this would use LLM to generate responses
        # For now, return template response

        fw_name = FRAMEWORK_BY_ID.get(framework, UserFramework(
            id=framework, name=framework, category="", keywords=set(),
            pdf_count=0, description="", requirements=[]
        )).name

        response = f"""
        Our solution fully addresses this requirement through our {fw_name} compliant implementation.

        We maintain comprehensive controls and processes that ensure:
        - Full compliance with {fw_name} requirements
        - Continuous monitoring and assessment
        - Regular audits and updates
        - Documentation and evidence management

        [Specific evidence and implementation details would be inserted here based on retrieved documents]
        """

        return response.strip()

class Block6_IntegrationOrchestrator:
    """
    Block 6: Framework Integration Orchestrator
    Manages integration of multiple frameworks.
    """

    def identify_overlaps(self, detected_frameworks: List[FrameworkEvidence]) -> List[Dict[str, str]]:
        """
        Identify integration points between frameworks.

        Returns:
            List of integration points
        """
        integration_points = []

        # Define known framework overlaps
        overlaps = {
            ("cmmc", "nist_800_171"): "CMMC Level 2 is based on NIST 800-171",
            ("cmmc", "dfars"): "DFARS requires NIST 800-171 implementation, foundation for CMMC",
            ("fedramp", "nist_800_53"): "FedRAMP uses NIST 800-53 control baselines",
            ("hipaa", "nist_800_53"): "Both require security controls for data protection",
            ("gdpr", "iso_27001"): "ISO 27001 helps demonstrate GDPR compliance",
            ("pci_dss", "iso_27001"): "Both require information security management",
            ("glba", "soc2"): "Both focus on customer data protection for financial services"
        }

        # Check for overlaps in detected frameworks
        fw_ids = [fw.framework_id for fw in detected_frameworks if fw.confidence_score > 0.5]

        for i, fw1 in enumerate(fw_ids):
            for fw2 in fw_ids[i+1:]:
                key = tuple(sorted([fw1, fw2]))
                if key in overlaps:
                    integration_points.append({
                        "framework_1": FRAMEWORK_BY_ID[fw1].name,
                        "framework_2": FRAMEWORK_BY_ID[fw2].name,
                        "integration": overlaps[key],
                        "benefit": "Unified compliance approach reduces duplication"
                    })

        return integration_points

    def generate_unified_approach(self, frameworks: List[FrameworkEvidence],
                                 integration_points: List[Dict[str, str]]) -> List[str]:
        """
        Generate recommendations for unified compliance.

        Returns:
            List of recommendations
        """
        recommendations = []

        if len(frameworks) > 1:
            recommendations.append(
                "Implement a unified compliance management system that addresses all detected frameworks simultaneously."
            )

        # Framework-specific recommendations
        fw_ids = [fw.framework_id for fw in frameworks if fw.confidence_score > 0.5]

        if "cmmc" in fw_ids and "nist_800_171" in fw_ids:
            recommendations.append(
                "Leverage NIST 800-171 implementation as foundation for CMMC Level 2 certification."
            )

        if "fedramp" in fw_ids:
            recommendations.append(
                "Use FedRAMP authorization package to demonstrate compliance with multiple federal requirements."
            )

        if "hipaa" in fw_ids and any(fw in fw_ids for fw in ["pci_dss", "glba"]):
            recommendations.append(
                "Implement unified data protection controls that satisfy HIPAA, PCI-DSS, and GLBA simultaneously."
            )

        if "gdpr" in fw_ids:
            recommendations.append(
                "Ensure privacy-by-design principles are embedded across all compliance activities."
            )

        if "iso_27001" in fw_ids:
            recommendations.append(
                "Use ISO 27001 ISMS as overarching framework to manage all compliance requirements."
            )

        # Add integration point recommendations
        for point in integration_points:
            recommendations.append(
                f"Integrate {point['framework_1']} and {point['framework_2']} controls: {point['benefit']}"
            )

        return recommendations

class UniversalComplianceEngine:
    """
    Main 6-Block Universal Compliance Engine.
    Orchestrates all compliance processing blocks.
    """

    def __init__(self, pinecone_client=None):
        # Initialize all blocks
        self.block1_detector = Block1_FrameworkDetector()
        self.block2_mapper = Block2_RequirementsMapper()
        self.block3_gap = Block3_GapAnalyzer()
        self.block4_evidence = Block4_EvidenceRetriever(pinecone_client)
        self.block5_writer = Block5_ComplianceWriter()
        self.block6_integrator = Block6_IntegrationOrchestrator()

    def analyze_rfp(self, rfp_text: str, parsed_sections: List[Any] = None,
                   rfp_requirements: List[str] = None) -> ComplianceAnalysis:
        """
        Perform complete compliance analysis on an RFP.

        Args:
            rfp_text: Full RFP text
            parsed_sections: Optional parsed RFP sections
            rfp_requirements: Optional extracted requirements

        Returns:
            Complete ComplianceAnalysis object
        """

        # Block 1: Detect frameworks
        detected_frameworks = self.block1_detector.detect(rfp_text, parsed_sections)

        # Block 2: Map requirements
        if not rfp_requirements:
            # Extract basic requirements if not provided
            rfp_requirements = self._extract_basic_requirements(rfp_text)

        compliance_matrix = self.block2_mapper.map_requirements(
            rfp_requirements, detected_frameworks
        )

        # Block 3: Analyze gaps
        risk_areas = self.block3_gap.analyze_gaps(compliance_matrix)

        # Block 4: Retrieve evidence (would query Pinecone in production)
        evidence_map = self.block4_evidence.retrieve_evidence(
            detected_frameworks, rfp_requirements
        )

        # Block 6: Identify integration points
        integration_points = self.block6_integrator.identify_overlaps(detected_frameworks)
        recommendations = self.block6_integrator.generate_unified_approach(
            detected_frameworks, integration_points
        )

        # Determine primary frameworks (top 3-5 by confidence)
        primary_frameworks = [
            fw.framework_id for fw in detected_frameworks[:5]
            if fw.confidence_score > 0.5
        ]

        # Compile metadata
        metadata = {
            "total_frameworks_detected": len(detected_frameworks),
            "high_confidence_count": sum(1 for fw in detected_frameworks
                                        if fw.confidence == ComplianceConfidence.HIGH),
            "total_requirements": len(rfp_requirements),
            "evidence_documents": sum(len(docs) for docs in evidence_map.values()),
            "risk_areas_identified": len(risk_areas),
            "integration_opportunities": len(integration_points)
        }

        return ComplianceAnalysis(
            detected_frameworks=detected_frameworks,
            primary_frameworks=primary_frameworks,
            compliance_matrix=compliance_matrix,
            risk_areas=risk_areas,
            integration_points=integration_points,
            recommendations=recommendations,
            metadata=metadata
        )

    def _extract_basic_requirements(self, text: str) -> List[str]:
        """Extract basic requirements from RFP text."""
        requirements = []

        # Look for requirement patterns
        patterns = [
            r"(?:shall|must|will|required to)\s+([^.]+\.)",
            r"(?:The\s+(?:vendor|contractor|supplier))\s+(?:shall|must|will)\s+([^.]+\.)",
            r"(?:Requirement|REQ)[-:\s]+([^.]+\.)"
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                req = match.group(0).strip()
                if 20 < len(req) < 500:  # Reasonable length
                    requirements.append(req)

        return requirements[:100]  # Limit to top 100

    def generate_compliance_summary(self, analysis: ComplianceAnalysis) -> str:
        """
        Generate human-readable compliance summary.

        Args:
            analysis: ComplianceAnalysis object

        Returns:
            Formatted summary string
        """
        lines = ["=" * 80, "COMPLIANCE ANALYSIS SUMMARY", "=" * 80, ""]

        # Detected frameworks
        lines.append("DETECTED COMPLIANCE FRAMEWORKS:")
        lines.append("-" * 40)
        for fw in analysis.detected_frameworks[:10]:
            confidence_str = f"[{fw.confidence.value.upper()}]"
            lines.append(f"{confidence_str:10} {fw.framework_name} ({fw.confidence_score:.1%})")
            if fw.keyword_matches:
                lines.append(f"           Keywords: {', '.join(fw.keyword_matches[:5])}")
            if fw.specific_clauses:
                lines.append(f"           Clauses: {', '.join(fw.specific_clauses[:3])}")

        # Primary frameworks
        lines.append("\nPRIMARY FRAMEWORKS (Highest Priority):")
        lines.append("-" * 40)
        for fw_id in analysis.primary_frameworks:
            fw_name = FRAMEWORK_BY_ID[fw_id].name
            lines.append(f"  • {fw_name}")

        # Risk areas
        if analysis.risk_areas:
            lines.append("\nRISK AREAS:")
            lines.append("-" * 40)
            for risk in analysis.risk_areas[:5]:
                lines.append(f"  [{risk['risk_level']}] {risk['framework']}: {risk['issue']}")

        # Integration opportunities
        if analysis.integration_points:
            lines.append("\nINTEGRATION OPPORTUNITIES:")
            lines.append("-" * 40)
            for point in analysis.integration_points[:5]:
                lines.append(f"  • {point['framework_1']} + {point['framework_2']}")
                lines.append(f"    {point['integration']}")

        # Recommendations
        lines.append("\nRECOMMENDATIONS:")
        lines.append("-" * 40)
        for i, rec in enumerate(analysis.recommendations[:7], 1):
            lines.append(f"  {i}. {rec}")

        # Metadata
        lines.append("\nANALYSIS METRICS:")
        lines.append("-" * 40)
        for key, value in analysis.metadata.items():
            lines.append(f"  {key.replace('_', ' ').title()}: {value}")

        lines.append("\n" + "=" * 80)

        return "\n".join(lines)

# Export main classes
__all__ = [
    'UniversalComplianceEngine',
    'ComplianceAnalysis',
    'FrameworkEvidence',
    'ComplianceConfidence'
]