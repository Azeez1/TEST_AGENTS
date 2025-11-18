# PROPOSAL_TEAM - Clean Architecture

## 🎯 Purpose
Automated RFP analysis and proposal generation system optimized for **10 priority compliance frameworks**.

## 📁 Clean Directory Structure

```
PROPOSAL_TEAM/
├── tools/                          # Core Python modules
│   ├── user_priority_frameworks.py    # Your 10 priority frameworks
│   ├── rfp_parser.py                  # Multi-format RFP parser
│   ├── compliance_engine.py           # 6-Block compliance engine
│   ├── pinecone_knowledge_base.py     # Pinecone vector DB integration
│   ├── adaptive_proposal_writer.py    # Adaptive proposal generator
│   └── legacy/                        # Archived original modules
│
├── tests/                          # Test suite
│   ├── test_integrated_system.py      # Full end-to-end test
│   ├── test_user_frameworks.py        # Framework detection test
│   └── test_compliance_suite.py       # Compliance test suite
│
├── scripts/                        # Utility scripts
│   ├── upload_compliance_to_pinecone.py   # Upload PDFs to Pinecone
│   └── verify_compliance_docs.py          # Verify PDF documents exist
│
├── config/                         # Configuration
│   ├── .env                           # API keys (Pinecone configured)
│   └── compliance_manifest.json       # Document manifest
│
├── docs/                           # Documentation
│   ├── README.md                      # Original documentation
│   ├── HOW_IT_WORKS.md                # System overview
│   └── SETUP.md                       # Setup instructions
│
├── .claude/                        # Claude agent definition
│   └── agents/
│       └── rfp-agent.md
│
└── archive/                        # Old test files (can be deleted)
```

## 🚀 Quick Start

### 1. Test the System
```bash
# Run the integrated test suite
python tests/test_integrated_system.py

# Test framework detection only
python tests/test_user_frameworks.py
```

### 2. Verify Compliance Documents
```bash
# Check that your 21 PDFs exist
python scripts/verify_compliance_docs.py
```

### 3. Upload to Pinecone
```bash
# Upload compliance documents to Pinecone
python scripts/upload_compliance_to_pinecone.py
```

## 🔧 Core Components

### 1. **user_priority_frameworks.py**
Your 10 equally-optimized compliance frameworks:
- CMMC 2.0 (6 PDFs)
- FedRAMP (3 PDFs)
- NIST 800-171 Rev 3 (2 PDFs)
- NIST 800-53 Rev 5 (3 PDFs)
- HIPAA (2 PDFs)
- PCI-DSS v4.0 (1 PDF)
- GDPR (1 PDF)
- SOC 2 (No PDFs - proprietary)
- ISO 27001 (No PDFs - paid standard)
- GLBA (2 PDFs)
- DFARS (1 PDF bonus)

### 2. **rfp_parser.py**
- Supports FAR Section L/M, SLED, Commercial, International formats
- Intelligent format detection with confidence scoring
- Adaptive parsing for each format type

### 3. **compliance_engine.py**
6-Block Universal Compliance Engine:
- Block 1: Framework Detection
- Block 2: Requirements Mapping
- Block 3: Gap Analysis
- Block 4: Evidence Retrieval
- Block 5: Response Generation
- Block 6: Integration Orchestration

### 4. **pinecone_knowledge_base.py**
- Framework-aware chunking strategies
- Smart indexing with metadata
- Optimized for 21 PDF documents
- API Key: `pcsk_YwCSZ_...` (configured in .env)

### 5. **adaptive_proposal_writer.py**
- Format-adaptive proposal generation
- Win themes and differentiators
- Compliance-focused content
- Export to JSON and Markdown

## ⚙️ Configuration

### API Keys (config/.env)
```bash
ANTHROPIC_API_KEY=your_key_here
PINECONE_API_KEY=pcsk_YwCSZ_SSsaxk2HxiZM5uRsQ1uCV2KsoNsgGdPmdpNZ99aiZLSaewmCmVEthUi97uENvjH
OPENAI_API_KEY=your_key_here  # Optional for LLM operations
```

### Compliance Documents Location
```
C:\Users\sabaa\OneDrive\Desktop\Compliance Frameworks\
```

## 📊 Key Features

✅ **Equal Optimization** - All 10 frameworks treated with equal priority
✅ **Multi-Format Support** - Handles Federal, State, Commercial, International RFPs
✅ **Smart Detection** - Confidence scoring for framework presence
✅ **Intelligent Chunking** - Framework-specific document processing
✅ **Integration Mapping** - Identifies framework overlaps
✅ **Adaptive Output** - Proposals adapt to RFP format automatically
✅ **Risk Analysis** - Identifies gaps and mitigation strategies

## 🧪 Testing

Run the comprehensive test suite:
```bash
cd PROPOSAL_TEAM
python tests/test_integrated_system.py
```

This will test:
- RFP parsing (4 formats)
- Framework detection (10 frameworks)
- Compliance analysis
- Proposal generation
- Knowledge base operations

## 📝 Notes

- The `archive/` folder contains old test files and can be safely deleted
- The `tools/legacy/` folder contains the original modules (kept for reference)
- The `kb/` folder appears unused and can be removed if not needed
- All imports have been updated to use the `tools.` prefix

## 🎉 Status

✅ **System is fully operational and cleaned up!**
- All 10 priority frameworks optimized equally
- Clean, organized directory structure
- No duplicate code
- Ready for production use