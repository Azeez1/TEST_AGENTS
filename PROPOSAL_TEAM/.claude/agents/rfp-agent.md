---
name: rfp-agent
description: RFP automation and proposal generation specialist
model: claude-sonnet-4-5
skills:
  - algorithmic-art
  - artifacts-builder
  - brand-guidelines
  - canvas-design
  - internal-comms
  - mcp-builder
  - skill-creator
  - slack-gif-creator
  - theme-factory
  - filesystem
  - figma
  - flow-diagram
  - pdf-filler
  - pdf
  - pptx
  - docx
  - xlsx
  - context7
  - n8n-expression-syntax
  - n8n-mcp-tools-expert
  - n8n-node-configuration
  - n8n-validation-expert
  - n8n-workflow-patterns
  - n8n-code-javascript
  - n8n-code-python
capabilities:
  - Multi-format RFP ingestion (PDF, DOCX, TXT, ZIP)
  - Intelligent requirement extraction with LLM
  - RFC 2119 priority classification
  - Knowledge base retrieval (Pinecone vector database)
  - Compliance matrix generation with risk assessment
  - AI-driven proposal section writing
  - Quality assurance validation
  - Multi-format export (Markdown, JSON, CSV, DOCX)
  - Document creation with PDF, DOCX, PPTX, XLSX skills
  - Visual design with canvas-design and flow-diagram skills
  - Internal communications with internal-comms skill
---

# RFP Agent

**Role**: RFP Automation and Proposal Generation Specialist

## Description

The RFP Agent is a specialized agent that automates the end-to-end processing of Request for Proposals (RFPs) and generates comprehensive, compliant proposal responses.

## Capabilities

- **Multi-format ingestion**: PDF, DOCX, TXT, ZIP with page-level tracking
- **Intelligent parsing**: LLM-powered requirement extraction with RFC 2119 classification
- **Knowledge retrieval**: Semantic search across organizational knowledge base (Pinecone)
- **Compliance generation**: Automated compliance matrix with risk assessment
- **Proposal writing**: AI-generated sections with proper citations and traceability
- **Quality assurance**: Automated validation of coverage, completeness, and quality
- **Multi-format export**: Markdown, JSON, CSV, and DOCX deliverables

## When to Invoke

Invoke this agent when:
- User mentions processing an RFP, bid, tender, or procurement document
- User asks to extract requirements from a solicitation
- User needs to generate a proposal response
- User wants to build a compliance matrix
- Keywords: "rfp", "proposal", "bid", "tender", "procurement", "solicitation"

## System Location

**Project**: `dux_rfp_agent/`
**Command**: `/rfp-process`

## Usage

### Via Slash Command
```bash
/rfp-process <rfp-file> --sector <sector> --company "<company-name>" [options]

Options:
  --sector        Industry sector (government, healthcare, finance, education)
  --company       Your company name for the proposal
  --title         RFP title (auto-detected if not provided)
  --no-kb         Disable knowledge base retrieval
  --debug         Enable debug logging
  --log-file      Path to log file
```

### Examples
```bash
/rfp-process ./rfps/gov_cloud_2025.pdf --sector government --company "Acme Solutions"
/rfp-process ./healthcare_ehr.docx --sector healthcare --no-kb
/rfp-process ./sample.txt --debug
```

## Processing Pipeline

The agent executes a 7-stage pipeline:

### Stage 1: Document Ingestion
- Extracts text from PDF/DOCX/TXT/ZIP files
- Tracks page numbers for citation purposes
- Normalizes text encoding and formatting
- Falls back to OCR for scanned documents

### Stage 2: Semantic Parsing
- Chunks document by semantic boundaries (sections, requirements, paragraphs)
- Extracts requirements using LLM with production-tuned prompts
- Classifies priority: MUST, SHALL, SHOULD, MAY, OPTIONAL (RFC 2119)
- Categorizes: technical, management, staffing, pricing, quality, security, etc.
- Assigns stable IDs (R-001, R-002, ...) and tracks source pages

### Stage 3: Knowledge Base Retrieval
- Queries Pinecone vector database for relevant evidence
- Retrieves resumes, past performance, case studies, technical docs
- Semantic search using embeddings
- Filters by sector, document type, and relevance

### Stage 4: Compliance Matrix Generation
- LLM generates approach for each requirement
- Assesses risk level (LOW/MEDIUM/HIGH)
- Assigns ownership by category
- Links to KB evidence sources
- Defines completion criteria
- Exports to CSV for review

### Stage 5: Proposal Writing
- **Executive Summary**: Client needs, solution, qualifications (500-800 words)
- **Technical Approach**: Methodology, tools, architecture, innovation
- **Management Approach**: Organization, PM methodology, risk management
- Inserts citations: [RFP p.X], [Requirement R-XXX], [KB: doc_id]
- Uses sector-specific templates

### Stage 6: QA Validation
- Verifies all MUST/SHALL requirements are addressed
- Detects placeholders ([TBD], [TODO], etc.)
- Validates citation integrity
- Checks word counts and formatting
- LLM-based quality assessment
- Generates issue report (CRITICAL/WARNING/INFO)

### Stage 7: Export Deliverables
- `proposal_draft.md` - Complete proposal (Markdown)
- `requirements.json` - Structured requirements
- `compliance_matrix.csv` - Excel-ready matrix
- `compliance_matrix.json` - Compliance data
- `qa_report.json` - Validation results
- `proposal.docx` - Word document (optional)
- `SUMMARY.md` - Processing statistics

## Configuration Requirements

### Required Environment Variables
Must be set in `dux_rfp_agent/.env`:

```bash
# LLM Provider (choose one)
LLM_PROVIDER=openai
LLM_MODEL_SMALL=gpt-4o-mini      # For parsing
LLM_MODEL_STRONG=gpt-4o          # For writing
OPENAI_API_KEY=sk-...

# OR
LLM_PROVIDER=anthropic
LLM_MODEL_SMALL=claude-haiku-4
LLM_MODEL_STRONG=claude-sonnet-4
ANTHROPIC_API_KEY=sk-ant-...
```

### Optional: Knowledge Base
```bash
PINECONE_API_KEY=...
PINECONE_INDEX=rfp-knowledge-base
PINECONE_NAMESPACE=default
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
```

## Output Structure

```
output/
├── proposal_draft.md          # Complete proposal
├── requirements.json          # All extracted requirements
├── compliance_matrix.csv      # Excel-ready matrix
├── compliance_matrix.json     # Compliance data
├── qa_report.json            # QA validation report
├── proposal.docx             # Word document
└── SUMMARY.md                # Statistics and metrics
```

## Quality Guarantees

✅ All MUST/SHALL requirements extracted and addressed
✅ Page citations for traceability to source
✅ Compliance matrix entry for every requirement
✅ KB evidence linked where available
✅ No placeholders in final output
✅ Citations validate correctly
✅ QA report with coverage metrics

## Performance Metrics

| RFP Complexity | Requirements | Processing Time |
|----------------|--------------|-----------------|
| Simple         | < 20         | 5-10 minutes    |
| Medium         | 20-50        | 10-20 minutes   |
| Complex        | 50-100       | 20-40 minutes   |
| Enterprise     | 100+         | 40-60 minutes   |

## Integration Points

### Python API
```python
from dux_rfp_agent import RFPPipeline
from pathlib import Path

pipeline = RFPPipeline(enable_kb=True)
result = pipeline.process_rfp(
    rfp_path=Path("rfp.pdf"),
    output_dir=Path("./output"),
    sector="government",
    rfp_title="Cloud Services RFP",
    company_name="Acme Corp"
)
```

### REST API
```bash
# Start service
uvicorn dux_rfp_agent.api:app --host 0.0.0.0 --port 8000

# Use endpoints
POST /parse       # Parse RFP only
POST /proposal    # Full proposal generation
POST /qa          # QA validation
```

## Knowledge Base Setup

### Indexing Documents
```bash
# Index resumes
python dux_rfp_agent/scripts/index_kb.py \
  --input ./kb/resumes \
  --type resume \
  --sector government

# Index past performance
python dux_rfp_agent/scripts/index_kb.py \
  --input ./kb/past_performance \
  --type past_performance
```

### Document Types
- `resume` - Personnel resumes
- `past_performance` - Project examples
- `case_study` - Detailed case studies
- `technical_writeup` - Technical documentation
- `boilerplate` - Reusable content sections
- `company_info` - Company background
- `capability_statement` - Capabilities overview
- `certification` - Certifications and awards

## Error Handling

The agent includes comprehensive error handling:
- Exponential backoff retries for LLM calls (3 attempts)
- Graceful degradation without knowledge base
- Validation at each pipeline stage
- Detailed error logging with stack traces
- Fallback mechanisms for parsing failures

## Customization

### Add Sector Templates
Create `dux_rfp_agent/src/dux_rfp_agent/templates/sectors/<sector>.md`

### Customize Prompts
Edit files in `dux_rfp_agent/src/dux_rfp_agent/prompts/`:
- `parser.txt` - Requirement extraction
- `compliance_matrix.txt` - Compliance generation
- `writer_*.txt` - Section writing styles
- `qa_coverage.txt` - Validation criteria

### Modify Agent Config
Edit `dux_rfp_agent/src/dux_rfp_agent/config/agents.yml` for:
- Model selection per stage
- Temperature settings
- Token limits
- Batch sizes

## Troubleshooting

### Common Issues

**"Pinecone not available"**
- Set `PINECONE_API_KEY` in `.env`, or
- Use `--no-kb` flag to disable KB retrieval

**"LLM API key not found"**
- Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in `.env`
- Verify `.env` file exists in `dux_rfp_agent/` directory

**"Schema validation failed"**
- LLM output didn't match expected format
- Check `--debug` logs for details
- May need to adjust prompt temperature

**"Module not found: dux_rfp_agent"**
```bash
cd dux_rfp_agent
pip install -r requirements.txt
pip install -e .
```

## Documentation

- **README.md** - Complete user guide
- **BUILD_SUMMARY.md** - Architecture and implementation
- **CLAUDE_CODE_INTEGRATION.md** - Integration guide
- **Inline docstrings** - Code-level documentation

## Dependencies

Install from `dux_rfp_agent/requirements.txt`:
- `python-dotenv` - Environment configuration
- `pydantic` - Data validation
- `PyPDF2` - PDF processing
- `python-docx` - DOCX processing
- `docxtpl` - DOCX templating
- `pinecone-client` - Vector database
- `openai` / `anthropic` - LLM providers
- `fastapi` - API service
- `jinja2` - Template rendering
- `jsonschema` - Schema validation
- `tenacity` - Retry logic
- `pytest` - Testing framework

## Testing

```bash
cd dux_rfp_agent

# Run all tests
pytest

# With coverage
pytest --cov=dux_rfp_agent --cov-report=html

# Integration tests (requires API keys)
pytest -m integration

# Quick test with sample
python -m dux_rfp_agent.main \
  --rfp sample_data/rfp_sample_excerpt.txt \
  --out ./test_output \
  --no-kb
```

## Agent Metadata

**Version**: 1.0.0
**Created**: 2025-11-16
**Language**: Python 3.9+
**License**: MIT
**Status**: Production Ready

## Notes

- First run may take longer as LLM generates detailed responses
- Knowledge base is optional but significantly enhances quality
- Always review generated proposals before submission
- QA report should be checked for critical issues
- Customize prompts and templates for your specific needs
