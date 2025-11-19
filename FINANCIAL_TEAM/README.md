# FINANCIAL_TEAM

A hybrid Private Equity / M&A + General Finance team with 10 specialized agents covering deal analysis, financial modeling, portfolio management, and corporate accounting.

## Team Overview

FINANCIAL_TEAM combines **PE/M&A capabilities** (due diligence, LBO modeling, valuations) with **general finance operations** (FP&A, accounting, tax) to support private equity investors, business owners, and CFOs.

## Agents (10)

### PE/M&A Focused Agents

#### 1. **Deal Analyst**
- **Focus**: Due diligence, deal structuring, LBO modeling, transaction support
- **Capabilities**: Financial DD, QoE review, working capital analysis, deal structuring, IC memos
- **Use Cases**: M&A transactions, buy-side DD, investment committee presentations

#### 2. **Valuation Agent**
- **Focus**: Business valuation using multiple methodologies
- **Capabilities**: DCF analysis, comparable companies, precedent transactions, WACC calculation
- **Use Cases**: Purchase price opinions, fairness opinions, fundraising valuations

#### 3. **Portfolio Manager**
- **Focus**: Portfolio company performance tracking and value creation
- **Capabilities**: KPI dashboards, board reporting, value creation tracking, exit planning
- **Use Cases**: Portfolio monitoring, board decks, fund-level reporting

### General Finance Agents

#### 4. **Financial Analyst**
- **Focus**: Financial modeling, 3-statement models, scenario analysis
- **Capabilities**: Financial models, DCF, scenario planning, business performance analysis
- **Use Cases**: Financial modeling, investment analysis, business planning

#### 5. **Forecasting Agent**
- **Focus**: Revenue/expense forecasting and predictive analytics
- **Capabilities**: Top-down/bottom-up forecasting, Monte Carlo simulation, rolling forecasts
- **Use Cases**: Annual budgets, scenario modeling, cash flow forecasting

#### 6. **FP&A Agent**
- **Focus**: Budgeting, variance analysis, management reporting
- **Capabilities**: Annual budgets, variance analysis, rolling forecasts, KPI dashboards
- **Use Cases**: Budget process, monthly variance reports, board packages

#### 7. **CFO Agent**
- **Focus**: Strategic finance leadership and capital strategy
- **Capabilities**: Fundraising, M&A strategy, board relations, capital allocation, exit planning
- **Use Cases**: Series A/B fundraising, strategic planning, board meetings

#### 8. **Accountant**
- **Focus**: Day-to-day accounting and bookkeeping
- **Capabilities**: Journal entries, AP/AR, reconciliations, payroll support, month-end close
- **Use Cases**: Daily transactions, vendor payments, customer collections

#### 9. **Controller**
- **Focus**: Financial reporting and compliance
- **Capabilities**: GAAP financials, audit coordination, internal controls, revenue recognition (ASC 606)
- **Use Cases**: Month/quarter/year-end close, audits, SOX compliance

#### 10. **Tax Advisor**
- **Focus**: Tax planning, compliance, and optimization
- **Capabilities**: Tax strategy, federal/state compliance, entity structuring, M&A tax, R&D credits
- **Use Cases**: Tax planning, tax returns, M&A structuring, credits/incentives

## Directory Structure

```
FINANCIAL_TEAM/
├── .claude/
│   ├── agents/              # 10 financial agent definitions
│   ├── commands/            # Custom slash commands
│   ├── skills/              # Custom skills
│   └── settings.json        # Team configuration
├── memory/                  # Financial assumptions, historical data
├── outputs/                 # Models, reports, memos
├── tools/                   # Custom Python tools (financial calculations)
├── scripts/                 # Automation scripts
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

## Key Use Cases

### Private Equity / M&A

**Buy-Side M&A Transaction:**
1. **Deal Analyst**: Lead financial due diligence, prepare QoE analysis
2. **Valuation Agent**: Build DCF and comparable company valuations
3. **Tax Advisor**: Structure deal for tax optimization
4. **CFO Agent**: Present IC memo and recommendation

**Portfolio Company Management:**
1. **Portfolio Manager**: Track KPIs across all portfolio companies
2. **FP&A Agent**: Monthly variance analysis for each company
3. **Financial Analyst**: Build 5-year strategic plan models
4. **CFO Agent**: Prepare for exit (IPO or strategic sale)

### General Corporate Finance

**Annual Budget Process:**
1. **FP&A Agent**: Lead annual budget process
2. **Forecasting Agent**: Build revenue and expense forecasts
3. **CFO Agent**: Present budget to board for approval
4. **Controller**: Implement budget in accounting system

**Fundraising (Series B):**
1. **CFO Agent**: Lead fundraising strategy and investor outreach
2. **Financial Analyst**: Build financial model and projections
3. **Controller**: Prepare audited financials and metrics
4. **FP&A Agent**: Create data room materials

**Month-End Close:**
1. **Accountant**: Process transactions, reconcile accounts
2. **Controller**: Review close, prepare financial statements
3. **FP&A Agent**: Variance analysis and commentary
4. **CFO Agent**: Present results to leadership

## MCP Integrations

- **google-workspace**: Financial models (Sheets), board decks (Slides), memos (Docs)
- **bright-data**: Market research, competitor analysis, industry benchmarking

## Getting Started

### 1. Configure Memory Files

Create these configuration files in `FINANCIAL_TEAM/memory/`:

**financial_assumptions.json:**
```json
{
  "wacc": 0.10,
  "terminal_growth_rate": 0.03,
  "tax_rate": 0.21,
  "discount_rate": 0.12
}
```

**historical_financials.json:**
```json
{
  "2023": {
    "revenue": 40000000,
    "ebitda": 8000000,
    "capex": 2000000
  },
  "2024": {
    "revenue": 50000000,
    "ebitda": 10000000,
    "capex": 2500000
  }
}
```

**chart_of_accounts.json:**
```json
{
  "1000": "Cash",
  "1100": "Accounts Receivable",
  "4000": "Revenue",
  "5000": "COGS"
}
```

### 2. Invoke Agents

```bash
# Build financial model
@financial-analyst Build a 5-year DCF model for this company

# Due diligence
@deal-analyst Review these financials for quality of earnings issues

# Tax planning
@tax-advisor What's our estimated tax liability for 2024?

# Portfolio tracking
@portfolio-manager Generate a monthly update for all portfolio companies

# Fundraising
@cfo-agent Build a Series B fundraising strategy
```

### 3. Team Workflows

**Monthly Close (5-day process):**
- **Day 1**: Accountant closes transactions, starts reconciliations
- **Day 2-3**: Controller reviews financials, makes adjustments
- **Day 4**: FP&A Agent performs variance analysis
- **Day 5**: CFO Agent presents results to leadership

**Annual Budget (Oct-Dec):**
- **Oct**: Forecasting Agent builds revenue/expense forecasts
- **Nov**: FP&A Agent consolidates department budgets
- **Dec**: CFO Agent presents to board for approval

**M&A Transaction (3-6 months):**
- **Month 1-2**: Deal Analyst leads due diligence
- **Month 2**: Valuation Agent builds valuation models
- **Month 3**: Tax Advisor structures deal
- **Month 3-4**: CFO Agent negotiates terms
- **Month 5-6**: Close transaction, Portfolio Manager onboards

## Performance Metrics

### PE/M&A Metrics
- Deal IRR (target: >20%)
- Multiple on Invested Capital (MOIC >2.5x)
- Portfolio company EBITDA growth
- Fund-level TVPI, DPI, IRR

### Corporate Finance Metrics
- Month-end close time (target: <5 days)
- Forecast accuracy (MAPE <10%)
- Budget variance (target: ±5%)
- Audit adjustments (target: <$500k)

### Operational Metrics
- AR DSO (target: <45 days)
- AP DPO (optimize for terms)
- Cash conversion cycle
- Runway (target: >12 months)

## Financial Models

FINANCIAL_TEAM agents can build various financial models:

### PE/M&A Models
- **LBO Model**: Sources & uses, returns analysis, debt paydown
- **DCF Model**: Free cash flow forecasting, terminal value, valuation
- **Comparable Analysis**: Trading comps, transaction comps
- **Merger Model**: Accretion/dilution, pro forma financials

### Corporate Models
- **3-Statement Model**: P&L, balance sheet, cash flow
- **Budget Model**: Annual budget with department detail
- **Forecast Model**: Rolling 12-month projections
- **Scenario Model**: Base/upside/downside cases

## Technical Accounting Topics

Agents are knowledgeable in:
- **Revenue Recognition** (ASC 606): 5-step model, contract modifications
- **Lease Accounting** (ASC 842): ROU assets, lease liabilities
- **Stock Compensation** (ASC 718): Options, RSUs, expense calculation
- **Income Taxes** (ASC 740): Deferred taxes, effective rate reconciliation
- **Business Combinations** (ASC 805): Purchase price allocation, goodwill

## Best Practices

1. **Always use absolute paths** for file operations
2. **Document assumptions** in all financial models
3. **Triangulate valuations** using multiple methods
4. **Reconcile everything** (trial balance must balance!)
5. **Track forecast accuracy** and learn from variances
6. **Maintain strong controls** (segregation of duties)
7. **Plan taxes proactively** (not reactively at year-end)

## Integration with Other Teams

- **SALES_TEAM**: Revenue forecasting, commission calculations, quota setting
- **ENGINEERING_TEAM**: R&D capitalization, technical debt quantification
- **MARKETING_TEAM**: Marketing ROI analysis, budget allocation

## Support

For issues or questions about FINANCIAL_TEAM agents:
- See [MULTI_AGENT_GUIDE.md](../MULTI_AGENT_GUIDE.md) for agent invocation patterns
- See [TOOL_REGISTRY.md](../TOOL_REGISTRY.md) for available tools and MCPs
- See individual agent files in `.claude/agents/` for detailed capabilities
