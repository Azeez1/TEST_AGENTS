---
name: tax-compliance
description: Calculate taxes, ensure compliance, optimize tax strategies, and prepare tax filings for corporate income tax, sales tax, payroll tax, and international tax. Use when calculating tax liabilities, preparing tax returns, analyzing tax implications of transactions, or optimizing tax strategies.
---

# Tax Compliance

## Overview

This skill provides tax calculation, compliance checking, and optimization strategies for corporate taxation.

## Core Capabilities

### 1. Corporate Income Tax
Calculate federal and state income tax liabilities, estimated tax payments, and tax provision accounting.

**Example request:** "Calculate our Q3 tax provision"

### 2. Sales Tax / VAT
Determine sales tax obligations, nexus analysis, and multi-state tax calculations.

**Example request:** "Do we have sales tax nexus in Texas?"

### 3. Payroll Tax
Calculate employer payroll tax obligations (FICA, FUTA, SUTA, unemployment).

**Example request:** "Calculate payroll taxes for $500K monthly payroll"

### 4. International Tax
Handle transfer pricing, withholding tax, permanent establishment, and tax treaty analysis.

**Example request:** "Analyze tax implications of opening UK subsidiary"

### 5. Tax Optimization
Identify tax-saving opportunities including R&D credits, Section 174 capitalization, NOL utilization.

**Example request:** "Calculate our R&D tax credit for 2024"

## Tax Calculations

### Federal Corporate Tax
- Current rate: 21% flat rate (C-corp)
- Calculate on taxable income (GAAP income ± adjustments)

### State Tax
- Varies by state (0% to 12%)
- Apportion based on sales, payroll, property
- Combined reporting considerations

### Quarterly Estimated Payments
- Required if annual tax > $500
- Pay 25% each quarter of annual estimate
- Penalties for underpayment

## Compliance Calendar

**Quarterly (15th of 4th month):** Estimated tax payments
**Annual (March 15 / April 15):** Tax return filing
**Monthly/Quarterly:** Payroll tax deposits and returns
**Ongoing:** Sales tax returns (varies by state)

## Resources

### scripts/
- `tax_calculator.py` - Multi-jurisdiction tax calculations
- `rd_credit_calculator.py` - R&D tax credit estimator

### references/
- `tax_rates.md` - Current federal and state tax rates
- `compliance_calendar.md` - Tax filing deadlines
