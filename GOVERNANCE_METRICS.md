# GOVERNANCE METRICS - Success Tracking

**Last Updated:** 2025-11-03
**Review Frequency:** Quarterly (security-auditor audit)
**Next Review:** 2025-12-03

---

## 🎯 Purpose

This document defines **measurable metrics** to track tool governance effectiveness across:
- Tool health (duplication, coverage, usage)
- Skill health (declaration accuracy, utilization)
- Governance processes (compliance, audits, deprecation)
- Conflict resolution (skill vs tool issues)

**Goal:** Data-driven governance decisions with clear success indicators

---

## 📊 Tool Health Metrics

### 1. Tool Registry Coverage

**Definition:** Percentage of active tools documented in TOOL_REGISTRY.md

**Formula:**
```
Tool Registry Coverage = (Tools in TOOL_REGISTRY.md / Total Active Tools) × 100%
```

**Measurement:**
```bash
# Count total active tools
total_tools=$(find . -name "*.py" -path "*/tools/*" -not -path "*/archive/*" | wc -l)

# Count tools in registry
registry_tools=$(grep -c "| \*\*.*\*\* |" TOOL_REGISTRY.md)

# Calculate coverage
echo "scale=2; ($registry_tools / $total_tools) * 100" | bc
```

**Targets:**
- **Current Baseline:** 95% (18/19 tools documented, pdf_generator.py orphaned)
- **Target:** 100% (all tools documented)
- **Critical Threshold:** <90% (urgent action required)

**Measured:** Quarterly (security-auditor audit)

---

### 2. Tool Duplication Rate

**Definition:** Percentage of tools with duplicate/overlapping functionality

**Formula:**
```
Duplication Rate = (Duplicate Tools / Total Tools) × 100%
```

**What Counts as Duplicate:**
- Same functionality, different names (e.g., send_email vs email_sender)
- Overlapping features without clear differentiation
- MCP exists but custom tool also exists (unless justified MCP gap-filler)

**Exclusions (NOT duplicates):**
- MCP gap-fillers (documented in TOOL_REGISTRY.md)
- HYBRID strategies (e.g., Perplexity custom tools + MCP fallback)
- Multi-agent skills with specialized use cases (e.g., canvas-design)

**Measurement:**
```markdown
# Manual audit during quarterly review
# Check TOOL_AUDITOR_CHECKLIST.md Section 4 (Duplication Detection)

# Example findings:
# - send_email_with_attachment.py (justified - MCP can't do attachments)
# - platform_formatters.py vs router_tools.py (potential overlap - audit needed)
```

**Targets:**
- **Current Baseline:** ~10% (2 potential overlaps out of 19 tools)
- **Target:** <5% (acceptable level - some justified duplicates)
- **Critical Threshold:** >15% (too much duplication)

**Measured:** Quarterly

---

### 3. MCP Adoption Rate

**Definition:** Percentage of tool operations using MCP servers vs custom Python tools

**Formula:**
```
MCP Adoption = (MCP Tool Declarations / Total Tool Declarations) × 100%
```

**Measurement:**
```bash
# Count MCP tool declarations across all agent YAML files
mcp_count=$(grep -r "mcp__" .claude/agents/*.md | wc -l)

# Count custom Python tool declarations
custom_count=$(grep -r "tools:" .claude/agents/*.md -A 20 | grep "  - " | grep -v "mcp__" | grep -v "skills:" | wc -l)

# Calculate adoption rate
total=$((mcp_count + custom_count))
echo "scale=2; ($mcp_count / $total) * 100" | bc
```

**Targets:**
- **Current Baseline:** ~65% (estimated - needs measurement)
- **Target:** >60% (MCP should be primary)
- **Stretch Goal:** >70% (excellent MCP adoption)

**Rationale:** Higher MCP adoption = less custom code to maintain, better cloud integration

**Measured:** Quarterly

---

### 4. Tool Usage Rate

**Definition:** Percentage of tools actively used by at least one agent

**Formula:**
```
Tool Usage = ((Total Tools - Orphaned Tools) / Total Tools) × 100%
```

**Measurement:**
```bash
# Find orphaned tools (zero agent declarations)
orphaned=0
for tool in $(find . -name "*.py" -path "*/tools/*" -not -path "*/archive/*"); do
    tool_name=$(basename "$tool" .py)
    if ! grep -r "$tool_name" .claude/agents/*.md > /dev/null; then
        orphaned=$((orphaned + 1))
    fi
done

total_tools=$(find . -name "*.py" -path "*/tools/*" -not -path "*/archive/*" | wc -l)

# Calculate usage rate
echo "scale=2; (($total_tools - $orphaned) / $total_tools) * 100" | bc
```

**Targets:**
- **Current Baseline:** 95% (18/19 tools used, 1 orphaned)
- **Target:** 100% (zero orphaned tools)
- **Critical Threshold:** <80% (too many unused tools)

**Measured:** Quarterly

---

### 5. Documentation Quality Score

**Definition:** Percentage of tools with comprehensive documentation (docstring + registry + changelog)

**Formula:**
```
Documentation Quality = (Tools with Complete Docs / Total Tools) × 100%
```

**What Counts as Complete:**
- ✅ Comprehensive docstring (purpose, parameters, returns, examples, MCP gap explanation if applicable)
- ✅ Entry in TOOL_REGISTRY.md (category, priority, status, agents using)
- ✅ Entry in CHANGELOG.md (date created, purpose)

**Measurement:**
```markdown
# Manual audit during quarterly review
# Check TOOL_AUDITOR_CHECKLIST.md Section 8 (Documentation Quality)

# For each tool, verify 3 elements:
# 1. Docstring completeness (head -50 tool.py)
# 2. Registry entry (grep tool_name TOOL_REGISTRY.md)
# 3. Changelog entry (grep tool_name CHANGELOG.md)
```

**Targets:**
- **Current Baseline:** ~85% (most tools have docs, some incomplete)
- **Target:** 100% (all tools fully documented)
- **Critical Threshold:** <70% (poor documentation)

**Measured:** Quarterly

---

## 🎨 Skill Health Metrics

### 6. Skill Declaration Accuracy

**Definition:** Percentage of agents with skill declarations that match enabled skills in `.claude/settings.json`

**Formula:**
```
Skill Accuracy = (Agents with Correct Declarations / Total Agents with Skills) × 100%
```

**What Counts as Incorrect:**
- Agent declares skill not enabled in settings.json (e.g., docx, xlsx)
- Agent declares skill that doesn't exist in `.claude/skills/` folder

**Measurement:**
```bash
# Step 1: Extract all skill declarations from agent YAML
grep -r "^skills:" .claude/agents/*.md -A 20 | grep "  - " | cut -d':' -f3 | tr -d ' ' | sort | uniq > /tmp/declared_skills.txt

# Step 2: Extract enabled skills from settings
cat MARKETING_TEAM/.claude/settings.json | jq '.skills | keys' | grep -v '\[' | grep -v '\]' | tr -d ' ",' | sort > /tmp/enabled_skills.txt

# Step 3: Find mismatches
comm -23 /tmp/declared_skills.txt /tmp/enabled_skills.txt > /tmp/mismatches.txt

# Step 4: Count agents with mismatches
mismatch_count=$(cat /tmp/mismatches.txt | wc -l)

# Step 5: Calculate accuracy
# (Manual - count agents declaring skills, subtract mismatches)
```

**Targets:**
- **Current Baseline:** 60% (4/10 agents incorrect - docx/xlsx not enabled)
- **Target:** 100% (zero mismatches)
- **Critical Threshold:** <80% (widespread configuration errors)

**Measured:** Quarterly

**Priority:** CRITICAL (breaks agents silently)

---

### 7. Skill Utilization Rate

**Definition:** Percentage of enabled skills actively used by at least one agent

**Formula:**
```
Skill Utilization = (Skills Used / Skills Enabled) × 100%
```

**Measurement:**
```bash
# Count enabled skills
enabled_skills=$(cat MARKETING_TEAM/.claude/settings.json | jq '.skills | keys | length')

# For each enabled skill, check if any agent declares it
used_count=0
for skill in $(cat MARKETING_TEAM/.claude/settings.json | jq -r '.skills | keys | .[]'); do
    if grep -r "$skill" .claude/agents/*.md > /dev/null; then
        used_count=$((used_count + 1))
    fi
done

# Calculate utilization
echo "scale=2; ($used_count / $enabled_skills) * 100" | bc
```

**Targets:**
- **Current Baseline:** Unknown (needs measurement)
- **Target:** >80% (most skills actively used)
- **Acceptable:** >60% (some skills may be reserves)

**Measured:** Quarterly

---

### 8. Priority Documentation Coverage

**Definition:** Percentage of agents with dual capabilities (skill + MCP) that document priority order

**Formula:**
```
Priority Coverage = (Agents with Priority Docs / Dual-Capability Agents) × 100%
```

**Dual-Capability Agents:**
- analyst.md (xlsx skill + Google Sheets MCP)
- copywriter.md (docx skill + Google Docs MCP)
- pdf-specialist.md (pdf skill + Google Docs MCP)
- lead-gen-agent.md (xlsx skill + Google Sheets MCP)
- seo-specialist.md (xlsx skill + Google Sheets MCP)
- visual-designer.md (canvas-design skill + GPT-4o MCP)

**What Counts as Priority Documentation:**
- ✅ Lists BOTH methods (skill and MCP)
- ✅ Specifies which is PRIMARY (Method 1/RECOMMENDED)
- ✅ Explains WHEN to use each (use cases, decision matrix)
- ✅ Notes current status (skill enabled/not enabled)
- ✅ Documents fallback logic (primary fails → fallback)

**Measurement:**
```bash
# Manual audit of 6 dual-capability agents
# Check agent instructions for priority documentation
# See AGENT_GOVERNANCE_RULES.md Section 2.1 for template
```

**Targets:**
- **Current Baseline:** 40% (2/5 agents have priority docs - pdf-specialist, presentation-designer)
- **Target:** 100% (all dual-capability agents document priority)
- **Critical Threshold:** <50% (most agents don't document priority)

**Measured:** Quarterly

**Priority:** HIGH (causes confusion, agents use wrong tool)

---

### 9. Fallback Logic Coverage

**Definition:** Percentage of agents with documented fallback strategy (skill fails → try MCP)

**Formula:**
```
Fallback Coverage = (Agents with Fallback Docs / Dual-Capability Agents) × 100%
```

**What Counts as Fallback Documentation:**
- ✅ Explains what happens if primary method fails
- ✅ Lists fallback method(s) in order
- ✅ Provides troubleshooting for when both fail

**Measurement:**
```bash
# Manual audit of dual-capability agents
# Search for "fallback" or "if.*fails" in instructions
grep -A 20 "fallback\|if.*fail" MARKETING_TEAM/.claude/agents/*.md
```

**Targets:**
- **Current Baseline:** 0% (no agents document fallback logic)
- **Target:** 100% (all agents explain fallback strategy)
- **Acceptable:** >80% (most agents have fallback docs)

**Measured:** Quarterly

**Priority:** HIGH (poor error handling without fallback docs)

---

## 🔄 Governance Process Metrics

### 10. Pre-Flight Compliance Rate

**Definition:** Percentage of new tools created that followed PRE_FLIGHT_CHECKS.md workflow

**Formula:**
```
Pre-Flight Compliance = (Tools with Pre-Flight Evidence / New Tools Created) × 100%
```

**Evidence of Pre-Flight:**
- ✅ Tool has justification comment in docstring (why MCP insufficient)
- ✅ Tool added to TOOL_REGISTRY.md within 1 day of creation
- ✅ Tool has CHANGELOG.md entry on creation date
- ✅ Agent YAML updated to declare tool

**Measurement:**
```bash
# Review git commits for new tools (quarterly)
# Check each new tool has all 4 evidence pieces
git log --since="3 months ago" --diff-filter=A --name-only | grep "tools/.*\.py$"

# For each new tool, verify:
# 1. Docstring has justification
# 2. TOOL_REGISTRY.md has entry (check git blame)
# 3. CHANGELOG.md has entry (check git blame)
# 4. Agent YAML declares tool
```

**Targets:**
- **Current Baseline:** Unknown (new metric - needs baseline)
- **Target:** 100% (all new tools follow pre-flight)
- **Critical Threshold:** <75% (governance not enforced)

**Measured:** Quarterly (retroactive)

---

### 11. Audit Frequency

**Definition:** Number of governance audits completed per quarter

**Formula:**
```
Audit Frequency = Audits Completed / Quarters Elapsed
```

**Measurement:**
```markdown
# Check TOOL_AUDITOR_CHECKLIST.md completion
# Count audit reports generated (search for "Audit Report" in CHANGELOG.md or docs/)
```

**Targets:**
- **Target:** 1 audit per quarter (minimum)
- **Stretch Goal:** 1.5 audits per quarter (mid-quarter spot checks)
- **Critical Threshold:** <0.75 audits per quarter (governance neglected)

**Measured:** Annually (review audit history)

---

### 12. Deprecation Speed

**Definition:** Average days from deprecation marking to archival

**Formula:**
```
Deprecation Speed = Total Days (Deprecation → Archival) / Number of Deprecations
```

**Measurement:**
```bash
# Review CHANGELOG.md for deprecation events
# Calculate days between "Deprecated" and "Archived" entries
grep -A 5 "Deprecated" CHANGELOG.md
grep -A 5 "Archived" CHANGELOG.md

# Example:
# pdf_generator.py: Deprecated 2025-11-03, Archived 2025-12-03 = 30 days
```

**Targets:**
- **Target:** 30 days (standard grace period per TOOL_CLEANUP_WORKFLOW.md)
- **Acceptable Range:** 25-35 days (minor variation acceptable)
- **Critical Threshold:** >45 days (deprecations lingering too long)

**Measured:** Quarterly

---

### 13. New Tool Justification Rate

**Definition:** Percentage of new tools created with written justification for why existing tools/MCPs insufficient

**Formula:**
```
Justification Rate = (New Tools with Justification / Total New Tools) × 100%
```

**What Counts as Justification:**
- ✅ Docstring explains why MCP insufficient (or N/A if no MCP)
- ✅ Docstring explains why skill insufficient (or N/A if no skill)
- ✅ Docstring notes MCP gap-filler status (if applicable)

**Measurement:**
```bash
# Review new tools created in past quarter
# Check docstrings for justification section
git log --since="3 months ago" --diff-filter=A --name-only | grep "tools/.*\.py$"

# For each new tool:
head -50 <new_tool>.py | grep -i "gap\|insufficient\|why\|reason"
```

**Targets:**
- **Current Baseline:** Unknown (new metric)
- **Target:** 100% (all new tools justify why needed)
- **Critical Threshold:** <80% (tools created without justification)

**Measured:** Quarterly

---

## 🚨 Conflict Resolution Metrics

### 14. Skill/Tool Conflicts Identified

**Definition:** Number of skill vs tool conflicts identified per quarter

**Measurement:**
```markdown
# From quarterly audit (TOOL_AUDITOR_CHECKLIST.md Section 2)
# Count conflicts found:
# - Skills declared but not enabled
# - Dual capabilities without priority docs
# - Orphaned tools
# - Naming collisions
```

**Baseline (2025-11-03 Audit):**
- 8 conflicts identified:
  1. PDF triple duplication (pdf skill, pdf-filler, canvas-design, pdf_generator.py)
  2. Document skills not enabled (docx, xlsx declared but not in settings)
  3. No MCP vs Skill priority order (analyst, copywriter, etc.)
  4. Canvas-design under-governed (4 agents, unclear ownership)
  5. Orphaned pdf_generator.py (zero declarations)
  6. Analyst/Lead-Gen/SEO xlsx ambiguity (skill not enabled)
  7. Copywriter docx vs Docs ambiguity (skill not enabled)
  8. No fallback logic documented (0% coverage)

**Targets:**
- **Q1 2026 Target:** Reduce to 4 conflicts (50% reduction)
- **Q2 2026 Target:** Reduce to 0 conflicts (100% resolved)
- **Ongoing:** <2 conflicts per quarter (low steady state)

**Measured:** Quarterly

---

### 15. Conflict Resolution Rate

**Definition:** Percentage of identified conflicts resolved within 1 quarter

**Formula:**
```
Resolution Rate = (Conflicts Resolved / Conflicts Identified) × 100%
```

**Measurement:**
```markdown
# Compare conflicts from previous audit to current audit
# Count how many were resolved (no longer appear in current audit)

# Example:
# Q4 2025: 8 conflicts identified
# Q1 2026: 4 conflicts identified (4 from Q4 resolved, 0 new)
# Resolution Rate: (4 / 8) × 100% = 50%
```

**Targets:**
- **Target:** >75% (most conflicts resolved within 1 quarter)
- **Stretch Goal:** 100% (all conflicts resolved)
- **Critical Threshold:** <50% (conflicts accumulating faster than resolved)

**Measured:** Quarterly

---

### 16. Orphaned Tool Removal Rate

**Definition:** Average days from orphan detection to removal (archival)

**Formula:**
```
Removal Rate = Total Days (Detection → Archival) / Number of Orphans Removed
```

**Measurement:**
```bash
# Review CHANGELOG.md for orphan deprecations
# Calculate days between detection (audit report) and archival

# Example:
# pdf_generator.py: Detected 2025-11-03, Archived 2025-12-03 = 30 days
```

**Targets:**
- **Target:** <30 days (per TOOL_CLEANUP_WORKFLOW.md)
- **Acceptable:** 25-35 days
- **Critical Threshold:** >45 days (orphans lingering)

**Measured:** Quarterly

---

## 📈 Governance Health Dashboard

**Summary view of all metrics (updated quarterly):**

| Category | Metric | Current | Target | Status |
|----------|--------|---------|--------|--------|
| **Tool Health** | Tool Registry Coverage | 95% (18/19) | 100% | ⚠️ NEAR TARGET |
| **Tool Health** | Tool Duplication Rate | 10% (2/19) | <5% | ⚠️ NEEDS IMPROVEMENT |
| **Tool Health** | MCP Adoption Rate | 65% (est.) | >60% | ✅ PASSING |
| **Tool Health** | Tool Usage Rate | 95% (18/19) | 100% | ⚠️ NEAR TARGET |
| **Tool Health** | Documentation Quality | 85% (est.) | 100% | ⚠️ IMPROVING |
| **Skill Health** | Skill Declaration Accuracy | 60% (6/10) | 100% | ❌ FAILING |
| **Skill Health** | Skill Utilization Rate | Unknown | >80% | 🔍 NEEDS MEASUREMENT |
| **Skill Health** | Priority Documentation Coverage | 40% (2/5) | 100% | ❌ FAILING |
| **Skill Health** | Fallback Logic Coverage | 0% (0/6) | 100% | ❌ FAILING |
| **Governance** | Pre-Flight Compliance | Unknown | 100% | 🔍 NEEDS BASELINE |
| **Governance** | Audit Frequency | 0 (new) | 1/quarter | 🔍 FIRST AUDIT PENDING |
| **Governance** | Deprecation Speed | N/A | 30 days | 🔍 NO DEPRECATIONS YET |
| **Governance** | Justification Rate | Unknown | 100% | 🔍 NEEDS BASELINE |
| **Conflicts** | Conflicts Identified | 8 (baseline) | 0 | 🔍 BASELINE SET |
| **Conflicts** | Resolution Rate | N/A (first audit) | >75% | 🔍 TRACK NEXT QUARTER |
| **Conflicts** | Orphan Removal Rate | 30 days (target) | <30 days | 🔍 ON TARGET |

**Legend:**
- ✅ PASSING - Meeting or exceeding target
- ⚠️ NEAR TARGET - Within 10% of target, improving
- ❌ FAILING - Below target, needs urgent action
- 🔍 NEEDS MEASUREMENT - Baseline not yet established

---

## 📊 Quarterly Audit Report Template

**Include these metrics in every quarterly audit:**

```markdown
# Governance Metrics Report - Q[X] YYYY

**Audit Date:** YYYY-MM-DD
**Auditor:** security-auditor agent
**Period:** [Start Date] to [End Date]

---

## Executive Summary

**Overall Governance Health:** [Excellent / Good / Fair / Poor]

**Key Highlights:**
- [Number] critical issues resolved
- [Number] new tools created (all followed pre-flight: Yes/No)
- [Number] deprecations completed
- MCP adoption increased from X% to Y%

**Priority Actions:**
1. [Action item 1 - severity, deadline]
2. [Action item 2 - severity, deadline]

---

## Metric Summary

### Tool Health
- Tool Registry Coverage: X% (target: 100%)
- Tool Duplication Rate: X% (target: <5%)
- MCP Adoption Rate: X% (target: >60%)
- Tool Usage Rate: X% (target: 100%)
- Documentation Quality: X% (target: 100%)

### Skill Health
- Skill Declaration Accuracy: X% (target: 100%) [CRITICAL if <80%]
- Skill Utilization Rate: X% (target: >80%)
- Priority Documentation Coverage: X% (target: 100%) [HIGH if <50%]
- Fallback Logic Coverage: X% (target: 100%)

### Governance Processes
- Pre-Flight Compliance: X% (target: 100%)
- Audit Frequency: X audits/quarter (target: 1)
- Deprecation Speed: X days (target: 30)
- Justification Rate: X% (target: 100%)

### Conflict Resolution
- Conflicts Identified: X (target: 0)
- Conflicts Resolved: X (resolution rate: X%)
- Orphan Removal Rate: X days (target: <30)

---

## Trends (Quarter-over-Quarter)

| Metric | Previous Quarter | This Quarter | Change |
|--------|------------------|--------------|--------|
| MCP Adoption | X% | Y% | +Z% ⬆️ |
| Skill Accuracy | X% | Y% | +Z% ⬆️ |
| Priority Docs | X% | Y% | +Z% ⬆️ |
| ... | ... | ... | ... |

**Trend Analysis:**
- [Improving trends - explain why]
- [Declining trends - explain why, action plan]

---

## Action Items from This Audit

| Priority | Action | Owner | Deadline | Status |
|----------|--------|-------|----------|--------|
| CRITICAL | Fix skill declaration mismatch | CTO | [Date] | ☐ Pending |
| HIGH | Add priority docs to 4 agents | Technical-writer | [Date] | ☐ Pending |
| MEDIUM | Audit email tool overlap | Security-auditor | [Date] | ☐ Pending |

---

## Next Audit

**Date:** [3 months from this audit]
**Focus Areas:** [Areas needing improvement based on this audit]
```

---

## 🔗 Related Documentation

- **[TOOL_REGISTRY.md](TOOL_REGISTRY.md)** - Tool inventory (data source for metrics)
- **[TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md)** - Policy for MCP adoption targets
- **[PRE_FLIGHT_CHECKS.md](PRE_FLIGHT_CHECKS.md)** - Pre-flight compliance checks
- **[AGENT_GOVERNANCE_RULES.md](AGENT_GOVERNANCE_RULES.md)** - Skill accuracy standards
- **[TOOL_AUDITOR_CHECKLIST.md](TOOL_AUDITOR_CHECKLIST.md)** - Audit process (generates metrics)
- **[TOOL_CLEANUP_WORKFLOW.md](TOOL_CLEANUP_WORKFLOW.md)** - Deprecation speed standards

---

**Next Metric Update:** 2025-12-03 (first quarterly audit)

---

**End of Metrics**
