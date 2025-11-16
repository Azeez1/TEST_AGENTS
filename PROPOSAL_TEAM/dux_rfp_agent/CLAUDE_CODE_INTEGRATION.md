# Claude Code Integration Guide

The Dux RFP Agent is now fully integrated with Claude Code and can be invoked as an agent!

## ✅ What Was Added

### 1. Slash Command: `/rfp-process`
Location: `.claude/commands/rfp-process.md`

A dedicated slash command for processing RFPs directly from Claude Code.

### 2. Skill: `rfp-agent`
Location: `.claude/skills/rfp-agent/`

A skill that auto-activates when you mention RFP-related keywords in your conversation.

### 3. Agent Registration
Location: `.claude/settings.json`

The RFP agent is registered in workspace settings with full capabilities and auto-activation triggers.

---

## 🚀 How to Use

### Method 1: Slash Command

```
/rfp-process path/to/rfp.pdf --sector government --company "Your Company Name"
```

**Full Syntax:**
```
/rfp-process <rfp-file> [options]

Options:
  --sector <sector>      Industry sector (government, healthcare, finance, etc.)
  --company <name>       Your company name
  --no-kb                Disable knowledge base retrieval
  --debug                Enable debug logging
  --title <title>        RFP title (auto-detected if not provided)
```

**Examples:**
```
/rfp-process ./rfps/gov_cloud_2025.pdf --sector government --company "Acme Solutions"
/rfp-process ./rfps/healthcare_ehr.docx --sector healthcare --no-kb
/rfp-process ./sample_rfp.txt --debug
```

### Method 2: Natural Language (Auto-Activation)

Just mention RFP-related keywords in your conversation:

```
"I need to process this RFP document: ./rfps/procurement.pdf"
"Help me generate a proposal for this government bid"
"Extract requirements from this procurement document"
"Analyze this RFP and create a compliance matrix"
```

**Auto-activation triggers:**
- "rfp"
- "proposal"
- "bid"
- "tender"
- "procurement"
- "solicitation"
- "request for proposal"

### Method 3: Programmatic (via Python)

```python
from dux_rfp_agent import RFPPipeline
from pathlib import Path

pipeline = RFPPipeline(enable_kb=True)
result = pipeline.process_rfp(
    rfp_path=Path("rfp.pdf"),
    output_dir=Path("./output"),
    sector="government",
    rfp_title="Cloud Services RFP",
    company_name="Your Company"
)

print(f"✅ Extracted {result['requirements_count']} requirements")
print(f"✅ Generated {result['compliance_items']} compliance items")
print(f"✅ QA Status: {result['qa_status']}")
```

### Method 4: API Service

```bash
# Start the API
cd dux_rfp_agent
uvicorn dux_rfp_agent.api:app --host 0.0.0.0 --port 8000

# Process via API
curl -X POST "http://localhost:8000/proposal" \
  -F "file=@rfp.pdf" \
  -F "sector=government" \
  -F "company_name=Acme Corp" \
  -F "enable_kb=true"
```

---

## 📋 Configuration

### Required: LLM API Keys

Edit `dux_rfp_agent/.env`:
```bash
# Choose your provider
LLM_PROVIDER=openai

# Set models
LLM_MODEL_SMALL=gpt-4o-mini      # For parsing
LLM_MODEL_STRONG=gpt-4o          # For writing

# Add API key
OPENAI_API_KEY=sk-...

# OR for Anthropic
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-...
```

### Optional: Knowledge Base (Pinecone)

```bash
PINECONE_API_KEY=...
PINECONE_INDEX=rfp-knowledge-base
EMBEDDING_MODEL=text-embedding-3-small
```

---

## 📤 Output Files

After processing, you'll get:

```
output/
├── proposal_draft.md          # Complete proposal in Markdown
├── requirements.json          # Extracted requirements with metadata
├── compliance_matrix.csv      # Excel-ready compliance matrix
├── compliance_matrix.json     # Compliance data (JSON)
├── qa_report.json            # QA validation results
├── proposal.docx             # Word document (if docxtpl installed)
└── SUMMARY.md                # Processing summary with statistics
```

---

## 🎯 Quick Test

Try the sample RFP to verify everything works:

```
/rfp-process dux_rfp_agent/sample_data/rfp_sample_excerpt.txt --sector government --no-kb
```

This will:
1. ✅ Ingest the sample RFP (5 sections, 30+ requirements)
2. ✅ Extract all requirements with LLM
3. ✅ Generate compliance matrix
4. ✅ Write proposal sections
5. ✅ Run QA validation
6. ✅ Export all deliverables

Expected output location: `./output/`

---

## 🔧 Troubleshooting

### "Command not found: /rfp-process"
- The slash command should be automatically recognized
- Check that `.claude/commands/rfp-process.md` exists
- Restart Claude Code if needed

### "LLM API key not found"
```bash
cd dux_rfp_agent
cp config/.env.example .env
# Edit .env and add your API keys
```

### "Pinecone not available"
- Either add `PINECONE_API_KEY` to `.env`
- Or use `--no-kb` flag to disable KB retrieval

### "Module not found: dux_rfp_agent"
```bash
cd dux_rfp_agent
pip install -r requirements.txt
pip install -e .
```

---

## 📚 Documentation

### In This Repo
- **SKILL.md** - Complete skill capabilities and architecture
- **README.md** - User guide and quick start
- **BUILD_SUMMARY.md** - Implementation details
- `/rfp-process` command - Inline help and examples

### System Files
- **Slash Command**: `.claude/commands/rfp-process.md`
- **Skill Definition**: `.claude/skills/rfp-agent/SKILL.md`
- **Agent Config**: `.claude/settings.json` (agents.rfp-agent)

---

## 🎨 Customization

### Add Custom Sectors

Create new template in `src/dux_rfp_agent/templates/sectors/`:
```markdown
## Finance Sector Addendum

### Regulatory Compliance
- SOC 2 Type II requirements
- PCI-DSS compliance
- GLBA considerations
```

### Customize Prompts

Edit prompts in `src/dux_rfp_agent/prompts/`:
- `parser.txt` - Requirement extraction style
- `compliance_matrix.txt` - Compliance format
- `writer_executive_summary.txt` - Executive summary tone
- `writer_technical_approach.txt` - Technical depth
- `writer_management_approach.txt` - Management style
- `qa_coverage.txt` - Validation criteria

### Modify Agent Configuration

Edit `src/dux_rfp_agent/config/agents.yml`:
```yaml
agents:
  parser:
    model: "${LLM_MODEL_SMALL}"
    temperature: 0.1
    max_tokens: 4000
    retry_attempts: 3
```

---

## 🌟 Advanced Features

### Knowledge Base Indexing

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

# Index technical docs
python dux_rfp_agent/scripts/index_kb.py \
  --input ./kb/technical \
  --type technical_writeup
```

### Supported Document Types
- `resume` - Personnel resumes
- `past_performance` - Project examples
- `case_study` - Detailed case studies
- `technical_writeup` - Technical documentation
- `boilerplate` - Reusable content
- `company_info` - Company background
- `capability_statement` - Capabilities
- `certification` - Certifications and awards

---

## 📊 What Gets Automated

| Task | Automated | Quality |
|------|-----------|---------|
| Document ingestion | ✅ 100% | High |
| Requirements extraction | ✅ 100% | High (LLM) |
| Priority classification | ✅ 100% | High (RFC 2119) |
| Page citation tracking | ✅ 100% | Precise |
| KB evidence retrieval | ✅ 100% | Semantic |
| Compliance matrix | ✅ 100% | High (LLM) |
| Proposal writing | ✅ 100% | High (LLM) |
| QA validation | ✅ 100% | Automated + LLM |
| Export (MD/JSON/CSV) | ✅ 100% | Perfect |
| DOCX generation | ✅ 100% | Formatted |

---

## 🚦 Processing Time

| RFP Complexity | Requirements | Estimated Time |
|----------------|--------------|----------------|
| Simple | < 20 | 5-10 minutes |
| Medium | 20-50 | 10-20 minutes |
| Complex | 50-100 | 20-40 minutes |
| Enterprise | 100+ | 40-60 minutes |

*Times vary based on document size, LLM response latency, and KB queries*

---

## ✅ Success Checklist

After processing, verify:
- [ ] All MUST/SHALL requirements extracted
- [ ] Page citations present for traceability
- [ ] Compliance matrix covers all requirements
- [ ] Proposal sections generated
- [ ] No placeholders ([TBD], [TODO]) in output
- [ ] QA report shows PASS or acceptable warnings
- [ ] All output files present in directory

---

## 🔗 Quick Links

- **Sample RFP**: `dux_rfp_agent/sample_data/rfp_sample_excerpt.txt`
- **Config Template**: `dux_rfp_agent/config/.env.example`
- **Tests**: `dux_rfp_agent/tests/`
- **API Docs**: Start server and visit http://localhost:8000/docs

---

## 💡 Pro Tips

1. **Start with Sample**: Test with the sample RFP first to verify setup
2. **Use --no-kb Initially**: Disable KB for faster testing without Pinecone
3. **Enable Debug**: Use `--debug` flag to see detailed processing logs
4. **Check QA Report**: Always review `qa_report.json` for issues
5. **Customize Prompts**: Adjust prompts for your specific needs
6. **Index Your KB**: Populate Pinecone with your company's content
7. **Review Before Submission**: Generated proposals need human review
8. **Iterate Prompts**: Tune prompts based on output quality

---

**The RFP Agent is ready to automate your proposal generation workflow!** 🚀
