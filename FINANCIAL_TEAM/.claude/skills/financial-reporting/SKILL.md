---
name: financial-reporting
description: Generate comprehensive financial reports including executive summaries, variance analysis, KPI dashboards, and board presentations. Use when creating financial reports, analyzing period-over-period performance, building dashboards, or preparing stakeholder communications with financial data and visualizations.
---

# Financial Reporting

## Overview

This skill enables creation of professional financial reports with analysis, visualizations, and insights for stakeholders at all levels.

## Core Capabilities

### 1. Executive Financial Summaries

Create concise, high-level financial summaries for executives.

**Example request:** "Create an executive summary of Q3 financial results"

### 2. Variance Analysis Reports

Analyze actual vs budget/forecast performance with detailed variance breakdowns and explanatory commentary.

**Example request:** "Analyze Q2 actuals vs budget and explain major variances"

### 3. Financial KPI Dashboards

Build visual dashboards tracking key metrics including SaaS metrics (MRR, CAC, LTV), profitability metrics (EBITDA, margins), and cash metrics (runway, FCF).

**Example request:** "Create a SaaS metrics dashboard for the board"

### 4. Period-over-Period Analysis

Compare performance across time periods (MoM, QoQ, YoY, TTM) with trend visualizations and growth rate analysis.

**Example request:** "Show revenue trends over the past 12 months with QoQ growth rates"

### 5. Board and Investor Reports

Prepare comprehensive reports for board meetings including business updates, financial performance, operational metrics, and strategic discussion topics.

**Example request:** "Create a board deck for our Q2 review"

## Report Formats

Deliver reports in multiple formats:
- **Excel/Spreadsheet:** Interactive dashboards with pivot tables and charts (use `xlsx` skill)
- **PDF Reports:** Professional documents for distribution
- **PowerPoint:** Board presentations with visual-heavy slides

## Visualization Best Practices

### Chart Selection
- **Trend over time:** Line charts
- **Comparison:** Bar charts
- **Variance:** Waterfall charts
- **Distribution:** Histograms

### Design Principles
- Use consistent color scheme (limit to 3-4 colors)
- Label axes clearly with data labels on key points
- Remove unnecessary chart elements
- Use green for revenue/positive, red for expenses
- Show negatives with parentheses: $(1,234)

## Common Reporting Patterns

**Revenue Bridge (Waterfall):** Show components of revenue change from period to period

**Cohort Analysis:** Track customer cohorts over time to understand retention patterns

**Rule of 40 Tracking:** Monitor growth rate + profit margin to assess company health

## Resources

### scripts/
- `variance_analyzer.py` - Automated variance analysis
- `dashboard_generator.py` - KPI dashboard builder
- `cohort_analyzer.py` - Customer cohort analysis

### references/
- `kpi_definitions.md` - Standard KPI formulas and definitions
- `reporting_templates.md` - Report structure templates

### assets/
- `executive_summary_template.pptx` - PowerPoint template
- `board_deck_template.pptx` - Board presentation template
- `dashboard_template.xlsx` - Excel dashboard template
