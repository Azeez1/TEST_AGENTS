# RFP Agent Skill

Production-ready RFP automation system for processing Request for Proposals and generating comprehensive proposal responses.

## Quick Start

### Via Slash Command
```
/rfp-process path/to/rfp.pdf --sector government --company "Your Company"
```

### Via Direct Invocation
Just mention "RFP" or "proposal" in your request and the skill will auto-activate:
```
"I need to process this RFP document and generate a proposal"
"Help me extract requirements from this procurement document"
"Generate a bid response for this government RFP"
```

## What It Does

1. **Ingests** RFP documents (PDF, DOCX, TXT, ZIP)
2. **Extracts** requirements with LLM (MUST/SHALL/SHOULD classification)
3. **Retrieves** evidence from knowledge base (Pinecone)
4. **Generates** compliance matrix with risk assessment
5. **Writes** proposal sections (executive, technical, management)
6. **Validates** coverage and quality with QA agent
7. **Exports** deliverables (Markdown, JSON, CSV, DOCX)

## Configuration

Set these environment variables in `dux_rfp_agent/.env`:
```bash
LLM_PROVIDER=openai
LLM_MODEL_SMALL=gpt-4o-mini
LLM_MODEL_STRONG=gpt-4o
OPENAI_API_KEY=sk-...

# Optional for KB
PINECONE_API_KEY=...
PINECONE_INDEX=rfp-knowledge-base
```

## Output

Generated in specified output directory:
- `proposal_draft.md` - Complete proposal
- `requirements.json` - All requirements
- `compliance_matrix.csv` - Excel-ready matrix
- `qa_report.json` - Validation results
- `proposal.docx` - Word document (optional)

## Learn More

See:
- **SKILL.md** - Complete capabilities and architecture
- **dux_rfp_agent/README.md** - Full documentation
- **dux_rfp_agent/BUILD_SUMMARY.md** - Implementation details
