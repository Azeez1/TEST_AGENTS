# RFP Agent: Comprehensive Compliance Framework Knowledge Base

## Overview

The RFP Agent now includes a **comprehensive, built-in compliance framework knowledge base** that automatically:

1. **Detects** applicable compliance requirements from RFP keywords
2. **Generates** compliance sections for proposals
3. **Maps** requirements to frameworks with evidence
4. **Enriches** sector-specific templates with compliance content

This knowledge base covers **30+ compliance frameworks** across Government, Healthcare, Finance, Cloud, Privacy, DevSecOps, and Physical Security domains.

---

## Key Features

### 🎯 Auto-Detection
The agent analyzes RFP text and automatically identifies applicable frameworks based on:
- **Keyword matching**: "FedRAMP", "HIPAA", "SOC 2", etc.
- **Sector context**: Government, Healthcare, Finance, Cloud
- **Requirements analysis**: CUI, PHI, PCI, export control mentions

### 📋 Auto-Generation
Once frameworks are detected, the agent can:
- **Generate compliance narrative sections** for proposals
- **Create compliance matrices** mapping requirements → approach → evidence
- **Build framework summary tables** for executive review
- **Enrich proposal templates** with framework-specific language

### 🧠 Evergreen Knowledge
All frameworks are **stable, built-in, and do not require live search**. This includes:
- Full descriptions and applicability conditions
- Key requirements and control objectives
- Detection keywords and triggers
- Compliance levels and tiers

---

## Supported Compliance Frameworks

### 🔵 Government (U.S. Federal/State/DoD)

| Framework | ID | Applies To | Levels |
|-----------|-----|-----------|--------|
| **FedRAMP** | `fedramp` | Cloud providers for federal agencies | Low, Moderate, High |
| **NIST 800-53** | `nist_800_53` | Federal information systems | Security control families |
| **NIST 800-171** | `nist_800_171` | Contractors handling CUI | 110 requirements |
| **CMMC** | `cmmc` | DoD contractors and DIB | Level 1, 2, 3 |
| **FISMA** | `fisma` | Federal agencies and contractors | Risk categorization |
| **CJIS** | `cjis` | Law enforcement systems | FBI access requirements |
| **ITAR** | `itar` | Defense/aerospace contractors | Export control |
| **EAR** | `ear` | Dual-use technology exports | Commerce controls |
| **Section 508** | `section_508` | Federal ICT and websites | WCAG 2.1 Level AA |

### 🟣 Healthcare

| Framework | ID | Applies To | Key Requirements |
|-----------|-----|-----------|------------------|
| **HIPAA** | `hipaa` | Healthcare providers, BAs | Privacy, Security, Breach Notification |
| **HITECH** | `hitech` | HIPAA-covered entities | Enhanced breach notification |
| **HITRUST CSF** | `hitrust` | Healthcare orgs, health IT | e1, i1, r2 assessments |
| **HL7/FHIR** | `hl7_fhir` | EHR, HIE, medical devices | Interoperability standards |

### 🔶 Cloud & Data Center

| Framework | ID | Applies To | Trust Service Criteria |
|-----------|-----|-----------|------------------------|
| **SOC 2** | `soc2` | SaaS, cloud providers | Security, Availability, Confidentiality, Processing Integrity, Privacy |
| **ISO 27001** | `iso_27001` | Global enterprises | 114 controls, ISMS |
| **ISO 27017** | `iso_27017` | Cloud service providers | Cloud-specific controls |
| **ISO 27018** | `iso_27018` | Public cloud (PII processing) | Privacy controls |
| **PCI-DSS** | `pci_dss` | Payment card processors | 12 requirements, 6 control objectives |

### 🟢 Financial Services

| Framework | ID | Applies To | Key Regulations |
|-----------|-----|-----------|-----------------|
| **SOX** | `sox` | Public companies | Section 302, 404, ITGC |
| **GLBA** | `glba` | Financial institutions | Safeguards Rule, Privacy Rule |
| **FFIEC** | `ffiec` | Banks, credit unions | IT examination handbook, CAT |
| **FINRA** | `finra` | Broker-dealers | Rules 4511, 3110, 4370 |

### 🔴 Privacy Laws

| Framework | ID | Applies To | Consumer Rights |
|-----------|-----|-----------|-----------------|
| **GDPR** | `gdpr` | EU data processing | Data subject rights, 72-hour breach notification |
| **CCPA/CPRA** | `ccpa` | California consumers | Right to know, delete, opt-out |
| **State Privacy Laws** | `state_privacy_laws` | VA, CO, CT, UT | Similar to CCPA |

### 🔥 DevSecOps

| Framework | ID | Applies To | Requirements |
|-----------|-----|-----------|--------------|
| **OWASP** | `owasp` | Web/API applications | Top 10, secure coding |
| **Secure SDLC** | `secure_sdlc` | Software development | Shift-left security |
| **SBOM** | `sbom` | Software vendors | CycloneDX, SPDX, CVE mapping |

### 🟡 Physical & Operational

| Framework | ID | Applies To | Controls |
|-----------|-----|-----------|----------|
| **Physical Security** | `physical_security` | Data centers, facilities | Access control, DRP, BCP, IRP |

---

## Usage in RFP Agent

### 1. Automatic Framework Detection

```python
from dux_rfp_agent.compliance_frameworks import detect_applicable_frameworks

# Detect frameworks from RFP text
rfp_text = """
The contractor must maintain FedRAMP Moderate authorization and comply with
NIST 800-53 security controls. All data must be encrypted using FIPS 140-2
validated cryptography. The solution must support HIPAA compliance for PHI.
"""

frameworks = detect_applicable_frameworks(rfp_text, sector="government")

# Results:
# - FedRAMP
# - NIST 800-53
# - HIPAA
```

### 2. Compliance Matrix Integration

```python
from dux_rfp_agent.compliance import ComplianceMatrixBuilder

builder = ComplianceMatrixBuilder(sector="government")

# Detect frameworks from RFP
builder.detect_frameworks(rfp_text)

# Build compliance matrix with framework context
matrix = builder.build_matrix(
    requirements=parsed_requirements,
    kb_evidence=kb_docs,
    rfp_text=rfp_text
)

# matrix now includes:
# - compliance_items: requirement-by-requirement mapping
# - detected_frameworks: list of applicable frameworks
```

### 3. Generate Compliance Narrative

```python
# Generate compliance section for proposal
narrative = builder.generate_compliance_narrative(company_name="Acme Corp")

# Output: Full markdown section describing how Acme Corp meets
# FedRAMP, NIST, HIPAA, etc. with controls and requirements
```

### 4. Generate Framework Summary Table

```python
# Generate framework matrix table
table = builder.generate_framework_matrix_table()

# Output: Markdown table with Framework | Category | Status | Controls
```

---

## Detection Keywords

Each framework includes **detection keywords** that trigger auto-detection:

### Example: FedRAMP
Keywords: `fedramp`, `federal`, `cloud`, `authorization`, `3pao`, `ato`, `moderate`, `high`, `low`, `conmon`

### Example: HIPAA
Keywords: `hipaa`, `phi`, `protected health`, `baa`, `business associate`, `healthcare`, `medical`

### Example: SOC 2
Keywords: `soc 2`, `soc2`, `type ii`, `type i`, `aicpa`, `trust service`, `audit`

When the RFP contains these keywords, the corresponding framework is detected and prioritized.

---

## Sector Templates

The following **enhanced sector templates** now include comprehensive compliance sections:

### Government Template
`src/dux_rfp_agent/templates/sectors/government.md`

Covers:
- FedRAMP, NIST 800-53, NIST 800-171, CMMC, FISMA
- CJIS, ITAR/EAR, Section 508
- Clearance requirements
- Federal acquisition (FAR/DFARS)
- Cloud security, data protection, incident response

### Healthcare Template
`src/dux_rfp_agent/templates/sectors/healthcare.md`

Covers:
- HIPAA (Privacy, Security, Breach Notification)
- HITECH, HITRUST CSF
- HL7/FHIR interoperability
- PHI encryption and access controls
- BAA management, telehealth, clinical trials

### Finance Template
`src/dux_rfp_agent/templates/sectors/finance.md`

Covers:
- SOX (Section 302, 404, ITGC)
- GLBA (Safeguards Rule, Privacy Rule)
- FFIEC IT Handbook, FINRA compliance
- PCI-DSS (12 requirements)
- AML/BSA, vendor risk management

### Cloud Template
`src/dux_rfp_agent/templates/sectors/cloud.md`

Covers:
- SOC 2 Type II (all 5 TSCs)
- ISO 27001, ISO 27017, ISO 27018
- Infrastructure security, API security
- GDPR and CCPA compliance
- SBOM and supply chain security

---

## Integration with Pinecone KB

Compliance framework information is **built into the agent** and does not require Pinecone indexing. However:

### For Compliance Evidence
Store actual **compliance artifacts** in Pinecone:
- SOC 2 Type II reports
- FedRAMP ATO letters
- HITRUST certification
- Penetration test reports
- Control implementation documentation

### Metadata Schema
When indexing compliance docs to Pinecone:

```json
{
  "doc_type": "compliance_certificate",
  "framework": "fedramp",
  "level": "moderate",
  "sector": "government",
  "certification_date": "2024-01-15",
  "expiration_date": "2025-01-15",
  "assessor": "3PAO-XYZ",
  "tags": ["ato", "nist-800-53", "cloud"]
}
```

This allows retrieval of **specific evidence** when building compliance matrices.

---

## Extending the Framework

To add a new compliance framework:

### 1. Add Framework Definition

Edit `src/dux_rfp_agent/compliance_frameworks.py`:

```python
MY_FRAMEWORK = ComplianceFramework(
    id="my_framework",
    name="My Compliance Standard",
    category="government",  # or healthcare, finance, cloud, privacy, devsecops, physical
    description="Description of when this applies",
    applies_to=[
        "Industry 1",
        "Use case 2"
    ],
    levels=["Level 1", "Level 2"],  # Optional
    requirements=[
        "Requirement 1",
        "Requirement 2",
        # ...
    ],
    keywords=[
        "keyword1",
        "keyword2",
        "acronym"
    ]
)

# Add to ALL_FRAMEWORKS
ALL_FRAMEWORKS.append(MY_FRAMEWORK)
```

### 2. Add to Sector Template

Add a section in the appropriate sector template describing compliance measures.

### 3. Test Detection

```python
from dux_rfp_agent.compliance_frameworks import detect_applicable_frameworks

text = "Our RFP requires keyword1 and keyword2 compliance"
frameworks = detect_applicable_frameworks(text)
assert "my_framework" in [fw.id for fw in frameworks]
```

---

## Benefits for Proposal Quality

### ✅ Comprehensive Coverage
Never miss a compliance requirement. Auto-detection ensures all frameworks are identified.

### ✅ Consistent Language
Use industry-standard terminology and control descriptions.

### ✅ Evidence Mapping
Link requirements directly to certifications and KB evidence.

### ✅ Faster Turnaround
Generate compliance sections in seconds instead of hours.

### ✅ Reduced Risk
Ensure proposals accurately reflect compliance capabilities and avoid false claims.

---

## Future Enhancements

Potential additions to the compliance framework:

- [ ] **International Standards**: Add APEC CBPR, Japan APPI, Brazil LGPD
- [ ] **Industry-Specific**: Add FDA 21 CFR Part 11, NERC CIP (energy), PSD2 (payments)
- [ ] **State/Local**: Add NY SHIELD Act, Illinois BIPA, local government frameworks
- [ ] **Framework Relationships**: Map overlapping controls (e.g., NIST 800-53 → FedRAMP → CMMC)
- [ ] **Control Libraries**: Link to CIS Controls, NIST CSF, MITRE ATT&CK
- [ ] **Auto-Scoring**: Calculate compliance coverage percentage based on KB evidence
- [ ] **Gap Analysis**: Identify missing controls and recommend KB additions

---

## Conclusion

The RFP Agent's compliance framework knowledge base is a **game-changer for government and enterprise proposals**. By automating framework detection, compliance section generation, and evidence mapping, the agent dramatically improves:

- **Proposal quality**: Comprehensive, accurate compliance coverage
- **Speed**: Compliance sections generated in seconds
- **Consistency**: Standardized language and control descriptions
- **Win rate**: More competitive, compliant proposals

For questions or enhancements, consult the `compliance_frameworks.py` module or sector templates.

---

**Built for production RFP automation. Compliance made simple.**
