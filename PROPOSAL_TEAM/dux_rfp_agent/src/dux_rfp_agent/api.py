"""
FastAPI service for RFP Agent.
"""

import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from .logger import logger
from .pipeline import RFPPipeline

# Initialize FastAPI app
app = FastAPI(
    title="Dux RFP Agent API",
    description="Automated RFP processing and proposal generation",
    version="1.0.0",
)

# Initialize pipeline
pipeline = RFPPipeline(enable_kb=True)


class ParseRequest(BaseModel):
    """Request model for parsing endpoint."""

    sector: str = "government"
    rfp_title: Optional[str] = None


class ProposalRequest(BaseModel):
    """Request model for proposal generation."""

    sector: str = "government"
    rfp_title: Optional[str] = None
    company_name: Optional[str] = None
    enable_kb: bool = True


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Dux RFP Agent API",
        "version": "1.0.0",
        "endpoints": {
            "parse": "POST /parse - Parse RFP and extract requirements",
            "proposal": "POST /proposal - Generate complete proposal",
            "health": "GET /health - Health check",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "dux-rfp-agent"}


@app.post("/parse")
async def parse_rfp(
    file: UploadFile = File(...),
    sector: str = Form("government"),
    rfp_title: Optional[str] = Form(None),
):
    """
    Parse RFP document and extract requirements.

    Args:
        file: RFP document (PDF, DOCX, TXT, ZIP)
        sector: Industry sector
        rfp_title: Optional RFP title

    Returns:
        Requirements JSON
    """
    logger.info(f"Parse request received: {file.filename}")

    try:
        # Save uploaded file to temp
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=Path(file.filename).suffix
        ) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = Path(tmp_file.name)

        # Ingest document
        from .ingestion import DocumentIngestion

        ingestion = DocumentIngestion()
        doc_data = ingestion.ingest(tmp_path)

        # Parse requirements
        from .parser import RFPParser

        parser = RFPParser()
        requirements_data = parser.parse_rfp(doc_data["text"], doc_data["pages"])

        # Clean up temp file
        tmp_path.unlink()

        return JSONResponse(content=requirements_data)

    except Exception as e:
        logger.error(f"Parse failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/proposal")
async def generate_proposal(
    file: UploadFile = File(...),
    sector: str = Form("government"),
    rfp_title: Optional[str] = Form(None),
    company_name: Optional[str] = Form(None),
    enable_kb: bool = Form(True),
):
    """
    Generate complete proposal from RFP.

    Args:
        file: RFP document
        sector: Industry sector
        rfp_title: Optional RFP title
        company_name: Optional company name
        enable_kb: Whether to enable KB retrieval

    Returns:
        Processing result with download links
    """
    logger.info(f"Proposal generation request: {file.filename}")

    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=Path(file.filename).suffix
        ) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            rfp_path = Path(tmp_file.name)

        # Create output directory
        output_dir = Path(tempfile.mkdtemp(prefix="rfp_output_"))

        # Initialize pipeline
        rfp_pipeline = RFPPipeline(enable_kb=enable_kb)

        # Process RFP
        result = rfp_pipeline.process_rfp(
            rfp_path=rfp_path,
            output_dir=output_dir,
            sector=sector,
            rfp_title=rfp_title,
            company_name=company_name,
        )

        # Clean up temp RFP file
        rfp_path.unlink()

        # Return result with file paths
        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Proposal generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{output_dir}/{filename}")
async def download_file(output_dir: str, filename: str):
    """
    Download generated file.

    Args:
        output_dir: Output directory name
        filename: File name

    Returns:
        File download
    """
    file_path = Path(f"/tmp/{output_dir}/{filename}")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path, filename=filename, media_type="application/octet-stream"
    )


@app.post("/qa")
async def run_qa(
    requirements_file: UploadFile = File(...),
    proposal_file: UploadFile = File(...),
    compliance_file: UploadFile = File(...),
):
    """
    Run QA validation on proposal.

    Args:
        requirements_file: Requirements JSON
        proposal_file: Proposal markdown
        compliance_file: Compliance matrix JSON

    Returns:
        QA report
    """
    logger.info("QA validation request received")

    try:
        import json

        # Read uploaded files
        requirements_data = json.loads(await requirements_file.read())
        proposal_md = (await proposal_file.read()).decode("utf-8")
        compliance_data = json.loads(await compliance_file.read())

        # Run QA
        from .qa_agent import QAAgent

        qa = QAAgent()

        sections = {"proposal": proposal_md}

        qa_report = qa.validate_proposal(
            requirements_data.get("requirements", []), sections, compliance_data
        )

        return JSONResponse(content=qa_report)

    except Exception as e:
        logger.error(f"QA validation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
