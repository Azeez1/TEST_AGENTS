#!/usr/bin/env python3
"""
Test script for compliance framework auto-detection.

This demonstrates the RFP Agent's ability to automatically detect
applicable compliance frameworks from RFP text.
"""

import sys
sys.path.insert(0, 'dux_rfp_agent/src')

from dux_rfp_agent.compliance_frameworks import (
    detect_applicable_frameworks,
    generate_compliance_section,
    generate_compliance_matrix_table
)


def test_government_rfp():
    """Test detection of government compliance frameworks."""
    print("=" * 80)
    print("TEST 1: Government RFP with FedRAMP and NIST requirements")
    print("=" * 80)

    rfp_text = """
    STATEMENT OF WORK

    The contractor shall provide cloud-based case management system
    that meets the following requirements:

    1. The system must maintain FedRAMP Moderate authorization
    2. All security controls must comply with NIST SP 800-53 rev 5
    3. The contractor must protect Controlled Unclassified Information (CUI)
       in accordance with NIST 800-171
    4. All deliverables must meet Section 508 accessibility requirements
    5. The system must be hosted in a FedRAMP authorized cloud environment
    6. Continuous monitoring (ConMon) must be implemented
    7. The contractor must have a current Authority to Operate (ATO)
    """

    frameworks = detect_applicable_frameworks(rfp_text, sector="government")

    print(f"\n✅ Detected {len(frameworks)} frameworks:\n")
    for i, fw in enumerate(frameworks, 1):
        print(f"{i}. {fw.name} ({fw.id})")
        print(f"   Category: {fw.category}")
        print(f"   Description: {fw.description}")
        print()

    assert any(fw.id == "fedramp" for fw in frameworks), "FedRAMP not detected!"
    assert any(fw.id == "nist_800_53" for fw in frameworks), "NIST 800-53 not detected!"
    assert any(fw.id == "nist_800_171" for fw in frameworks), "NIST 800-171 not detected!"
    assert any(fw.id == "section_508" for fw in frameworks), "Section 508 not detected!"

    print("✅ All expected frameworks detected!\n")
    return frameworks


def test_healthcare_rfp():
    """Test detection of healthcare compliance frameworks."""
    print("=" * 80)
    print("TEST 2: Healthcare RFP with HIPAA and HITRUST requirements")
    print("=" * 80)

    rfp_text = """
    The vendor must provide an electronic health record (EHR) system that:

    - Complies with HIPAA Privacy and Security Rules
    - Maintains a current Business Associate Agreement (BAA)
    - Protects Protected Health Information (PHI) at rest and in transit
    - Achieves HITRUST CSF r2 validated assessment
    - Supports HL7 FHIR R4 for interoperability
    - Implements HITECH breach notification procedures
    - Encrypts all PHI using FIPS 140-2 validated cryptography
    """

    frameworks = detect_applicable_frameworks(rfp_text, sector="healthcare")

    print(f"\n✅ Detected {len(frameworks)} frameworks:\n")
    for i, fw in enumerate(frameworks, 1):
        print(f"{i}. {fw.name} ({fw.id})")
        print(f"   Category: {fw.category}")
        print()

    assert any(fw.id == "hipaa" for fw in frameworks), "HIPAA not detected!"
    assert any(fw.id == "hitrust" for fw in frameworks), "HITRUST not detected!"
    assert any(fw.id == "hl7_fhir" for fw in frameworks), "HL7/FHIR not detected!"
    assert any(fw.id == "hitech" for fw in frameworks), "HITECH not detected!"

    print("✅ All expected frameworks detected!\n")
    return frameworks


def test_cloud_rfp():
    """Test detection of cloud and enterprise compliance frameworks."""
    print("=" * 80)
    print("TEST 3: Cloud SaaS RFP with SOC 2 and ISO requirements")
    print("=" * 80)

    rfp_text = """
    The SaaS provider must demonstrate:

    1. SOC 2 Type II audit report (all Trust Service Criteria)
    2. ISO 27001 certification
    3. ISO 27017 for cloud security controls
    4. ISO 27018 for cloud privacy
    5. GDPR compliance for EU data processing
    6. CCPA compliance for California residents
    7. PCI-DSS compliance for payment processing
    """

    frameworks = detect_applicable_frameworks(rfp_text, sector="cloud")

    print(f"\n✅ Detected {len(frameworks)} frameworks:\n")
    for i, fw in enumerate(frameworks, 1):
        print(f"{i}. {fw.name} ({fw.id})")
        print(f"   Category: {fw.category}")
        print()

    assert any(fw.id == "soc2" for fw in frameworks), "SOC 2 not detected!"
    assert any(fw.id == "iso_27001" for fw in frameworks), "ISO 27001 not detected!"
    assert any(fw.id == "gdpr" for fw in frameworks), "GDPR not detected!"
    assert any(fw.id == "ccpa" for fw in frameworks), "CCPA not detected!"
    assert any(fw.id == "pci_dss" for fw in frameworks), "PCI-DSS not detected!"

    print("✅ All expected frameworks detected!\n")
    return frameworks


def test_narrative_generation():
    """Test compliance narrative generation."""
    print("=" * 80)
    print("TEST 4: Generate compliance narrative for proposal")
    print("=" * 80)

    rfp_text = "The contractor must maintain FedRAMP Moderate and HIPAA compliance."
    frameworks = detect_applicable_frameworks(rfp_text)

    narrative = generate_compliance_section(frameworks, company_name="Acme Corporation")

    print("\n✅ Generated compliance narrative:\n")
    print(narrative[:500] + "...\n")  # Show first 500 chars

    assert "Acme Corporation" in narrative
    assert "FedRAMP" in narrative
    assert "HIPAA" in narrative

    print("✅ Narrative generation successful!\n")


def test_matrix_table_generation():
    """Test compliance matrix table generation."""
    print("=" * 80)
    print("TEST 5: Generate compliance framework matrix table")
    print("=" * 80)

    rfp_text = "Must comply with SOC 2, ISO 27001, and GDPR."
    frameworks = detect_applicable_frameworks(rfp_text)

    table = generate_compliance_matrix_table(frameworks)

    print("\n✅ Generated compliance matrix table:\n")
    print(table)
    print()

    assert "SOC 2" in table
    assert "ISO 27001" in table
    assert "GDPR" in table

    print("✅ Table generation successful!\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("RFP AGENT: COMPLIANCE FRAMEWORK AUTO-DETECTION TESTS")
    print("=" * 80 + "\n")

    try:
        # Run tests
        test_government_rfp()
        test_healthcare_rfp()
        test_cloud_rfp()
        test_narrative_generation()
        test_matrix_table_generation()

        # Summary
        print("=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print("\nThe compliance framework auto-detection is working correctly.")
        print("The RFP Agent can now:")
        print("  - Detect applicable frameworks from RFP keywords")
        print("  - Generate compliance narrative sections")
        print("  - Create compliance framework summary tables")
        print("  - Map requirements to frameworks with evidence")
        print("\nReady for production use in government, healthcare, finance, and cloud proposals!")
        print("=" * 80 + "\n")

        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
