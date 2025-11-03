# TOOL AUDITOR CHECKLIST

**Last Updated:** 2025-11-03
**Responsibility:** Security-auditor agent
**Frequency:** Quarterly (March, June, September, December)
**Next Audit:** 2025-12-03

---

## 🎯 Purpose

This checklist guides the **security-auditor agent** through quarterly tool governance audits to detect:
- Configuration mismatches (skills declared but not enabled)
- Tool duplication and naming collisions
- Orphaned tools (zero agent declarations)
- Priority order documentation gaps
- Deprecation candidates

**Output:** Governance audit report with metrics, issues found, and recommendations

---

## ✅ Section 1: Configuration Mismatch Audit

### 1.1 Skill Declaration vs Settings Verification

**Goal:** Find agents declaring skills not enabled in `.claude/settings.json`

**Manual Process:**
```bash
# Step 1: Extract all skills declared in agent YAML files
grep -r "^skills:" .claude/agents/*.md -A 20 | grep "  - " | sort | uniq > /tmp/declared_skills.txt

# Step 2: Extract enabled skills from settings
cat MARKETING_TEAM/.claude/settings.json | jq '.skills | keys' | grep -v '\[' | grep -v '\]' | tr -d ' ",' | sort > /tmp/enabled_skills.txt

# Step 3: Find mismatches (declared but not enabled)
comm -23 /tmp/declared_skills.txt /tmp/enabled_skills.txt
# Output shows skills declared but NOT enabled (CRITICAL ERROR)
```

**Checklist:**
- ☐ All skills declared in agent YAML exist in `.claude/skills/` folder
- ☐ All skills declared in agent YAML are enabled in team `.claude/settings.json`
- ☐ Document skills (pdf, pptx, docx, xlsx) status is correct
- ☐ No agents declare disabled skills (docx, xlsx)

**Expected Findings:**
- ✅ pdf, pptx skills: Declared AND enabled (correct)
- ❌ docx, xlsx skills: Declared but NOT enabled (CRITICAL - fix immediately)

**Remediation:**
- **Option A:** Enable skills in settings.json (test they work)
- **Option B:** Remove skill declarations from agents (use MCP instead)
- **Option C:** Selective (enable pdf/pptx, remove docx/xlsx declarations)

**Severity:** CRITICAL (breaks agents silently)

---

### 1.2 Orphaned Skill Detection

**Goal:** Find skills enabled but no agents use them

```bash
# Step 1: Get enabled skills
cat MARKETING_TEAM/.claude/settings.json | jq '.skills | keys' | grep -v '\[' | grep -v '\]' | tr -d ' ",' > /tmp/enabled_skills.txt

# Step 2: For each enabled skill, check if any agent declares it
while read skill; do
    if ! grep -r "$skill" .claude/agents/*.md > /dev/null; then
        echo "ORPHANED SKILL (enabled but unused): $skill"
    fi
done < /tmp/enabled_skills.txt
```

**Checklist:**
- ☐ All enabled skills have at least 1 agent using them
- ☐ Orphaned skills identified (enabled but no agents declare)
- ☐ Reason documented (reserved for future use, legacy, etc.)

**Severity:** MEDIUM (waste of resources, not critical)

---

## ✅ Section 2: Priority Order Documentation Audit

### 2.1 Dual-Capability Agents Verification

**Goal:** Verify agents with BOTH skill and MCP document priority order

**Agents to Audit (Dual Capabilities):**

| Agent | Dual Capability | Priority Documented? |
|-------|-----------------|---------------------|
| **analyst.md** | xlsx skill vs Google Sheets MCP | ☐ Check |
| **copywriter.md** | docx skill vs Google Docs MCP | ☐ Check |
| **pdf-specialist.md** | pdf skill vs Google Docs MCP | ☐ Check |
| **lead-gen-agent.md** | xlsx skill (if enabled) | ☐ Check |
| **seo-specialist.md** | xlsx skill (if enabled) | ☐ Check |
| **visual-designer.md** | canvas-design vs GPT-4o MCP | ☐ Check |

**Verification Steps:**

```bash
# For each agent, check if instructions document priority order
grep -A 50 "Priority" MARKETING_TEAM/.claude/agents/analyst.md
# Expected: Priority Order section with decision matrix

grep -A 50 "Method 1" MARKETING_TEAM/.claude/agents/analyst.md
grep -A 50 "Method 2" MARKETING_TEAM/.claude/agents/analyst.md
# Expected: Two methods listed with use cases
```

**Required Elements (check for each agent):**
- ☐ Lists BOTH methods (skill and MCP)
- ☐ Specifies which is PRIMARY (Method 1/RECOMMENDED)
- ☐ Explains WHEN to use each method (use cases)
- ☐ Notes current status (skill enabled/not enabled)
- ☐ Documents fallback logic (primary fails → fallback)

**Current Baseline:**
- ✅ pdf-specialist.md: Priority documented (pdf skill → MCP fallback)
- ✅ presentation-designer.md: Priority documented (pptx skill primary)
- ❌ analyst.md: Priority MISSING (add Google Sheets vs xlsx priority)
- ❌ copywriter.md: Priority MISSING (add Google Docs vs docx priority)
- ❌ lead-gen-agent.md: xlsx usage MISSING (document not enabled)
- ❌ seo-specialist.md: xlsx usage MISSING (document not enabled)

**Target:** 100% of dual-capability agents document priority

**Severity:** HIGH (causes confusion, agents may use wrong tool)

---

### 2.2 Fallback Logic Documentation

**Goal:** Verify agents document what happens when primary tool fails

**Check for:**
```markdown
**Fallback Logic:**
1. Try <primary tool> (explain why primary)
2. If primary fails: Try <fallback tool> (explain when/why)
3. If both fail: Raise clear error with troubleshooting steps
```

**Checklist:**
- ☐ All dual-capability agents document fallback strategy
- ☐ Error messages include troubleshooting (API key, settings, etc.)
- ☐ Fallback logic doesn't skip steps (always try primary first)

**Current Baseline:** 0% of agents document fallback logic

**Target:** 100%

**Severity:** HIGH (silent failures, poor user experience)

---

## ✅ Section 3: Orphaned Tool Detection

### 3.1 Find Tools with Zero Agent Declarations

**Goal:** Identify Python tools that no agents declare in YAML frontmatter

**Automated Detection:**
```bash
# Find all Python tools in tools/ folders
find . -name "*.py" -path "*/tools/*" -not -path "*/archive/*" > /tmp/all_tools.txt

# For each tool, check if ANY agent declares it
while read tool_path; do
    tool_name=$(basename "$tool_path" .py)

    # Search for tool name in agent YAML frontmatter
    if ! grep -r "tools:" .claude/agents/*.md -A 20 | grep -q "$tool_name"; then
        echo "ORPHANED TOOL: $tool_path (no agents declare this tool)"
    fi
done < /tmp/all_tools.txt
```

**Manual Verification:**
```bash
# Check if tool is referenced in agent instructions (not YAML)
grep -r "pdf_generator" .claude/agents/*.md
# Result: Found in pdf-specialist.md section header but NOT in YAML tools list
# Verdict: ORPHANED (misleading reference, should remove)
```

**Current Known Orphans:**
- ☐ `MARKETING_TEAM/tools/pdf_generator.py` - Zero declarations (section header mentions it but YAML doesn't declare)

**Checklist:**
- ☐ All Python tools in `*/tools/*.py` have at least 1 agent declaration
- ☐ Tools referenced in instructions are also declared in YAML frontmatter
- ☐ Orphaned tools marked as 🚫 DEPRECATED in TOOL_REGISTRY.md
- ☐ Orphaned tools have deprecation docstring

**Remediation:**
1. ✅ Mark tool as 🚫 DEPRECATED in TOOL_REGISTRY.md
2. ✅ Add deprecation docstring to tool file
3. ✅ Remove misleading references from agent instructions
4. ✅ Move to `archive/tools/deprecated/` after 30 days
5. ✅ Update CHANGELOG.md

**Severity:** MEDIUM (confusing, but not breaking)

---

## ✅ Section 4: Duplication Detection

### 4.1 Tool Name Collision Detection

**Goal:** Find tools with same filename across different teams

**Automated Detection:**
```bash
# Find duplicate tool names
find . -name "*.py" -path "*/tools/*" -not -path "*/archive/*" | \
  xargs basename -a | sort | uniq -d
```

**Current Known Collisions:**
- ☐ `router_tools.py` - Exists in both MARKETING_TEAM and QA_TEAM with different purposes

**Checklist:**
- ☐ No two tools have identical filenames (unless intentional shared tool)
- ☐ Naming collisions resolved (rename to team-specific names)
- ☐ Updated agent YAML declarations after renaming
- ☐ Updated imports in agent files

**Remediation:**
```bash
# Rename QA_TEAM tool to unique name
mv QA_TEAM/tools/router_tools.py QA_TEAM/tools/qa_router_tools.py

# Update test-orchestrator.md YAML
# Change: router_tools → qa_router_tools
```

**Severity:** HIGH (import confusion, wrong tool used)

---

### 4.2 Functional Overlap Detection

**Goal:** Find tools with similar/overlapping functionality

**Manual Review:**
```bash
# Search for tools with similar purposes
grep -r "email" */tools/*.py | grep "def " | grep -v "__"
# Result: send_email_with_attachment.py, send_deliverables_email.py
# Action: Audit both tools for overlap

grep -r "platform.*format" */tools/*.py | grep "def "
# Result: platform_formatters.py, router_tools.py (formatters section)
# Action: Audit for duplicate formatting logic
```

**Potential Overlaps to Audit:**
- ☐ `send_email_with_attachment.py` vs `send_deliverables_email.py` (both send emails)
- ☐ `platform_formatters.py` vs `router_tools.py` (both format social media content)
- ☐ Custom Perplexity tools vs Perplexity MCP (HYBRID strategy - intentional)

**Checklist:**
- ☐ No two tools provide identical functionality (unless MCP gap-filler + MCP)
- ☐ Overlapping tools have documented differentiation (why both exist)
- ☐ Deprecated duplicate tools removed

**Severity:** MEDIUM (code duplication, maintenance burden)

---

## ✅ Section 5: Canvas-Design Multi-Agent Usage Audit

**Goal:** Verify 4 agents using canvas-design have specialized use cases

**Agents Using canvas-design:**
1. ☐ visual-designer (PRIMARY OWNER - all design tasks)
2. ☐ pdf-specialist (one-page materials only)
3. ☐ social-media-manager (social graphics only)
4. ☐ presentation-designer (rare poster slides, pptx is primary)

**Verification:**
```bash
# Check each agent documents when to use canvas-design
grep -A 30 "canvas-design" MARKETING_TEAM/.claude/agents/visual-designer.md | grep "Use.*when"
grep -A 30 "canvas-design" MARKETING_TEAM/.claude/agents/pdf-specialist.md | grep "Use.*when"
# ... repeat for all 4 agents
```

**Required Elements:**
- ☐ **visual-designer:** Designated as PRIMARY OWNER (coordinates usage)
- ☐ **visual-designer:** Documents when other agents should defer
- ☐ **pdf-specialist:** Specifies "one-page materials only" use case
- ☐ **social-media-manager:** Specifies "social graphics only" use case
- ☐ **presentation-designer:** Specifies "rare poster slides" use case
- ☐ No overlap in use cases (each agent distinct purpose)

**Governance Rule:** Multi-agent skill use is ACCEPTABLE if:
1. ✅ PRIMARY OWNER designated (visual-designer)
2. ✅ Each agent documents SPECIALIZED use case
3. ✅ Agents defer to primary owner for complex cases
4. ✅ No overlap in use cases

**Severity:** LOW (acceptable multi-agent use, but needs documentation)

---

## ✅ Section 6: Usage Analysis

### 6.1 Tool Usage Frequency

**Goal:** Identify highly-used vs rarely-used tools

**Metrics:**
```bash
# Count agent declarations per tool
for tool in $(find . -name "*.py" -path "*/tools/*" -not -path "*/archive/*"); do
    tool_name=$(basename "$tool" .py)
    count=$(grep -r "$tool_name" .claude/agents/*.md | wc -l)
    echo "$count declarations: $tool_name"
done | sort -rn
```

**Categorize:**
- **Multi-agent tools** (3+ agents): upload_to_drive.py, send_email_with_attachment.py
- **Single-agent tools** (1 agent): test_generator.py, sora_video.py
- **Orphaned tools** (0 agents): pdf_generator.py

**Checklist:**
- ☐ Highly-used tools (3+ agents) documented in TOOL_REGISTRY.md
- ☐ Single-agent tools have clear ownership
- ☐ Orphaned tools marked for deprecation

**Severity:** INFO (informational, not critical)

---

### 6.2 MCP vs Custom Tool Ratio

**Goal:** Track MCP adoption vs custom tool usage

**Metrics:**
```bash
# Count MCP tool declarations
grep -r "mcp__" .claude/agents/*.md | wc -l

# Count custom Python tool declarations
grep -r "tools:" .claude/agents/*.md -A 20 | grep "  - " | grep -v "mcp__" | wc -l

# Calculate ratio
# Example: 150 MCP declarations / 50 custom = 75% MCP adoption
```

**Target:** >60% MCP adoption (MCP should be primary)

**Checklist:**
- ☐ MCP adoption rate calculated
- ☐ If <60%, identify opportunities to migrate custom tools to MCP
- ☐ Documented in GOVERNANCE_METRICS.md

**Severity:** INFO (governance health metric)

---

## ✅ Section 7: Deprecation Candidates

### 7.1 MCP Replacement Opportunities

**Goal:** Find custom tools that MCP now provides

**Check for:**
```bash
# Find email tools (Google Workspace MCP now handles)
grep -r "send.*email" */tools/*.py
# Result: send_email_with_attachment.py (justified - MCP can't do attachments)

# Find document tools (Google Workspace MCP now handles)
grep -r "create.*doc" */tools/*.py
# Result: pdf_generator.py (deprecated - pdf skill better)
```

**Checklist:**
- ☐ No custom tools duplicate MCP functionality (unless MCP gap-filler)
- ☐ MCP gap-fillers documented in TOOL_REGISTRY.md
- ☐ Deprecated tools have migration guide

**Current MCP Gap-Fillers (Justified):**
- ✅ `upload_to_drive.py` - MCP can't handle binary files
- ✅ `send_email_with_attachment.py` - MCP can't send attachments
- ✅ `openai_gpt4o_image.py` - Wrapped by marketing-tools MCP but also callable directly
- ✅ `sora_video.py` - MCP can't handle multi-clip stitching

**Severity:** MEDIUM (technical debt if not MCP gap-filler)

---

### 7.2 Unused Tools Detection

**Goal:** Find tools that haven't been used recently

**Manual Process:**
- ☐ Review git commit history for each tool (last modified date)
- ☐ Tools not modified in 6+ months may be unused
- ☐ Check agent definitions for declarations (orphaned?)
- ☐ Interview agents/users about tool usage

**Checklist:**
- ☐ All tools have been used/modified in last 6 months
- ☐ Unused tools investigated (why unused?)
- ☐ Deprecated if no longer needed

**Severity:** LOW (cleanup, not critical)

---

## ✅ Section 8: Documentation Quality

### 8.1 Tool Docstring Audit

**Goal:** Verify all tools have comprehensive docstrings

**Required Elements:**
```python
"""
Tool Name - One-line description

Purpose: Detailed explanation
Parameters: Type and description
Returns: Type and description
Raises: Error types
Usage Examples: Code examples
MCP Gap-Filler: If applicable
Used By: Agent list
"""
```

**Checklist:**
- ☐ All tools have docstrings with required elements
- ☐ Usage examples provided and correct
- ☐ MCP gap-fillers explicitly documented
- ☐ Agent list accurate (matches YAML declarations)

**Automated Check:**
```bash
# Find tools missing docstrings
for tool in $(find . -name "*.py" -path "*/tools/*" -not -path "*/archive/*"); do
    if ! head -20 "$tool" | grep -q '"""'; then
        echo "MISSING DOCSTRING: $tool"
    fi
done
```

**Severity:** MEDIUM (poor developer experience)

---

### 8.2 TOOL_REGISTRY.md Completeness

**Goal:** Verify all tools/skills/MCPs documented in registry

**Checklist:**
- ☐ All 19 custom tools in registry
- ☐ All 7 MCP servers in registry
- ☐ All 18 skills in registry
- ☐ Priority order documented for each capability
- ☐ Status accurate (Active/Deprecated/Config Required)
- ☐ Agents using each tool listed

**Automated Check:**
```bash
# Find tools not in registry
for tool in $(find . -name "*.py" -path "*/tools/*" -not -path "*/archive/*"); do
    tool_name=$(basename "$tool" .py)
    if ! grep -q "$tool_name" TOOL_REGISTRY.md; then
        echo "NOT IN REGISTRY: $tool_name"
    fi
done
```

**Severity:** HIGH (registry is single source of truth)

---

### 8.3 CHANGELOG.md Entries

**Goal:** Verify all tools have CHANGELOG.md entries

**Checklist:**
- ☐ All tools have creation date in CHANGELOG.md
- ☐ Deprecation events documented
- ☐ Major tool updates documented

**Severity:** LOW (historical tracking)

---

## 📊 Audit Report Template

**After completing checklist, generate report:**

```markdown
# Tool Governance Audit Report

**Date:** YYYY-MM-DD
**Auditor:** security-auditor agent
**Scope:** All 37 agents, 19 custom tools, 7 MCP servers, 18 skills

---

## Executive Summary

- **Critical Issues:** X found (configuration mismatches, orphaned tools)
- **High Priority Issues:** Y found (priority order missing, naming collisions)
- **Medium Priority Issues:** Z found (duplication, documentation gaps)
- **Low Priority Issues:** W found (cleanup, informational)

---

## Critical Issues (Fix Immediately)

### Issue #1: Skill Declaration Mismatch
**Severity:** CRITICAL
**Description:** Agents declare docx/xlsx skills but NOT enabled in settings.json
**Affected Agents:** analyst.md, copywriter.md, lead-gen-agent.md, seo-specialist.md
**Impact:** Agents fail silently when trying to use skills
**Recommendation:** Enable skills in settings OR remove declarations (use MCP)
**Remediation:** See AGENT_GOVERNANCE_RULES.md Section 5.2 (Option C recommended)

---

## High Priority Issues (Fix Within 1 Week)

### Issue #2: Priority Order Missing
**Severity:** HIGH
**Description:** 4 agents with dual capabilities don't document priority order
**Affected Agents:** analyst.md, copywriter.md, lead-gen-agent.md, seo-specialist.md
**Impact:** Agents don't know which tool to use first, confusion
**Recommendation:** Add priority documentation with decision matrix
**Remediation:** See AGENT_GOVERNANCE_RULES.md Section 2.1 templates

### Issue #3: Orphaned Tool
**Severity:** HIGH
**Description:** pdf_generator.py has zero agent declarations
**Affected Tools:** MARKETING_TEAM/tools/pdf_generator.py
**Impact:** Dead code, misleading section header in pdf-specialist.md
**Recommendation:** Remove tool, update section header
**Remediation:** Archive to archive/tools/deprecated/, update CHANGELOG.md

---

## Medium Priority Issues (Fix Within 1 Month)

(List medium issues)

---

## Low Priority Issues (Fix When Convenient)

(List low issues)

---

## Governance Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| **Skill Declaration Accuracy** | 60% (4/10 agents incorrect) | 100% | ❌ FAILING |
| **Priority Documentation Coverage** | 40% (2/5 dual-capability agents) | 100% | ❌ FAILING |
| **Tool Registry Coverage** | 95% (18/19 tools documented) | 100% | ⚠️ NEAR TARGET |
| **MCP Adoption Rate** | 65% (MCP vs custom) | >60% | ✅ PASSING |
| **Orphaned Tool Rate** | 5% (1/19 tools orphaned) | <5% | ⚠️ AT LIMIT |
| **Documentation Quality** | 85% (tools with complete docs) | 100% | ⚠️ IMPROVING |

---

## Recommendations

1. **Immediate:** Fix skill declaration mismatch (enable or remove)
2. **This Week:** Add priority documentation to 4 agents
3. **This Week:** Remove orphaned pdf_generator.py tool
4. **This Month:** Audit send_deliverables_email.py vs send_email_with_attachment.py overlap
5. **This Month:** Rename QA_TEAM/tools/router_tools.py to qa_router_tools.py
6. **Continuous:** Monitor MCP adoption rate, aim for 70%+

---

## Next Audit

**Date:** YYYY-MM-DD + 3 months
**Focus:** Verify issues resolved, measure metric improvements
```

---

## 🔗 Related Documentation

- **[TOOL_REGISTRY.md](TOOL_REGISTRY.md)** - Complete inventory (audit source)
- **[TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md)** - Priority hierarchy reference
- **[PRE_FLIGHT_CHECKS.md](PRE_FLIGHT_CHECKS.md)** - Creation checklist
- **[AGENT_GOVERNANCE_RULES.md](AGENT_GOVERNANCE_RULES.md)** - Compliance rules
- **[TOOL_CLEANUP_WORKFLOW.md](TOOL_CLEANUP_WORKFLOW.md)** - Deprecation process
- **[GOVERNANCE_METRICS.md](GOVERNANCE_METRICS.md)** - Metric tracking

---

**End of Checklist**
