#!/usr/bin/env python3
"""
Simple test script for compliance framework auto-detection.
Tests the core detection logic without requiring full agent dependencies.
"""

import sys
import os

# Add the source directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dux_rfp_agent/src'))

# Import only the compliance frameworks module (no dependencies)
from dux_rfp_agent.compliance_frameworks import (
    detect_applicable_frameworks,
    generate_compliance_section,
    generate_compliance_matrix_table,
    ALL_FRAMEWORKS,
    FRAMEWORKS_BY_CATEGORY
)


def test_framework_registry():
    """Test that all frameworks are loaded."""
    print("=" * 80)
    print("TEST 1: Framework Registry")
    print("=" * 80)

    print(f"\n✅ Loaded {len(ALL_FRAMEWORKS)} compliance frameworks:")
    print(f"\nFrameworks by category:")
    for category, frameworks in FRAMEWORKS_BY_CATEGORY.items():
        print(f"  - {category.upper()}: {len(frameworks)} frameworks")

    assert len(ALL_FRAMEWORKS) >= 30, "Expected at least 30 frameworks"
    print(f"\n✅ Registry test passed!\n")


def test_government_detection():
    """Test government framework detection."""
    print("=" * 80)
    print("TEST 2: Government Compliance Detection")
    print("=" * 80)

    rfp_text = """
    The contractor shall maintain FedRAMP Moderate authorization and comply with
    NIST 800-53 security controls. All CUI must be protected per NIST 800-171.
    The solution must support Section 508 accessibility and maintain a current ATO.
    """

    frameworks = detect_applicable_frameworks(rfp_text, sector="government")

    print(f"\n✅ Detected {len(frameworks)} frameworks from government RFP:\n")
    for fw in frameworks[:10]:  # Show top 10
        print(f"  - {fw.name} ({fw.id}) - Category: {fw.category}")

    # Verify key frameworks detected
    detected_ids = [fw.id for fw in frameworks]
    assert "fedramp" in detected_ids, "FedRAMP not detected"
    assert "nist_800_53" in detected_ids, "NIST 800-53 not detected"
    assert "nist_800_171" in detected_ids, "NIST 800-171 not detected"
    assert "section_508" in detected_ids, "Section 508 not detected"

    print(f"\n✅ Government detection test passed!\n")


def test_healthcare_detection():
    """Test healthcare framework detection."""
    print("=" * 80)
    print("TEST 3: Healthcare Compliance Detection")
    print("=" * 80)

    rfp_text = """
    The vendor must comply with HIPAA Privacy and Security Rules. All PHI must be
    protected and a Business Associate Agreement (BAA) is required. The system must
    achieve HITRUST CSF certification and support HL7 FHIR for interoperability.
    """

    frameworks = detect_applicable_frameworks(rfp_text, sector="healthcare")

    print(f"\n✅ Detected {len(frameworks)} frameworks from healthcare RFP:\n")
    for fw in frameworks[:10]:
        print(f"  - {fw.name} ({fw.id}) - Category: {fw.category}")

    detected_ids = [fw.id for fw in frameworks]
    assert "hipaa" in detected_ids, "HIPAA not detected"
    assert "hitrust" in detected_ids, "HITRUST not detected"
    assert "hl7_fhir" in detected_ids, "HL7/FHIR not detected"

    print(f"\n✅ Healthcare detection test passed!\n")


def test_cloud_detection():
    """Test cloud/enterprise framework detection."""
    print("=" * 80)
    print("TEST 4: Cloud/Enterprise Compliance Detection")
    print("=" * 80)

    rfp_text = """
    The SaaS provider must have SOC 2 Type II audit report and ISO 27001 certification.
    GDPR compliance is required for EU data, and CCPA for California residents.
    PCI-DSS compliance is needed for payment processing.
    """

    frameworks = detect_applicable_frameworks(rfp_text, sector="cloud")

    print(f"\n✅ Detected {len(frameworks)} frameworks from cloud RFP:\n")
    for fw in frameworks[:10]:
        print(f"  - {fw.name} ({fw.id}) - Category: {fw.category}")

    detected_ids = [fw.id for fw in frameworks]
    assert "soc2" in detected_ids, "SOC 2 not detected"
    assert "iso_27001" in detected_ids, "ISO 27001 not detected"
    assert "gdpr" in detected_ids, "GDPR not detected"
    assert "ccpa" in detected_ids, "CCPA not detected"
    assert "pci_dss" in detected_ids, "PCI-DSS not detected"

    print(f"\n✅ Cloud detection test passed!\n")


def test_narrative_generation():
    """Test compliance narrative generation."""
    print("=" * 80)
    print("TEST 5: Compliance Narrative Generation")
    print("=" * 80)

    rfp_text = "Must comply with FedRAMP and HIPAA"
    frameworks = detect_applicable_frameworks(rfp_text)

    narrative = generate_compliance_section(frameworks[:3], company_name="Acme Corp")

    print(f"\n✅ Generated narrative ({len(narrative)} characters):\n")
    print(narrative[:400] + "...")

    assert "Acme Corp" in narrative
    assert len(narrative) > 100

    print(f"\n✅ Narrative generation test passed!\n")


def test_table_generation():
    """Test compliance matrix table generation."""
    print("=" * 80)
    print("TEST 6: Compliance Matrix Table Generation")
    print("=" * 80)

    rfp_text = "SOC 2, ISO 27001, and GDPR compliance required"
    frameworks = detect_applicable_frameworks(rfp_text)

    table = generate_compliance_matrix_table(frameworks[:5])

    print(f"\n✅ Generated compliance matrix table:\n")
    print(table)

    assert "Framework" in table
    assert "Category" in table
    assert "|" in table  # Markdown table format

    print(f"\n✅ Table generation test passed!\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("🎯 RFP AGENT: COMPLIANCE FRAMEWORK AUTO-DETECTION TESTS")
    print("=" * 80 + "\n")

    try:
        test_framework_registry()
        test_government_detection()
        test_healthcare_detection()
        test_cloud_detection()
        test_narrative_generation()
        test_table_generation()

        print("=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print("\n📊 Summary:")
        print(f"  - Total frameworks loaded: {len(ALL_FRAMEWORKS)}")
        print(f"  - Categories: {', '.join(FRAMEWORKS_BY_CATEGORY.keys())}")
        print("\n🚀 Features verified:")
        print("  ✅ Auto-detection from RFP keywords")
        print("  ✅ Sector-aware framework matching")
        print("  ✅ Compliance narrative generation")
        print("  ✅ Framework matrix table generation")
        print("\n🎉 The compliance framework is ready for production use!")
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
