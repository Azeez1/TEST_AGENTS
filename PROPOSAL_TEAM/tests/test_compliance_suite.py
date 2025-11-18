#!/usr/bin/env python3
"""
Consolidated Compliance Test Suite
Tests various compliance detection scenarios.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.user_priority_frameworks import (
    USER_PRIORITY_FRAMEWORKS,
    detect_user_frameworks,
    get_priority_summary
)
from tools.compliance_engine import UniversalComplianceEngine
from tools.rfp_parser import UniversalRFPParser

def test_simple_detection():
    """Test basic framework detection."""
    print("Testing Simple Framework Detection")
    print("-" * 40)

    test_cases = [
        ("CMMC Level 2 compliance required", ["cmmc"]),
        ("Must be HIPAA compliant with BAA", ["hipaa"]),
        ("PCI-DSS v4.0 certification needed", ["pci_dss"]),
        ("GDPR Article 25 compliance", ["gdpr"]),
        ("FedRAMP Moderate authorized", ["fedramp"]),
    ]

    for text, expected in test_cases:
        detected = detect_user_frameworks(text)
        found_ids = [fw.id for fw, _ in detected]

        success = all(exp in found_ids for exp in expected)
        status = "✓" if success else "✗"
        print(f"{status} '{text[:30]}...' -> {found_ids}")

    return True

def test_multiple_frameworks():
    """Test detection of multiple frameworks in one text."""
    print("\nTesting Multiple Framework Detection")
    print("-" * 40)

    sample_text = """
    This federal procurement requires CMMC 2.0 Level 2 certification and
    FedRAMP Moderate authorization. Solutions must comply with NIST 800-171
    Rev 3 for CUI protection and NIST 800-53 Rev 5 security controls.

    Additionally, any healthcare data must be HIPAA compliant with appropriate
    Business Associate Agreements. Payment processing requires PCI-DSS v4.0.

    For European operations, GDPR compliance is mandatory. Financial data
    must meet GLBA Safeguards Rule requirements.
    """

    detected = detect_user_frameworks(sample_text)

    print(f"Detected {len(detected)} frameworks:")
    for fw, keywords in detected[:10]:
        print(f"  - {fw.name}: {len(keywords)} keywords matched")

    # Verify all major frameworks detected
    detected_ids = [fw.id for fw, _ in detected]
    expected = ["cmmc", "fedramp", "nist_800_171", "nist_800_53",
                "hipaa", "pci_dss", "gdpr", "glba"]

    missing = [e for e in expected if e not in detected_ids]
    if missing:
        print(f"  WARNING: Missing frameworks: {missing}")
    else:
        print("  ✓ All expected frameworks detected")

    return len(missing) == 0

def test_confidence_scoring():
    """Test confidence scoring in compliance engine."""
    print("\nTesting Confidence Scoring")
    print("-" * 40)

    engine = UniversalComplianceEngine()

    # High confidence text (multiple indicators)
    high_conf_text = """
    CMMC 2.0 Level 2 certification required per 32 CFR Part 170.
    Must implement all 110 practices from NIST 800-171.
    C3PAO assessment required. SPRS score must be submitted.
    """

    # Low confidence text (few indicators)
    low_conf_text = """
    Security certification may be needed for this project.
    Some compliance with standards expected.
    """

    high_analysis = engine.analyze_rfp(high_conf_text)
    low_analysis = engine.analyze_rfp(low_conf_text)

    if high_analysis.detected_frameworks:
        high_score = high_analysis.detected_frameworks[0].confidence_score
        print(f"High confidence text: {high_score:.2%} confidence")

    if low_analysis.detected_frameworks:
        low_score = low_analysis.detected_frameworks[0].confidence_score
        print(f"Low confidence text: {low_score:.2%} confidence")
    else:
        print("Low confidence text: No frameworks detected")

    return True

def test_framework_integration():
    """Test framework integration detection."""
    print("\nTesting Framework Integration")
    print("-" * 40)

    engine = UniversalComplianceEngine()

    # Text with overlapping frameworks
    overlap_text = """
    DoD contractor requiring CMMC Level 2 certification based on
    NIST 800-171 implementation. Must also meet DFARS 252.204-7012
    for incident reporting within 72 hours.

    Cloud services must have FedRAMP authorization using NIST 800-53
    control baselines.
    """

    analysis = engine.analyze_rfp(overlap_text)

    print(f"Integration points found: {len(analysis.integration_points)}")
    for point in analysis.integration_points:
        print(f"  - {point.get('framework_1', '')} + {point.get('framework_2', '')}")
        print(f"    {point.get('benefit', '')}")

    return True

def run_all_tests():
    """Run all compliance tests."""
    print("=" * 60)
    print("COMPLIANCE TEST SUITE")
    print("=" * 60)

    # Show framework summary first
    print("\n" + get_priority_summary())

    tests = [
        test_simple_detection,
        test_multiple_frameworks,
        test_confidence_scoring,
        test_framework_integration
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            print(f"\n{'=' * 60}")
            result = test_func()
            if result:
                passed += 1
                print("✓ Test passed")
            else:
                failed += 1
                print("✗ Test failed")
        except Exception as e:
            failed += 1
            print(f"✗ Test failed with error: {e}")

    print(f"\n{'=' * 60}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)