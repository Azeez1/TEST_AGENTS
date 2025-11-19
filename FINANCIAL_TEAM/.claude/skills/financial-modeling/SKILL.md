---
name: financial-modeling
description: Build comprehensive financial models including DCF valuation, NPV/IRR calculations, scenario analysis, sensitivity analysis, and pro forma statements. Use when building valuation models, analyzing investment opportunities, creating projection models, or performing what-if analyses with financial data.
---

# Financial Modeling

## Overview

This skill enables building sophisticated financial models for valuation, forecasting, and investment analysis using Python and Excel integration.

## Core Capabilities

### 1. Discounted Cash Flow (DCF) Analysis

Build DCF models to value companies and projects:

**Key components:**
- Free Cash Flow (FCF) projections (5-10 years)
- Terminal value calculation (Gordon Growth or Exit Multiple)
- Weighted Average Cost of Capital (WACC) calculation
- Discount cash flows to present value
- Sensitivity tables for key assumptions

**Example request:** "Build a DCF model for a SaaS company with $10M revenue growing 40% YoY"

**Implementation approach:**
```python
import pandas as pd
import numpy as np

def calculate_wacc(equity_weight, cost_of_equity, debt_weight, cost_of_debt, tax_rate):
    return (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - tax_rate))

def dcf_valuation(fcf_projections, terminal_growth_rate, wacc):
    # Discount projected cash flows
    pv_fcf = [fcf / (1 + wacc)**i for i, fcf in enumerate(fcf_projections, 1)]

    # Calculate terminal value
    terminal_fcf = fcf_projections[-1] * (1 + terminal_growth_rate)
    terminal_value = terminal_fcf / (wacc - terminal_growth_rate)
    pv_terminal = terminal_value / (1 + wacc)**len(fcf_projections)

    enterprise_value = sum(pv_fcf) + pv_terminal
    return enterprise_value, pv_fcf, pv_terminal
```

### 2. NPV and IRR Analysis

Calculate Net Present Value and Internal Rate of Return for capital projects:

**Use cases:**
- Capital budgeting decisions
- Project prioritization
- Investment opportunity evaluation

**Example request:** "Calculate NPV and IRR for a project with $500K initial investment and 5-year cash flows"

### 3. Scenario and Sensitivity Analysis

Model multiple scenarios and test assumption sensitivity:

**Scenario types:**
- Base case, best case, worst case
- Monte Carlo simulation for probabilistic outcomes
- Tornado charts for sensitivity ranking

**Example request:** "Create a three-scenario model (bull/base/bear) for revenue projections"

**Implementation approach:**
- Use data tables or loops to vary key assumptions
- Calculate impact on valuation/returns
- Visualize results with heatmaps or charts

### 4. Pro Forma Financial Statements

Build projected Income Statement, Balance Sheet, and Cash Flow Statement:

**Components:**
- Revenue build-up (units × price, or driver-based)
- Cost structure (COGS, OpEx)
- Working capital requirements
- Debt schedule and interest expense
- Three-statement integration

**Example request:** "Build 3-year pro forma financials for a manufacturing company"

### 5. LBO (Leveraged Buyout) Models

Model private equity transactions:

**Key elements:**
- Sources and uses of funds
- Debt schedule with multiple tranches
- Cash flow waterfall
- Exit valuation and returns (MOIC, IRR)

**Example request:** "Build an LBO model with 60% debt financing and 5-year hold"

## Output Formats

Financial models can be delivered in multiple formats:

### Excel/Spreadsheet (.xlsx)
Use the `xlsx` skill for Excel-based models with:
- Multiple sheets (Assumptions, Revenue Model, Financial Statements, Valuation)
- Formulas for dynamic calculations
- Formatted tables and charts
- Data validation for inputs

### Python/Pandas
Use DataFrames for:
- Programmatic model building
- Large dataset analysis
- Automated scenario generation
- Integration with data pipelines

### Visualizations
Create charts to communicate findings:
- Waterfall charts for value bridges
- Sensitivity tornado charts
- Scenario comparison charts
- DCF visualization showing components

## Best Practices

### Model Structure
- Separate assumptions from calculations
- Use consistent time periods (monthly/quarterly/annual)
- Color code: blue for inputs, black for formulas, green for links
- Include executive summary with key outputs

### Assumptions Documentation
- Document all key assumptions and sources
- Use reasonable, defensible numbers
- Provide ranges for uncertain inputs
- Reference market data where applicable

### Error Checking
- Verify three-statement balance (Cash Flow = BS Cash change)
- Check circular references
- Validate formula logic
- Test edge cases (negative growth, high leverage)

### Flexibility
- Build models to handle multiple scenarios easily
- Use named ranges and variables
- Make models auditable and easy to follow
- Include sensitivity toggles for key drivers

## Common Financial Modeling Patterns

### Revenue Build-Up
```python
# Units-based revenue model
units_sold = base_units * (1 + growth_rate)**year
price_per_unit = base_price * (1 + price_inflation)**year
revenue = units_sold * price_per_unit

# Or driver-based (e.g., SaaS)
arr = prior_arr + new_arr - churn_arr
monthly_revenue = arr / 12
```

### Working Capital
```python
# Changes in working capital impact cash flow
days_receivable = 45
days_payable = 30
days_inventory = 60

accounts_receivable = (revenue / 365) * days_receivable
accounts_payable = (cogs / 365) * days_payable
inventory = (cogs / 365) * days_inventory

nwc = accounts_receivable + inventory - accounts_payable
change_in_nwc = nwc - prior_nwc  # Cash outflow if positive
```

### Debt Schedule
```python
# Debt amortization schedule
for period in range(1, term + 1):
    interest_payment = beginning_balance * interest_rate

    if payment_type == "amortizing":
        principal_payment = pmt - interest_payment
    else:  # interest-only
        principal_payment = 0

    ending_balance = beginning_balance - principal_payment
```

## Resources

### scripts/
Contains Python utilities for common financial calculations:
- `dcf_calculator.py` - DCF model builder
- `scenario_analyzer.py` - Multi-scenario analysis
- `sensitivity_analysis.py` - Tornado charts and data tables

### references/
Contains financial modeling reference materials:
- `modeling_standards.md` - Industry best practices
- `formulas.md` - Common financial formulas and calculations

### assets/
Contains templates:
- `dcf_template.xlsx` - Starter DCF model template
- `3statement_template.xlsx` - Integrated financial statement template
