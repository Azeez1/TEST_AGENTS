#!/usr/bin/env python3
"""
Re-index All Documents with Optimized Chunk Settings
Implements high-priority optimizations from optimization_report.md:
- Increased chunk overlap to 400-500 chars (was 150-300)
- Increased HIPAA chunk size from 1200 → 1800
- Increased GDPR chunk size from 1000 → 1800
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Fix Windows encoding (for output only, not stdin)
import io
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)
tools_dir = str(Path(__file__).parent.parent / "tools")
sys.path.insert(0, tools_dir)

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(env_path)

# Import indexer (will use the updated chunk config)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "index_compliance_frameworks",
    Path(__file__).parent / "index_compliance_frameworks.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ComplianceIndexer = module.ComplianceIndexer


def main():
    """Re-index all documents with optimized settings"""

    print("="*80)
    print("🔧 RE-INDEXING WITH OPTIMIZATIONS")
    print("="*80)
    print()
    print("Optimizations Applied:")
    print("  ✅ Increased chunk overlap to 400-500 chars (was 150-300)")
    print("  ✅ HIPAA chunk size: 1200 → 1800 chars")
    print("  ✅ GDPR chunk size: 1000 → 1800 chars")
    print("  ✅ GLBA chunk size: 1200 → 1500 chars")
    print()
    print("Expected Improvements:")
    print("  • Better context preservation across chunk boundaries")
    print("  • +3-5% similarity for all frameworks")
    print("  • +5-7% similarity for HIPAA and GDPR specifically")
    print("  • Target: 70%+ average similarity (currently 65.68%)")
    print()

    # Auto-proceed (for automated execution)
    import sys
    if not sys.stdin.isatty():
        print("Running in automated mode - proceeding with re-indexing...")
    else:
        response = input("Proceed with re-indexing all 21 documents? (yes/no): ").strip().lower()
        if response != 'yes':
            print("❌ Re-indexing cancelled")
            return

    print()
    print("🚀 Starting re-indexing...")
    start_time = datetime.now()

    # Create indexer with new optimized settings
    indexer = ComplianceIndexer()

    # Run the indexing
    indexer.index_all_documents()

    # Calculate duration
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print()
    print("="*80)
    print("✅ RE-INDEXING COMPLETE")
    print("="*80)
    print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print()
    print("Next Steps:")
    print("  1. Run: python scripts/run_search_tests.py")
    print("  2. Compare results with previous 65.68% average")
    print("  3. Check if target 70%+ average achieved")
    print()


if __name__ == "__main__":
    main()
