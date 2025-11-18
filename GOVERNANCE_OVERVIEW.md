# Governance Overview

This document serves as the **central navigation hub** for all governance documentation in TEST_AGENTS. Use this as your starting point to understand tool creation rules, skill declaration policies, and quality standards.

## Purpose

The governance system ensures:
- **Quality**: Tools, skills, and agents meet high standards
- **Consistency**: Standardized processes across all teams
- **Efficiency**: Avoid redundant tool creation
- **Maintainability**: Clear deprecation and cleanup workflows
- **Accountability**: Track success metrics and improvements

## Governance Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    GOVERNANCE WORKFLOW                        │
└─────────────────────────────────────────────────────────────┘

Before Creating Tool/Skill:
   ↓
[1] PRE_FLIGHT_CHECKS.md
   ↓ (Check if tool exists)
   ↓
[2] TOOL_USAGE_POLICY.md
   ↓ (Understand priority: MCP → Skill → Custom Tool)
   ↓
[3] AGENT_GOVERNANCE_RULES.md
   ↓ (Follow agent-specific rules)
   ↓
Create Tool/Skill
   ↓
[4] TOOL_REGISTRY.md
   ↓ (Register in inventory)
   ↓
Regular Operations
   ↓
[5] TOOL_AUDITOR_CHECKLIST.md (Quarterly)
   ↓ (Audit all tools/skills)
   ↓
[6] TOOL_CLEANUP_WORKFLOW.md
   ↓ (Deprecate unused tools)
   ↓
[7] GOVERNANCE_METRICS.md
   └─ (Track success metrics)
```

## The 7 Governance Documents

### [1] PRE_FLIGHT_CHECKS.md
**Purpose:** Pre-creation checklist to prevent redundant tools/skills

**When to Use:** BEFORE creating any new tool, skill, or custom solution

**Key Sections:**
- Pre-Flight Checklist (5 steps)
- Existing Inventory Check (TOOL_REGISTRY.md reference)
- Priority Hierarchy Validation (MCP → Skill → Custom)
- Documentation Requirements
- Registration Process

**Quick Reference:**
```
Step 1: Check TOOL_REGISTRY.md for existing solutions
Step 2: Verify MCP server availability
Step 3: Check available skills
Step 4: Validate genuine need
Step 5: Document and register
```

**Read This:** [PRE_FLIGHT_CHECKS.md](PRE_FLIGHT_CHECKS.md)

---

### [2] TOOL_USAGE_POLICY.md
**Purpose:** Define priority hierarchy for tool selection

**When to Use:** When deciding which tool/skill/MCP to use for a task

**Key Sections:**
- Priority Hierarchy (MCP → Skill → Custom Tool → Create New)
- Decision Matrix
- Rationale for Each Priority Level
- Exceptions and Edge Cases

**Priority Hierarchy:**
```
1. MCP Server (HIGHEST PRIORITY)
   - Pre-integrated, maintained by community
   - Examples: mcp__google-drive, mcp__gmail

2. Official Skills (SECOND PRIORITY)
   - Claude-maintained, .claude/skills/
   - Examples: pdf, pptx, docx, xlsx

3. Custom Tools (THIRD PRIORITY)
   - Team-created for specific workflows
   - Examples: identify_edge_cases, analyze_function

4. Create New Tool (LAST RESORT)
   - Only when nothing else exists
   - Requires full governance approval
```

**Read This:** [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md)

---

### [3] AGENT_GOVERNANCE_RULES.md
**Purpose:** Agent-specific rules and skill declaration policies

**When to Use:** When creating agent definitions or managing skills

**Key Sections:**
- Rule 1: Skill Declaration Standard (YAML frontmatter)
- Rule 2: Priority Hierarchy (MCP → Skill → Custom)
- Rule 3: Configuration Status (which skills enabled/disabled)
- Rule 4: Exceptions and Overrides
- Rule 5: Enforcement and Compliance

**Skill Declaration Format:**
```yaml
---
name: agent-name
skills:
  - skill-name-1
  - skill-name-2
tools:
  - mcp__service__tool-name
capabilities:
  - Capability 1
  - Capability 2
---
```

**Read This:** [AGENT_GOVERNANCE_RULES.md](AGENT_GOVERNANCE_RULES.md)

---

### [4] TOOL_REGISTRY.md
**Purpose:** Complete inventory of all tools, skills, and MCPs

**When to Use:**
- Before creating new tools (check if exists)
- Reference available tools for agents
- Understand tool capabilities and usage

**Key Sections:**
- MCP Servers (Google Drive, Gmail, Google Sheets, etc.)
- Official Skills (pdf, pptx, docx, xlsx, etc.)
- Custom Tools by Team
  - MARKETING_TEAM tools
  - QA_TEAM tools
  - ENGINEERING_TEAM tools
- Document Generation Skills (detailed)
- UGC Video Workflow (Veo/Sora integration)

**Categories:**
- **Document Generation:** pdf, pptx, docx, xlsx
- **Communication:** gmail, google-drive
- **Development:** Custom QA tools, ENGINEERING tools
- **Marketing:** UGC video, visual design, content creation
- **Research:** Perplexity, Bright Data

**Read This:** [TOOL_REGISTRY.md](TOOL_REGISTRY.md)

---

### [5] TOOL_AUDITOR_CHECKLIST.md
**Purpose:** Quarterly audit workflow for all tools and skills

**When to Use:** Every quarter (Q1, Q2, Q3, Q4)

**Key Sections:**
- Audit Schedule (quarterly)
- Audit Checklist (usage review, quality assessment, deprecation candidates)
- Audit Report Template
- Action Items and Remediation
- Success Metrics

**Audit Checklist:**
```
□ Review all tools in TOOL_REGISTRY.md
□ Check usage logs for each tool
□ Identify unused tools (0 usage in 90 days)
□ Assess quality and performance
□ Document deprecation candidates
□ Update TOOL_REGISTRY.md
□ Generate GOVERNANCE_METRICS.md report
```

**Read This:** [TOOL_AUDITOR_CHECKLIST.md](TOOL_AUDITOR_CHECKLIST.md)

---

### [6] TOOL_CLEANUP_WORKFLOW.md
**Purpose:** Deprecation process for unused/outdated tools

**When to Use:** When removing tools, skills, or custom solutions

**Key Sections:**
- Deprecation Criteria (0 usage, superseded, low quality)
- Deprecation Workflow (5-step process)
- Communication Plan
- Archive Process
- Migration Guide (if replacement exists)

**Deprecation Workflow:**
```
Step 1: Identify deprecation candidates
Step 2: Notify stakeholders (teams using the tool)
Step 3: Provide migration path (if applicable)
Step 4: Archive tool definition and documentation
Step 5: Remove from TOOL_REGISTRY.md and agent definitions
```

**Read This:** [TOOL_CLEANUP_WORKFLOW.md](TOOL_CLEANUP_WORKFLOW.md)

---

### [7] GOVERNANCE_METRICS.md
**Purpose:** Track success metrics and improvements

**When to Use:**
- After quarterly audits
- When measuring governance effectiveness
- For stakeholder reporting

**Key Sections:**
- Success Metrics (tool usage, redundancy reduction, agent performance)
- Quarterly Reports
- Trends and Insights
- Improvement Recommendations

**Key Metrics:**
```
- Tool Inventory Size (trending down = good)
- Tool Usage Rate (% of tools actively used)
- Redundancy Rate (% of duplicate tools)
- Agent Performance (success rate, quality scores)
- Governance Compliance (% agents following rules)
```

**Read This:** [GOVERNANCE_METRICS.md](GOVERNANCE_METRICS.md)

---

## Quick Decision Tree

### "Should I create a new tool?"

```
START
  ↓
Does this functionality exist in an MCP server?
  ├─ YES → Use MCP server (STOP)
  └─ NO → Continue
       ↓
Does this functionality exist in an official skill?
  ├─ YES → Use skill (STOP)
  └─ NO → Continue
       ↓
Does this functionality exist as a custom tool in TOOL_REGISTRY.md?
  ├─ YES → Use custom tool (STOP)
  └─ NO → Continue
       ↓
Is this a one-time task or reusable functionality?
  ├─ ONE-TIME → Don't create tool, do manually (STOP)
  └─ REUSABLE → Continue
       ↓
Does this benefit multiple agents or just one?
  ├─ JUST ONE → Consider inline implementation (STOP)
  └─ MULTIPLE → Continue
       ↓
Have you completed PRE_FLIGHT_CHECKS.md?
  ├─ NO → Complete checklist first
  └─ YES → CREATE NEW TOOL
            ↓
            Register in TOOL_REGISTRY.md
            ↓
            Document in agent definitions
            ↓
            DONE
```

## Common Governance Scenarios

### Scenario 1: I need to send emails
**Answer:** Use MCP server `mcp__gmail__send_email`

**Why:** MCP servers have HIGHEST priority (TOOL_USAGE_POLICY.md)

**See:**
- [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md) - Priority hierarchy
- [TOOL_REGISTRY.md](TOOL_REGISTRY.md) - MCP servers section

---

### Scenario 2: I need to generate a PDF
**Answer:** Use official skill `pdf`

**Why:** Official skills have SECOND priority

**See:**
- [AGENT_GOVERNANCE_RULES.md](AGENT_GOVERNANCE_RULES.md) - Skill declaration
- [TOOL_REGISTRY.md](TOOL_REGISTRY.md) - Document generation section

---

### Scenario 3: I need to identify edge cases in QA
**Answer:** Use custom tool `identify_edge_cases`

**Why:** Custom tool exists in TOOL_REGISTRY.md

**See:**
- [TOOL_REGISTRY.md](TOOL_REGISTRY.md) - QA_TEAM custom tools
- [QA_TEAM/README.md](QA_TEAM/README.md) - Usage examples

---

### Scenario 4: I need a tool that doesn't exist
**Answer:** Complete [PRE_FLIGHT_CHECKS.md](PRE_FLIGHT_CHECKS.md) first

**Process:**
1. Check TOOL_REGISTRY.md (confirm it doesn't exist)
2. Validate genuine need (not one-time use)
3. Design tool specification
4. Create tool
5. Register in TOOL_REGISTRY.md
6. Document in agent definitions

**See:**
- [PRE_FLIGHT_CHECKS.md](PRE_FLIGHT_CHECKS.md) - Complete checklist
- [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md) - Priority hierarchy

---

### Scenario 5: Quarterly audit is due
**Answer:** Follow [TOOL_AUDITOR_CHECKLIST.md](TOOL_AUDITOR_CHECKLIST.md)

**Process:**
1. Review all tools in TOOL_REGISTRY.md
2. Check usage logs (identify 0-usage tools)
3. Assess quality and performance
4. Identify deprecation candidates
5. Generate audit report
6. Update GOVERNANCE_METRICS.md

**See:**
- [TOOL_AUDITOR_CHECKLIST.md](TOOL_AUDITOR_CHECKLIST.md) - Audit workflow
- [GOVERNANCE_METRICS.md](GOVERNANCE_METRICS.md) - Metrics tracking

---

## Enforcement and Compliance

### Who Enforces Governance?
- **Agents:** Follow governance rules in their definitions
- **supervisor:** Verifies cross-team compliance
- **Quarterly Audits:** Systematic review (TOOL_AUDITOR_CHECKLIST.md)
- **Developers:** Responsible for following PRE_FLIGHT_CHECKS.md

### How is Compliance Measured?
See [GOVERNANCE_METRICS.md](GOVERNANCE_METRICS.md):
- Tool usage rate (% of tools actively used)
- Redundancy rate (% of duplicate tools)
- Agent compliance rate (% following skill declaration rules)
- Quarterly audit completion rate

### What Happens When Rules Are Violated?
1. **Detection:** Quarterly audit identifies violations
2. **Notification:** Team notified via audit report
3. **Remediation:** 30-day window to fix issues
4. **Cleanup:** Tools/skills removed if not fixed (TOOL_CLEANUP_WORKFLOW.md)

---

## Governance by Role

### For Agents
**Read:**
- [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md) - Priority hierarchy
- [AGENT_GOVERNANCE_RULES.md](AGENT_GOVERNANCE_RULES.md) - Skill declaration rules
- [TOOL_REGISTRY.md](TOOL_REGISTRY.md) - Available tools/skills

**Follow:**
- Declare skills in YAML frontmatter
- Use MCP servers first, then skills, then custom tools
- Never create duplicate tools

---

### For Developers
**Read:**
- [PRE_FLIGHT_CHECKS.md](PRE_FLIGHT_CHECKS.md) - Pre-creation checklist
- [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md) - Priority hierarchy
- [TOOL_REGISTRY.md](TOOL_REGISTRY.md) - Existing tools

**Follow:**
- Complete pre-flight checks before creating tools
- Register all new tools in TOOL_REGISTRY.md
- Document tools in agent definitions

---

### For Auditors
**Read:**
- [TOOL_AUDITOR_CHECKLIST.md](TOOL_AUDITOR_CHECKLIST.md) - Audit workflow
- [TOOL_CLEANUP_WORKFLOW.md](TOOL_CLEANUP_WORKFLOW.md) - Deprecation process
- [GOVERNANCE_METRICS.md](GOVERNANCE_METRICS.md) - Metrics tracking

**Follow:**
- Conduct quarterly audits (Q1, Q2, Q3, Q4)
- Generate audit reports
- Update GOVERNANCE_METRICS.md
- Manage deprecation workflow

---

### For Maintainers
**Read:**
- ALL governance documents
- Especially [GOVERNANCE_METRICS.md](GOVERNANCE_METRICS.md) for trends

**Follow:**
- Review governance effectiveness quarterly
- Update policies as needed
- Ensure compliance across all teams

---

## Related Documentation

**Core System:**
- [claude.md](claude.md) - Repository navigation
- [GETTING_STARTED.md](GETTING_STARTED.md) - Quick start guide
- [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) - All agents reference

**Governance (You Are Here):**
- [GOVERNANCE_OVERVIEW.md](GOVERNANCE_OVERVIEW.md) - This document
- [PRE_FLIGHT_CHECKS.md](PRE_FLIGHT_CHECKS.md) - Pre-creation checklist
- [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md) - Priority hierarchy
- [AGENT_GOVERNANCE_RULES.md](AGENT_GOVERNANCE_RULES.md) - Agent rules
- [TOOL_REGISTRY.md](TOOL_REGISTRY.md) - Tool inventory
- [TOOL_AUDITOR_CHECKLIST.md](TOOL_AUDITOR_CHECKLIST.md) - Audit workflow
- [TOOL_CLEANUP_WORKFLOW.md](TOOL_CLEANUP_WORKFLOW.md) - Deprecation process
- [GOVERNANCE_METRICS.md](GOVERNANCE_METRICS.md) - Success metrics

**Other:**
- [GLOSSARY.md](GLOSSARY.md) - Terms and definitions
- [FAQ.md](FAQ.md) - Common questions
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Debugging guide

---

## Summary

This governance system ensures:
1. **No duplicate tools** - Check TOOL_REGISTRY.md first
2. **Consistent priorities** - MCP → Skill → Custom Tool
3. **Regular audits** - Quarterly reviews (TOOL_AUDITOR_CHECKLIST.md)
4. **Clean deprecation** - Clear removal process (TOOL_CLEANUP_WORKFLOW.md)
5. **Measurable success** - Track metrics (GOVERNANCE_METRICS.md)

**Start Here:**
- New to governance? Read [PRE_FLIGHT_CHECKS.md](PRE_FLIGHT_CHECKS.md)
- Need a tool? Check [TOOL_REGISTRY.md](TOOL_REGISTRY.md)
- Creating an agent? See [AGENT_GOVERNANCE_RULES.md](AGENT_GOVERNANCE_RULES.md)
- Running an audit? Follow [TOOL_AUDITOR_CHECKLIST.md](TOOL_AUDITOR_CHECKLIST.md)

**Questions?** See [FAQ.md](FAQ.md) or [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
