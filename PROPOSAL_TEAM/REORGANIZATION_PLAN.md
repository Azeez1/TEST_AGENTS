# PROPOSAL_TEAM Directory Reorganization Plan

## Current Issues
- Duplicate test files (6 test files doing similar things)
- Old dux_rfp_agent structure still present
- Mixed organization between tools/ and other directories
- Unclear hierarchy

## Proposed Clean Structure

```
PROPOSAL_TEAM/
├── .claude/
│   └── agents/
│       └── rfp-agent.md              # Agent definition
│
├── tools/                             # All Python modules (following repo convention)
│   ├── __init__.py
│   ├── user_priority_frameworks.py   # Your 10 frameworks (KEEP)
│   ├── rfp_parser.py                 # Multi-format parser (KEEP)
│   ├── compliance_engine.py          # 6-Block engine (KEEP)
│   ├── pinecone_knowledge_base.py    # Pinecone integration (KEEP)
│   ├── adaptive_proposal_writer.py   # Proposal generator (KEEP)
│   │
│   ├── compliance_frameworks.py      # Extended 37 frameworks (CONSOLIDATE with above?)
│   ├── priority_frameworks.py        # Duplicate of user_priority? (REMOVE)
│   │
│   └── legacy/                       # Original modules (ARCHIVE)
│       ├── parser.py
│       ├── chunking.py
│       ├── retrieval.py
│       └── ...
│
├── tests/                             # Consolidated test suite
│   ├── test_integrated_system.py     # Main integration test (KEEP)
│   ├── test_user_frameworks.py       # Test 10 frameworks (KEEP)
│   └── test_compliance_detection.py  # Test detection (CONSOLIDATE)
│
├── config/
│   ├── .env                           # API keys (Pinecone configured)
│   └── compliance_manifest.json      # Document manifest
│
├── docs/
│   ├── README.md                     # Main documentation
│   ├── HOW_IT_WORKS.md               # System overview
│   └── SETUP.md                      # Setup guide
│
├── examples/                          # Sample RFPs and outputs
│   └── sample_rfps/
│
├── scripts/                           # Utility scripts
│   ├── upload_to_pinecone.py        # Upload compliance docs
│   └── verify_compliance_docs.py     # Verify PDFs exist
│
└── .gitignore
```

## Actions to Take

### 1. Clean up tools/
- KEEP: Core 5 new modules (user_priority_frameworks, rfp_parser, compliance_engine, pinecone_knowledge_base, adaptive_proposal_writer)
- ARCHIVE: Move original modules to tools/legacy/
- REMOVE: priority_frameworks.py (duplicate of user_priority_frameworks)
- QUESTION: Should we keep compliance_frameworks.py (37 frameworks) or just use user_priority_frameworks.py (10 frameworks)?

### 2. Consolidate tests/
- KEEP: test_integrated_system.py (main test)
- KEEP: test_user_frameworks.py (focused test)
- MERGE: Combine other test files into test_compliance_suite.py

### 3. Move scripts
- MOVE: upload_compliance_to_pinecone.py → scripts/
- MOVE: verify_compliance_docs.py → scripts/

### 4. Remove old structure
- DELETE: dux_rfp_agent/ (empty structure)
- DELETE: kb/ (if not used)

### 5. Update imports
- Fix all import paths to use tools.module_name
- Update test imports

## Benefits
- Clear separation: tools/, tests/, config/, docs/, scripts/
- Follows repository convention (tools/ for modules)
- No duplicate code
- Easy to understand hierarchy
- Clean git tracking