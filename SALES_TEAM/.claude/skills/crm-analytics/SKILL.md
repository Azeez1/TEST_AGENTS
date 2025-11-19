---
name: crm-analytics
description: Analyze CRM and sales data to uncover insights on pipeline health, conversion rates, sales performance, forecasting accuracy, and sales productivity. Use when analyzing sales data, reviewing pipeline, tracking quota attainment, identifying bottlenecks, or building sales dashboards.
---

# CRM Analytics

## Overview

This skill enables analysis of CRM and sales data to drive insights, improve performance, and make data-driven sales decisions.

## Core Capabilities

### 1. Pipeline Analysis
Analyze sales pipeline health and trends.

**Key metrics:**
- Pipeline coverage ratio (Pipeline / Quota)
- Stage distribution and progression rates
- Average deal size by stage/source
- Pipeline velocity (time in each stage)
- Pipeline generation trends

**Example request:** "Analyze our Q4 pipeline coverage and identify gaps"

### 2. Conversion Rate Analysis
Track conversion rates through the funnel.

**Funnel stages:**
- Lead → MQL: Marketing qualified rate
- MQL → SQL: Sales accepted rate
- SQL → Opportunity: Conversion to pipeline
- Opp → Closed Won: Win rate

**Example request:** "Show conversion rates by lead source and identify bottlenecks"

### 3. Sales Performance Tracking
Monitor individual and team quota attainment.

**Metrics:**
- Quota attainment % by rep
- Bookings vs target (monthly/quarterly/annual)
- Activity metrics (calls, meetings, proposals)
- Average deal size and velocity
- Win rate and pipeline generation

**Example request:** "Create a sales performance dashboard for the team"

### 4. Forecast Analysis
Analyze forecast accuracy and deal progression.

**Components:**
- Weighted pipeline forecast
- Stage-based probability weighting
- Historical close rate analysis
- Forecast vs actual comparison
- Deal slippage tracking

**Example request:** "Analyze our forecast accuracy for the past 4 quarters"

### 5. Sales Productivity Analytics
Measure efficiency and identify improvement opportunities.

**Productivity metrics:**
- Time to first meeting
- Sales cycle length
- Meetings per closed deal
- Average contract value (ACV)
- CAC payback period

**Example request:** "Identify our most productive sales activities and channels"

## Key Sales Metrics

### Pipeline Metrics
```
Pipeline Coverage = Pipeline Value / Quota
Healthy coverage: 3-4x for early quarters, 1.5-2x for current quarter

Stage Conversion Rates:
- Demo → Proposal: ~50%
- Proposal → Negotiation: ~60%
- Negotiation → Closed Won: ~70%
- Overall Win Rate: 20-30% (varies by business)
```

### Performance Metrics
```python
# Quota attainment
quota_attainment = actual_bookings / quota * 100

# Average deal size
avg_deal_size = total_bookings / num_deals

# Sales cycle length
avg_sales_cycle = mean(close_date - create_date for won deals)

# Win rate
win_rate = won_deals / (won_deals + lost_deals) * 100
```

### Activity Metrics
```
Activities per closed deal:
- Outbound calls: 10-20
- Meetings: 5-8
- Proposals sent: 1-2
- Decision makers engaged: 3-5
```

## Analysis Patterns

### Cohort Analysis
Track deal cohorts by create month through the funnel.

```python
# Group deals by month created
cohorts = deals.groupby(deals['created_date'].dt.to_period('M'))

# Track progression over time
for cohort in cohorts:
    month_0_count = len(cohort)
    month_1_closed = len(cohort[cohort['close_date'] <= cohort['created_date'] + 30])
    # ... continue for each month
```

### Funnel Conversion Analysis
```python
funnel_data = {
    'Stage': ['Leads', 'MQLs', 'SQLs', 'Opps', 'Closed Won'],
    'Count': [10000, 2000, 1000, 500, 100]
}

# Calculate conversion rates
conversion_rates = []
for i in range(len(funnel_data['Count']) - 1):
    rate = funnel_data['Count'][i+1] / funnel_data['Count'][i]
    conversion_rates.append(rate)
```

### Rep Performance Ranking
```python
rep_performance = deals.groupby('owner').agg({
    'amount': ['sum', 'mean', 'count'],
    'is_won': 'mean',  # win rate
    'days_to_close': 'mean'
})

# Rank by quota attainment
rep_performance['quota_attainment'] = rep_performance['amount']['sum'] / quota
rep_performance.sort_values('quota_attainment', ascending=False)
```

## Dashboards and Reports

### Executive Sales Dashboard
- Current quarter bookings vs quota
- Pipeline coverage
- Win rate trend
- Top deals and risks
- Team quota attainment leaderboard

### Pipeline Review Dashboard
- Pipeline by stage
- Deal aging (deals stuck too long)
- Expected close dates
- Win probability distribution
- New pipeline generation

### Rep Performance Dashboard
- Individual quota attainment
- Activity metrics (calls, meetings)
- Win rate and avg deal size
- Pipeline generation
- Deal velocity

## Resources

### scripts/
- `pipeline_analyzer.py` - Pipeline health analysis
- `conversion_funnel.py` - Funnel conversion tracking
- `forecast_accuracy.py` - Forecast vs actual analysis

### references/
- `sales_metrics_definitions.md` - Standard sales metric formulas
- `benchmark_data.md` - Industry benchmark conversion rates

### assets/
- `sales_dashboard_template.xlsx` - Excel dashboard template
