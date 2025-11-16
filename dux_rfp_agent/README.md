# Dux Proposal Architect (RFP Agent)

Production-ready scaffold for an **RFP / Proposal Automation Agent** that:
- Ingests RFPs (PDF/DOCX/TXT/ZIP)
- Extracts structured **requirements** + **compliance items**
- Builds a **compliance matrix**
- Retrieves reusable content from a **knowledge base** (Pinecone)
- Generates a polished **proposal draft** using sector templates
- Exports to **DOCX** (and PDF via your converter of choice)
- Runs as a **CLI** and optional **FastAPI** service

> **Created**: 2025-11-16

---

## Features

### Core Capabilities
- **Multi-format ingestion**: PDF, DOCX, TXT, ZIP with page tracking
- **Intelligent parsing**: LLM-based requirement extraction with RFC 2119 priority levels
- **Knowledge base**: Pinecone-powered retrieval of resumes, past performance, case studies
- **Compliance matrix**: Automated mapping of requirements to approaches with risk assessment
- **Proposal generation**: Section-by-section writing with citation tracking
- **QA validation**: Automated coverage checks and placeholder detection
- **Multiple outputs**: Markdown, JSON, CSV, and DOCX formats

### Architecture
```
┌─────────────┐     ┌──────────┐     ┌─────────┐     ┌────────────┐
│ RFP Upload  │────▶│ Ingestion│────▶│ Chunking│────▶│   Parser   │
└─────────────┘     └──────────┘     └─────────┘     └────────────┘
                                                             │
                    ┌──────────────────────────────────────┘
                    │
                    ▼
              ┌──────────┐     ┌───────────┐     ┌─────────┐
              │ KB Query │────▶│Compliance │────▶│ Writers │
              └──────────┘     └───────────┘     └─────────┘
                    │                                   │
                    ▼                                   ▼
              ┌──────────┐                        ┌─────────┐
              │ Pinecone │                        │   QA    │
              └──────────┘                        └─────────┘
                                                       │
                                                       ▼
                                                  ┌─────────┐
                                                  │ Exports │
                                                  └─────────┘
```

---

## Quick Start

### Installation

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install package in editable mode
pip install -e .
```

### Configuration

```bash
# 1. Copy environment template
cp config/.env.example .env

# 2. Edit .env and add your API keys
# Required:
#   - OPENAI_API_KEY or ANTHROPIC_API_KEY
# Optional (for KB):
#   - PINECONE_API_KEY
#   - PINECONE_INDEX
```

### Basic Usage

```bash
# Process an RFP (without KB)
python -m dux_rfp_agent.main \
  --rfp sample_data/rfp_sample_excerpt.txt \
  --out ./output \
  --no-kb

# Process with knowledge base
python -m dux_rfp_agent.main \
  --rfp input.pdf \
  --out ./output \
  --sector government \
  --title "Cloud Case Management RFP"

# With custom company name
python -m dux_rfp_agent.main \
  --rfp input.pdf \
  --out ./output \
  --company "Acme Corp" \
  --sector healthcare

# Enable debug logging
python -m dux_rfp_agent.main \
  --rfp input.pdf \
  --out ./output \
  --debug \
  --log-file ./rfp_agent.log
```

---

## Project Structure

```
dux_rfp_agent/
├── src/dux_rfp_agent/
│   ├── __init__.py
│   ├── main.py                 # CLI entry point
│   ├── api.py                  # FastAPI service
│   ├── pipeline.py             # Main orchestrator
│   ├── config.py               # Configuration management
│   ├── logger.py               # Logging setup
│   ├── llm_client.py           # LLM API wrapper
│   ├── ingestion.py            # Document ingestion
│   ├── chunking.py             # Text chunking
│   ├── parser.py               # Requirements parser
│   ├── retrieval.py            # Pinecone KB retrieval
│   ├── compliance.py           # Compliance matrix builder
│   ├── writer.py               # Proposal writers
│   ├── qa_agent.py             # QA validation
│   ├── export.py               # Export handlers
│   ├── config/
│   │   └── agents.yml          # Agent configuration
│   ├── prompts/                # LLM prompts
│   │   ├── parser.txt
│   │   ├── compliance_matrix.txt
│   │   ├── writer_executive_summary.txt
│   │   ├── writer_technical_approach.txt
│   │   ├── writer_management_approach.txt
│   │   └── qa_coverage.txt
│   ├── schemas/                # JSON schemas
│   │   ├── requirements.schema.json
│   │   ├── compliance.schema.json
│   │   └── pinecone_metadata.schema.json
│   └── templates/              # Jinja templates
│       ├── proposal_template.md
│       └── sectors/
│           ├── government.md
│           └── healthcare.md
├── scripts/
│   └── index_kb.py             # KB indexing script
├── sample_data/
│   └── rfp_sample_excerpt.txt  # Sample RFP
├── tests/                      # Test suite
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Knowledge Base Setup

### Indexing Documents

```bash
# Index resumes
python scripts/index_kb.py \
  --input ./kb/resumes \
  --type resume \
  --sector government

# Index past performance
python scripts/index_kb.py \
  --input ./kb/past_performance \
  --type past_performance \
  --sector government

# Index to custom namespace
python scripts/index_kb.py \
  --input ./kb/technical_docs \
  --type technical_writeup \
  --namespace engineering
```

### Metadata Schema

Documents are indexed with the following metadata:
- `doc_id`: Unique identifier
- `doc_type`: resume, past_performance, case_study, etc.
- `content_type`: full_document, section, paragraph, summary
- `title`: Document title
- `sector`: government, healthcare, finance, etc.
- `tags`: Keywords and technologies
- `source_file`: Original filename

See `src/dux_rfp_agent/schemas/pinecone_metadata.schema.json` for full schema.

---

## API Service

### Starting the API

```bash
# Development
uvicorn dux_rfp_agent.api:app --reload

# Production
uvicorn dux_rfp_agent.api:app --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Parse RFP
```bash
curl -X POST "http://localhost:8000/parse" \
  -F "file=@rfp.pdf" \
  -F "sector=government"
```

#### Generate Proposal
```bash
curl -X POST "http://localhost:8000/proposal" \
  -F "file=@rfp.pdf" \
  -F "sector=government" \
  -F "company_name=Acme Corp" \
  -F "enable_kb=true"
```

#### QA Validation
```bash
curl -X POST "http://localhost:8000/qa" \
  -F "requirements_file=@requirements.json" \
  -F "proposal_file=@proposal.md" \
  -F "compliance_file=@compliance.json"
```

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=dux_rfp_agent --cov-report=html

# Run specific test file
pytest tests/test_ingestion.py

# Run with markers
pytest -m "not integration"  # Skip integration tests
```

---

## Output Files

After processing, the following files are generated:

- **proposal_draft.md**: Complete proposal in Markdown
- **requirements.json**: Extracted requirements with metadata
- **compliance_matrix.json**: Compliance matrix data
- **compliance_matrix.csv**: Spreadsheet format for review
- **qa_report.json**: QA validation results
- **proposal.docx**: Word document (if docxtpl available)
- **SUMMARY.md**: Processing summary

---

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LLM_PROVIDER` | openai or anthropic | Yes |
| `LLM_MODEL_SMALL` | Model for parsing (e.g., gpt-4o-mini) | Yes |
| `LLM_MODEL_STRONG` | Model for writing (e.g., gpt-4o) | Yes |
| `OPENAI_API_KEY` | OpenAI API key | If using OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic API key | If using Anthropic |
| `PINECONE_API_KEY` | Pinecone API key | For KB retrieval |
| `PINECONE_INDEX` | Pinecone index name | For KB retrieval |
| `EMBEDDING_MODEL` | Embedding model (e.g., text-embedding-3-small) | For KB retrieval |

### Agent Configuration

Edit `src/dux_rfp_agent/config/agents.yml` to customize:
- Model selection per agent
- Temperature settings
- Token limits
- Retry attempts
- Batch sizes

---

## Customization

### Adding Sector Templates

Create a new template in `src/dux_rfp_agent/templates/sectors/`:

```markdown
## Custom Sector Addendum

### Specific Requirements
- Industry-specific requirement 1
- Industry-specific requirement 2

### Compliance Standards
- Relevant compliance framework
- Certification requirements
```

### Customizing Prompts

Edit prompt files in `src/dux_rfp_agent/prompts/` to adjust:
- Parsing behavior
- Compliance matrix format
- Writing style and tone
- QA validation criteria

### Adding Document Types

Extend the Pinecone metadata schema in:
`src/dux_rfp_agent/schemas/pinecone_metadata.schema.json`

---

## Troubleshooting

### Common Issues

**1. "Pinecone not available"**
- Install: `pip install pinecone-client`
- Set `PINECONE_API_KEY` in `.env`
- Create index at pinecone.io

**2. "LLM API key not found"**
- Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in `.env`
- Ensure `.env` file is in the project root

**3. "docxtpl not available"**
- Install: `pip install docxtpl`
- Or use Markdown output only

**4. "Schema validation failed"**
- LLM output didn't match expected format
- Check prompt templates
- Verify model supports JSON mode

### Debug Mode

```bash
# Enable detailed logging
python -m dux_rfp_agent.main --rfp input.pdf --out ./output --debug
```

---

## Development

### Code Style

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type checking (if using)
mypy src/
```

### Adding Tests

```python
# tests/test_mymodule.py
import pytest
from dux_rfp_agent.mymodule import MyClass

class TestMyClass:
    def test_feature(self):
        obj = MyClass()
        assert obj.method() == expected_result
```

---

## License

MIT License - Use commercially at will.

---

## Support

For issues, questions, or contributions:
- GitHub Issues: [Your repo URL]
- Documentation: This README
- Example: See `sample_data/rfp_sample_excerpt.txt`

---

## Roadmap

Potential enhancements:
- [ ] Support for additional LLM providers (Google, Cohere)
- [ ] PDF export via WeasyPrint or Gotenberg
- [ ] Multi-language support
- [ ] Interactive web UI
- [ ] Template library for common RFP types
- [ ] Cost estimation and tracking
- [ ] Collaborative editing features

---

**Built with production-ready architecture for real-world RFP automation.**
