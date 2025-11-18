#!/usr/bin/env python3
"""
Test script for user's 10 priority compliance frameworks.
"""

import sys
import os

# Import the module directly
spec_file = os.path.join(os.path.dirname(__file__),
                         'tools/user_priority_frameworks.py')

# Read and execute the module
with open(spec_file, 'r') as f:
    exec(f.read(), globals())

def test_framework_detection():
    """Test framework detection with sample RFP text."""

    # Sample RFP text mentioning multiple frameworks
    sample_rfp = """
    This procurement requires compliance with CMMC 2.0 Level 2 certification
    and adherence to NIST 800-171 Rev 3 requirements for protecting CUI.

    Cloud solutions must be FedRAMP Moderate authorized and comply with
    NIST 800-53 Rev 5 security controls.

    For healthcare data, HIPAA compliance is mandatory with appropriate
    Business Associate Agreements in place.

    Payment processing must be PCI-DSS v4.0 compliant.

    The solution must also meet DFARS 252.204-7012 requirements for
    cybersecurity incident reporting within 72 hours.
    """

    print("=" * 80)
    print("TESTING USER'S 10 PRIORITY FRAMEWORKS")
    print("=" * 80)

    # Show summary
    print("\n" + get_priority_summary())

    # Test detection
    print("\n" + "=" * 80)
    print("FRAMEWORK DETECTION TEST")
    print("=" * 80)
    print("\nSample RFP mentions:")

    detected = detect_user_frameworks(sample_rfp)

    for fw, matched_keywords in detected:
        print(f"\n[DETECTED] {fw.name}")
        print(f"  Category: {fw.category}")
        print(f"  Keywords matched: {', '.join(matched_keywords)}")
        print(f"  PDF documents: {fw.pdf_count}")

    # Show frameworks NOT detected
    print("\n" + "-" * 40)
    print("Frameworks NOT mentioned in sample:")
    detected_ids = {fw.id for fw, _ in detected}
    for fw in USER_PRIORITY_FRAMEWORKS:
        if fw.id not in detected_ids:
            print(f"  - {fw.name}")

    # Test individual framework lookup
    print("\n" + "=" * 80)
    print("INDIVIDUAL FRAMEWORK TEST")
    print("=" * 80)

    test_ids = ["cmmc", "fedramp", "hipaa", "soc2"]
    for fw_id in test_ids:
        fw = FRAMEWORK_BY_ID.get(fw_id)
        if fw:
            print(f"\n{fw.name}:")
            print(f"  {fw.description}")
            print(f"  Requirements: {len(fw.requirements)}")
            if fw.requirements:
                print(f"  First requirement: {fw.requirements[0]}")

if __name__ == "__main__":
    test_framework_detection()