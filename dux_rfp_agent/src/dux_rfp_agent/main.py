"""
Main CLI entry point for RFP Agent.
"""

import argparse
import sys
from pathlib import Path

from .logger import logger, setup_logger
from .pipeline import RFPPipeline


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Dux RFP Agent - Automated RFP processing and proposal generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process RFP with default settings
  python -m dux_rfp_agent.main --rfp input.pdf --out ./output

  # Process with specific sector and disable KB
  python -m dux_rfp_agent.main --rfp input.pdf --out ./output --sector healthcare --no-kb

  # Enable debug logging
  python -m dux_rfp_agent.main --rfp input.pdf --out ./output --debug
        """,
    )

    parser.add_argument(
        "--rfp", type=str, required=True, help="Path to RFP document (PDF, DOCX, TXT, or ZIP)"
    )

    parser.add_argument(
        "--out", type=str, required=True, help="Output directory for generated files"
    )

    parser.add_argument(
        "--sector",
        type=str,
        default="government",
        choices=["government", "healthcare", "finance", "education", "other"],
        help="Industry sector (default: government)",
    )

    parser.add_argument("--title", type=str, help="RFP title (auto-detected if not provided)")

    parser.add_argument(
        "--company", type=str, help="Company name for proposal (default: Your Company)"
    )

    parser.add_argument(
        "--no-kb", action="store_true", help="Disable knowledge base retrieval"
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    parser.add_argument(
        "--log-file", type=str, help="Optional log file path (default: stdout only)"
    )

    args = parser.parse_args()

    # Setup logging
    if args.debug:
        import os

        os.environ["LOG_LEVEL"] = "DEBUG"

    if args.log_file:
        log_path = Path(args.log_file)
        global logger
        logger = setup_logger("dux_rfp_agent", log_path)

    # Validate inputs
    rfp_path = Path(args.rfp)
    if not rfp_path.exists():
        logger.error(f"RFP file not found: {rfp_path}")
        sys.exit(1)

    output_dir = Path(args.out)

    # Initialize pipeline
    try:
        logger.info("Initializing RFP pipeline...")
        pipeline = RFPPipeline(enable_kb=not args.no_kb)

        # Process RFP
        result = pipeline.process_rfp(
            rfp_path=rfp_path,
            output_dir=output_dir,
            sector=args.sector,
            rfp_title=args.title,
            company_name=args.company,
        )

        # Print summary
        print("\n" + "=" * 80)
        print("RFP PROCESSING COMPLETE")
        print("=" * 80)
        print(f"Output Directory: {result['output_dir']}")
        print(f"Duration: {result['duration_seconds']:.1f} seconds")
        print(f"\nRequirements: {result['requirements_count']} total, {result['must_requirements']} critical")
        print(f"Compliance Items: {result['compliance_items']}")
        print(f"QA Status: {result['qa_status']}")
        print(f"QA Issues: {result['qa_issues']}")
        print(f"\nGenerated Files:")
        for name, path in result["files"].items():
            print(f"  - {name}: {path}")
        print("=" * 80 + "\n")

        # Exit with appropriate code
        if result["qa_status"] == "FAIL":
            logger.warning("QA validation failed - manual review required")
            sys.exit(2)

        sys.exit(0)

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        print(f"\nERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
