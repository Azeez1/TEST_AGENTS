# RFP Agent Skill

Production-ready RFP automation system for processing Request for Proposals and generating comprehensive proposal responses.

## When to Use This Skill

Use this skill when:
- User wants to process an RFP document
- User asks to extract requirements from an RFP
- User needs to generate a proposal response
- User mentions "RFP", "proposal", "bid", "tender"
- User wants to build a compliance matrix
- User asks to analyze procurement documents

## Core Capabilities

### 1. Document Ingestion
- PDF extraction with page tracking
- DOCX processing
- TXT file handling
- ZIP archive extraction
- OCR for scanned documents
- Multi-page text normalization

### 2. Requirements Parsing
- LLM-powered requirement extraction
- RFC 2119 priority classification (MUST, SHALL, SHOULD, MAY)
- Category assignment (technical, management, staffing, pricing, etc.)
- Page citation tracking
- Keyword extraction
- Automatic deduplication
- Stable ID assignment (R-001, R-002, etc.)

### 3. Knowledge Base Integration
- Pinecone vector database search
- Resume retrieval for staffing
- Past performance matching
- Case study retrieval
- Technical documentation search
- Boilerplate content access

### 4. Compliance Matrix Generation
- Automated approach descriptions
- Risk assessment (LOW/MEDIUM/HIGH)
- Owner assignment by category
- Evidence linking to KB
- Completion criteria
- CSV export for review

### 5. Proposal Writing
- Executive Summary generation
- Technical Approach section
- Management Approach section
- Staffing Plan (with KB resumes)
- Citation insertion [RFP p.X], [Requirement R-XXX]
- Sector-specific templates

### 6. Quality Assurance
- MUST/SHALL coverage validation
- Placeholder detection
- Citation integrity checks
- Word count validation
- LLM-based quality review
- Issue reporting (CRITICAL/WARNING/INFO)

### 7. Export & Deliverables
- Markdown proposal
- JSON requirements
- CSV compliance matrix
- DOCX Word document
- QA validation report
- Complete bundle generation

## Usage Pattern

```python
# The RFP agent is invoked via CLI or programmatically

# CLI Usage
python -m dux_rfp_agent.main \
  --rfp path/to/rfp.pdf \
  --out ./output \
  --sector government \
  --company "Your Company"

# Programmatic Usage
from dux_rfp_agent import RFPPipeline

pipeline = RFPPipeline(enable_kb=True)
result = pipeline.process_rfp(
    rfp_path=Path("rfp.pdf"),
    output_dir=Path("./output"),
    sector="government"
)
```

## Architecture

```
RFP Document → Ingestion → Chunking → Parser (LLM)
                                         ↓
                                   Requirements
                                         ↓
                     ┌──────────────────┴──────────────────┐
                     ↓                                      ↓
            KB Query (Pinecone)                    Compliance Builder
                     ↓                                      ↓
                Evidence                              Matrix + Risk
                     └──────────────────┬──────────────────┘
                                        ↓
                                  Proposal Writers
                                        ↓
                           ┌────────────┼────────────┐
                           ↓            ↓            ↓
                    Executive     Technical    Management
                    Summary       Approach     Approach
                                        ↓
                                   QA Validation
                                        ↓
                                Export Deliverables
```

## Configuration Requirements

### Environment Variables
```bash
# LLM Configuration (Required)
LLM_PROVIDER=openai
LLM_MODEL_SMALL=gpt-4o-mini
LLM_MODEL_STRONG=gpt-4o
OPENAI_API_KEY=sk-...

# Knowledge Base (Optional)
PINECONE_API_KEY=...
PINECONE_INDEX=rfp-knowledge-base
EMBEDDING_MODEL=text-embedding-3-small
```

### File Locations
- **Source Code**: `dux_rfp_agent/src/dux_rfp_agent/`
- **Configuration**: `dux_rfp_agent/config/agents.yml`
- **Prompts**: `dux_rfp_agent/src/dux_rfp_agent/prompts/`
- **Templates**: `dux_rfp_agent/src/dux_rfp_agent/templates/`
- **Schemas**: `dux_rfp_agent/src/dux_rfp_agent/schemas/`

## Key Components

### Modules
- `ingestion.py` - Document processing
- `chunking.py` - Text chunking with page tracking
- `parser.py` - LLM requirement extraction
- `retrieval.py` - Pinecone KB integration
- `compliance.py` - Compliance matrix builder
- `writer.py` - Proposal section generators
- `qa_agent.py` - Quality validation
- `export.py` - Multi-format export
- `pipeline.py` - End-to-end orchestration

### Prompts (Production-Tuned)
- `parser.txt` - Requirements extraction
- `compliance_matrix.txt` - Compliance generation
- `writer_executive_summary.txt` - Executive summary
- `writer_technical_approach.txt` - Technical section
- `writer_management_approach.txt` - Management section
- `qa_coverage.txt` - QA validation

### Schemas
- `requirements.schema.json` - Requirements validation
- `compliance.schema.json` - Compliance validation
- `pinecone_metadata.schema.json` - KB metadata

## Supported Sectors

- **government** - FedRAMP, NIST SP 800-53, FAR/DFARS
- **healthcare** - HIPAA, HITRUST, HL7/FHIR
- **finance** - SOC2, PCI-DSS
- **education** - FERPA, accessibility
- **other** - General commercial

## Output Structure

```
output/
├── proposal_draft.md          # Complete proposal
├── requirements.json          # Extracted requirements
├── compliance_matrix.csv      # Excel-ready matrix
├── compliance_matrix.json     # Compliance data
├── qa_report.json            # Validation results
├── proposal.docx             # Word document
└── SUMMARY.md                # Statistics
```

## Workflow

1. **User provides RFP** → document path + sector + company name
2. **Ingest** → extract text with page numbers
3. **Chunk** → split into 6k char chunks with 400 overlap
4. **Parse** → LLM extracts requirements per chunk → merge & dedupe
5. **Query KB** → retrieve evidence for each requirement (if enabled)
6. **Build Compliance** → LLM generates matrix with approaches
7. **Write Sections** → LLM writes executive, technical, management
8. **Validate QA** → check coverage, placeholders, citations
9. **Export** → generate all deliverables (MD, JSON, CSV, DOCX)

## Advanced Features

### Knowledge Base Setup
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

### API Service
```bash
uvicorn dux_rfp_agent.api:app --host 0.0.0.0 --port 8000

# Endpoints:
# POST /parse - Parse RFP only
# POST /proposal - Full proposal generation
# POST /qa - QA validation
```

### Customization
- **Prompts**: Edit `prompts/*.txt` for different styles
- **Sectors**: Add templates in `templates/sectors/`
- **Schemas**: Modify validation in `schemas/*.json`
- **Agents**: Configure in `config/agents.yml`

## Error Handling

- Retry logic with exponential backoff
- Graceful degradation (works without KB)
- Schema validation at each stage
- Comprehensive logging
- Fallback mechanisms

## Performance

- **Simple RFP** (< 20 reqs): 5-10 minutes
- **Medium RFP** (20-50 reqs): 10-20 minutes
- **Complex RFP** (50+ reqs): 20-40 minutes

## Quality Guarantees

✅ All MUST/SHALL requirements extracted
✅ Page citations for traceability
✅ Compliance matrix for all requirements
✅ KB evidence linked where available
✅ Citations validate correctly
✅ No placeholders in output
✅ QA report with coverage metrics

## Limitations

- Requires LLM API keys (OpenAI or Anthropic)
- KB features require Pinecone setup
- DOCX export requires docxtpl package
- OCR requires pytesseract installation
- Processing time depends on document size

## Examples

### Example 1: Government RFP
```bash
python -m dux_rfp_agent.main \
  --rfp ./rfps/dod_cloud_2025.pdf \
  --out ./proposals/dod_cloud \
  --sector government \
  --company "Defense Solutions Inc"
```

### Example 2: Healthcare RFP (no KB)
```bash
python -m dux_rfp_agent.main \
  --rfp ./rfps/hospital_ehr.docx \
  --out ./proposals/hospital_ehr \
  --sector healthcare \
  --no-kb \
  --debug
```

### Example 3: Sample Test
```bash
python -m dux_rfp_agent.main \
  --rfp dux_rfp_agent/sample_data/rfp_sample_excerpt.txt \
  --out ./test \
  --no-kb
```

## Integration Points

### As a Library
```python
from dux_rfp_agent import RFPPipeline
from pathlib import Path

pipeline = RFPPipeline(enable_kb=False)
result = pipeline.process_rfp(
    rfp_path=Path("rfp.pdf"),
    output_dir=Path("./output"),
    sector="government",
    rfp_title="Cloud Services RFP",
    company_name="Acme Corp"
)

print(f"Extracted {result['requirements_count']} requirements")
print(f"QA Status: {result['qa_status']}")
```

### Via API
```python
import requests

with open("rfp.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/proposal",
        files={"file": f},
        data={
            "sector": "government",
            "company_name": "Acme Corp"
        }
    )

result = response.json()
```

## Testing

```bash
cd dux_rfp_agent

# Run tests
pytest

# Run with coverage
pytest --cov=dux_rfp_agent --cov-report=html

# Integration tests (requires API keys)
pytest -m integration
```

## Documentation

- **README.md** - User guide and quick start
- **BUILD_SUMMARY.md** - Architecture details
- **Code docstrings** - Inline documentation
- **Schemas** - JSON validation schemas
- **Prompts** - LLM prompt templates

## Support

- **Sample Data**: `dux_rfp_agent/sample_data/rfp_sample_excerpt.txt`
- **Tests**: `dux_rfp_agent/tests/`
- **Config**: `dux_rfp_agent/config/.env.example`
