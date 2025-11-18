"""
User's 10 Priority Compliance Frameworks
Streamlined implementation focusing only on the core frameworks needed.
"""

from typing import List, Set
from dataclasses import dataclass, field

@dataclass
class UserFramework:
    """User's priority framework definition."""
    id: str
    name: str
    category: str
    keywords: Set[str]
    pdf_count: int
    description: str
    requirements: List[str] = field(default_factory=list)

# YOUR 10 PRIORITY FRAMEWORKS
USER_PRIORITY_FRAMEWORKS = [
    UserFramework(
        id="cmmc",
        name="CMMC 2.0",
        category="government",
        keywords={"cmmc", "cmmc 2.0", "level 1", "level 2", "level 3", "c3pao", "dod", "defense", "cybersecurity maturity"},
        pdf_count=6,
        description="DoD cybersecurity certification (32 CFR Part 170)",
        requirements=[
            "Level 1: 17 practices (FAR 52.204-21)",
            "Level 2: 110 practices (NIST 800-171)",
            "Level 3: 110+ practices (NIST 800-172 subset)",
            "Third-party assessment (C3PAO)",
            "3-year certification validity"
        ]
    ),

    UserFramework(
        id="fedramp",
        name="FedRAMP",
        category="government",
        keywords={"fedramp", "ato", "moderate", "high", "low", "3pao", "cloud", "continuous monitoring", "conmon"},
        pdf_count=3,
        description="Federal cloud security authorization",
        requirements=[
            "Low: 125 NIST 800-53 controls",
            "Moderate: 325 NIST 800-53 controls",
            "High: 421 NIST 800-53 controls",
            "Continuous monitoring (ConMon)",
            "Annual 3PAO assessment"
        ]
    ),

    UserFramework(
        id="nist_800_171",
        name="NIST 800-171 Rev 3",
        category="government",
        keywords={"nist 800-171", "800-171", "cui", "controlled unclassified", "sprs", "rev 3", "revision 3"},
        pdf_count=2,
        description="Protection of Controlled Unclassified Information",
        requirements=[
            "110+ security requirements",
            "14 requirement families",
            "Organization-Defined Parameters (ODPs)",
            "SPRS score reporting",
            "External Service Provider requirements"
        ]
    ),

    UserFramework(
        id="nist_800_53",
        name="NIST 800-53 Rev 5",
        category="government",
        keywords={"nist 800-53", "800-53", "security controls", "control families", "rev 5", "revision 5"},
        pdf_count=3,
        description="Security and Privacy Controls for Federal Systems",
        requirements=[
            "20 control families",
            "Over 1000 controls",
            "Low/Moderate/High baselines",
            "Privacy controls integrated",
            "Supply chain controls"
        ]
    ),

    UserFramework(
        id="hipaa",
        name="HIPAA",
        category="healthcare",
        keywords={"hipaa", "phi", "healthcare", "privacy rule", "security rule", "baa", "business associate"},
        pdf_count=2,
        description="Healthcare data privacy and security",
        requirements=[
            "Administrative safeguards",
            "Physical safeguards",
            "Technical safeguards",
            "Privacy Rule compliance",
            "Security Rule compliance",
            "Breach Notification Rule"
        ]
    ),

    UserFramework(
        id="pci_dss",
        name="PCI-DSS v4.0",
        category="financial",
        keywords={"pci", "pci-dss", "pci dss", "payment card", "credit card", "cardholder", "v4.0"},
        pdf_count=1,
        description="Payment card data security",
        requirements=[
            "12 requirements",
            "6 control objectives",
            "Customized approach option",
            "Annual validation",
            "Quarterly scans"
        ]
    ),

    UserFramework(
        id="gdpr",
        name="GDPR",
        category="privacy",
        keywords={"gdpr", "privacy", "eu", "data protection", "right to erasure", "dpo", "data controller"},
        pdf_count=1,
        description="EU data protection regulation",
        requirements=[
            "Lawful basis for processing",
            "Data subject rights",
            "Privacy by design",
            "Data Protection Officer (DPO)",
            "72-hour breach notification"
        ]
    ),

    UserFramework(
        id="soc2",
        name="SOC 2",
        category="financial",
        keywords={"soc 2", "soc2", "trust services", "type 1", "type 2", "type i", "type ii", "aicpa"},
        pdf_count=0,  # Proprietary
        description="Trust services criteria for service organizations",
        requirements=[
            "Security criteria (required)",
            "Availability (optional)",
            "Processing Integrity (optional)",
            "Confidentiality (optional)",
            "Privacy (optional)"
        ]
    ),

    UserFramework(
        id="iso_27001",
        name="ISO 27001",
        category="security",
        keywords={"iso 27001", "iso27001", "isms", "information security", "27001", "certification"},
        pdf_count=0,  # Paid standard
        description="Information security management system",
        requirements=[
            "114 controls in Annex A",
            "Risk assessment",
            "Statement of Applicability",
            "Management review",
            "Internal audit"
        ]
    ),

    UserFramework(
        id="glba",
        name="GLBA",
        category="financial",
        keywords={"glba", "gramm-leach", "safeguards rule", "financial privacy", "16 cfr 314"},
        pdf_count=2,
        description="Financial institution customer data protection",
        requirements=[
            "Safeguards Rule",
            "Privacy Rule",
            "Pretexting provisions",
            "Risk assessment",
            "Employee training"
        ]
    ),

    UserFramework(
        id="dfars",
        name="DFARS 252.204-7012",
        category="government",
        keywords={"dfars", "7012", "252.204", "cyber incident", "72 hours", "cui", "covered defense"},
        pdf_count=1,
        description="DoD cybersecurity requirements for contractors",
        requirements=[
            "NIST 800-171 implementation",
            "72-hour incident reporting",
            "Forensic preservation (90 days)",
            "Flow down to subcontractors",
            "SPRS reporting"
        ]
    )
]

def detect_user_frameworks(text: str) -> List[UserFramework]:
    """Detect which of the user's 10 priority frameworks apply to an RFP."""
    text_lower = text.lower()
    detected = []

    for fw in USER_PRIORITY_FRAMEWORKS:
        score = 0
        matched_keywords = []

        for keyword in fw.keywords:
            if keyword in text_lower:
                score += 1
                matched_keywords.append(keyword)

        if score > 0:
            detected.append((score, fw, matched_keywords))

    # Sort by score descending
    detected.sort(key=lambda x: x[0], reverse=True)

    return [(fw, matches) for _, fw, matches in detected]

def get_framework_by_priority(framework_id: str) -> UserFramework:
    """Get a specific priority framework by ID."""
    for fw in USER_PRIORITY_FRAMEWORKS:
        if fw.id == framework_id:
            return fw
    return None

def get_priority_summary() -> str:
    """Get a summary of the 10 priority frameworks."""
    lines = ["YOUR 10 PRIORITY COMPLIANCE FRAMEWORKS", "=" * 50]

    gov_count = sum(1 for fw in USER_PRIORITY_FRAMEWORKS if fw.category == "government")
    fin_count = sum(1 for fw in USER_PRIORITY_FRAMEWORKS if fw.category == "financial")

    lines.append(f"\nGovernment: {gov_count} frameworks")
    lines.append(f"Financial: {fin_count} frameworks")
    lines.append("Healthcare: 1 framework")
    lines.append("Privacy: 1 framework")
    lines.append("Security: 1 framework")

    lines.append("\n" + "-" * 50)
    for fw in USER_PRIORITY_FRAMEWORKS:
        pdf_status = f"{fw.pdf_count} PDFs" if fw.pdf_count > 0 else "No PDFs (proprietary)"
        lines.append(f"{fw.name:20} | {fw.category:10} | {pdf_status}")

    return "\n".join(lines)

# Quick lookup dictionaries
FRAMEWORK_BY_ID = {fw.id: fw for fw in USER_PRIORITY_FRAMEWORKS}
FRAMEWORKS_BY_CATEGORY = {}
for fw in USER_PRIORITY_FRAMEWORKS:
    if fw.category not in FRAMEWORKS_BY_CATEGORY:
        FRAMEWORKS_BY_CATEGORY[fw.category] = []
    FRAMEWORKS_BY_CATEGORY[fw.category].append(fw)