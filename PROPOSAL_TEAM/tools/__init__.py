"""Proposal helper modules; optional pipeline code is not bundled here."""

__version__ = "1.0.0"
__author__ = "Dux Team"

__all__ = ["RFPPipeline"]


def __getattr__(name: str):
    """Preserve the historical name without breaking unrelated helper imports."""
    if name == "RFPPipeline":
        raise ImportError("RFPPipeline is not bundled in PROPOSAL_TEAM.tools; use the deployed proposal pipeline package")
    raise AttributeError(name)
