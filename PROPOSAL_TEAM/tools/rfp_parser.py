"""
Universal RFP Parser - Handles Multiple RFP Formats
Supports: FAR Section L/M, SLED, Commercial, International
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

class RFPFormat(Enum):
    """Supported RFP format types."""
    FAR_SECTION_L_M = "far_section_l_m"  # Federal Acquisition Regulation
    SLED = "sled"  # State/Local/Education
    COMMERCIAL = "commercial"  # Private sector RFPs
    INTERNATIONAL = "international"  # Global/UN/World Bank
    UNKNOWN = "unknown"

@dataclass
class RFPSection:
    """Represents a parsed section of an RFP."""
    section_id: str
    title: str
    content: str
    section_type: str  # "instructions", "requirements", "evaluation", "technical", etc.
    subsections: List['RFPSection'] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    compliance_refs: List[str] = field(default_factory=list)
    page_numbers: List[int] = field(default_factory=list)

@dataclass
class ParsedRFP:
    """Complete parsed RFP document."""
    format_type: RFPFormat
    title: str
    solicitation_number: str
    issuing_agency: str
    due_date: Optional[str]
    sections: List[RFPSection]
    detected_frameworks: List[Tuple[str, float]]  # (framework_id, confidence)
    technical_requirements: List[str]
    evaluation_criteria: Dict[str, Any]
    submission_instructions: Dict[str, str]
    metadata: Dict[str, Any]

class RFPFormatDetector:
    """Detects RFP format from document content."""

    # Format detection patterns
    FAR_PATTERNS = {
        "section_l": r"section\s+l\s*[-–—]\s*instructions",
        "section_m": r"section\s+m\s*[-–—]\s*evaluation",
        "section_c": r"section\s+c\s*[-–—]\s*(?:description|statement\s+of\s+work)",
        "far_clause": r"FAR\s+\d+\.\d+",
        "dfars_clause": r"DFARS\s+\d+\.\d+",
        "naics_code": r"NAICS\s+(?:Code|#)?\s*:?\s*\d+",
        "federal_terms": r"(?:GSA|FedRAMP|DUNS|SAM|Cage\s+Code|Small\s+Business)"
    }

    SLED_PATTERNS = {
        "state_terms": r"(?:State\s+of|Commonwealth|County|Municipality|School\s+District)",
        "procurement_code": r"(?:RFP|ITB|RFQ|IFB)\s*#?\s*\d+[-\w]+",
        "state_contract": r"(?:State\s+Contract|Master\s+Agreement|Cooperative\s+Purchasing)",
        "education": r"(?:University|College|K-12|School\s+Board|Educational\s+Institution)"
    }

    COMMERCIAL_PATTERNS = {
        "corporate_terms": r"(?:Vendor|Supplier|Service\s+Provider|Partner|Solution)",
        "commercial_sections": r"(?:Executive\s+Summary|Business\s+Requirements|Functional\s+Requirements)",
        "pricing_models": r"(?:SaaS|License|Subscription|Professional\s+Services|Time\s+and\s+Materials)",
        "corporate_compliance": r"(?:NDA|MSA|SLA|SoW|Terms\s+and\s+Conditions)"
    }

    INTERNATIONAL_PATTERNS = {
        "un_terms": r"(?:United\s+Nations|UN|World\s+Bank|IMF|UNESCO|UNDP)",
        "international": r"(?:International|Global|Multi-country|Cross-border)",
        "currencies": r"(?:USD|EUR|GBP|CHF|SDR)",
        "international_standards": r"(?:ISO\s+\d+|IEC\s+\d+|ITU)"
    }

    def detect_format(self, text: str) -> Tuple[RFPFormat, float]:
        """
        Detect RFP format with confidence score.
        Returns: (format_type, confidence_score)
        """
        text_lower = text.lower()
        scores = {}

        # Check FAR patterns
        far_score = 0
        for pattern_name, pattern in self.FAR_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                far_score += 2 if pattern_name in ["section_l", "section_m"] else 1
        scores[RFPFormat.FAR_SECTION_L_M] = far_score

        # Check SLED patterns
        sled_score = 0
        for pattern_name, pattern in self.SLED_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                sled_score += 1.5 if pattern_name == "state_terms" else 1
        scores[RFPFormat.SLED] = sled_score

        # Check Commercial patterns
        commercial_score = 0
        for pattern_name, pattern in self.COMMERCIAL_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                commercial_score += 1
        scores[RFPFormat.COMMERCIAL] = commercial_score

        # Check International patterns
        international_score = 0
        for pattern_name, pattern in self.INTERNATIONAL_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                international_score += 1.5 if pattern_name == "un_terms" else 1
        scores[RFPFormat.INTERNATIONAL] = international_score

        # Determine format with highest score
        max_score = max(scores.values()) if scores else 0
        if max_score < 2:  # Low confidence threshold
            return (RFPFormat.UNKNOWN, 0.0)

        format_type = max(scores, key=scores.get)
        # Calculate confidence (normalize to 0-1)
        confidence = min(max_score / 10, 1.0)

        return (format_type, confidence)

class UniversalRFPParser:
    """
    Adaptive RFP parser that handles multiple formats.
    """

    def __init__(self):
        self.format_detector = RFPFormatDetector()
        self.parsers = {
            RFPFormat.FAR_SECTION_L_M: FARSectionParser(),
            RFPFormat.SLED: SLEDParser(),
            RFPFormat.COMMERCIAL: CommercialParser(),
            RFPFormat.INTERNATIONAL: InternationalParser(),
            RFPFormat.UNKNOWN: GenericParser()
        }

    def parse(self, text: str, filename: str = "") -> ParsedRFP:
        """
        Parse RFP with automatic format detection.
        """
        # Detect format
        format_type, confidence = self.format_detector.detect_format(text)

        # Select appropriate parser
        parser = self.parsers.get(format_type, self.parsers[RFPFormat.UNKNOWN])

        # Parse document
        parsed = parser.parse(text, filename)
        parsed.format_type = format_type
        parsed.metadata["format_confidence"] = confidence

        return parsed

class FARSectionParser:
    """Parser for FAR Section L/M format RFPs."""

    def parse(self, text: str, filename: str) -> ParsedRFP:
        """Parse FAR format RFP."""
        sections = []

        # Extract Section L (Instructions)
        section_l = self._extract_section(text, "Section L", "instructions")
        if section_l:
            sections.append(section_l)

        # Extract Section M (Evaluation)
        section_m = self._extract_section(text, "Section M", "evaluation")
        if section_m:
            sections.append(section_m)

        # Extract Section C (Statement of Work)
        section_c = self._extract_section(text, "Section C", "technical")
        if section_c:
            sections.append(section_c)

        # Extract metadata
        solicitation = self._extract_solicitation_number(text)
        agency = self._extract_agency(text)
        due_date = self._extract_due_date(text)

        # Extract evaluation criteria from Section M
        eval_criteria = self._extract_evaluation_criteria(section_m.content if section_m else text)

        # Extract submission instructions from Section L
        submission = self._extract_submission_instructions(section_l.content if section_l else text)

        return ParsedRFP(
            format_type=RFPFormat.FAR_SECTION_L_M,
            title=self._extract_title(text),
            solicitation_number=solicitation,
            issuing_agency=agency,
            due_date=due_date,
            sections=sections,
            detected_frameworks=[],  # Will be populated by framework detector
            technical_requirements=self._extract_technical_requirements(text),
            evaluation_criteria=eval_criteria,
            submission_instructions=submission,
            metadata={"filename": filename, "format": "FAR"}
        )

    def _extract_section(self, text: str, section_name: str, section_type: str) -> Optional[RFPSection]:
        """Extract a specific section from FAR document."""
        pattern = rf"{section_name}\s*[-–—:]\s*(.*?)(?=Section\s+[A-Z]|\Z)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            content = match.group(1).strip()

            # Extract subsections (L.1, L.2, etc.)
            subsections = []
            subsection_pattern = rf"{section_name[0]}\.(\d+)\s*[-–—:]\s*(.*?)(?={section_name[0]}\.\d+|\Z)"
            for submatch in re.finditer(subsection_pattern, content, re.IGNORECASE | re.DOTALL):
                subsections.append(RFPSection(
                    section_id=f"{section_name[0]}.{submatch.group(1)}",
                    title=self._clean_title(submatch.group(2).split('\n')[0]),
                    content=submatch.group(2).strip(),
                    section_type=section_type
                ))

            return RFPSection(
                section_id=section_name,
                title=section_name,
                content=content,
                section_type=section_type,
                subsections=subsections
            )
        return None

    def _extract_solicitation_number(self, text: str) -> str:
        """Extract solicitation number."""
        patterns = [
            r"Solicitation\s+(?:Number|#|No\.?)\s*:?\s*([\w-]+)",
            r"RFP\s+(?:Number|#|No\.?)\s*:?\s*([\w-]+)",
            r"(?:Contract|Requisition)\s+(?:Number|#|No\.?)\s*:?\s*([\w-]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""

    def _extract_agency(self, text: str) -> str:
        """Extract issuing agency."""
        patterns = [
            r"(?:Issued\s+by|Agency|Department|Office)\s*:?\s*([A-Za-z\s&]+?)(?:\n|$)",
            r"U\.?S\.?\s+(Department\s+of\s+[A-Za-z\s]+)",
            r"(Department\s+of\s+[A-Za-z\s]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""

    def _extract_due_date(self, text: str) -> str:
        """Extract proposal due date."""
        patterns = [
            r"(?:Due|Submission|Closing)\s+Date\s*:?\s*([A-Za-z]+\s+\d+,?\s+\d{4})",
            r"(?:Due|Submit)\s+(?:by|before)\s*:?\s*([A-Za-z]+\s+\d+,?\s+\d{4})",
            r"Proposals?\s+due\s*:?\s*([A-Za-z]+\s+\d+,?\s+\d{4})"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""

    def _extract_title(self, text: str) -> str:
        """Extract RFP title."""
        lines = text.split('\n')
        for line in lines[:20]:  # Check first 20 lines
            if 'request for proposal' in line.lower() or 'rfp' in line.lower():
                return line.strip()
        return "Untitled RFP"

    def _extract_evaluation_criteria(self, text: str) -> Dict[str, Any]:
        """Extract evaluation criteria and weights."""
        criteria = {}

        # Look for evaluation factors
        factor_pattern = r"Factor\s+(\d+)\s*[-–—:]\s*([^\n]+)"
        for match in re.finditer(factor_pattern, text, re.IGNORECASE):
            factor_num = match.group(1)
            factor_name = match.group(2).strip()
            criteria[f"factor_{factor_num}"] = factor_name

        # Look for weights/percentages
        weight_pattern = r"([A-Za-z\s]+)\s*[-–—:]\s*(\d+)%"
        for match in re.finditer(weight_pattern, text):
            criteria[f"{match.group(1).strip().lower()}_weight"] = f"{match.group(2)}%"

        return criteria

    def _extract_submission_instructions(self, text: str) -> Dict[str, str]:
        """Extract submission instructions."""
        instructions = {}

        # Page limits
        page_pattern = r"(?:Page|Pages)\s+Limit\s*:?\s*(\d+)"
        match = re.search(page_pattern, text, re.IGNORECASE)
        if match:
            instructions["page_limit"] = match.group(1)

        # Format requirements
        format_pattern = r"Format\s*:?\s*([^\n]+)"
        match = re.search(format_pattern, text, re.IGNORECASE)
        if match:
            instructions["format"] = match.group(1).strip()

        # Number of copies
        copies_pattern = r"(\d+)\s+copies?"
        match = re.search(copies_pattern, text, re.IGNORECASE)
        if match:
            instructions["copies"] = match.group(1)

        return instructions

    def _extract_technical_requirements(self, text: str) -> List[str]:
        """Extract technical requirements."""
        requirements = []

        # Look for numbered requirements
        req_pattern = r"(?:shall|must|will|required to)\s+([^.]+\.)"
        for match in re.finditer(req_pattern, text, re.IGNORECASE):
            requirement = match.group(0).strip()
            if len(requirement) > 20:  # Filter out short phrases
                requirements.append(requirement)

        return requirements[:50]  # Limit to top 50 requirements

    def _clean_title(self, title: str) -> str:
        """Clean section title."""
        return re.sub(r'\s+', ' ', title).strip()

class SLEDParser:
    """Parser for State/Local/Education RFPs."""

    def parse(self, text: str, filename: str) -> ParsedRFP:
        """Parse SLED format RFP."""
        sections = self._extract_sections(text)

        return ParsedRFP(
            format_type=RFPFormat.SLED,
            title=self._extract_title(text),
            solicitation_number=self._extract_rfp_number(text),
            issuing_agency=self._extract_agency(text),
            due_date=self._extract_due_date(text),
            sections=sections,
            detected_frameworks=[],
            technical_requirements=self._extract_requirements(text),
            evaluation_criteria=self._extract_evaluation(text),
            submission_instructions=self._extract_submission(text),
            metadata={"filename": filename, "format": "SLED"}
        )

    def _extract_sections(self, text: str) -> List[RFPSection]:
        """Extract sections from SLED RFP."""
        sections = []

        # Common SLED section patterns
        section_patterns = [
            (r"(?:Scope\s+of\s+Work|Statement\s+of\s+Work)", "technical"),
            (r"(?:Technical\s+Requirements|Specifications)", "technical"),
            (r"(?:Proposal\s+Requirements|Submission\s+Requirements)", "instructions"),
            (r"(?:Evaluation\s+Criteria|Selection\s+Criteria)", "evaluation"),
            (r"(?:Terms\s+and\s+Conditions|Contract\s+Terms)", "terms"),
            (r"(?:Pricing|Cost\s+Proposal)", "pricing")
        ]

        for pattern, section_type in section_patterns:
            match = re.search(f"{pattern}[:\s]*(.*?)(?=(?:{pattern})|$)",
                            text, re.IGNORECASE | re.DOTALL)
            if match:
                sections.append(RFPSection(
                    section_id=f"section_{len(sections)+1}",
                    title=pattern.replace(r"(?:", "").replace("|", "/").replace(")", ""),
                    content=match.group(1).strip() if match.lastindex else "",
                    section_type=section_type
                ))

        return sections

    def _extract_title(self, text: str) -> str:
        """Extract SLED RFP title."""
        patterns = [
            r"Request\s+for\s+Proposal[:\s]*([^\n]+)",
            r"RFP\s+for[:\s]*([^\n]+)",
            r"Title[:\s]*([^\n]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "State/Local RFP"

    def _extract_rfp_number(self, text: str) -> str:
        """Extract RFP number for SLED."""
        patterns = [
            r"RFP\s*#?\s*:?\s*([\w-]+)",
            r"Solicitation\s*#?\s*:?\s*([\w-]+)",
            r"Bid\s*#?\s*:?\s*([\w-]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""

    def _extract_agency(self, text: str) -> str:
        """Extract issuing agency for SLED."""
        patterns = [
            r"(?:State\s+of|County\s+of|City\s+of)\s+([A-Za-z\s]+)",
            r"([A-Za-z\s]+(?:University|College|School\s+District))",
            r"Issued\s+by[:\s]*([^\n]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""

    def _extract_due_date(self, text: str) -> str:
        """Extract due date."""
        patterns = [
            r"Due\s+Date[:\s]*([^\n]+\d{4})",
            r"Submission\s+Deadline[:\s]*([^\n]+\d{4})",
            r"Proposals?\s+Due[:\s]*([^\n]+\d{4})"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""

    def _extract_requirements(self, text: str) -> List[str]:
        """Extract technical requirements."""
        requirements = []
        patterns = [
            r"(?:Vendor|Contractor|Proposer)\s+(?:shall|must|will)\s+([^.]+\.)",
            r"(?:System|Solution|Service)\s+(?:shall|must|will)\s+([^.]+\.)"
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                req = match.group(0).strip()
                if len(req) > 20:
                    requirements.append(req)
        return requirements[:30]

    def _extract_evaluation(self, text: str) -> Dict[str, Any]:
        """Extract evaluation criteria."""
        criteria = {}

        # Look for evaluation criteria sections
        eval_section = re.search(r"Evaluation\s+Criteria(.*?)(?=\n\n|\Z)",
                                text, re.IGNORECASE | re.DOTALL)
        if eval_section:
            content = eval_section.group(1)
            # Extract criteria with percentages
            for match in re.finditer(r"([A-Za-z\s]+)\s*[-–]\s*(\d+)%", content):
                criteria[match.group(1).strip().lower()] = f"{match.group(2)}%"

        return criteria

    def _extract_submission(self, text: str) -> Dict[str, str]:
        """Extract submission instructions."""
        instructions = {}

        # Submission method
        if "electronic" in text.lower():
            instructions["method"] = "electronic"
        elif "hard copy" in text.lower() or "printed" in text.lower():
            instructions["method"] = "hard copy"

        # Number of copies
        copies = re.search(r"(\d+)\s+copies", text, re.IGNORECASE)
        if copies:
            instructions["copies"] = copies.group(1)

        return instructions

class CommercialParser:
    """Parser for commercial/private sector RFPs."""

    def parse(self, text: str, filename: str) -> ParsedRFP:
        """Parse commercial RFP."""
        sections = self._extract_sections(text)

        return ParsedRFP(
            format_type=RFPFormat.COMMERCIAL,
            title=self._extract_title(text),
            solicitation_number=self._extract_reference(text),
            issuing_agency=self._extract_company(text),
            due_date=self._extract_deadline(text),
            sections=sections,
            detected_frameworks=[],
            technical_requirements=self._extract_requirements(text),
            evaluation_criteria=self._extract_criteria(text),
            submission_instructions=self._extract_submission(text),
            metadata={"filename": filename, "format": "Commercial"}
        )

    def _extract_sections(self, text: str) -> List[RFPSection]:
        """Extract sections from commercial RFP."""
        sections = []

        # Common commercial RFP sections
        patterns = [
            (r"Executive\s+Summary", "executive"),
            (r"(?:Business|Functional)\s+Requirements", "requirements"),
            (r"Technical\s+(?:Requirements|Specifications)", "technical"),
            (r"(?:Pricing|Commercial)\s+(?:Model|Terms)", "pricing"),
            (r"Implementation\s+(?:Plan|Timeline)", "implementation"),
            (r"Support\s+and\s+Maintenance", "support"),
            (r"Service\s+Level\s+Agreement", "sla")
        ]

        for pattern, section_type in patterns:
            match = re.search(f"{pattern}[:\s]*(.*?)(?=\d+\.|{pattern}|$)",
                            text, re.IGNORECASE | re.DOTALL)
            if match:
                sections.append(RFPSection(
                    section_id=f"section_{len(sections)+1}",
                    title=pattern,
                    content=match.group(1).strip() if match.lastindex else "",
                    section_type=section_type
                ))

        return sections

    def _extract_title(self, text: str) -> str:
        """Extract title."""
        patterns = [
            r"Request\s+for\s+Proposal[:\s]*([^\n]+)",
            r"RFP[:\s]+([^\n]+)",
            r"^([^\n]+RFP[^\n]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        return "Commercial RFP"

    def _extract_reference(self, text: str) -> str:
        """Extract reference number."""
        patterns = [
            r"Reference[:\s]*#?\s*([\w-]+)",
            r"RFP[:\s]*#?\s*([\w-]+)",
            r"Project[:\s]*#?\s*([\w-]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""

    def _extract_company(self, text: str) -> str:
        """Extract issuing company."""
        patterns = [
            r"(?:Issued\s+by|Company|Organization)[:\s]*([^\n]+)",
            r"^([A-Z][A-Za-z\s&]+(?:Inc|LLC|Ltd|Corporation|Corp))"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        return ""

    def _extract_deadline(self, text: str) -> str:
        """Extract submission deadline."""
        patterns = [
            r"(?:Submission|Response)\s+Deadline[:\s]*([^\n]+)",
            r"Due\s+(?:Date|by)[:\s]*([^\n]+)",
            r"Proposals?\s+must\s+be\s+(?:submitted|received)\s+by[:\s]*([^\n]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""

    def _extract_requirements(self, text: str) -> List[str]:
        """Extract business/technical requirements."""
        requirements = []

        # Look for numbered requirements
        for match in re.finditer(r"\d+\.\s+([^.]+\.)", text):
            req = match.group(1).strip()
            if 20 < len(req) < 500:
                requirements.append(req)

        # Look for bulleted requirements
        for match in re.finditer(r"[•·-]\s+([^•·-\n]+)", text):
            req = match.group(1).strip()
            if 20 < len(req) < 500:
                requirements.append(req)

        return requirements[:40]

    def _extract_criteria(self, text: str) -> Dict[str, Any]:
        """Extract evaluation criteria."""
        criteria = {}

        # Look for evaluation sections
        eval_patterns = [
            r"Evaluation\s+Criteria[:\s]*(.*?)(?=\n\n|\d+\.|\Z)",
            r"Selection\s+Criteria[:\s]*(.*?)(?=\n\n|\d+\.|\Z)",
            r"Scoring[:\s]*(.*?)(?=\n\n|\d+\.|\Z)"
        ]

        for pattern in eval_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1)
                # Extract criteria items
                for item_match in re.finditer(r"([A-Za-z\s]+)\s*[-–:]\s*(\d+)", content):
                    criteria[item_match.group(1).strip().lower()] = item_match.group(2)
                break

        return criteria

    def _extract_submission(self, text: str) -> Dict[str, str]:
        """Extract submission instructions."""
        instructions = {}

        # Email submission
        email = re.search(r"(?:Email|Submit\s+to)[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", text)
        if email:
            instructions["email"] = email.group(1)

        # Format requirements
        if "pdf" in text.lower():
            instructions["format"] = "PDF"
        elif "word" in text.lower() or "docx" in text.lower():
            instructions["format"] = "Word"

        return instructions

class InternationalParser:
    """Parser for international organization RFPs."""

    def parse(self, text: str, filename: str) -> ParsedRFP:
        """Parse international RFP."""
        sections = self._extract_sections(text)

        return ParsedRFP(
            format_type=RFPFormat.INTERNATIONAL,
            title=self._extract_title(text),
            solicitation_number=self._extract_reference(text),
            issuing_agency=self._extract_organization(text),
            due_date=self._extract_deadline(text),
            sections=sections,
            detected_frameworks=[],
            technical_requirements=self._extract_requirements(text),
            evaluation_criteria=self._extract_evaluation(text),
            submission_instructions=self._extract_submission(text),
            metadata={"filename": filename, "format": "International"}
        )

    def _extract_sections(self, text: str) -> List[RFPSection]:
        """Extract sections from international RFP."""
        sections = []

        # UN/World Bank common sections
        patterns = [
            (r"Terms\s+of\s+Reference", "tor"),
            (r"Technical\s+(?:Proposal|Specifications)", "technical"),
            (r"Financial\s+Proposal", "financial"),
            (r"Evaluation\s+(?:Criteria|Methodology)", "evaluation"),
            (r"(?:Special|General)\s+Conditions", "conditions"),
            (r"Deliverables", "deliverables")
        ]

        for pattern, section_type in patterns:
            match = re.search(f"{pattern}[:\s]*(.*?)(?={pattern}|\Z)",
                            text, re.IGNORECASE | re.DOTALL)
            if match:
                sections.append(RFPSection(
                    section_id=f"section_{len(sections)+1}",
                    title=pattern,
                    content=match.group(1).strip() if match.lastindex else "",
                    section_type=section_type
                ))

        return sections

    def _extract_title(self, text: str) -> str:
        """Extract title."""
        patterns = [
            r"Request\s+for\s+(?:Proposal|Quotation)[:\s]*([^\n]+)",
            r"Title[:\s]*([^\n]+)",
            r"Project[:\s]*([^\n]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "International RFP"

    def _extract_reference(self, text: str) -> str:
        """Extract reference number."""
        patterns = [
            r"Reference[:\s]*(?:No\.?|Number|#)?\s*([\w/-]+)",
            r"RFP[:\s]*(?:No\.?|Number|#)?\s*([\w/-]+)",
            r"Procurement\s+Reference[:\s]*([\w/-]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""

    def _extract_organization(self, text: str) -> str:
        """Extract issuing organization."""
        patterns = [
            r"(United\s+Nations[^,\n]*)",
            r"(World\s+Bank[^,\n]*)",
            r"((?:UNDP|UNESCO|UNICEF|WHO|ILO|FAO|IMF)[^,\n]*)",
            r"(?:Issued\s+by|Organization)[:\s]*([^\n]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""

    def _extract_deadline(self, text: str) -> str:
        """Extract deadline."""
        patterns = [
            r"(?:Submission|Closing)\s+(?:Date|Deadline)[:\s]*([^\n]+\d{4})",
            r"Deadline[:\s]*([^\n]+\d{4})",
            r"(?:Due|Submit)\s+by[:\s]*([^\n]+\d{4})"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""

    def _extract_requirements(self, text: str) -> List[str]:
        """Extract requirements from Terms of Reference."""
        requirements = []

        # Look in Terms of Reference section
        tor = re.search(r"Terms\s+of\s+Reference(.*?)(?=\d+\.|Terms|\Z)",
                       text, re.IGNORECASE | re.DOTALL)
        if tor:
            content = tor.group(1)
            # Extract requirements
            for match in re.finditer(r"(?:shall|must|will|required)\s+([^.]+\.)", content, re.IGNORECASE):
                req = match.group(0).strip()
                if len(req) > 20:
                    requirements.append(req)

        return requirements[:30]

    def _extract_evaluation(self, text: str) -> Dict[str, Any]:
        """Extract evaluation criteria."""
        criteria = {}

        # Common international evaluation criteria
        eval_section = re.search(r"Evaluation\s+(?:Criteria|Methodology)(.*?)(?=\d+\.|\Z)",
                                text, re.IGNORECASE | re.DOTALL)
        if eval_section:
            content = eval_section.group(1)

            # Technical/Financial split (common in international RFPs)
            tech_match = re.search(r"Technical[:\s]*(\d+)%", content, re.IGNORECASE)
            if tech_match:
                criteria["technical_weight"] = f"{tech_match.group(1)}%"

            fin_match = re.search(r"Financial[:\s]*(\d+)%", content, re.IGNORECASE)
            if fin_match:
                criteria["financial_weight"] = f"{fin_match.group(1)}%"

        return criteria

    def _extract_submission(self, text: str) -> Dict[str, str]:
        """Extract submission instructions."""
        instructions = {}

        # Look for submission portal/system
        portal = re.search(r"(?:submit|upload)\s+(?:through|via|at)[:\s]*([^\n]+)", text, re.IGNORECASE)
        if portal:
            instructions["portal"] = portal.group(1).strip()

        # Language requirements
        if "english" in text.lower():
            instructions["language"] = "English"

        # Currency
        currency = re.search(r"(?:Currency|Prices?\s+in)[:\s]*(USD|EUR|GBP|CHF)", text, re.IGNORECASE)
        if currency:
            instructions["currency"] = currency.group(1)

        return instructions

class GenericParser:
    """Fallback parser for unknown RFP formats."""

    def parse(self, text: str, filename: str) -> ParsedRFP:
        """Parse unknown format RFP with best-effort extraction."""

        # Try to extract basic sections
        sections = self._extract_generic_sections(text)

        return ParsedRFP(
            format_type=RFPFormat.UNKNOWN,
            title=self._extract_title(text),
            solicitation_number=self._extract_number(text),
            issuing_agency=self._extract_issuer(text),
            due_date=self._extract_date(text),
            sections=sections,
            detected_frameworks=[],
            technical_requirements=self._extract_requirements(text),
            evaluation_criteria={},
            submission_instructions={},
            metadata={"filename": filename, "format": "Unknown", "warning": "Generic parser used"}
        )

    def _extract_generic_sections(self, text: str) -> List[RFPSection]:
        """Extract sections using generic patterns."""
        sections = []

        # Look for numbered sections
        for match in re.finditer(r"(\d+)\.\s+([A-Z][^.]+)\n(.*?)(?=\d+\.\s+[A-Z]|\Z)",
                                text, re.DOTALL):
            sections.append(RFPSection(
                section_id=f"section_{match.group(1)}",
                title=match.group(2).strip(),
                content=match.group(3).strip(),
                section_type="generic"
            ))

        # If no numbered sections, try headers
        if not sections:
            for match in re.finditer(r"^([A-Z][A-Z\s]+)$\n(.*?)(?=^[A-Z][A-Z\s]+$|\Z)",
                                    text, re.MULTILINE | re.DOTALL):
                sections.append(RFPSection(
                    section_id=f"section_{len(sections)+1}",
                    title=match.group(1).strip(),
                    content=match.group(2).strip(),
                    section_type="generic"
                ))

        return sections

    def _extract_title(self, text: str) -> str:
        """Extract title with fallback."""
        lines = text.split('\n')
        for line in lines[:10]:
            if len(line) > 10 and len(line) < 200:
                return line.strip()
        return "Unknown RFP"

    def _extract_number(self, text: str) -> str:
        """Extract any reference number."""
        match = re.search(r"(?:RFP|Reference|Number|#)[:\s]*([\w-]+)", text, re.IGNORECASE)
        return match.group(1) if match else ""

    def _extract_issuer(self, text: str) -> str:
        """Extract issuer with fallback."""
        match = re.search(r"(?:Issued\s+by|From|Organization)[:\s]*([^\n]+)", text, re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _extract_date(self, text: str) -> str:
        """Extract any date that might be due date."""
        # Look for date patterns
        date_pattern = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}"
        dates = re.findall(date_pattern, text, re.IGNORECASE)
        # Return last date found (often the due date)
        return dates[-1] if dates else ""

    def _extract_requirements(self, text: str) -> List[str]:
        """Extract any requirement-like statements."""
        requirements = []

        # Look for requirement keywords
        for match in re.finditer(r"(?:must|shall|required|need\s+to)\s+([^.]+\.)", text, re.IGNORECASE):
            req = match.group(0).strip()
            if 20 < len(req) < 500:
                requirements.append(req)

        return requirements[:25]

# Export main parser class
__all__ = ['UniversalRFPParser', 'ParsedRFP', 'RFPFormat', 'RFPSection']