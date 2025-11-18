#!/usr/bin/env python3
"""
Standalone script to verify and prepare compliance documents for Pinecone upload.
Focuses on your 10 priority frameworks.
"""

import os
from pathlib import Path
import json

# Your 10 Priority Frameworks
PRIORITY_FRAMEWORKS = {
    "cmmc": {
        "name": "CMMC 2.0",
        "files": [
            "CMMC_32 CFR 170 (CMMC Program Rule).pdf",
            "CMMC_AssessmentGuideL1v2.pdf",
            "CMMC_AssessmentGuideL2v2.pdf",
            "CMMC_ModelOverview.pdf",
            "CMMC_ScopingGuideL1v2.pdf",
            "CMMC_ScopingGuideL2v2.pdf"
        ]
    },
    "fedramp": {
        "name": "FedRAMP",
        "files": [
            "FEDRAMP_Agency_Authorization_Playbook.pdf",
            "FEDRAMP_CSP_Authorization_Playbook.pdf",
            "FEDRAMP_CSP_Continuous_Monitoring_Performance_Management_Guide.pdf"
        ]
    },
    "nist_800_171": {
        "name": "NIST 800-171",
        "files": [
            "NIST.SP.800-171r3.pdf",
            "NIST.SP.800-171Ar3.pdf"
        ]
    },
    "nist_800_53": {
        "name": "NIST 800-53",
        "files": [
            "NIST.SP.800-53r5.pdf",
            "NIST.SP.800-53Ar5.pdf",
            "NIST.SP.800-53B.pdf"
        ]
    },
    "hipaa": {
        "name": "HIPAA",
        "files": [
            "HIPAA_privacysummary.pdf",
            "HIPAA_security101.pdf"
        ]
    },
    "pci_dss": {
        "name": "PCI-DSS",
        "files": [
            "PCI-DSS-v4_0_1.pdf"
        ]
    },
    "gdpr": {
        "name": "GDPR",
        "files": [
            "GDPR_CELEX_32016R0679_EN_TXT.pdf"
        ]
    },
    "soc2": {
        "name": "SOC 2",
        "files": []  # No PDFs - proprietary
    },
    "iso_27001": {
        "name": "ISO 27001",
        "files": []  # No PDFs - paid standard
    },
    "glba": {
        "name": "GLBA",
        "files": [
            "GLBA_16 CFR Part 314 (up to date as of 9-30-2025).pdf",
            "GLBA_Privacy_viii-1.1.pdf"
        ]
    },
    "dfars": {
        "name": "DFARS",
        "files": [
            "CMMC_DFARS 2019-D041 (Cybersecurity Requirements).pdf"
        ]
    }
}

# Compliance folder
COMPLIANCE_FOLDER = Path(r"C:\Users\sabaa\OneDrive\Desktop\Compliance Frameworks")

def main():
    print("=" * 80)
    print("VERIFYING YOUR 10 PRIORITY COMPLIANCE FRAMEWORKS")
    print("=" * 80)

    total_frameworks = len(PRIORITY_FRAMEWORKS)
    total_files = 0
    found_files = 0
    manifest = []

    for fw_id, fw_info in PRIORITY_FRAMEWORKS.items():
        print(f"\n{fw_info['name']} ({fw_id}):")
        print("-" * 40)

        if not fw_info['files']:
            print("  [INFO] No PDF documents (proprietary/paid framework)")
            continue

        for pdf_file in fw_info['files']:
            total_files += 1
            file_path = COMPLIANCE_FOLDER / pdf_file

            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"  [OK] {pdf_file} ({size_mb:.1f} MB)")
                found_files += 1

                # Add to manifest
                manifest.append({
                    "framework_id": fw_id,
                    "framework_name": fw_info['name'],
                    "file_name": pdf_file,
                    "file_path": str(file_path),
                    "size_mb": round(size_mb, 2)
                })
            else:
                print(f"  [MISSING] {pdf_file}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Priority Frameworks: {total_frameworks}")
    print(f"Total PDF Files Expected: {total_files}")
    print(f"PDF Files Found: {found_files}")
    print(f"PDF Files Missing: {total_files - found_files}")

    # Frameworks with documents
    frameworks_with_docs = sum(1 for fw in PRIORITY_FRAMEWORKS.values() if fw['files'])
    print(f"\nFrameworks with PDFs: {frameworks_with_docs}/10")
    print("Frameworks without PDFs: SOC 2, ISO 27001 (proprietary/paid)")

    # Save manifest
    output_file = "compliance_manifest.json"
    with open(output_file, 'w') as f:
        json.dump({
            "total_frameworks": total_frameworks,
            "total_files": total_files,
            "found_files": found_files,
            "documents": manifest,
            "pinecone_config": {
                "api_key": "pcsk_YwCSZ_SSsaxk2HxiZM5uRsQ1uCV2KsoNsgGdPmdpNZ99aiZLSaewmCmVEthUi97uENvjH",
                "index": "rfp-knowledge-base",
                "namespace": "compliance_frameworks"
            }
        }, f, indent=2)

    print(f"\nManifest saved to: {output_file}")
    print("\nYour compliance documents are ready for Pinecone upload!")

if __name__ == "__main__":
    main()