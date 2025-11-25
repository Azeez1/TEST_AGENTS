"""
Query Expansion for Compliance Framework Searches

Expands user queries with domain-specific synonyms and related terms to improve
semantic search quality. Particularly effective for HIPAA, GDPR, and other frameworks
with specialized terminology.

Usage:
    from query_expander import QueryExpander

    expander = QueryExpander()
    expanded = expander.expand_query(
        "HIPAA requirements for patient data encryption",
        framework_id="hipaa"
    )
"""

import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class QueryExpander:
    """Expands queries with framework-specific synonyms and related terms"""

    # Compliance terminology synonym dictionary
    # Maps key terms to their domain-specific synonyms and related concepts
    COMPLIANCE_SYNONYMS = {
        "hipaa": {
            # Patient data terminology
            "patient data": [
                "protected health information",
                "PHI",
                "electronic protected health information",
                "ePHI",
                "individually identifiable health information"
            ],
            "medical records": [
                "health records",
                "patient records",
                "clinical data",
                "protected health information"
            ],

            # Security measures
            "encryption": [
                "safeguards",
                "technical security measures",
                "data protection",
                "cryptographic protection",
                "secure transmission"
            ],
            "access control": [
                "authentication",
                "authorization",
                "unique user identification",
                "user access management",
                "access management"
            ],

            # Safeguard categories
            "administrative safeguards": [
                "administrative security",
                "policies and procedures",
                "workforce security",
                "security management process",
                "164.308"
            ],
            "physical safeguards": [
                "physical security",
                "facility access controls",
                "workstation security",
                "device and media controls",
                "164.310"
            ],
            "technical safeguards": [
                "technical security",
                "access controls",
                "audit controls",
                "integrity controls",
                "transmission security",
                "164.312"
            ],

            # Compliance concepts
            "breach": [
                "security incident",
                "unauthorized access",
                "disclosure",
                "data breach",
                "privacy incident"
            ],
            "business associate": [
                "covered entity",
                "business associate agreement",
                "BAA",
                "third-party service provider"
            ]
        },

        "gdpr": {
            # Data terminology
            "personal data": [
                "data subject information",
                "identifiable information",
                "processing",
                "personal information",
                "individual data"
            ],
            "sensitive data": [
                "special categories of personal data",
                "sensitive personal information",
                "Article 9 data"
            ],

            # Legal basis
            "consent": [
                "lawful basis",
                "legitimate interest",
                "explicit consent",
                "Article 6",
                "legal ground"
            ],

            # Data subject rights
            "data subject rights": [
                "right to erasure",
                "right to rectification",
                "right of access",
                "right to data portability",
                "right to object",
                "Articles 15-22"
            ],
            "right to erasure": [
                "right to be forgotten",
                "deletion rights",
                "Article 17"
            ],

            # Roles and responsibilities
            "controller": [
                "data controller",
                "data processor",
                "joint controller",
                "processor"
            ],
            "data protection officer": [
                "DPO",
                "supervisory authority",
                "data protection authority",
                "Article 37"
            ],

            # Compliance requirements
            "data protection impact assessment": [
                "DPIA",
                "privacy impact assessment",
                "Article 35",
                "risk assessment"
            ],
            "data breach": [
                "personal data breach",
                "breach notification",
                "Article 33",
                "security incident"
            ]
        },

        "cmmc": {
            # Access control
            "access control": [
                "AC",
                "user authentication",
                "least privilege",
                "access management",
                "privileged access"
            ],

            # CUI terminology
            "controlled unclassified information": [
                "CUI",
                "federal contract information",
                "FCI",
                "sensitive information",
                "DoD data"
            ],

            # Assessment terminology
            "assessment": [
                "verification",
                "validation",
                "maturity level",
                "C3PAO assessment",
                "certification"
            ],
            "level 2": [
                "CMMC Level 2",
                "NIST SP 800-171",
                "110 practices",
                "advanced"
            ],
            "level 3": [
                "CMMC Level 3",
                "NIST SP 800-172",
                "expert",
                "advanced cybersecurity"
            ],

            # Domains
            "incident response": [
                "IR",
                "security incident",
                "incident handling",
                "event management"
            ]
        },

        "fedramp": {
            # Cloud terminology
            "cloud service provider": [
                "CSP",
                "cloud provider",
                "SaaS",
                "PaaS",
                "IaaS"
            ],

            # Monitoring
            "continuous monitoring": [
                "ConMon",
                "ongoing monitoring",
                "security monitoring",
                "real-time monitoring"
            ],

            # Authorization
            "authorization": [
                "ATO",
                "authority to operate",
                "FedRAMP authorization",
                "authorization boundary"
            ],

            # Incident response
            "incident response": [
                "IR",
                "security incident",
                "incident reporting",
                "breach notification",
                "CISA directive"
            ]
        },

        "nist_800_171": {
            # CUI protection
            "controlled unclassified information": [
                "CUI",
                "federal contract information",
                "FCI",
                "sensitive information"
            ],

            # Security requirements
            "security requirements": [
                "security controls",
                "safeguarding requirements",
                "protection requirements",
                "110 requirements"
            ],

            # Access control
            "access control": [
                "3.1",
                "user authentication",
                "least privilege",
                "access management"
            ],

            # System and communications protection
            "encryption": [
                "3.13",
                "cryptographic protection",
                "data protection",
                "secure transmission"
            ]
        },

        "pci_dss": {
            # Cardholder data
            "cardholder data": [
                "CHD",
                "payment card data",
                "credit card data",
                "card account data",
                "PAN"
            ],
            "primary account number": [
                "PAN",
                "card number",
                "account number"
            ],

            # Security measures
            "encryption": [
                "strong cryptography",
                "data protection",
                "secure transmission",
                "cryptographic controls"
            ],

            # Network security
            "network security": [
                "firewall",
                "network segmentation",
                "DMZ",
                "cardholder data environment",
                "CDE"
            ],

            # Authentication
            "multi-factor authentication": [
                "MFA",
                "two-factor authentication",
                "2FA",
                "strong authentication"
            ]
        }
    }

    def __init__(self):
        """Initialize the QueryExpander"""
        logger.info("Initialized QueryExpander with compliance terminology")

    def expand_query(
        self,
        query: str,
        framework_id: Optional[str] = None,
        max_synonyms: int = 3,
        include_original: bool = True
    ) -> str:
        """
        Expand query with framework-specific synonyms

        Args:
            query: Original user query
            framework_id: Framework to use for synonym lookup (e.g., 'hipaa', 'gdpr')
            max_synonyms: Maximum number of synonyms to add per matched term
            include_original: Whether to include original query in expansion

        Returns:
            Expanded query string
        """
        if not query:
            return query

        # Normalize framework_id
        if framework_id:
            framework_id = framework_id.lower().replace(" ", "_").replace("-", "_")

        # Start with original query if requested
        expanded_terms = [query] if include_original else []

        # If no framework specified or framework not in dictionary, return original
        if not framework_id or framework_id not in self.COMPLIANCE_SYNONYMS:
            logger.debug(f"No expansion for framework: {framework_id}")
            return query

        # Get framework-specific synonyms
        framework_synonyms = self.COMPLIANCE_SYNONYMS[framework_id]

        # Find matching terms and add synonyms
        query_lower = query.lower()
        matches_found = 0

        for key_term, synonyms in framework_synonyms.items():
            # Check if key term appears in query
            if key_term in query_lower:
                # Add top N synonyms
                added_synonyms = synonyms[:max_synonyms]
                expanded_terms.extend(added_synonyms)
                matches_found += 1

                logger.debug(
                    f"Matched '{key_term}' in query, added {len(added_synonyms)} synonyms"
                )

        # Combine all terms
        expanded_query = " ".join(expanded_terms)

        if matches_found > 0:
            logger.info(
                f"Expanded query with {matches_found} term matches "
                f"({len(expanded_terms)} total terms)"
            )
        else:
            logger.debug("No matching terms found for expansion")

        return expanded_query

    def get_synonyms(
        self,
        term: str,
        framework_id: str
    ) -> List[str]:
        """
        Get synonyms for a specific term within a framework

        Args:
            term: Term to look up
            framework_id: Framework to search in

        Returns:
            List of synonyms (empty if not found)
        """
        framework_id = framework_id.lower().replace(" ", "_").replace("-", "_")

        if framework_id not in self.COMPLIANCE_SYNONYMS:
            return []

        return self.COMPLIANCE_SYNONYMS[framework_id].get(term.lower(), [])

    def list_frameworks(self) -> List[str]:
        """Get list of supported frameworks"""
        return list(self.COMPLIANCE_SYNONYMS.keys())

    def get_framework_terms(self, framework_id: str) -> Dict[str, List[str]]:
        """
        Get all defined terms and synonyms for a framework

        Args:
            framework_id: Framework identifier

        Returns:
            Dictionary of terms and their synonyms
        """
        framework_id = framework_id.lower().replace(" ", "_").replace("-", "_")
        return self.COMPLIANCE_SYNONYMS.get(framework_id, {})


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 80)
    print("Query Expander - Compliance Framework Terminology")
    print("=" * 80)
    print()

    expander = QueryExpander()

    # Test HIPAA query expansion
    print("Example 1: HIPAA Query Expansion")
    print("-" * 80)
    original = "HIPAA requirements for patient data encryption and access control"
    expanded = expander.expand_query(original, framework_id="hipaa", max_synonyms=2)
    print(f"Original: {original}")
    print(f"Expanded: {expanded}")
    print()

    # Test GDPR query expansion
    print("Example 2: GDPR Query Expansion")
    print("-" * 80)
    original = "GDPR data subject rights and consent management"
    expanded = expander.expand_query(original, framework_id="gdpr", max_synonyms=2)
    print(f"Original: {original}")
    print(f"Expanded: {expanded}")
    print()

    # Test CMMC query expansion
    print("Example 3: CMMC Query Expansion")
    print("-" * 80)
    original = "CMMC Level 2 access control for controlled unclassified information"
    expanded = expander.expand_query(original, framework_id="cmmc", max_synonyms=2)
    print(f"Original: {original}")
    print(f"Expanded: {expanded}")
    print()

    # Show supported frameworks
    print("Supported Frameworks:")
    print("-" * 80)
    for fw in expander.list_frameworks():
        term_count = len(expander.get_framework_terms(fw))
        print(f"  • {fw.upper()}: {term_count} key terms defined")
    print()
