"""
Priority Compliance Frameworks - User's Core 10 Frameworks
These are the main frameworks to focus on for RFP processing.
"""

from typing import List, Dict
from dataclasses import dataclass

@dataclass
class PriorityFramework:
    """Simplified framework definition for priority frameworks."""
    id: str
    name: str
    short_name: str
    pdf_files: List[str]  # PDF files in Compliance Frameworks folder
    keywords: List[str]
    description: str

# Your 10 Priority Frameworks with their actual PDF documents
PRIORITY_FRAMEWORKS = {
    "cmmc": PriorityFramework(
        id="cmmc",
        name="Cybersecurity Maturity Model Certification 2.0",
        short_name="CMMC",
        pdf_files=[
            "CMMC_32 CFR 170 (CMMC Program Rule).pdf",
            "CMMC_AssessmentGuideL1v2.pdf",
            "CMMC_AssessmentGuideL2v2.pdf",
            "CMMC_ModelOverview.pdf",
            "CMMC_ScopingGuideL1v2.pdf",
            "CMMC_ScopingGuideL2v2.pdf"
        ],
        keywords=["cmmc", "cmmc 2.0", "level 1", "level 2", "level 3", "c3pao", "dod", "defense"],
        description="DoD cybersecurity certification required for defense contractors"
    ),

    "fedramp": PriorityFramework(
        id="fedramp",
        name="Federal Risk and Authorization Management Program",
        short_name="FedRAMP",
        pdf_files=[
            "FEDRAMP_Agency_Authorization_Playbook.pdf",
            "FEDRAMP_CSP_Authorization_Playbook.pdf",
            "FEDRAMP_CSP_Continuous_Monitoring_Performance_Management_Guide.pdf"
        ],
        keywords=["fedramp", "ato", "moderate", "high", "low", "3pao", "cloud", "conmon"],
        description="Cloud security authorization for federal agencies"
    ),

    "nist_800_171": PriorityFramework(
        id="nist_800_171",
        name="NIST SP 800-171 Rev 3",
        short_name="NIST 800-171",
        pdf_files=[
            "NIST.SP.800-171r3.pdf",
            "NIST.SP.800-171Ar3.pdf"
        ],
        keywords=["nist 800-171", "cui", "controlled unclassified", "sprs", "rev 3"],
        description="Protection of Controlled Unclassified Information"
    ),

    "nist_800_53": PriorityFramework(
        id="nist_800_53",
        name="NIST SP 800-53 Rev 5",
        short_name="NIST 800-53",
        pdf_files=[
            "NIST.SP.800-53r5.pdf",
            "NIST.SP.800-53Ar5.pdf",
            "NIST.SP.800-53B.pdf"
        ],
        keywords=["nist 800-53", "security controls", "control families", "rev 5"],
        description="Security and Privacy Controls for Information Systems"
    ),

    "hipaa": PriorityFramework(
        id="hipaa",
        name="Health Insurance Portability and Accountability Act",
        short_name="HIPAA",
        pdf_files=[
            "HIPAA_privacysummary.pdf",
            "HIPAA_security101.pdf"
        ],
        keywords=["hipaa", "phi", "healthcare", "privacy rule", "security rule", "baa"],
        description="Healthcare data privacy and security requirements"
    ),

    "pci_dss": PriorityFramework(
        id="pci_dss",
        name="Payment Card Industry Data Security Standard v4.0",
        short_name="PCI-DSS",
        pdf_files=[
            "PCI-DSS-v4_0_1.pdf"
        ],
        keywords=["pci", "pci-dss", "payment card", "credit card", "cardholder data"],
        description="Security standards for payment card processing"
    ),

    "gdpr": PriorityFramework(
        id="gdpr",
        name="General Data Protection Regulation",
        short_name="GDPR",
        pdf_files=[
            "GDPR_CELEX_32016R0679_EN_TXT.pdf"
        ],
        keywords=["gdpr", "privacy", "eu", "data protection", "right to erasure", "dpo"],
        description="EU data protection and privacy regulation"
    ),

    "soc2": PriorityFramework(
        id="soc2",
        name="Service Organization Control 2",
        short_name="SOC 2",
        pdf_files=[],  # SOC 2 is proprietary, usually not in PDF form
        keywords=["soc 2", "soc2", "trust services", "type 1", "type 2", "aicpa"],
        description="Trust services criteria for service organizations"
    ),

    "iso_27001": PriorityFramework(
        id="iso_27001",
        name="ISO/IEC 27001",
        short_name="ISO 27001",
        pdf_files=[],  # ISO standards are paid documents
        keywords=["iso 27001", "isms", "information security", "certification"],
        description="Information security management system standard"
    ),

    "glba": PriorityFramework(
        id="glba",
        name="Gramm-Leach-Bliley Act",
        short_name="GLBA",
        pdf_files=[
            "GLBA_16 CFR Part 314 (up to date as of 9-30-2025).pdf",
            "GLBA_Privacy_viii-1.1.pdf"
        ],
        keywords=["glba", "gramm-leach", "safeguards rule", "financial privacy"],
        description="Financial institution customer data protection"
    ),

    "dfars": PriorityFramework(
        id="dfars",
        name="DFARS 252.204-7012",
        short_name="DFARS",
        pdf_files=[
            "CMMC_DFARS 2019-D041 (Cybersecurity Requirements).pdf"
        ],
        keywords=["dfars", "7012", "252.204", "cyber incident", "72 hours", "cui"],
        description="DoD cybersecurity requirements for contractors"
    )
}

def get_priority_frameworks() -> List[PriorityFramework]:
    """Get list of all priority frameworks."""
    return list(PRIORITY_FRAMEWORKS.values())

def get_priority_framework(framework_id: str) -> PriorityFramework:
    """Get a specific priority framework by ID."""
    return PRIORITY_FRAMEWORKS.get(framework_id)

def get_framework_pdfs(framework_id: str) -> List[str]:
    """Get list of PDF files for a framework."""
    fw = PRIORITY_FRAMEWORKS.get(framework_id)
    if fw:
        return fw.pdf_files
    return []

def detect_priority_frameworks(text: str) -> List[PriorityFramework]:
    """Detect which priority frameworks apply to an RFP."""
    text_lower = text.lower()
    detected = []

    for fw in PRIORITY_FRAMEWORKS.values():
        score = 0
        for keyword in fw.keywords:
            if keyword in text_lower:
                score += 1

        if score > 0:
            detected.append((score, fw))

    # Sort by score descending
    detected.sort(key=lambda x: x[0], reverse=True)
    return [fw for score, fw in detected]

def get_framework_summary() -> str:
    """Get a summary of all priority frameworks."""
    lines = ["Priority Compliance Frameworks (10 Core):", "=" * 50]

    for fw in PRIORITY_FRAMEWORKS.values():
        pdf_count = len(fw.pdf_files)
        lines.append(f"\n{fw.short_name} ({fw.id})")
        lines.append(f"  - {fw.description}")
        lines.append(f"  - {pdf_count} PDF documents available")

    return "\n".join(lines)

# Mapping to compliance categories for easy grouping
FRAMEWORK_CATEGORIES = {
    "Government": ["cmmc", "fedramp", "nist_800_171", "nist_800_53", "dfars"],
    "Healthcare": ["hipaa"],
    "Financial": ["pci_dss", "glba", "soc2"],
    "Privacy": ["gdpr"],
    "Security": ["iso_27001"]
}

def get_frameworks_by_category(category: str) -> List[PriorityFramework]:
    """Get frameworks by category."""
    framework_ids = FRAMEWORK_CATEGORIES.get(category, [])
    return [PRIORITY_FRAMEWORKS[fid] for fid in framework_ids if fid in PRIORITY_FRAMEWORKS]