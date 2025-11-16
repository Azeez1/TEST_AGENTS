# Process RFP and Generate Proposal

Automated RFP processing and proposal generation using the Dux RFP Agent.

## What This Does

The RFP Agent ingests RFP documents, extracts requirements, builds compliance matrices, retrieves knowledge base evidence, writes proposal sections, validates coverage, and exports professional deliverables.

## Usage

```
/rfp-process [path-to-rfp] --sector [sector] --company [name]
```

## Example

```
/rfp-process ./rfps/gov_cloud_2025.pdf --sector government --company "Acme Solutions"
/rfp-process ./rfps/healthcare_ehr.docx --sector healthcare --no-kb
/rfp-process ./sample_rfp.txt --sector government --debug
```

## Process

1. **Document Ingestion** (automatic)
   - Multi-format support (PDF, DOCX, TXT, ZIP)
   - Page-level text extraction
   - Metadata collection
   - Text normalization
   - OCR fallback for scanned documents

2. **Requirements Parsing** (LLM-powered)
   - Extract all MUST/SHALL/SHOULD/MAY requirements
   - RFC 2119 priority classification
   - Category assignment (technical, management, staffing, etc.)
   - Page citation tracking
   - Keyword extraction
   - Deduplication across document sections
   - Stable ID assignment (R-001, R-002, etc.)

3. **Knowledge Base Retrieval** (Pinecone)
   - Semantic search for relevant evidence
   - Resume matching for staffing requirements
   - Past performance examples
   - Case studies and technical writeups
   - Boilerplate content retrieval
   - Citation tracking [KB: doc_id]

4. **Compliance Matrix Generation** (LLM-powered)
   - Approach description for each requirement
   - Risk assessment (LOW/MEDIUM/HIGH)
   - Owner assignment by category
   - Evidence source linking
   - Completion criteria definition
   - CSV export for review

5. **Proposal Section Writing** (LLM-powered)
   - **Executive Summary**
     - Client needs understanding
     - Our solution overview
     - Key qualifications
     - Value proposition

   - **Technical Approach**
     - Detailed methodology
     - Tools and technologies
     - Architecture and design
     - Performance and scalability
     - Innovation highlights

   - **Management Approach**
     - Project organization
     - PM methodology (Agile/Waterfall/Hybrid)
     - Reporting and communication
     - Risk management
     - Change control

   - Auto-insert citations [RFP p.X], [Requirement R-XXX], [KB: doc_id]

6. **QA Validation** (automatic + LLM)
   - MUST/SHALL requirement coverage check
   - Placeholder detection ([TBD], [TODO])
   - Citation validation
   - Word count verification
   - Quality assessment
   - Issue categorization (CRITICAL/WARNING/INFO)

7. **Export Deliverables** (automatic)
   - proposal_draft.md - Complete proposal (Markdown)
   - requirements.json - Extracted requirements
   - compliance_matrix.csv - Spreadsheet format
   - compliance_matrix.json - Structured data
   - qa_report.json - Validation results
   - proposal.docx - Word document (if configured)
   - SUMMARY.md - Processing summary

## Deliverables

### Generated Files
- **proposal_draft.md** - Complete proposal in Markdown format
- **requirements.json** - Structured requirements with metadata
- **compliance_matrix.csv** - Compliance matrix spreadsheet
- **compliance_matrix.json** - Compliance data in JSON
- **qa_report.json** - Quality assurance validation results
- **proposal.docx** - Word document (requires docxtpl)
- **SUMMARY.md** - Processing summary and statistics

### Statistics Provided
- Total requirements extracted
- MUST/SHALL requirement count
- Compliance items generated
- QA status and coverage percentage
- Processing duration
- Issues found and severity

## Configuration

### Required Environment Variables
```bash
# LLM Provider (OpenAI or Anthropic)
LLM_PROVIDER=openai
LLM_MODEL_SMALL=gpt-4o-mini      # For parsing
LLM_MODEL_STRONG=gpt-4o          # For writing
OPENAI_API_KEY=sk-...

# Optional: Knowledge Base (Pinecone)
PINECONE_API_KEY=...
PINECONE_INDEX=rfp-knowledge-base
EMBEDDING_MODEL=text-embedding-3-small
```

### Command Options
- `--rfp` - Path to RFP document (required)
- `--out` - Output directory (required)
- `--sector` - Industry sector (government, healthcare, finance, etc.)
- `--title` - RFP title (auto-detected if not provided)
- `--company` - Your company name
- `--no-kb` - Disable knowledge base retrieval
- `--debug` - Enable debug logging
- `--log-file` - Log file path

## Sectors Supported

- **government** - FedRAMP, NIST, FAR/DFARS compliance
- **healthcare** - HIPAA, HITRUST, HL7/FHIR
- **finance** - SOC2, PCI-DSS, financial regulations
- **education** - FERPA, accessibility standards
- **other** - General commercial

## Knowledge Base Setup

### Indexing Documents
```bash
# Index resumes for staffing sections
python dux_rfp_agent/scripts/index_kb.py \
  --input ./kb/resumes \
  --type resume \
  --sector government

# Index past performance
python dux_rfp_agent/scripts/index_kb.py \
  --input ./kb/past_performance \
  --type past_performance

# Index technical documentation
python dux_rfp_agent/scripts/index_kb.py \
  --input ./kb/technical \
  --type technical_writeup
```

### Document Types
- resume - Personnel resumes
- past_performance - Project examples
- case_study - Detailed case studies
- technical_writeup - Technical documentation
- boilerplate - Reusable content
- company_info - Company background
- capability_statement - Capabilities overview
- certification - Certifications and awards

## Time Estimate

- **Simple RFP** (< 20 requirements): 5-10 minutes
- **Medium RFP** (20-50 requirements): 10-20 minutes
- **Complex RFP** (50+ requirements): 20-40 minutes

*Processing time depends on document length, number of requirements, and LLM response times*

## Output Format

The system generates a complete proposal bundle in the specified output directory:

```
output/
├── proposal_draft.md          # Complete proposal
├── requirements.json          # All extracted requirements
├── compliance_matrix.csv      # Excel-ready compliance matrix
├── compliance_matrix.json     # Compliance data
├── qa_report.json            # QA validation results
├── proposal.docx             # Word document (optional)
└── SUMMARY.md                # Processing summary
```

## Success Criteria

✅ All MUST/SHALL requirements extracted and addressed
✅ Compliance matrix covers all requirements
✅ Citations link to valid sources
✅ No placeholders ([TBD], [TODO]) in final output
✅ Executive summary within word count
✅ QA validation passes
✅ Professional formatting maintained

## API Alternative

For programmatic access:
```bash
# Start API service
cd dux_rfp_agent
uvicorn dux_rfp_agent.api:app --host 0.0.0.0 --port 8000

# Process via API
curl -X POST "http://localhost:8000/proposal" \
  -F "file=@rfp.pdf" \
  -F "sector=government" \
  -F "company_name=Acme Corp"
```

## Error Handling

The system includes comprehensive error handling:
- Retries with exponential backoff for LLM calls
- Graceful degradation without KB
- Validation at each pipeline stage
- Detailed error logging
- Fallback mechanisms for failures

## Notes

- **First Run**: May take longer as LLM generates detailed responses
- **Knowledge Base**: Optional but enhances proposal quality significantly
- **API Keys**: Required for OpenAI or Anthropic
- **DOCX Export**: Requires docxtpl package (optional)
- **Sectors**: Templates can be customized in `templates/sectors/`

## Project Location

```
dux_rfp_agent/
├── src/dux_rfp_agent/      # Source code
├── scripts/                 # KB indexing scripts
├── sample_data/            # Sample RFP
├── tests/                  # Test suite
└── README.md               # Full documentation
```

## Troubleshooting

**"Pinecone not available"**
- Set PINECONE_API_KEY in environment
- Or use --no-kb flag

**"LLM API key not found"**
- Set OPENAI_API_KEY or ANTHROPIC_API_KEY
- Check .env file exists

**"Schema validation failed"**
- LLM output format issue
- Check logs for details
- Try with --debug flag

## Learn More

See `dux_rfp_agent/README.md` and `dux_rfp_agent/BUILD_SUMMARY.md` for:
- Complete architecture details
- API documentation
- Customization guide
- Advanced usage examples
