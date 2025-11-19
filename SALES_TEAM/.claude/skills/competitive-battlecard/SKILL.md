---
name: competitive-battlecard
description: Research competitors and create battle cards with positioning, differentiation, objection handlers, and win strategies. Use when preparing for competitive deals, creating sales enablement materials, analyzing competitive threats, or positioning against alternatives.
---

# Competitive Battle Card

## Overview

This skill creates comprehensive competitive battle cards that arm sales teams with insights, positioning, and strategies to win against competitors.

## Core Capabilities

### 1. Competitor Research
Gather intelligence on competitors across multiple dimensions.

**Research areas:**
- Product features and capabilities
- Pricing and packaging
- Target market and ICP
- Go-to-market strategy
- Strengths and weaknesses
- Recent news and funding
- Customer reviews and sentiment

**Example request:** "Research Salesforce as our competitor in CRM space"

### 2. Competitive Positioning
Define how to position your solution vs competitors.

**Positioning framework:**
- **When they come up:** Typical scenarios
- **Their strengths:** What they're good at
- **Their weaknesses:** Where they fall short
- **Our advantages:** Why we're better
- **Proof points:** Evidence (case studies, metrics, reviews)

**Example request:** "Create positioning for us vs HubSpot in the SMB market"

### 3. Feature Comparison
Build side-by-side feature comparison matrices.

**Example request:** "Create a feature comparison: us vs Competitor X"

```
Feature                 | Us    | Competitor A | Competitor B
------------------------|-------|--------------|-------------
AI-powered insights     | ✓ Yes | ✓ Yes        | ✗ No
Custom reporting        | ✓ Yes | ⚠ Limited    | ✓ Yes
API access             | ✓ Yes | $ Paid add-on | ✓ Yes
Mobile app             | ✓ Yes | ✓ Yes        | ✗ No
Implementation time    | 2 weeks| 8-12 weeks   | 4 weeks
```

### 4. Win/Loss Analysis
Analyze patterns in competitive wins and losses.

**Track:**
- Win rate vs each competitor
- Common win reasons
- Common loss reasons
- Deal characteristics (size, industry, use case)
- Effective counter-strategies

**Example request:** "Analyze our wins/losses against Microsoft over past quarter"

### 5. Objection Handling
Prepare responses to competitor-specific objections.

**Common scenarios:**
- "Competitor X is cheaper"
- "Competitor Y has feature Z that you don't"
- "We're already using Competitor A"
- "Competitor B is more established"

**Example request:** "Create objection handlers for when prospects say we're more expensive than Competitor X"

## Battle Card Components

### Overview Section
```
Competitor: [Name]
Category: [Direct / Indirect]
When They Come Up: [Deal characteristics]
Quick Summary: [2-3 sentence overview]
```

### Strengths & Weaknesses
```
Their Strengths:
• Established brand recognition
• Large ecosystem of integrations
• Enterprise-focused sales team

Their Weaknesses:
• Complex, hard to use
• Expensive and rigid pricing
• Slow implementation (6+ months)
• Poor support for SMB
```

### Differentiation
```
Why We Win:
1. Faster time-to-value (2 weeks vs 3 months)
2. Modern, intuitive UI (NPS 72 vs their 45)
3. Flexible pricing (starts at $X vs $Y)
4. Superior customer support (response time, etc.)
```

### Competitive Positioning
```
What to Say:

"While [Competitor] is a solid choice for [their strength],
many of our customers chose us because [our advantage].

For example, [Customer X] switched from [Competitor] and saw [Result] in [Time].

The key differences are:
• [Differentiator 1 with proof]
• [Differentiator 2 with proof]
• [Differentiator 3 with proof]"
```

### Trap-Setting Questions
Questions that expose competitor weaknesses:

```
Discovery Questions:
• "How important is implementation speed to your timeline?"
  (If fast: highlight our 2-week vs their 3-month)

• "Will you need to integrate with [System X]?"
  (If yes: highlight our native integration vs their custom work)

• "What's your budget for training and onboarding?"
  (Expose their complex onboarding costs)
```

### Proof Points
```
Evidence to Use:
• G2 ratings: 4.7/5 vs their 4.1/5
• Case study: [Company] switched from [Competitor], saved $X, achieved [Metric]
• Review quote: "[Testimonial highlighting our advantage]"
• Analyst mention: Gartner noted [our strength]
```

## Competitive Intelligence Gathering

### Sources
- **Website & product:** Pricing, features, positioning
- **Review sites:** G2, Capterra, TrustRadius
- **Social media:** LinkedIn, Twitter for announcements
- **News:** Funding, acquisitions, leadership changes
- **Sales calls:** What prospects tell you
- **Former employees:** Hiring from competitors
- **Win/loss interviews:** Post-mortem with prospects

### Maintaining Battle Cards
- **Review quarterly:** Update with new intel
- **After wins/losses:** Capture learnings
- **Product launches:** Update when features change
- **Price changes:** Monitor pricing updates
- **Sales feedback:** Incorporate field insights

## Resources

### scripts/
- `competitor_tracker.py` - Monitor competitor changes
- `win_loss_analyzer.py` - Analyze competitive outcomes

### references/
- `competitor_intel.md` - Detailed competitor profiles
- `win_loss_patterns.md` - Historical win/loss analysis

### assets/
- `battlecard_template.pptx` - Battle card slide template
- `feature_comparison_template.xlsx` - Comparison matrix template
