---
name: roi-calculator
description: Build interactive ROI and TCO calculators for sales demos showing financial impact, payback periods, and business value. Use when creating sales tools, demonstrating financial justification, building business cases, or helping prospects quantify value of your solution.
---

# ROI Calculator

## Overview

This skill creates interactive calculators that help prospects quantify the financial impact and ROI of purchasing your product or service.

## Core Capabilities

### 1. ROI Calculators
Calculate return on investment with payback period analysis.

**Formula:**
```
ROI = (Total Benefits - Total Costs) / Total Costs × 100%
Payback Period = Initial Investment / Annual Net Benefit
```

**Example request:** "Build an ROI calculator for our sales automation tool"

### 2. TCO (Total Cost of Ownership) Calculators
Compare total costs of your solution vs alternatives.

**Include:**
- Upfront costs (licenses, implementation, training)
- Ongoing costs (maintenance, support, infrastructure)
- Hidden costs of alternatives (manual work, errors, opportunity cost)
- 3-5 year time horizon

**Example request:** "Create a TCO comparison: our SaaS vs on-premise competitor"

### 3. Savings Calculators
Quantify cost savings from efficiency improvements.

**Common savings categories:**
- **Time savings:** Hours saved × hourly cost × team size
- **Error reduction:** Error rate × cost per error × volume
- **Resource optimization:** Reduced headcount/tools needed
- **Automation:** Manual process time × frequency × cost

**Example request:** "Calculate savings from automating invoice processing"

### 4. Value Calculators
Quantify revenue/business impact.

**Revenue impact:**
- Increased conversion rates
- Faster sales cycles
- Larger deal sizes
- Improved retention/upsell

**Example request:** "Show revenue impact of improving sales conversion by 3%"

### 5. Interactive Demos
Build web-based calculators for prospects to self-serve.

**Features:**
- Input sliders for key variables
- Real-time calculation updates
- Visualization of results
- Export/share functionality
- Industry benchmarks

**Example request:** "Create an interactive web calculator for our website"

## Calculator Components

### Input Assumptions
```
Current State:
- Team size: [   ]
- Hours per task: [   ]
- Tasks per month: [   ]
- Hourly cost: $[   ]

With Our Solution:
- Time reduction: [   ]%
- Error reduction: [   ]%
```

### Calculations
```python
# Current state cost
current_monthly_cost = team_size * hours_per_task * tasks_per_month * hourly_cost

# Future state cost
time_saved = hours_per_task * time_reduction_pct
new_time_per_task = hours_per_task - time_saved
future_monthly_cost = team_size * new_time_per_task * tasks_per_month * hourly_cost

# Monthly savings
monthly_savings = current_monthly_cost - future_monthly_cost
annual_savings = monthly_savings * 12

# ROI calculation
annual_subscription_cost = 50000
implementation_cost = 25000
total_investment = annual_subscription_cost + implementation_cost

roi = ((annual_savings - annual_subscription_cost) / total_investment) * 100
payback_months = total_investment / (monthly_savings - (annual_subscription_cost / 12))
```

### Results Display
```
INVESTMENT:
- Implementation: $25,000 (one-time)
- Annual subscription: $50,000/year

ANNUAL BENEFIT:
- Time savings: $180,000
- Error reduction: $45,000
- Total annual benefit: $225,000

NET ANNUAL BENEFIT: $175,000 ($225K - $50K)

ROI: 233% first year
Payback Period: 5 months
3-Year Value: $450,000
```

## Calculator Best Practices

### Input Design
- Use realistic defaults (industry benchmarks)
- Limit inputs to 5-8 key variables
- Provide range sliders (min/max) to prevent unrealistic numbers
- Include tooltips explaining each input

### Calculations
- Show your work (transparent formulas)
- Use conservative assumptions
- Include confidence ranges (best/worst case)
- Reference industry benchmarks

### Output Presentation
- Lead with the headline number (ROI %, payback months)
- Show year-by-year breakdown
- Visualize with charts (especially cumulative value)
- Include comparison to alternatives

### Credibility
- Cite data sources for benchmarks
- Show customer case study validation
- Allow customization for their specific situation
- Provide detailed methodology

## Common ROI Patterns

### SaaS Tool ROI
```
Benefits:
- Time savings from automation
- Productivity improvement
- Error reduction
- Faster time-to-value

Costs:
- Subscription fee
- Implementation/setup
- Training time
- Change management
```

### Sales Tool ROI
```
Benefits:
- Increased win rates
- Shorter sales cycles
- Larger deal sizes
- Improved forecast accuracy

Costs:
- Platform cost
- Integration/setup
- User training
- Ongoing administration
```

## Resources

### scripts/
- `roi_calculator.py` - Flexible ROI calculation engine
- `tco_analyzer.py` - TCO comparison tool
- `web_calculator_template.html` - Interactive HTML calculator

### references/
- `industry_benchmarks.md` - ROI benchmarks by industry
- `calculator_formulas.md` - Standard ROI formulas

### assets/
- `calculator_template.xlsx` - Excel calculator template
- `roi_presentation_template.pptx` - ROI results presentation
