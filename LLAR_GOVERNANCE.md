# LLAR 1-12 Governance Framework

**Version:** 1.0.0
**Last Updated:** 2025-12-14
**Configuration:** [LLAR_CONFIG.json](LLAR_CONFIG.json)

---

## Overview

LLAR (Layered Language Agent Reasoning) is a meta-governance framework that provides structured decision-making for the 59-agent multi-team system. It formalizes task routing, agent coordination, reflection checks, memory persistence, and conflict resolution.

**Key Principles:**
- Orchestrators govern teams (specialists stay lean)
- One agent, one role (no overlapping responsibilities)
- Reflect before output (catch issues early)
- Store what matters (preferences, goals, strategies)
- Explicit conflict resolution hierarchy

---

## Architecture

```
                    ┌─────────────────────┐
                    │     SUPERVISOR      │
                    │   (LLAR-12 Full)    │
                    │ Conflict Resolution │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ router-agent  │    │     cto       │    │test-orchestr. │
│  MARKETING    │    │ ENGINEERING   │    │    QA_TEAM    │
│  (18 agents)  │    │  (14 agents)  │    │  (4 agents)   │
│   LLAR 6-11   │    │   LLAR 6-11   │    │   LLAR 6-11   │
└───────────────┘    └───────────────┘    └───────────────┘
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  rfp-agent    │    │  cfo-agent    │    │sales-manager  │
│   PROPOSAL    │    │  FINANCIAL    │    │  SALES_TEAM   │
│  (1 agent)    │    │  (9 agents)   │    │  (7 agents)   │
│   LLAR 6-11   │    │   LLAR 6-11   │    │   LLAR 6-11   │
└───────────────┘    └───────────────┘    └───────────────┘
```

---

## LLAR-6: Task Routing Protocol

Before processing ANY task, orchestrators classify using routing modes:

### Routing Modes

| Mode | Description | Route To |
|------|-------------|----------|
| **direct_llm** | Conceptual or text-only tasks | Orchestrator handles directly |
| **single_tool** | Exactly one tool required | Single specialist |
| **multi_tool_chain** | Multiple tools/steps | Coordinate specialists |
| **ask_user** | Missing required inputs | Request clarification |

### Routing Decision Tree

```
                    ┌─────────────────┐
                    │   New Task      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Is conceptual/  │
                    │ text-only?      │
                    └────────┬────────┘
                        Yes/ \No
                          /   \
              ┌──────────▼┐   ┌▼──────────────┐
              │direct_llm │   │Requires tools?│
              │Handle self│   └───────┬───────┘
              └───────────┘       Yes/ \No
                                   /   \
                      ┌───────────▼┐   ┌▼───────────┐
                      │How many    │   │ask_user    │
                      │tools?      │   │Clarify     │
                      └──────┬─────┘   └────────────┘
                         1 / \2+
                          /   \
             ┌───────────▼┐   ┌▼───────────────┐
             │single_tool │   │multi_tool_chain│
             │1 specialist│   │Coordinate team │
             └────────────┘   └────────────────┘
```

### Examples by Team

**MARKETING_TEAM:**
- "What's our brand voice?" → `direct_llm` (router-agent answers)
- "Generate a product image" → `single_tool` (visual-designer)
- "Create a product launch campaign" → `multi_tool_chain` (copywriter → social-media-manager → visual-designer → email-specialist)
- "Write copy for [undefined audience]" → `ask_user`

**ENGINEERING_TEAM:**
- "Explain microservices" → `direct_llm` (cto answers)
- "Review this PR" → `single_tool` (code-reviewer)
- "Build authentication feature" → `multi_tool_chain` (backend-architect → frontend-developer → security-auditor → test-engineer)
- "Deploy to [unspecified environment]" → `ask_user`

**QA_TEAM:**
- "What's the testing strategy?" → `direct_llm` (test-orchestrator answers)
- "Generate unit tests for file.py" → `single_tool` (unit-test-agent)
- "Create comprehensive test suite" → `multi_tool_chain` (unit-test-agent → integration-test-agent → edge-case-agent → fixture-agent)
- "Test [undefined feature]" → `ask_user`

---

## LLAR-7: Agent Execution Rules

### One Agent One Role

Each specialist handles ONE responsibility:
- copywriter = writing (not design)
- visual-designer = images (not video)
- devops-engineer = infrastructure (not frontend)

**Violation:** Asking copywriter to also design graphics
**Solution:** Route design task to visual-designer

### Parallel Execution

When tasks are **independent** (no data dependencies):

```
Task A (research-agent): Research competitors
Task B (seo-specialist): Analyze keywords     [PARALLEL]
Task C (analyst): Review market data
```

**Benefits:** Faster execution, better resource utilization

### Sequential Execution

When outputs **depend** on prior results:

```
Task 1 (copywriter): Write blog post
   ↓ [WAIT]
Task 2 (editor): Review and refine
   ↓ [WAIT]
Task 3 (seo-specialist): Optimize for SEO
```

**Key:** Never parallelize dependent tasks

---

## LLAR-8: Reflection Protocol

Before returning final output, run reflection checks:

### Reflection Checks

| Check | Description | Action if Failed |
|-------|-------------|------------------|
| **Count** | Expected number of outputs produced | Retry (max 2) |
| **Atomicity** | Each output is independent and complete | Request completion |
| **Groundedness** | Claims traceable to source material | Flag for review |
| **Uniqueness** | No duplicate outputs | Deduplicate |
| **Format** | Output matches expected schema | Reformat |
| **Hallucination** | No fabricated facts or citations | Escalate immediately |

### Retry Logic

```
Attempt 1 → Check fails
    ↓
Retry with stricter instructions
    ↓
Attempt 2 → Check fails
    ↓
Fallback: Log reason + Escalate to user
```

**Retry Limit:** 2 attempts
**Fallback Required:** Yes, always have escape path

### Escalation Path

| Severity | Action |
|----------|--------|
| Minor (format, count) | Orchestrator handles |
| Moderate (groundedness) | Flag for review |
| Critical (hallucination) | Escalate to supervisor |

---

## LLAR-9: Memory System

### What to Store

| Category | Examples | Why Store |
|----------|----------|-----------|
| **Preferences** | Output format, communication style, quality threshold | Consistency across tasks |
| **Goals** | KPIs, objectives, constraints | Alignment with strategy |
| **Strategies** | Successful patterns, optimizations | Learn from experience |
| **Constraints** | Hard limits, soft preferences | Avoid repeated mistakes |
| **Traits** | Team strengths, preferred tools | Leverage capabilities |

### What to Ignore

| Category | Examples | Why Ignore |
|----------|----------|------------|
| **Temporary Tasks** | One-off requests | Not reusable |
| **Rewrite Requests** | "Make it shorter" iterations | Session-specific |
| **Ephemeral Details** | Today's meeting notes | Expires quickly |

### Team Memory Files

Each team maintains: `{TEAM}/memory/llar_memory.json`

```json
{
  "team": "MARKETING_TEAM",
  "preferences": {
    "output_format": "markdown",
    "quality_threshold": 8
  },
  "goals": {
    "primary": ["Increase brand awareness"],
    "kpis": ["Engagement rate > 5%"]
  },
  "strategies": {
    "successful_patterns": ["Visual-first content"],
    "failed_patterns": ["Text-heavy emails"]
  },
  "constraints": {
    "hard": ["Brand voice compliance"],
    "soft": ["Prefer short-form content"]
  },
  "traits": {
    "team_strengths": ["Visual content", "Social media"],
    "preferred_tools": ["GPT-4o images", "Google Workspace"]
  }
}
```

---

## LLAR-10: Evaluation Metrics

### Core Metrics

| Metric | Description | Threshold |
|--------|-------------|-----------|
| **Groundedness** | Claims traceable to sources | 95% |
| **Hallucination Rate** | Rate of fabricated content | < 2% |
| **Accuracy** | Correctness of outputs | 90% |
| **Precision** | Relevance of retrieved info | 85% |
| **Recall** | Coverage of required info | 80% |

### Enforcement

When threshold breached:
1. Tighten prompts
2. Strengthen reflection rules
3. Adjust retrieval parameters
4. Escalate if persistent

---

## LLAR-11: Tool Governance

### Integration with Existing Governance

LLAR extends [TOOL_REGISTRY.md](TOOL_REGISTRY.md) and [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md):

**Priority Order:**
```
MCP Server → Skill → Custom Tool → Create New
```

### Schema Enforcement

All tool calls must match defined schemas:
- Validate input parameters
- Verify output format
- Log schema violations

### Circuit Breaker

Prevents cascading failures:
- **Failure Threshold:** 3 consecutive failures
- **Reset Timeout:** 5 minutes
- **Action:** Route to fallback tool

### Rate Limiting

Protects resources:
- **Default:** 60 requests/minute per tool
- **Burst:** Allow 2x for 10 seconds
- **Action:** Queue excess requests

### Boundary Violations

Cross-team access without permission = ERROR:
- MARKETING cannot read ENGINEERING memory
- Exception: Supervisor can read all
- Exception: Explicit user permission

---

## LLAR-12: Conflict Resolution Hierarchy

### Resolution Priority Order

When conflicts arise, resolve using this hierarchy:

```
1. PERMISSIONS (highest authority)
       ↓
2. REFEREE (fact disputes)
       ↓
3. CONSENSUS (merge valid outputs)
       ↓
4. VOTING (select one output)
       ↓
5. ORCHESTRATOR (workflow ordering)
       ↓
6. SELF-HEALING (malfunction recovery)
```

### 1. Permissions (Authority Conflicts)

**When:** Agents have conflicting authority levels
**Resolution:** Higher authority wins
**Example:** Supervisor overrides team orchestrator

### 2. Referee (Fact Conflicts)

**When:** Agents disagree on facts
**Resolution:** Supervisor adjudicates
**Example:** Research-agent and analyst disagree on market size

### 3. Consensus (Merge Valid Outputs)

**When:** Multiple valid outputs exist
**Resolution:** Merge best elements
**Example:** Two copywriters write different angles → combine strengths

### 4. Voting (Select One Output)

**When:** Must choose single output
**Resolution:** Score by criteria, select highest
**Example:** Three design options → vote on best fit for brand

### 5. Orchestrator (Workflow Ordering)

**When:** Execution sequence disputed
**Resolution:** Orchestrator determines order
**Example:** Frontend vs backend first → orchestrator decides

### 6. Self-Healing (Malfunction Recovery)

**When:** Agent/tool failure
**Resolution:** Retry 2x → fallback → escalate
**Example:** API timeout → retry → use cached → alert user

### Supervisor Role (LLAR-12 Full)

The ROOT supervisor has **full LLAR-12 authority**:
- Adjudicates cross-team conflicts
- Final arbiter of fact disputes
- Merges cross-team outputs
- Determines cross-team workflow
- Monitors self-healing across all teams

### Team Orchestrator Role (LLAR 6-11)

Team orchestrators handle **intra-team** conflicts:
- Route using LLAR-6
- Coordinate using LLAR-7
- Reflect using LLAR-8
- Persist using LLAR-9
- Evaluate using LLAR-10
- Govern tools using LLAR-11
- Escalate to supervisor for cross-team issues

---

## Implementation Guide

### For Team Orchestrators

**At task start:**
1. Read `LLAR_CONFIG.json`
2. Read `{TEAM}/memory/llar_memory.json`
3. Classify task using routing protocol

**During execution:**
1. Apply one-agent-one-role
2. Parallelize independent tasks
3. Sequence dependent tasks

**Before returning:**
1. Run reflection checks
2. Retry if checks fail (max 2)
3. Escalate if still failing

**After completion:**
1. Update llar_memory.json with learnings
2. Log metrics for evaluation

### For Specialists

Specialists do NOT implement LLAR directly:
- Follow orchestrator instructions
- Report results to orchestrator
- Contribute learnings via orchestrator

---

## Related Documentation

- [TOOL_REGISTRY.md](TOOL_REGISTRY.md) - Tool inventory
- [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md) - Tool priority hierarchy
- [PRE_FLIGHT_CHECKS.md](PRE_FLIGHT_CHECKS.md) - Before creating tools
- [AGENT_GOVERNANCE_RULES.md](AGENT_GOVERNANCE_RULES.md) - Agent rules
- [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) - Memory configuration
- [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) - All 59 agents

---

## Changelog

### v1.0.0 (2025-12-14)
- Initial LLAR 1-12 framework
- 7 orchestrators enhanced (supervisor + 6 team leads)
- Team memory files created (6 llar_memory.json)
- Integration with existing governance
