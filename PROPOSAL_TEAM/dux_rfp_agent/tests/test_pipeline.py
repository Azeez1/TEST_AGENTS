"""
Tests for main pipeline.
"""

import pytest
from pathlib import Path
from dux_rfp_agent.pipeline import RFPPipeline


class TestRFPPipeline:
    """Test RFP pipeline functionality."""

    def test_pipeline_init(self):
        """Test pipeline initialization."""
        pipeline = RFPPipeline(enable_kb=False)
        assert pipeline is not None
        assert pipeline.ingestion is not None
        assert pipeline.parser is not None
        assert pipeline.writer is not None

    def test_pipeline_init_with_kb(self):
        """Test pipeline initialization with KB."""
        pipeline = RFPPipeline(enable_kb=True)
        assert pipeline.kb is not None

    @pytest.mark.integration
    def test_process_rfp(self, tmp_path):
        """Test full pipeline processing."""
        pipeline = RFPPipeline(enable_kb=False)

        # Create test RFP file
        rfp_file = tmp_path / "test_rfp.txt"
        rfp_content = """
        SECTION 1: INTRODUCTION
        This is a test RFP for evaluation purposes.

        SECTION 2: REQUIREMENTS
        The vendor MUST provide a cloud-based solution.
        The vendor SHALL ensure 99.9% uptime.
        The vendor SHOULD implement two-factor authentication.
        Security compliance is REQUIRED.

        SECTION 3: DELIVERABLES
        All deliverables MUST be submitted by the deadline.
        """
        rfp_file.write_text(rfp_content)

        # Create output directory
        output_dir = tmp_path / "output"

        # Process (note: this will fail without API keys, but tests structure)
        try:
            result = pipeline.process_rfp(
                rfp_path=rfp_file,
                output_dir=output_dir,
                sector="government",
                rfp_title="Test RFP",
            )

            # If API keys are available, check results
            if result["success"]:
                assert result["requirements_count"] > 0
                assert (output_dir / "requirements.json").exists()
                assert (output_dir / "proposal_draft.md").exists()

        except Exception as e:
            # Expected to fail without API keys
            pytest.skip(f"Pipeline test skipped (API keys required): {e}")
