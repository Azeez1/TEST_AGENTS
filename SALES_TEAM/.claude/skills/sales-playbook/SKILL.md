---
name: sales-playbook
description: Generate sales enablement content including call scripts, email templates, objection handlers, discovery questions, and sales methodologies. Use when creating sales training materials, building talk tracks, handling common objections, or standardizing sales processes.
---

# Sales Playbook

## Overview

This skill creates sales enablement content and playbooks that equip sales teams with proven scripts, templates, and methodologies to sell more effectively.

## Core Capabilities

### 1. Call Scripts and Talk Tracks
Create structured scripts for different sales scenarios.

**Types:**
- Cold calling scripts
- Discovery call frameworks
- Demo scripts and flow
- Closing scripts
- Follow-up sequences

**Example request:** "Create a cold call script for enterprise SaaS outreach"

**Structure:**
```
Opening (10 sec):
"Hi [Name], this is [Your Name] from [Company]. We help [Target Customer] solve [Problem]. Do you have 2 minutes?"

Value Prop (20 sec):
"We work with companies like [Similar Co] to [Specific Outcome]. For example, [Customer X] saw [Metric]."

Ask (10 sec):
"Would it make sense to explore if we could help you achieve similar results?"
```

### 2. Email Templates
Build email sequences for different stages.

**Campaign types:**
- Initial outreach (cold)
- Follow-up sequences
- Meeting requests
- Post-demo follow-up
- Proposal delivery
- Contract negotiation

**Example request:** "Create a 5-email outreach sequence for HR Tech buyers"

**Template:**
```
Subject: [Specific outcome] for [Their Company]

Hi [Name],

I noticed [Specific observation about their company].

Many [Title] at [Similar Companies] face [Problem]. They typically see:
• [Pain point 1]
• [Pain point 2]

We help [Customer Type] achieve [Outcome] through [Approach].
[Customer Example] saw [Specific Result] in [Timeframe].

Would it make sense to explore how we could help [Their Company] with [Goal]?

[Your Name]
```

### 3. Objection Handlers
Prepare responses to common objections.

**Common objections:**
- "Too expensive / no budget"
- "Happy with current solution"
- "Not the right time"
- "Need to think about it"
- "Can you send me information?"
- "Your competitor is cheaper"

**Example request:** "Create objection handlers for pricing concerns"

**Framework:**
```
Objection: "This is too expensive"

Response Pattern:
1. Acknowledge: "I understand budget is a concern..."
2. Clarify: "Help me understand - is it the total cost, or the timing?"
3. Reframe: "Let's look at the ROI... if this saves you $X/year..."
4. Evidence: "Company Y had similar concerns, but once they saw [outcome]..."
5. Options: "We have flexible payment terms / phased approach..."
```

### 4. Discovery Question Banks
Build comprehensive discovery question sets.

**Discovery areas:**
- Current state and challenges
- Goals and desired outcomes
- Decision process and timeline
- Budget and authority
- Success criteria
- Competitor evaluation

**Example request:** "Create discovery questions for selling marketing automation"

**Question types:**
```
Situation: "Walk me through your current process for..."
Problem: "What challenges do you face with..."
Implication: "How does that impact your team's ability to..."
Need-Payoff: "If you could [outcome], what would that mean for..."
```

### 5. Sales Methodologies
Document structured sales frameworks.

**Popular methodologies:**
- **MEDDIC:** Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, Champion
- **SPIN:** Situation, Problem, Implication, Need-Payoff
- **Challenger:** Teach, Tailor, Take Control
- **BANT:** Budget, Authority, Need, Timeline
- **SNAP:** Simple, iNvaluable, Align, Priorities

**Example request:** "Create a MEDDIC qualification checklist"

## Playbook Components

### Value Proposition Library
Organize value props by:
- Industry vertical
- Company size
- Buyer persona
- Use case
- Pain point

### Competitive Battle Cards
Quick reference for vs competitor positioning:
- When they come up
- How to position against them
- Key differentiators
- Proof points

### Customer Success Stories
Template for salespeople to reference:
- Customer name and industry
- Problem they faced
- Solution provided
- Results achieved (metrics)
- Quote from customer

## Sales Process Documentation

### Opportunity Stages
Define what qualifies a deal for each stage:

```
Stage 1 - Qualified Lead:
☐ BANT criteria met
☐ Pain identified
☐ Initial interest confirmed

Stage 2 - Discovery Complete:
☐ MEDDIC qualification done
☐ Decision criteria understood
☐ Champion identified

Stage 3 - Proposal:
☐ Solution designed
☐ Pricing approved
☐ Business case presented

... (continue for all stages)
```

### Exit Criteria Checklist
What must be true to advance to next stage.

## Resources

### scripts/
- `email_template_generator.py` - Personalized email creation
- `objection_handler_db.py` - Searchable objection handler database

### references/
- `discovery_frameworks.md` - Complete discovery question banks
- `sales_methodologies.md` - Detailed methodology guides
- `value_prop_library.md` - Industry-specific value propositions

### assets/
- `call_script_template.docx` - Call script template
- `email_templates.xlsx` - Email sequence library
- `battlecard_template.pptx` - Competitive battle card template
