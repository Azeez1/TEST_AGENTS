"""
Master Compliance Framework Knowledge Base.

This module contains comprehensive compliance framework definitions across
Government, Healthcare, Cloud, Finance, and Enterprise sectors.

These frameworks are stable and evergreen, used for:
- Auto-detecting applicable compliance requirements in RFPs
- Auto-generating compliance sections in proposals
- Building compliance matrices with evidence mapping
- Enriching sector-specific templates
"""

from typing import Dict, List, Set
from dataclasses import dataclass, field


@dataclass
class ComplianceFramework:
    """A compliance framework definition."""

    id: str
    name: str
    category: str  # government, healthcare, cloud, finance, privacy, devsecops, physical
    applies_to: List[str]  # Conditions where this applies
    levels: List[str] = field(default_factory=list)  # e.g., Low/Moderate/High
    requirements: List[str] = field(default_factory=list)  # Key requirements
    keywords: List[str] = field(default_factory=list)  # Detection keywords
    description: str = ""


# ============================================================================
# GOVERNMENT COMPLIANCE
# ============================================================================

FEDRAMP = ComplianceFramework(
    id="fedramp",
    name="FedRAMP (Federal Risk and Authorization Management Program)",
    category="government",
    description="Required for cloud service providers hosting federal agency data",
    applies_to=[
        "Cloud service providers to federal agencies",
        "SaaS/PaaS/IaaS for government clients",
        "Federal data hosting"
    ],
    levels=["FedRAMP Low", "FedRAMP Moderate", "FedRAMP High"],
    requirements=[
        "NIST 800-53 security controls",
        "Continuous monitoring (ConMon)",
        "Incident response procedures",
        "Encryption at rest and in transit",
        "Identity & access management (MFA, RBAC)",
        "System Security Plan (SSP)",
        "Plan of Action & Milestones (POA&M)",
        "3PAO assessment and authorization"
    ],
    keywords=[
        "fedramp", "federal", "cloud", "authorization", "3pao",
        "ato", "moderate", "high", "low", "conmon"
    ]
)

NIST_800_53 = ComplianceFramework(
    id="nist_800_53",
    name="NIST SP 800-53 (Security and Privacy Controls)",
    category="government",
    description="Core security controls framework for federal information systems",
    applies_to=[
        "Federal information systems",
        "FedRAMP compliance",
        "Federal contractors"
    ],
    requirements=[
        "Access control (AC family)",
        "Audit and accountability (AU family)",
        "Security assessment (CA family)",
        "Configuration management (CM family)",
        "Identification and authentication (IA family)",
        "Incident response (IR family)",
        "System and communications protection (SC family)",
        "System and information integrity (SI family)"
    ],
    keywords=[
        "nist", "800-53", "security controls", "federal",
        "control families", "assessment"
    ]
)

NIST_800_171 = ComplianceFramework(
    id="nist_800_171",
    name="NIST SP 800-171 (Protecting Controlled Unclassified Information)",
    category="government",
    description="Required for contractors handling Controlled Unclassified Information (CUI)",
    applies_to=[
        "Federal contractors",
        "CUI handling systems",
        "Non-federal systems processing federal CUI"
    ],
    requirements=[
        "Access control (14 requirements)",
        "Awareness and training (3 requirements)",
        "Audit and accountability (9 requirements)",
        "Configuration management (9 requirements)",
        "Identification and authentication (11 requirements)",
        "Incident response (3 requirements)",
        "Maintenance (6 requirements)",
        "Media protection (9 requirements)",
        "Personnel security (2 requirements)",
        "Physical protection (6 requirements)",
        "Risk assessment (3 requirements)",
        "Security assessment (4 requirements)",
        "System and communications protection (16 requirements)",
        "System and information integrity (7 requirements)"
    ],
    keywords=[
        "nist", "800-171", "cui", "controlled unclassified",
        "contractor", "dfars"
    ]
)

CMMC = ComplianceFramework(
    id="cmmc",
    name="CMMC (Cybersecurity Maturity Model Certification)",
    category="government",
    description="DoD cybersecurity certification for defense contractors",
    applies_to=[
        "Department of Defense contractors",
        "Defense Industrial Base (DIB)",
        "Federal Contract Information (FCI) handlers",
        "Controlled Unclassified Information (CUI) handlers"
    ],
    levels=["CMMC Level 1 (Foundational)", "CMMC Level 2 (Advanced)", "CMMC Level 3 (Expert)"],
    requirements=[
        "Level 1: Basic cybersecurity hygiene (17 practices)",
        "Level 2: Aligns with NIST 800-171 (110 practices)",
        "Level 3: Advanced/progressive cybersecurity (110+ practices)",
        "Third-party assessment (C3PAO)",
        "Self-assessment (Level 1 only)",
        "Annual certification renewal"
    ],
    keywords=[
        "cmmc", "dod", "defense", "maturity model", "c3pao",
        "level 1", "level 2", "level 3", "dib"
    ]
)

FISMA = ComplianceFramework(
    id="fisma",
    name="FISMA (Federal Information Security Management Act)",
    category="government",
    description="Federal mandate for information security programs",
    applies_to=[
        "Federal agencies",
        "Federal information systems",
        "Contractors processing federal data"
    ],
    requirements=[
        "Security categorization (FIPS 199)",
        "Risk management framework (NIST 800-37)",
        "Continuous monitoring",
        "Annual FISMA reporting",
        "Authority to Operate (ATO)",
        "Security controls implementation",
        "Independent security assessments"
    ],
    keywords=[
        "fisma", "ato", "authority to operate", "federal",
        "categorization", "fips 199"
    ]
)

CJIS = ComplianceFramework(
    id="cjis",
    name="CJIS (Criminal Justice Information Services Security Policy)",
    category="government",
    description="Security requirements for law enforcement and criminal justice data",
    applies_to=[
        "Law enforcement systems",
        "Criminal justice information",
        "State/local/federal justice agencies",
        "FBI CJIS systems access"
    ],
    requirements=[
        "Personnel background screening",
        "Advanced authentication (MFA)",
        "Audit trails and logging",
        "Encryption (FIPS 140-2)",
        "Access control and authorization",
        "Physical security controls",
        "Incident response",
        "Security awareness training",
        "CJIS Security Addendum"
    ],
    keywords=[
        "cjis", "criminal justice", "law enforcement", "fbi",
        "ncic", "fingerprint", "background check"
    ]
)

ITAR = ComplianceFramework(
    id="itar",
    name="ITAR (International Traffic in Arms Regulations)",
    category="government",
    description="Export control regulations for defense articles and services",
    applies_to=[
        "Defense contractors",
        "Aerospace industry",
        "Military technology",
        "Defense-related technical data"
    ],
    requirements=[
        "US persons only access restrictions",
        "Encryption of controlled technical data",
        "Physical facility access controls",
        "Export authorization",
        "ITAR registration with DDTC",
        "Technology transfer controls",
        "Foreign national restrictions"
    ],
    keywords=[
        "itar", "export control", "defense", "munitions",
        "us person", "ddtc", "technical data"
    ]
)

EAR = ComplianceFramework(
    id="ear",
    name="EAR (Export Administration Regulations)",
    category="government",
    description="Export controls for dual-use items and technologies",
    applies_to=[
        "Commercial technology exports",
        "Dual-use items",
        "Software and technology transfer"
    ],
    requirements=[
        "Export classification (ECCN)",
        "Export licensing",
        "Deemed export controls",
        "Encryption controls",
        "End-use/end-user screening"
    ],
    keywords=[
        "ear", "export", "eccn", "dual-use", "bis",
        "commerce control"
    ]
)

SECTION_508 = ComplianceFramework(
    id="section_508",
    name="Section 508 Compliance",
    category="government",
    description="Accessibility requirements for federal ICT",
    applies_to=[
        "Federal websites and web applications",
        "Federal electronic documents",
        "Federal ICT procurement"
    ],
    requirements=[
        "WCAG 2.1 Level AA conformance",
        "Screen reader compatibility",
        "Keyboard navigation",
        "Alternative text for images",
        "Accessible forms and controls",
        "Color contrast requirements",
        "Video captions and transcripts",
        "Accessible PDFs"
    ],
    keywords=[
        "508", "section 508", "accessibility", "wcag",
        "ada", "screen reader", "accessible"
    ]
)

# ============================================================================
# HEALTHCARE COMPLIANCE
# ============================================================================

HIPAA = ComplianceFramework(
    id="hipaa",
    name="HIPAA (Health Insurance Portability and Accountability Act)",
    category="healthcare",
    description="Privacy and security of protected health information",
    applies_to=[
        "Healthcare providers",
        "Health plans",
        "Healthcare clearinghouses",
        "Business associates handling PHI"
    ],
    requirements=[
        "Administrative safeguards",
        "Physical safeguards",
        "Technical safeguards",
        "Privacy Rule compliance",
        "Security Rule compliance",
        "Breach Notification Rule",
        "Business Associate Agreement (BAA)",
        "Minimum necessary standard",
        "Patient rights (access, amendment, accounting)",
        "Encryption of PHI in transit and at rest",
        "Access controls and audit logs",
        "Risk analysis and management"
    ],
    keywords=[
        "hipaa", "phi", "protected health", "baa",
        "business associate", "healthcare", "medical"
    ]
)

HITECH = ComplianceFramework(
    id="hitech",
    name="HITECH Act (Health Information Technology for Economic and Clinical Health)",
    category="healthcare",
    description="Strengthens HIPAA with breach notification and enforcement",
    applies_to=[
        "HIPAA covered entities",
        "Business associates",
        "Healthcare technology vendors"
    ],
    requirements=[
        "Enhanced breach notification (60-day rule)",
        "Business associate liability",
        "Increased penalties for violations",
        "Encryption safe harbor provisions",
        "Patient right to electronic copy",
        "Accounting of disclosures from EHRs"
    ],
    keywords=[
        "hitech", "breach notification", "meaningful use",
        "ehr", "electronic health"
    ]
)

HITRUST = ComplianceFramework(
    id="hitrust",
    name="HITRUST CSF (Common Security Framework)",
    category="healthcare",
    description="Comprehensive healthcare security and privacy framework",
    applies_to=[
        "Healthcare organizations",
        "Health IT vendors",
        "Business associates",
        "Health insurance companies"
    ],
    requirements=[
        "Risk-based certification (e1, i1, r2 assessments)",
        "Integration of HIPAA, NIST, ISO, PCI-DSS",
        "Control framework implementation",
        "Third-party validated assessment",
        "Annual certification renewal",
        "MyCSF assessment tool",
        "Continuous monitoring and reporting"
    ],
    keywords=[
        "hitrust", "csf", "healthcare security", "certification",
        "assessment", "validated"
    ]
)

HL7_FHIR = ComplianceFramework(
    id="hl7_fhir",
    name="HL7/FHIR Standards",
    category="healthcare",
    description="Interoperability standards for healthcare data exchange",
    applies_to=[
        "Healthcare IT systems",
        "Electronic Health Records (EHR)",
        "Health information exchange (HIE)",
        "Medical device integration"
    ],
    requirements=[
        "HL7 v2.x message standards (legacy)",
        "HL7 FHIR (Fast Healthcare Interoperability Resources)",
        "RESTful API implementation",
        "Resource-based data exchange",
        "SMART on FHIR authentication",
        "US Core Data for Interoperability (USCDI)",
        "Bulk Data Access (FHIR Bulk Data Export)"
    ],
    keywords=[
        "hl7", "fhir", "interoperability", "ehr", "smart",
        "uscdi", "health exchange", "medical data"
    ]
)

# ============================================================================
# CLOUD & DATA CENTER COMPLIANCE
# ============================================================================

SOC2 = ComplianceFramework(
    id="soc2",
    name="SOC 2 (Service Organization Control 2)",
    category="cloud",
    description="Trust service criteria for service organizations",
    applies_to=[
        "Cloud service providers",
        "SaaS vendors",
        "Data center operators",
        "Managed service providers"
    ],
    levels=["SOC 2 Type I (point in time)", "SOC 2 Type II (6-12 month period)"],
    requirements=[
        "Security (required for all)",
        "Availability (optional TSC)",
        "Processing Integrity (optional TSC)",
        "Confidentiality (optional TSC)",
        "Privacy (optional TSC)",
        "Independent CPA audit",
        "Control design and operating effectiveness",
        "Risk assessment and monitoring",
        "Vendor management",
        "Incident response procedures"
    ],
    keywords=[
        "soc 2", "soc2", "type ii", "type i", "aicpa",
        "trust service", "audit"
    ]
)

ISO_27001 = ComplianceFramework(
    id="iso_27001",
    name="ISO 27001 (Information Security Management)",
    category="cloud",
    description="International standard for information security management systems",
    applies_to=[
        "Global enterprises",
        "Cloud providers",
        "Any organization managing sensitive data"
    ],
    requirements=[
        "Information Security Management System (ISMS)",
        "Risk assessment and treatment",
        "Security policy framework",
        "114 controls across 14 domains (Annex A)",
        "Internal audits",
        "Management review",
        "Continuous improvement",
        "Third-party certification audit"
    ],
    keywords=[
        "iso 27001", "iso27001", "isms", "information security",
        "certified", "certification"
    ]
)

ISO_27017 = ComplianceFramework(
    id="iso_27017",
    name="ISO 27017 (Cloud Security)",
    category="cloud",
    description="Cloud-specific security controls based on ISO 27001/27002",
    applies_to=[
        "Cloud service providers",
        "Cloud customers"
    ],
    requirements=[
        "Cloud-specific implementation of ISO 27002 controls",
        "Shared responsibility model",
        "Cloud service customer controls (7 controls)",
        "Cloud service provider controls (30 controls)",
        "Virtual machine hardening",
        "Cloud-specific incident management"
    ],
    keywords=[
        "iso 27017", "iso27017", "cloud security", "cloud controls"
    ]
)

ISO_27018 = ComplianceFramework(
    id="iso_27018",
    name="ISO 27018 (Cloud Privacy)",
    category="cloud",
    description="Privacy controls for cloud service providers as PII processors",
    applies_to=[
        "Cloud service providers processing PII",
        "Public cloud services"
    ],
    requirements=[
        "Consent and choice controls",
        "Purpose specification and limitation",
        "Collection limitation",
        "Data minimization",
        "Use, retention, and disclosure limitation",
        "Accuracy and quality",
        "Openness, transparency, and notice",
        "Individual participation and access",
        "Accountability",
        "Information security",
        "Privacy compliance"
    ],
    keywords=[
        "iso 27018", "iso27018", "cloud privacy", "pii", "personal data"
    ]
)

PCI_DSS = ComplianceFramework(
    id="pci_dss",
    name="PCI-DSS (Payment Card Industry Data Security Standard)",
    category="cloud",
    description="Security standards for organizations handling credit card data",
    applies_to=[
        "Merchants processing credit cards",
        "Payment processors",
        "Service providers handling cardholder data"
    ],
    levels=["Level 1 (6M+ transactions/year)", "Level 2 (1M-6M)", "Level 3 (20K-1M)", "Level 4 (<20K)"],
    requirements=[
        "Build and maintain secure network (firewalls, secure configs)",
        "Protect cardholder data (encryption, truncation)",
        "Maintain vulnerability management program",
        "Implement strong access control measures",
        "Regularly monitor and test networks",
        "Maintain information security policy",
        "12 core requirements across 6 control objectives",
        "Annual assessment (SAQ or ROC)",
        "Quarterly network scans by ASV"
    ],
    keywords=[
        "pci", "pci-dss", "pci dss", "payment card", "credit card",
        "cardholder", "saq", "roc", "asv"
    ]
)

# ============================================================================
# FINANCIAL / BANKING COMPLIANCE
# ============================================================================

SOX = ComplianceFramework(
    id="sox",
    name="SOX (Sarbanes-Oxley Act)",
    category="finance",
    description="Financial reporting and internal controls for public companies",
    applies_to=[
        "Publicly traded companies",
        "Financial reporting systems",
        "IT systems supporting financial data"
    ],
    requirements=[
        "Section 302: CEO/CFO certification of financial reports",
        "Section 404: Internal control assessment",
        "IT general controls (ITGC)",
        "Change management controls",
        "Access controls for financial systems",
        "Audit trails and logging",
        "Segregation of duties",
        "Independent auditor attestation"
    ],
    keywords=[
        "sox", "sarbanes-oxley", "section 404", "section 302",
        "itgc", "financial controls", "public company"
    ]
)

GLBA = ComplianceFramework(
    id="glba",
    name="GLBA (Gramm-Leach-Bliley Act)",
    category="finance",
    description="Privacy and security of consumer financial information",
    applies_to=[
        "Financial institutions",
        "Banks, credit unions, insurance companies",
        "Companies offering financial products/services"
    ],
    requirements=[
        "Financial Privacy Rule (consumer opt-out rights)",
        "Safeguards Rule (information security program)",
        "Pretexting provisions (identity theft protection)",
        "Risk assessment",
        "Access controls",
        "Encryption of customer data",
        "Vendor management",
        "Incident response plan",
        "Annual privacy notices"
    ],
    keywords=[
        "glba", "gramm-leach-bliley", "financial privacy",
        "safeguards rule", "financial institution"
    ]
)

FFIEC = ComplianceFramework(
    id="ffiec",
    name="FFIEC IT Examination Handbook",
    category="finance",
    description="IT examination standards for financial institutions",
    applies_to=[
        "Banks and credit unions",
        "Financial institution service providers",
        "Banking technology vendors"
    ],
    requirements=[
        "Information security program",
        "Business continuity planning",
        "Cybersecurity assessment tool (CAT)",
        "Outsourcing technology services guidance",
        "Audit and compliance",
        "Development and acquisition",
        "E-banking",
        "Operations",
        "Wholesale payment systems"
    ],
    keywords=[
        "ffiec", "bank examination", "financial institution",
        "cybersecurity cat", "banking"
    ]
)

FINRA = ComplianceFramework(
    id="finra",
    name="FINRA (Financial Industry Regulatory Authority)",
    category="finance",
    description="Regulatory requirements for broker-dealers",
    applies_to=[
        "Broker-dealers",
        "Securities firms",
        "Investment platforms"
    ],
    requirements=[
        "Recordkeeping requirements (Rule 4511)",
        "Books and records retention",
        "Supervision and compliance (Rule 3110)",
        "Cybersecurity and system integrity",
        "Business continuity planning (Rule 4370)",
        "Customer protection (Rule 15c3-3)",
        "Anti-money laundering (AML) program"
    ],
    keywords=[
        "finra", "broker-dealer", "securities", "rule 4511",
        "rule 3110", "recordkeeping"
    ]
)

# ============================================================================
# PRIVACY LAWS
# ============================================================================

GDPR = ComplianceFramework(
    id="gdpr",
    name="GDPR (General Data Protection Regulation)",
    category="privacy",
    description="EU data protection and privacy regulation",
    applies_to=[
        "Organizations processing EU residents' data",
        "Controllers and processors of EU personal data",
        "Any business offering goods/services to EU"
    ],
    requirements=[
        "Lawful basis for processing (consent, contract, legitimate interest, etc.)",
        "Data subject rights (access, erasure, portability, rectification)",
        "Data Protection Impact Assessments (DPIA)",
        "Privacy by design and by default",
        "Data minimization principle",
        "Purpose limitation",
        "Storage limitation",
        "Breach notification (72 hours)",
        "Data Processing Agreements (DPA)",
        "Data Protection Officer (DPO) where required",
        "Records of processing activities (ROPA)",
        "International data transfer mechanisms (SCCs, adequacy)"
    ],
    keywords=[
        "gdpr", "general data protection", "eu privacy", "personal data",
        "data subject", "dpo", "dpia", "right to erasure"
    ]
)

CCPA = ComplianceFramework(
    id="ccpa",
    name="CCPA/CPRA (California Consumer Privacy Act)",
    category="privacy",
    description="California consumer privacy rights",
    applies_to=[
        "Businesses serving California residents",
        "Companies with $25M+ revenue or 100K+ CA consumers",
        "Data brokers"
    ],
    requirements=[
        "Right to know what personal information is collected",
        "Right to delete personal information",
        "Right to opt-out of sale/sharing of personal information",
        "Right to correct inaccurate information (CPRA)",
        "Right to limit use of sensitive personal information (CPRA)",
        "Privacy policy and notice requirements",
        "Do Not Sell or Share My Personal Information link",
        "Reasonable security measures",
        "Data minimization and purpose limitation (CPRA)",
        "Risk assessments for sensitive data (CPRA)",
        "California Privacy Rights Act (CPRA) - enhanced requirements"
    ],
    keywords=[
        "ccpa", "cpra", "california privacy", "do not sell",
        "consumer privacy", "opt-out"
    ]
)

STATE_PRIVACY_LAWS = ComplianceFramework(
    id="state_privacy_laws",
    name="US State Privacy Laws (VCDPA, CPA, etc.)",
    category="privacy",
    description="Emerging state-level privacy regulations",
    applies_to=[
        "Businesses operating in Virginia, Colorado, Connecticut, etc.",
        "Multi-state consumer data processing"
    ],
    requirements=[
        "Virginia VCDPA (Consumer Data Protection Act)",
        "Colorado Privacy Act (CPA)",
        "Connecticut Data Privacy Act (CTDPA)",
        "Utah Consumer Privacy Act (UCPA)",
        "Similar rights to CCPA (access, deletion, opt-out)",
        "Data protection assessments",
        "Privacy policy updates",
        "Consumer request mechanisms"
    ],
    keywords=[
        "vcdpa", "virginia privacy", "colorado privacy", "cpa",
        "ctdpa", "ucpa", "state privacy"
    ]
)

# ============================================================================
# SOFTWARE DEVELOPMENT / DEVSECOPS
# ============================================================================

OWASP = ComplianceFramework(
    id="owasp",
    name="OWASP Security Standards",
    category="devsecops",
    description="Web application security best practices",
    applies_to=[
        "Web applications",
        "APIs",
        "Mobile applications",
        "Software development"
    ],
    requirements=[
        "OWASP Top 10 mitigation (Injection, Broken Auth, XSS, etc.)",
        "Secure coding guidelines",
        "Security testing (SAST, DAST, IAST)",
        "Dependency scanning (SCA)",
        "API security (OWASP API Security Top 10)",
        "Threat modeling",
        "Security design review",
        "Penetration testing"
    ],
    keywords=[
        "owasp", "top 10", "web security", "injection", "xss",
        "secure coding", "api security"
    ]
)

SECURE_SDLC = ComplianceFramework(
    id="secure_sdlc",
    name="Secure SDLC (Software Development Lifecycle)",
    category="devsecops",
    description="Security integrated throughout development lifecycle",
    applies_to=[
        "Software development projects",
        "DevSecOps pipelines",
        "Agile/CI/CD environments"
    ],
    requirements=[
        "Requirements phase: Security requirements elicitation",
        "Design phase: Threat modeling, secure architecture",
        "Development: Secure coding, code review, SAST",
        "Testing: Security testing, DAST, penetration testing",
        "Deployment: Secure configuration, secrets management",
        "Maintenance: Patch management, vulnerability management",
        "Continuous security monitoring",
        "Security champions program"
    ],
    keywords=[
        "secure sdlc", "devsecops", "secure development",
        "shift left", "security pipeline"
    ]
)

SBOM = ComplianceFramework(
    id="sbom",
    name="SBOM (Software Bill of Materials)",
    category="devsecops",
    description="Transparency and vulnerability tracking for software components",
    applies_to=[
        "Software vendors",
        "Government contractors (EO 14028)",
        "Critical infrastructure software",
        "Enterprise software procurement"
    ],
    requirements=[
        "Component inventory (all dependencies)",
        "Supplier/author identification",
        "Version identification",
        "Dependency relationships",
        "License information",
        "Known vulnerabilities (CVE mapping)",
        "SBOM formats: SPDX, CycloneDX, SWID",
        "Automated SBOM generation in CI/CD",
        "SBOM sharing with customers"
    ],
    keywords=[
        "sbom", "software bill of materials", "dependency",
        "supply chain", "spdx", "cyclonedx", "vulnerability"
    ]
)

# ============================================================================
# PHYSICAL SECURITY & OPERATIONS
# ============================================================================

PHYSICAL_SECURITY = ComplianceFramework(
    id="physical_security",
    name="Physical Security & Operational Controls",
    category="physical",
    description="Physical access controls and operational security",
    applies_to=[
        "Data centers",
        "Offices with sensitive data",
        "Facilities requiring controlled access"
    ],
    requirements=[
        "Background checks for personnel",
        "Badge access control systems",
        "Video surveillance (CCTV)",
        "Visitor logs and escort procedures",
        "Mantrap/dual authentication entry",
        "Environmental controls (HVAC, fire suppression)",
        "Asset tracking and inventory",
        "Secure disposal/destruction procedures",
        "Disaster recovery plan (DRP)",
        "Business continuity plan (BCP)",
        "Incident response procedures",
        "Change management processes"
    ],
    keywords=[
        "physical security", "access control", "badge",
        "background check", "cctv", "surveillance", "drp", "bcp"
    ]
)


# ============================================================================
# FRAMEWORK REGISTRY
# ============================================================================

ALL_FRAMEWORKS = [
    # Government
    FEDRAMP,
    NIST_800_53,
    NIST_800_171,
    CMMC,
    FISMA,
    CJIS,
    ITAR,
    EAR,
    SECTION_508,
    # Healthcare
    HIPAA,
    HITECH,
    HITRUST,
    HL7_FHIR,
    # Cloud
    SOC2,
    ISO_27001,
    ISO_27017,
    ISO_27018,
    PCI_DSS,
    # Finance
    SOX,
    GLBA,
    FFIEC,
    FINRA,
    # Privacy
    GDPR,
    CCPA,
    STATE_PRIVACY_LAWS,
    # DevSecOps
    OWASP,
    SECURE_SDLC,
    SBOM,
    # Physical
    PHYSICAL_SECURITY,
]

FRAMEWORKS_BY_ID = {fw.id: fw for fw in ALL_FRAMEWORKS}
FRAMEWORKS_BY_CATEGORY = {}
for fw in ALL_FRAMEWORKS:
    if fw.category not in FRAMEWORKS_BY_CATEGORY:
        FRAMEWORKS_BY_CATEGORY[fw.category] = []
    FRAMEWORKS_BY_CATEGORY[fw.category].append(fw)


# ============================================================================
# COMPLIANCE DETECTION UTILITIES
# ============================================================================

def detect_applicable_frameworks(text: str, sector: str = None) -> List[ComplianceFramework]:
    """
    Detect applicable compliance frameworks from RFP text and sector.

    Args:
        text: RFP text to analyze
        sector: Optional sector hint (government, healthcare, finance, etc.)

    Returns:
        List of applicable compliance frameworks, sorted by relevance
    """
    text_lower = text.lower()
    detected = []

    for framework in ALL_FRAMEWORKS:
        # Check if sector matches
        if sector and framework.category == sector:
            score = 2.0  # Bonus for sector match
        else:
            score = 0.0

        # Check keyword matches
        keyword_matches = 0
        for keyword in framework.keywords:
            if keyword in text_lower:
                keyword_matches += 1

        if keyword_matches > 0:
            score += keyword_matches
            detected.append((score, framework))

    # Sort by score descending
    detected.sort(key=lambda x: x[0], reverse=True)

    return [fw for score, fw in detected if score > 0]


def get_frameworks_by_category(category: str) -> List[ComplianceFramework]:
    """Get all frameworks for a specific category."""
    return FRAMEWORKS_BY_CATEGORY.get(category, [])


def get_framework_by_id(framework_id: str) -> ComplianceFramework:
    """Get a specific framework by ID."""
    return FRAMEWORKS_BY_ID.get(framework_id)


def generate_compliance_section(frameworks: List[ComplianceFramework], company_name: str = "Our Company") -> str:
    """
    Generate compliance section text for proposal.

    Args:
        frameworks: List of applicable frameworks
        company_name: Company name for proposal

    Returns:
        Formatted compliance section
    """
    if not frameworks:
        return ""

    lines = [
        "## Compliance & Security Frameworks\n",
        f"{company_name} maintains comprehensive compliance with industry-leading security and regulatory frameworks:\n"
    ]

    for fw in frameworks:
        lines.append(f"\n### {fw.name}")
        lines.append(f"\n{fw.description}\n")

        if fw.levels:
            lines.append(f"\n**Certification Levels**: {', '.join(fw.levels)}\n")

        if fw.requirements:
            lines.append("\n**Key Controls & Requirements**:\n")
            for req in fw.requirements[:8]:  # Top 8 requirements
                lines.append(f"- {req}")
            if len(fw.requirements) > 8:
                lines.append(f"- _{len(fw.requirements) - 8} additional controls implemented_")

        lines.append("\n")

    return "\n".join(lines)


def generate_compliance_matrix_table(frameworks: List[ComplianceFramework]) -> str:
    """
    Generate a compliance matrix summary table.

    Args:
        frameworks: List of applicable frameworks

    Returns:
        Markdown table of compliance frameworks
    """
    if not frameworks:
        return ""

    lines = [
        "| Framework | Category | Status | Key Controls |",
        "|-----------|----------|--------|--------------|"
    ]

    for fw in frameworks:
        category = fw.category.title()
        controls = f"{len(fw.requirements)} controls" if fw.requirements else "See documentation"
        status = "Implemented" if fw.category in ["cloud", "devsecops"] else "Compliant"

        lines.append(f"| {fw.name} | {category} | {status} | {controls} |")

    return "\n".join(lines)
