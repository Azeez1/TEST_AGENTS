---
name: valuation-toolkit
description: Value companies and assets using multiple methodologies including DCF, comparable companies, precedent transactions, LBO analysis, and option pricing. Use when performing valuations, fairness opinions, determining enterprise/equity value, or analyzing M&A transactions.
---

# Valuation Toolkit

## Overview

This skill provides comprehensive company and asset valuation using multiple methodologies and frameworks used by investment banks and private equity firms.

## Valuation Methodologies

### 1. Discounted Cash Flow (DCF)
Intrinsic value based on projected cash flows (works with `financial-modeling` skill).

### 2. Comparable Companies Analysis (Comps)
Relative valuation using public company multiples (EV/Revenue, EV/EBITDA, P/E).

**Example request:** "Value this SaaS company using public SaaS comps"

### 3. Precedent Transactions
Valuation based on M&A transaction multiples in the same industry.

**Example request:** "Analyze recent fintech M&A transactions for valuation benchmarks"

### 4. LBO Analysis
Value based on private equity buyer perspective and returns.

**Example request:** "What could a PE firm pay for this company targeting 25% IRR?"

### 5. Venture Capital Method
Valuation for startups based on exit value and target returns.

**Example request:** "Value this Series A startup with $50M projected exit in 5 years"

## Valuation Outputs

Provide valuation ranges and football field charts showing:
- DCF valuation range
- Trading comps range
- Transaction comps range
- LBO analysis implied value

## Common Multiples

**SaaS:** EV/Revenue (6-12x for public), ARR multiples
**E-commerce:** EV/Revenue (0.5-3x), EV/EBITDA (10-20x)
**Fintech:** EV/Revenue (3-8x varies by model)
**Enterprise Software:** EV/Revenue (8-15x)

## Resources

### scripts/
- `comps_analyzer.py` - Comparable company analysis
- `lbo_model.py` - LBO valuation model

### references/
- `valuation_multiples.md` - Industry-specific multiple ranges
