# Financial Analysis

Comprehensive financial analysis package with forecasting, budgeting, and strategic recommendations.

## What This Does

Orchestrates the Financial Team to provide complete financial analysis including:
1. Financial statement analysis and health metrics
2. Budget planning and variance analysis
3. Financial forecasting and projections
4. Valuation and business metrics
5. Tax planning considerations
6. Investment and portfolio recommendations
7. Strategic financial insights

## Usage

```
/financial-analysis [company/project name] [analysis type] [time period]
```

## Example

```
/financial-analysis "Dux Machina Q4 2025" "comprehensive" "next 12 months"
/financial-analysis "Product Launch Budget" "budget-focus" "Q1 2026"
/financial-analysis "Investment Portfolio" "portfolio-review" "annual"
```

## Process

Use the cfo-agent to coordinate this workflow:

1. **Data Collection & Validation** (accountant + controller)
   - Gather financial statements and records
   - Validate data accuracy and completeness
   - Identify missing information or data gaps
   - Compliance and control checks

2. **Financial Health Analysis** (financial-analyst + accountant)
   - Income statement analysis
   - Balance sheet health metrics
   - Cash flow analysis
   - Key financial ratios (liquidity, profitability, efficiency)
   - Trend analysis and historical comparisons

3. **Forecasting & Planning** (fpna-agent + forecasting-agent)
   - Revenue and expense forecasting
   - Scenario planning (best/base/worst case)
   - Budget creation and allocation
   - Variance analysis (budget vs. actual)
   - Sensitivity analysis for key drivers

4. **Valuation & Performance** (valuation-agent + financial-analyst)
   - Business valuation metrics (DCF, multiples)
   - Unit economics and KPIs
   - Customer lifetime value (LTV) analysis
   - Return on investment (ROI) calculations
   - Performance benchmarking

5. **Tax & Compliance** (tax-advisor + controller)
   - Tax planning opportunities
   - Compliance requirements
   - Tax optimization strategies
   - Regulatory considerations
   - Risk assessment

6. **Investment Strategy** (portfolio-manager + fpna-agent)
   - Investment portfolio analysis
   - Asset allocation recommendations
   - Risk-adjusted return analysis
   - Rebalancing strategies
   - Capital allocation priorities

7. **Strategic Recommendations** (cfo-agent coordinates all)
   - Executive summary with key insights
   - Strategic recommendations
   - Action items with priorities
   - Risk mitigation strategies
   - Growth opportunities

## Deliverables

- Executive summary (2-3 pages)
- Financial health scorecard with key metrics
- Detailed financial statements analysis
- 12-month financial forecast with scenarios
- Budget vs. actual variance report
- Valuation analysis and business metrics
- Tax planning recommendations
- Investment portfolio review (if applicable)
- Strategic action plan with priorities
- Visual dashboards and charts (Excel/PDF)

## Time Estimate

2-3 hours for comprehensive financial analysis package

## Related Commands

- `/budget-forecast` - Focus on budgeting and forecasting only
- `/deal-evaluation` - For M&A and deal analysis
- `/quarterly-planning` - Includes financial planning with other departments
