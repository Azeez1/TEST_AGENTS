---
name: budget-planning
description: Create comprehensive budgets, forecasts, and financial plans including annual operating plans, departmental budgets, headcount planning, and rolling forecasts. Use when building budgets from scratch, creating departmental spending plans, planning headcount and hiring, or performing scenario planning.
---

# Budget Planning

## Overview

This skill enables building detailed financial budgets and forecasts for companies, departments, and projects with driver-based modeling and scenario planning.

## Core Capabilities

### 1. Annual Operating Plan (AOP)
Build company-wide annual budgets with revenue targets, expense budgets by department, headcount planning, and capital expenditure budgets.

**Example request:** "Create an annual operating plan for 2025"

### 2. Departmental Budgets
Create detailed budgets for individual departments (Sales, Marketing, R&D, G&A) with headcount, software/tools, travel, contractors, and other operating expenses.

**Example request:** "Build a Q1 marketing budget with breakdown by channel"

### 3. Headcount Planning
Model hiring plans with fully-loaded cost calculations including salary, benefits (30-35% of salary), equity, taxes, and ramp time assumptions.

**Example request:** "Plan hiring for 15 engineers over 4 quarters"

### 4. Rolling Forecasts
Update forecasts quarterly with actuals and refresh projections for next 12-18 months.

**Example request:** "Update our Q3 forecast with August actuals"

### 5. Scenario Planning
Model multiple budget scenarios (conservative, base, aggressive) with different growth and spending assumptions.

**Example request:** "Create three budget scenarios for different ARR growth rates"

## Budgeting Best Practices

- **Top-down + Bottom-up:** Start with revenue targets, build bottom-up budgets, reconcile
- **Driver-based:** Model budgets based on business drivers (customers, headcount, usage)
- **Monthly detail:** Budget by month for first year, quarterly for year 2+
- **Budget vs Forecast:** Budget is annual target, forecast is rolling best estimate
- **Include contingency:** Hold 5-10% unallocated for unexpected needs

## Resources

### scripts/
- `budget_builder.py` - Template-based budget generator
- `headcount_planner.py` - Hiring and compensation modeling

### assets/
- `aop_template.xlsx` - Annual operating plan template
- `dept_budget_template.xlsx` - Department budget template
