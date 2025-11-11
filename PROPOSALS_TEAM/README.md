# 🏆 Proposal Copilot - RAG-Powered Contract Winning System

**Target Sectors:** U.S. Federal Government | Private Enterprise
**Architecture:** Pinecone RAG + Claude Code Agents
**Win Rate Target:** 60%+ (vs. 45% industry average)

---

## 📁 Project Structure

```
proposal-copilot/
├── .env.example              # Pinecone & embeddings config
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── configs/
│   ├── rag.yaml             # RAG settings (Pinecone, chunking)
│   └── jurisdictions.yaml   # US_FED & ENTERPRISE requirements
├── prompts/
│   ├── system_master.md     # Core agent system prompt
│   ├── section_technical.md # Technical approach guidance
│   ├── section_management.md
│   ├── section_pastperf.md
│   └── orals_script.md
├── skills/                   # 7 core Python tools
│   ├── rag_client.py        # Pinecone RAG interface
│   ├── requirements.py      # Extract shall/must/will
│   ├── rfp_ingest.py        # Parse PDF/DOCX
│   ├── evidence_store.py    # Case studies, bios, certs
│   ├── formatting_checker.py
│   ├── accessibility_checker.py
│   └── producer.py          # PDF assembly & packaging
├── agents/                   # 7 specialized agents
│   ├── reader.md            # Parse RFPs, extract L/M
│   ├── planner.md           # Build outline + win themes
│   ├── composer.md          # Draft sections with RAG
│   ├── evidence_assembler.md
│   ├── checker.md           # QA: coverage, evidence, 508
│   ├── scorer.md            # Red team evaluation sim
│   └── producer.md          # Final packaging
├── kb/                       # Seed documents (FAR, SOC2, etc.)
└── few_shots/               # Training examples
    ├── us_federal/
    │   ├── sample_LM_excerpt.txt
    │   ├── expected_compliance_matrix.csv
    │   └── expected_outline.md
    └── enterprise/
        ├── sample_sow_scoring.txt
        └── expected_outline.md
```

---

## 🎯 What Makes This Different

### 1. **Compliance-First Architecture**
- **Never miss a requirement:** Automated extraction of all shall/must/will statements
- **Section M alignment:** Every paragraph mapped to evaluation criteria
- **95%+ coverage target:** Quality gate before submission

### 2. **RAG-Powered Authoritative Citations**
- **No hallucinated regulations:** All FAR, SOC2, HIPAA, NIST citations fetched from vetted knowledge base
- **≤25 word quotes:** With source titles and URLs
- **Jurisdiction filtering:** US_FED vs. ENTERPRISE contexts separated

### 3. **Evidence-Based Claims**
- **60%+ proof ratio:** Every value statement backed by metrics, certs, or case studies
- **Startup mode support:** Micro-pilot offers when past performance is thin
- **Neutral Past Performance:** FAR 15.305(a)(2)(iv) compliant language

### 4. **Answer-First Writing**
- **Direct compliance:** First sentence answers the requirement verbatim
- **So-What endings:** Last sentence gives evaluator the takeaway
- **Evaluator-friendly:** Mirror RFP structure, short paragraphs, clear tables

### 5. **Accessibility Built-In (Federal)**
- **508 compliance:** Alt text, tagging, reading order, bookmarks
- **5-item 508 note:** Auto-generated for federal proposals

---

## 🚀 Quick Start (6 Steps)

### 1. Setup Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Configure Pinecone
cp .env.example .env
# Edit .env with your PINECONE_API_KEY and PINECONE_INDEX
```

### 2. Load Knowledge Base

```python
from skills.rag_client import RAGClient

rag = RAGClient()

# Seed with core references (FAR, SOC2, HIPAA, NIST, etc.)
records = [
    {
        "id": "far-15-305-1",
        "text": "FAR 15.305(a)(2)(iv) states: If an offeror has no relevant past performance...",
        "metadata": {
            "title": "FAR 15.305 - Proposal Evaluation",
            "jurisdiction": "US",
            "standard": "FAR",
            "source_url": "https://acquisition.gov/far/15.305"
        }
    },
    # Add more records...
]

rag.upsert(records)
```

### 3. Ingest RFP

```python
from skills.rfp_ingest import read
from skills.requirements import extract

# Parse RFP document
data = read("path/to/rfp.pdf")

# Extract requirements (shall/must/will)
requirements = extract(data["instructions"])

# Result: List of {req_id, verbatim, must_or_should, section, eval_factor}
```

### 4. Run Agent Chain

**Use Claude Code's Task tool to invoke agents sequentially:**

1. **Reader** → Parse L/M, create compliance matrix
2. **Planner** → Build outline + 3-5 win themes
3. **Composer** → Draft sections with RAG citations
4. **Evidence Assembler** → Insert proof (cases, bios, certs)
5. **Checker** → Validate coverage ≥95%, evidence ≥60%, formatting
6. **(Optional) Scorer** → Red team evaluation simulation
7. **Producer** → Package PDFs with bookmarks, submit-ready

### 5. Review & Iterate

```bash
# Check quality metrics
Coverage: 48/50 musts (96%) ✅
Evidence: 54/85 claims (63.5%) ✅
Formatting: All checks passed ✅
508 Note: Included ✅

# Address gaps if any
```

### 6. Submit

Producer agent outputs:
- `Technical_Proposal.pdf` (with bookmarks, 508-compliant)
- `Price_Proposal.pdf` (if separate)
- `Compliance_Matrix.xlsx`
- `Annexes.zip` (resumes, certs, PPQs)
- `deliverables.json` (manifest with checksums)

---

## 📊 Sector-Specific Strategies

### 🏛️ U.S. Federal Government

**Key Success Factors:**
- **Compliance = 50% of the battle:** Non-compliance auto-rejects 50%+ of first-time bids
- **Section M worship:** Mirror evaluation criteria exactly
- **FAR 15.305 mastery:** Understand Best Value vs. LPTA, neutral past performance
- **Orals preparation:** 12-15 slides + Q&A bank for oral presentations

**Deliverables:**
1. Compliance Matrix (all shall/must/will tracked)
2. Executive Summary (1–2 pp)
3. Technical Approach (M-1)
4. Management Approach (M-2)
5. Past Performance (M-3) or Neutral statement
6. Transition (30/60/90)
7. Risk Register (RAID)
8. Security/Privacy Annex (NIST 800-171, CMMC, 508)
9. Orals Script + Q&A

**Compliance Watchouts:**
- FAR 19.7 / 52.219-14 → Subcontracting plan required
- 508 accessibility → Alt text, tagging, bookmarks
- Past performance → If none, use FAR 15.305(a)(2)(iv) neutral language

---

### 🏢 Private Enterprise

**Key Success Factors:**
- **ROI/TCO focus:** Business value scores 40% typically
- **Pilot de-risking:** 4-week POC with measurable KPIs
- **Security due diligence:** SOC2, ISO27001, CAIQ/SIG
- **Reference strength:** 3+ verifiable clients

**Deliverables:**
1. Executive Summary (outcomes-driven)
2. Technical/Pilot Plan (4-week POC)
3. Security & Compliance (SOC2, ISO, CAIQ, HIPAA-aligned)
4. Integration & Change Management
5. Past Performance (3+ case studies with metrics)
6. Commercials (pilot separate from full implementation)
7. Risk & Mitigation

**Compliance Watchouts:**
- HIPAA: Use "HIPAA-aligned" NOT "HIPAA-certified" (doesn't exist)
- SOC2: Type II > Type I; include report or roadmap
- DPA/SLA: Templates required
- References: Must be contactable and verifiable

---

## 🧠 Master System Prompt (Copy-Paste)

**Located at:** `prompts/system_master.md`

**Key Rules:**
1. **Compliance first** - Mirror RFP order/IDs
2. **Write to the score** - Section M (federal) or rubric (enterprise)
3. **Evidence every claim** - Proof callouts with metrics
4. **RAG discipline** - Quote ≤25 words, include title + link
5. **No legal advice** - Flag `[Human Review – Legal]` when needed
6. **Accessibility** - 508 note for federal
7. **Evaluator readability** - Answer-first, So-What endings

---

## 🛠️ Skills Reference (7 Tools)

### 1. `rfp_ingest.read(file_path)`
**Purpose:** Parse PDF/DOCX RFPs
**Returns:** `{sections, instructions, eval_factors, page_map}`

### 2. `requirements.extract(rfp_text)`
**Purpose:** Extract all shall/must/will requirements
**Returns:** `[{req_id, verbatim, must_or_should, section, eval_factor}]`

### 3. `rag.search(query, filters, k)`
**Purpose:** Fetch authoritative citations from knowledge base
**Returns:** `[{verbatim, title, source_url, jurisdiction, standard, score}]`

**Example:**
```python
rag.search("FAR 15.305 past performance",
           filters={"jurisdiction":"US", "standard":"FAR"},
           k=3)
```

### 4. `evidence.get(filters)`
**Purpose:** Retrieve case studies, resumes, certs from evidence store
**Returns:** `{case_studies: [...], bios: [...], certs: [...]}`

### 5. `formatting.check(doc_path, rules)`
**Purpose:** Validate page limits, fonts, margins, filenames
**Returns:** `{page_limit_ok, font_ok, margins_ok, filenames_ok, notes}`

### 6. `accessibility.check(pdf_path)`
**Purpose:** Validate 508 compliance (federal only)
**Returns:** `{alt_text_ok, tagged_ok, reading_order_ok, bookmarks_ok, hints}`

### 7. `producer.package(sections, matrix, annexes)`
**Purpose:** Assemble final PDFs with bookmarks and manifest
**Returns:** `{bundle: "deliverables.json", matrix: "compliance_matrix.csv"}`

---

## 🎓 Win Themes Framework

**Every proposal needs 3–5 win themes with this structure:**

```
Theme: "[Compelling headline]"
├── Capability → What you can do
├── Benefit → What it means for the client
├── Proof → Evidence (metric, cert, case study)
├── Risk Removed → What problem it solves
└── So-What → Evaluator takeaway
```

**Example (Federal):**
```
Theme: "Mission-Ready 24/7 Operations with Proven Uptime"
├── Capability: 24/7 NOC with <2min response SLA
├── Benefit: Continuous service availability
├── Proof: 99.99% uptime on DoD Contract ABC-123 (2022-2025)
├── Risk Removed: No service interruptions
└── So-What: Government can rely on uninterrupted mission support
```

---

## 📈 Quality Gates (Must Pass Before Submit)

### Compliance
- [ ] **Coverage ≥95%** of must requirements
- [ ] **Section M mapping** - Every paragraph ties to eval factor
- [ ] **Page limits** observed
- [ ] **Font/formatting** per instructions
- [ ] **Filenames** exact match to RFP

### Content
- [ ] **Evidence ratio ≥60%** - Most claims have proof
- [ ] **Answer-first** pattern throughout
- [ ] **So-What endings** on key sections
- [ ] **No generic language** - All customized
- [ ] **No typos/errors** - Clean copy

### Federal-Specific
- [ ] **508 note** included (5 items)
- [ ] **Alt text** on all images
- [ ] **Tagged PDF** for screen readers
- [ ] **Bookmarks** functional
- [ ] **FAR citations** accurate (RAG-verified)

### Enterprise-Specific
- [ ] **ROI/TCO** clearly demonstrated
- [ ] **Pilot plan** with KPIs (4 weeks typical)
- [ ] **SOC2/ISO** evidence attached
- [ ] **CAIQ/SIG** completed
- [ ] **HIPAA-aligned** language (not "certified")

---

## 🔍 Few-Shot Examples

### Federal Example
**Input:** `few_shots/us_federal/sample_LM_excerpt.txt`
- Section L & M structure
- Requirements extraction
- Evaluation factors

**Expected Output:**
- `expected_compliance_matrix.csv` (7 requirements tracked)
- `expected_outline.md` (9 sections, 3 win themes)

### Enterprise Example
**Input:** `few_shots/enterprise/sample_sow_scoring.txt`
- Healthcare cloud migration RFP
- 100-point scoring rubric
- Security due diligence requirements

**Expected Output:**
- `expected_outline.md` (7 sections, 3 win themes, pilot plan)

---

## 🚨 Common Pitfalls & How We Avoid Them

### Pitfall #1: Missing Requirements
**Problem:** 50%+ of first-time federal bids fail compliance
**Solution:** Automated `requirements.extract()` + compliance matrix tracking

### Pitfall #2: Invented Regulations
**Problem:** AI hallucinates FAR/HIPAA/NIST text
**Solution:** RAG-only citations, ≤25 word quotes, source URLs required

### Pitfall #3: Weak Evidence
**Problem:** Claims without proof aren't trusted
**Solution:** 60% evidence ratio gate, automated proof callout scanning

### Pitfall #4: Generic Content
**Problem:** Evaluators spot templated proposals instantly
**Solution:** Answer-first pattern, RFP ID mirroring, custom win themes

### Pitfall #5: Accessibility Failure
**Problem:** Federal proposals rejected for 508 non-compliance
**Solution:** `accessibility.check()` + auto-generated 508 note

### Pitfall #6: Late Submission
**Problem:** Even 1 minute late = auto-reject
**Solution:** Producer outputs 24+ hours early, submission checklist verification

---

## 📚 Knowledge Base Seeding (First-Time Setup)

**Priority 1: Federal Regulations**
- FAR 15.102 (Oral presentations)
- FAR 15.304 (Evaluation factors)
- FAR 15.305 (Proposal evaluation, past performance)
- FAR 15.506 (Debriefs)
- FAR 19.7 (Subcontracting plans)
- FAR 52.219-14 (Limitations on subcontracting)

**Priority 2: Standards & Compliance**
- SOC 2 Type I/II overview
- ISO 27001 certification requirements
- NIST 800-171 controls (DoD)
- CMMC levels and self-assessment
- FedRAMP authorization process
- Section 508 accessibility standards

**Priority 3: Industry-Specific**
- HIPAA Privacy and Security Rules (HHS summary)
- PCI-DSS requirements (payment processing)
- CAIQ/SIG questionnaire guidance
- GDPR/CCPA data privacy (if applicable)

**How to Add:**
```python
from skills.rag_client import RAGClient
rag = RAGClient()

# Chunk your PDFs into 900-token segments with 15% overlap
# Add metadata: jurisdiction, standard, source_url, year

rag.upsert(records)
```

---

## 🎯 Success Metrics

### Win Rates (Target)
- **Federal:** 50%+ (baseline: 50% fail compliance)
- **Enterprise:** 65%+ (personalization + pilot advantage)
- **Overall:** 60%+ across both sectors

### Quality Metrics
- **Compliance Rate:** 100% (no missed requirements)
- **Evidence Ratio:** ≥60% (most claims proven)
- **On-Time Submission:** 100%
- **508 Compliance:** 100% (federal)

### Efficiency Metrics
- **Time to Proposal:** <80 hours (vs. 120+ manual)
- **Agent Automation:** ~60% of work
- **Human Focus:** Strategy, proof, review (40%)

---

## 🔄 Workflow Summary

```
1. RFP Drop → Reader Agent
   ├── Parse PDF/DOCX
   ├── Extract Section L/M (federal) or scoring (enterprise)
   ├── Build compliance matrix (shall/must/will)
   └── Create submission checklist

2. Planning → Planner Agent
   ├── Analyze evaluation criteria
   ├── Generate 3-5 win themes
   ├── Build proposal outline (mirror RFP structure)
   └── Assign sections to owners

3. Drafting → Composer Agent
   ├── Draft Executive Summary (LAST)
   ├── Draft Technical, Management, Past Performance
   ├── Use RAG for FAR/compliance citations
   ├── Answer-first pattern + So-What endings
   └── Insert proof callout placeholders

4. Evidence → Evidence Assembler Agent
   ├── Gather case studies, bios, certs
   ├── Fill proof callouts with metrics
   ├── Validate all claims
   └── Flag gaps (startup mode → micro-pilot)

5. QA → Checker Agent
   ├── Coverage: ≥95% musts answered
   ├── Evidence: ≥60% claims proven
   ├── Formatting: page limits, fonts, margins
   ├── Accessibility: 508 note (federal)
   └── Generate gap list

6. (Optional) Red Team → Scorer Agent
   ├── Simulate evaluator
   ├── Score against rubric
   ├── Identify weaknesses
   └── Suggest improvements

7. Packaging → Producer Agent
   ├── Assemble PDFs with bookmarks
   ├── Add 508 tagging (federal)
   ├── Verify filenames
   ├── Create deliverables.json manifest
   └── Output submission checklist

8. Human Review & Submit
   ├── Final review by humans
   ├── Address any remaining gaps
   ├── Upload to portal (SAM.gov, email, etc.)
   └── Confirm receipt 24+ hours early
```

---

## 🆘 Troubleshooting

### "RAG returns no results"
- Check Pinecone index name in `.env`
- Verify knowledge base is seeded (run upsert)
- Adjust filters (e.g., remove `year_min` constraint)

### "Requirements extraction misses some"
- `requirements.py` uses regex for shall/must/will
- If RFP uses "offeror will" instead of "shall", add pattern
- Manual review of compliance matrix always recommended

### "Evidence ratio <60%"
- Not enough case studies/certs in evidence store
- Composer may need more specific proof guidance
- Consider startup mode: offer micro-pilot

### "508 check fails"
- Use Adobe Acrobat Pro to add alt text
- Export as "Tagged PDF" from Word/LibreOffice
- Run `accessibility.check()` again after fixes

### "Page limit exceeded"
- Composer drafts may be verbose
- Trim intro paragraphs, use tables instead of prose
- Move detail to annexes

---

## 📞 Next Steps

1. **Set up Pinecone:** Create index, add API key to `.env`
2. **Seed knowledge base:** Load FAR, SOC2, HIPAA, NIST docs
3. **Test with few-shots:** Run federal + enterprise examples
4. **Add your evidence:** Case studies, resumes, certs to `evidence_store.py`
5. **Drop in a real RFP:** Start with Reader agent, follow the chain

---

## 📄 License & Credits

**System Prompt & Architecture:** Inspired by federal BD best practices, SOC 2 audits, and 100+ proposal wins
**RAG Implementation:** Pinecone vector database + sentence-transformers
**Claude Code:** Anthropic's agent framework for orchestration

---

**Remember:**
- **Compliance first** - You can't win if you're disqualified
- **Evidence always** - Evaluators trust proof, not promises
- **Answer-first** - Make it easy for evaluators to score you high
- **Never invent law** - RAG or flag for human review

**Now go win that contract.** 🏆
