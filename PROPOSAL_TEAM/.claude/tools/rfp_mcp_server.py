#!/usr/bin/env python3
"""
RFP Agent MCP Server

Exposes dux_rfp_agent functionality as MCP tools for the Claude agent.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add dux_rfp_agent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dux_rfp_agent" / "src"))

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    import mcp.server.stdio
except ImportError:
    print("ERROR: mcp package not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rfp-mcp-server")

# Initialize MCP server
server = Server("rfp-agent")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available RFP processing tools."""
    return [
        Tool(
            name="parse_rfp",
            description=(
                "Parse an RFP document and extract all requirements with RFC 2119 classification. "
                "Returns structured requirements with IDs, priorities (MUST/SHALL/SHOULD/MAY), "
                "categories, and page citations."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "rfp_path": {
                        "type": "string",
                        "description": "Path to RFP document (PDF, DOCX, TXT, or ZIP)"
                    },
                    "enable_kb": {
                        "type": "boolean",
                        "description": "Enable knowledge base retrieval (requires Pinecone)",
                        "default": True
                    }
                },
                "required": ["rfp_path"]
            }
        ),
        Tool(
            name="generate_compliance_matrix",
            description=(
                "Generate a compliance matrix for parsed requirements. Returns approach, "
                "risk assessment, ownership, and evidence sources for each requirement."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "requirements": {
                        "type": "array",
                        "description": "List of requirements from parse_rfp",
                        "items": {"type": "object"}
                    },
                    "kb_results": {
                        "type": "array",
                        "description": "Knowledge base retrieval results (optional)",
                        "items": {"type": "object"}
                    },
                    "sector": {
                        "type": "string",
                        "description": "Industry sector (government, healthcare, finance, education)",
                        "default": "government"
                    }
                },
                "required": ["requirements"]
            }
        ),
        Tool(
            name="write_proposal_section",
            description=(
                "Write a specific proposal section (executive_summary, technical_approach, "
                "or management_approach) based on requirements and compliance matrix."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "section_type": {
                        "type": "string",
                        "enum": ["executive_summary", "technical_approach", "management_approach"],
                        "description": "Type of section to write"
                    },
                    "requirements": {
                        "type": "array",
                        "description": "Parsed requirements",
                        "items": {"type": "object"}
                    },
                    "compliance_matrix": {
                        "type": "array",
                        "description": "Compliance matrix entries",
                        "items": {"type": "object"}
                    },
                    "rfp_title": {
                        "type": "string",
                        "description": "RFP title"
                    },
                    "company_name": {
                        "type": "string",
                        "description": "Your company name"
                    },
                    "sector": {
                        "type": "string",
                        "description": "Industry sector",
                        "default": "government"
                    }
                },
                "required": ["section_type", "requirements", "compliance_matrix", "rfp_title", "company_name"]
            }
        ),
        Tool(
            name="validate_proposal",
            description=(
                "Run QA validation on a proposal to check coverage, citations, placeholders, "
                "and quality. Returns issues categorized by severity (CRITICAL/WARNING/INFO)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "proposal_text": {
                        "type": "string",
                        "description": "Full proposal text to validate"
                    },
                    "requirements": {
                        "type": "array",
                        "description": "Original requirements",
                        "items": {"type": "object"}
                    },
                    "compliance_matrix": {
                        "type": "array",
                        "description": "Compliance matrix",
                        "items": {"type": "object"}
                    }
                },
                "required": ["proposal_text", "requirements", "compliance_matrix"]
            }
        ),
        Tool(
            name="process_rfp_full",
            description=(
                "Execute the complete RFP processing pipeline: ingestion → parsing → "
                "KB retrieval → compliance matrix → proposal writing → QA → export. "
                "Returns all outputs in a specified directory."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "rfp_path": {
                        "type": "string",
                        "description": "Path to RFP document"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Directory for outputs",
                        "default": "./output"
                    },
                    "sector": {
                        "type": "string",
                        "description": "Industry sector",
                        "default": "government"
                    },
                    "rfp_title": {
                        "type": "string",
                        "description": "RFP title (auto-detected if not provided)"
                    },
                    "company_name": {
                        "type": "string",
                        "description": "Your company name"
                    },
                    "enable_kb": {
                        "type": "boolean",
                        "description": "Enable knowledge base retrieval",
                        "default": True
                    }
                },
                "required": ["rfp_path", "company_name"]
            }
        ),
        Tool(
            name="index_knowledge_base",
            description=(
                "Index documents into the Pinecone knowledge base for retrieval during "
                "RFP processing. Supports resumes, past performance, case studies, etc."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Path to file or directory to index"
                    },
                    "doc_type": {
                        "type": "string",
                        "enum": [
                            "resume", "past_performance", "case_study", "technical_writeup",
                            "boilerplate", "company_info", "capability_statement", "certification"
                        ],
                        "description": "Type of document being indexed"
                    },
                    "sector": {
                        "type": "string",
                        "description": "Industry sector for filtering (optional)"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional metadata (optional)"
                    }
                },
                "required": ["input_path", "doc_type"]
            }
        ),
        Tool(
            name="query_knowledge_base",
            description=(
                "Query the knowledge base for relevant documents and evidence. "
                "Returns top matching documents with metadata and similarity scores."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query text"
                    },
                    "top_k": {
                        "type": "number",
                        "description": "Number of results to return",
                        "default": 10
                    },
                    "doc_type": {
                        "type": "string",
                        "description": "Filter by document type (optional)"
                    },
                    "sector": {
                        "type": "string",
                        "description": "Filter by sector (optional)"
                    }
                },
                "required": ["query"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Execute RFP processing tools."""
    try:
        if name == "parse_rfp":
            return await _parse_rfp(arguments)
        elif name == "generate_compliance_matrix":
            return await _generate_compliance_matrix(arguments)
        elif name == "write_proposal_section":
            return await _write_proposal_section(arguments)
        elif name == "validate_proposal":
            return await _validate_proposal(arguments)
        elif name == "process_rfp_full":
            return await _process_rfp_full(arguments)
        elif name == "index_knowledge_base":
            return await _index_knowledge_base(arguments)
        elif name == "query_knowledge_base":
            return await _query_knowledge_base(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Error executing {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _parse_rfp(args: Dict[str, Any]) -> List[TextContent]:
    """Parse RFP and extract requirements."""
    from dux_rfp_agent.ingestion import DocumentIngestion
    from dux_rfp_agent.parser import RFPParser
    from dux_rfp_agent.chunking import SemanticChunker

    rfp_path = Path(args["rfp_path"])
    enable_kb = args.get("enable_kb", True)

    # Ingest document
    ingestion = DocumentIngestion()
    text, pages = ingestion.ingest(rfp_path)

    # Parse requirements
    chunker = SemanticChunker()
    parser = RFPParser(chunker=chunker)
    result = parser.parse_rfp(text, pages)

    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


async def _generate_compliance_matrix(args: Dict[str, Any]) -> List[TextContent]:
    """Generate compliance matrix."""
    from dux_rfp_agent.compliance import ComplianceMatrixBuilder

    requirements = args["requirements"]
    kb_results = args.get("kb_results", [])
    sector = args.get("sector", "government")

    builder = ComplianceMatrixBuilder()
    matrix = builder.build_matrix(requirements, kb_results, sector)

    return [TextContent(
        type="text",
        text=json.dumps(matrix, indent=2)
    )]


async def _write_proposal_section(args: Dict[str, Any]) -> List[TextContent]:
    """Write a proposal section."""
    from dux_rfp_agent.writer import ProposalWriter

    section_type = args["section_type"]
    requirements = args["requirements"]
    compliance_matrix = args["compliance_matrix"]
    rfp_title = args["rfp_title"]
    company_name = args["company_name"]
    sector = args.get("sector", "government")

    writer = ProposalWriter()

    if section_type == "executive_summary":
        section_text = writer.write_executive_summary(
            requirements, compliance_matrix, rfp_title, company_name, sector
        )
    elif section_type == "technical_approach":
        section_text = writer.write_technical_approach(
            requirements, compliance_matrix, rfp_title, company_name, sector
        )
    elif section_type == "management_approach":
        section_text = writer.write_management_approach(
            requirements, compliance_matrix, rfp_title, company_name, sector
        )
    else:
        raise ValueError(f"Unknown section type: {section_type}")

    return [TextContent(type="text", text=section_text)]


async def _validate_proposal(args: Dict[str, Any]) -> List[TextContent]:
    """Validate proposal quality."""
    from dux_rfp_agent.qa_agent import QAAgent

    proposal_text = args["proposal_text"]
    requirements = args["requirements"]
    compliance_matrix = args["compliance_matrix"]

    qa = QAAgent()
    report = qa.validate_proposal(proposal_text, requirements, compliance_matrix)

    return [TextContent(
        type="text",
        text=json.dumps(report, indent=2)
    )]


async def _process_rfp_full(args: Dict[str, Any]) -> List[TextContent]:
    """Execute full RFP processing pipeline."""
    from dux_rfp_agent.pipeline import RFPPipeline

    rfp_path = Path(args["rfp_path"])
    output_dir = Path(args.get("output_dir", "./output"))
    sector = args.get("sector", "government")
    rfp_title = args.get("rfp_title")
    company_name = args["company_name"]
    enable_kb = args.get("enable_kb", True)

    pipeline = RFPPipeline(enable_kb=enable_kb)
    result = pipeline.process_rfp(
        rfp_path=rfp_path,
        output_dir=output_dir,
        sector=sector,
        rfp_title=rfp_title,
        company_name=company_name
    )

    return [TextContent(
        type="text",
        text=json.dumps({
            "status": "success",
            "output_dir": str(output_dir),
            "files_created": result.get("files_created", []),
            "stats": result.get("stats", {})
        }, indent=2)
    )]


async def _index_knowledge_base(args: Dict[str, Any]) -> List[TextContent]:
    """Index documents into knowledge base."""
    import subprocess

    input_path = args["input_path"]
    doc_type = args["doc_type"]
    sector = args.get("sector")

    # Build command
    cmd = [
        "python",
        str(Path(__file__).parent.parent.parent / "dux_rfp_agent" / "scripts" / "index_kb.py"),
        "--input", input_path,
        "--type", doc_type
    ]

    if sector:
        cmd.extend(["--sector", sector])

    # Execute indexing script
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        return [TextContent(type="text", text=f"Successfully indexed: {result.stdout}")]
    else:
        return [TextContent(type="text", text=f"Error indexing: {result.stderr}")]


async def _query_knowledge_base(args: Dict[str, Any]) -> List[TextContent]:
    """Query knowledge base."""
    from dux_rfp_agent.retrieval import KnowledgeBaseRetrieval

    query = args["query"]
    top_k = args.get("top_k", 10)
    doc_type = args.get("doc_type")
    sector = args.get("sector")

    # Build filter
    filter_metadata = {}
    if doc_type:
        filter_metadata["type"] = doc_type
    if sector:
        filter_metadata["sector"] = sector

    kb = KnowledgeBaseRetrieval()
    results = kb.query(query, top_k=top_k, filter_metadata=filter_metadata if filter_metadata else None)

    return [TextContent(
        type="text",
        text=json.dumps(results, indent=2)
    )]


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
