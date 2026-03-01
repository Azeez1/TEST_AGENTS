# PROPOSAL_TEAM

**RFP Automation & Proposal Generation Workspace**

Production-ready system for automating Request for Proposal (RFP) processing and generating comprehensive, compliant proposal responses.

---

## 🎯 Team Purpose

The PROPOSAL_TEAM workspace automates the end-to-end proposal development lifecycle:

1. **Ingest** RFPs in multiple formats (PDF, DOCX, TXT, ZIP)
2. **Extract** requirements with AI-powered semantic parsing
3. **Retrieve** evidence from organizational knowledge base
4. **Generate** compliance matrices with risk assessment
5. **Write** proposal sections with proper citations
6. **Validate** completeness and quality
7. **Export** professional deliverables in multiple formats

---

## 📁 Workspace Structure

```
PROPOSAL_TEAM/
├── .claude/
│   ├── agents/
│   │   └── rfp-agent.md          # RFP automation agent
│   ├── commands/
│   │   └── rfp-process.md        # Slash command for processing
│   └── settings.json             # Team workspace config
├── tools/                        # RFP processing tools
├── scripts/                      # Utility scripts
├── tests/                        # Test suite
├── config/                       # Configuration
├── outputs/                      # Generated proposals
├── kb/                           # Knowledge base documents
│   ├── resumes/                  # Personnel resumes
│   ├── past_performance/         # Project examples
│   ├── case_studies/             # Detailed case studies
│   ├── technical/                # Technical documentation
│   └── boilerplate/              # Reusable content
├── examples/                     # Example RFPs and outputs
├── docs/                         # Team documentation
└── README.md                     # This file
```

---

## 🚀 Quick Start

### 1. Setup

```bash
cd PROPOSAL_TEAM

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp config/.env.example .env
# Edit .env and add your OPENAI_API_KEY or ANTHROPIC_API_KEY
```

### 2. Process an RFP

#### Via Slash Command
```bash
/rfp-process ./path/to/rfp.pdf --sector government --company "Your Company"
```

#### Via Natural Language
Just say: *"Process this RFP and generate a proposal"*

Auto-activates on keywords: `rfp`, `proposal`, `bid`, `tender`, `procurement`, `solicitation`

### 3. Review Outputs

Check `outputs/` directory for:
- `proposal_draft.md` - Complete proposal
- `requirements.json` - Extracted requirements
- `compliance_matrix.csv` - Compliance matrix
- `qa_report.json` - Quality validation
- `proposal.docx` - Word document

---

## 🤖 Agents

### rfp-agent
**Location**: `.claude/agents/rfp-agent.md`

The main RFP automation specialist that orchestrates the entire proposal generation pipeline.

**Capabilities**:
- Multi-format document ingestion
- Semantic requirement extraction
- Knowledge base retrieval
- Compliance matrix generation
- AI-powered proposal writing
- Quality assurance validation
- Multi-format export

**Usage**:
```bash
/rfp-process <rfp-file> [options]

Options:
  --sector <sector>      Industry sector (government, healthcare, finance)
  --company <name>       Your company name
  --title <title>        RFP title (auto-detected if not provided)
  --no-kb                Disable knowledge base retrieval
  --debug                Enable debug logging
```

---

## 📚 Knowledge Base

The knowledge base (`kb/`) stores reusable content that gets retrieved during proposal generation:

### Directory Structure
```
kb/
├── resumes/              # Personnel resumes for staffing sections
├── past_performance/     # Project examples and case studies
├── case_studies/         # Detailed success stories
├── technical/            # Technical documentation and writeups
├── boilerplate/          # Reusable proposal content
├── certifications/       # Company and personnel certifications
└── company_info/         # Company background and capabilities
```

### Indexing Documents

```bash
# Index resumes
python scripts/index_kb.py \
  --input kb/resumes \
  --type resume \
  --sector government

# Index past performance
python scripts/index_kb.py \
  --input kb/past_performance \
  --type past_performance

# Index technical docs
python scripts/index_kb.py \
  --input kb/technical \
  --type technical_writeup
```

**Note**: Requires Pinecone API key configured in `.env`

---

## 📊 Outputs

All generated proposals are stored in `outputs/` with timestamps:

```
outputs/
├── 2025-11-16_gov_cloud_rfp/
│   ├── proposal_draft.md
│   ├── requirements.json
│   ├── compliance_matrix.csv
│   ├── compliance_matrix.json
│   ├── qa_report.json
│   ├── proposal.docx
│   └── SUMMARY.md
└── 2025-11-17_healthcare_ehr/
    └── ...
```

### Output Files

| File | Description |
|------|-------------|
| `proposal_draft.md` | Complete proposal in Markdown |
| `requirements.json` | All extracted requirements with metadata |
| `compliance_matrix.csv` | Excel-ready compliance matrix |
| `compliance_matrix.json` | Compliance data in JSON format |
| `qa_report.json` | Quality assurance validation report |
| `proposal.docx` | Word document (if docxtpl installed) |
| `SUMMARY.md` | Processing statistics and summary |

---

## ⚙️ Configuration

### Environment Variables

Edit `config/.env`:

```bash
# LLM Provider (Required)
LLM_PROVIDER=openai
LLM_MODEL_SMALL=gpt-4o-mini      # For parsing
LLM_MODEL_STRONG=gpt-4o          # For writing
OPENAI_API_KEY=sk-...

# Knowledge Base (Optional)
PINECONE_API_KEY=...
PINECONE_INDEX=rfp-knowledge-base
EMBEDDING_MODEL=text-embedding-3-small

# Logging
LOG_LEVEL=INFO
```

### Supported Sectors

- `government` - FedRAMP, NIST, FAR/DFARS compliance
- `healthcare` - HIPAA, HITRUST, HL7/FHIR standards
- `finance` - SOC2, PCI-DSS requirements
- `education` - FERPA, accessibility standards
- `other` - General commercial

---

## 🎯 Features

### Semantic Chunking
Intelligent document chunking that:
- Detects section headers (`SECTION 1:`, `1.`, `1.1`, etc.)
- Identifies requirement blocks (MUST/SHALL/SHOULD/MAY)
- Respects paragraph boundaries
- Never splits requirements mid-text
- Keeps sections together

### Requirements Extraction
- RFC 2119 priority classification (MUST, SHALL, SHOULD, MAY)
- Category assignment (technical, management, staffing, etc.)
- Page citation tracking for traceability
- Keyword extraction
- Automatic deduplication
- Stable ID assignment (R-001, R-002, ...)

### Compliance Matrix
- Automated approach descriptions
- Risk assessment (LOW/MEDIUM/HIGH)
- Owner assignment by category
- Evidence linking to knowledge base
- Completion criteria
- CSV export for review

### Proposal Writing
- Executive Summary (500-800 words)
- Technical Approach section
- Management Approach section
- Automatic citation insertion
  - `[RFP p.X]` for source pages
  - `[Requirement R-XXX]` for traceability
  - `[KB: doc_id]` for evidence
- Sector-specific templates

### Quality Assurance
- MUST/SHALL coverage verification
- Placeholder detection ([TBD], [TODO])
- Citation integrity validation
- Word count checking
- LLM-based quality assessment
- Detailed issue reporting

---

## 📖 Documentation

### Team Docs
- **README.md** (this file) - Workspace overview
- **HOW_IT_WORKS.md** - System architecture and pipeline details
- **COMPLIANCE_FRAMEWORKS.md** - 30+ compliance frameworks reference

### Agent Docs
- **.claude/agents/rfp-agent.md** - Complete agent definition
- **.claude/commands/rfp-process.md** - Slash command reference

---

## 🧪 Testing

```bash
cd PROPOSAL_TEAM

# Run all tests
pytest tests/

# With coverage
pytest tests/ --cov --cov-report=html

# Quick test with sample
python tools/main.py \
  --rfp examples/rfp_sample_excerpt.txt \
  --out outputs/test \
  --no-kb
```

---

## 🔧 Troubleshooting

### "LLM API key not found"
```bash
cd PROPOSAL_TEAM
cp config/.env.example .env
# Edit .env and add OPENAI_API_KEY or ANTHROPIC_API_KEY
```

### "Pinecone not available"
- Either add `PINECONE_API_KEY` to `.env`
- Or use `--no-kb` flag to disable KB retrieval

### "Module not found"
```bash
cd PROPOSAL_TEAM
pip install -r requirements.txt
```

---

## 🎓 Examples

### Example 1: Government RFP
```bash
/rfp-process ./examples/gov_cloud_services.pdf \
  --sector government \
  --company "Defense Solutions Inc"
```

### Example 2: Healthcare RFP (no KB)
```bash
/rfp-process ./examples/hospital_ehr.docx \
  --sector healthcare \
  --no-kb \
  --debug
```

### Example 3: Quick Test
```bash
/rfp-process examples/rfp_sample_excerpt.txt \
  --sector government \
  --no-kb
```

---

## 📊 Performance

| RFP Complexity | Requirements | Processing Time |
|----------------|--------------|-----------------|
| Simple         | < 20         | 5-10 minutes    |
| Medium         | 20-50        | 10-20 minutes   |
| Complex        | 50-100       | 20-40 minutes   |
| Enterprise     | 100+         | 40-60 minutes   |

---

## 🤝 Team Collaboration

### Workspace Benefits
- **Isolation**: Team-specific config doesn't affect other teams
- **Organization**: All proposal work in one place
- **Knowledge**: Centralized KB for the team
- **Outputs**: All proposals tracked in outputs/
- **Skills**: Inherits global skills, enables team-specific ones

### Best Practices
1. Keep KB updated with latest resumes and past performance
2. Review QA reports before finalizing proposals
3. Customize sector templates for your domain
4. Version control proposal outputs
5. Archive completed proposals for reference

---

## 📜 License

MIT - Use commercially at will

---

## 🚀 Next Steps

1. **Initial Setup**: Configure API keys in `.env`
2. **Populate KB**: Add resumes, past performance, technical docs
3. **Test**: Process sample RFP to verify setup
4. **Customize**: Adjust prompts and templates for your needs
5. **Process**: Run on real RFPs and refine

---

**PROPOSAL_TEAM is ready to automate your proposal development!** 🎯
