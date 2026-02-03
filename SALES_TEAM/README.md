# SALES_TEAM

A comprehensive, adaptable sales organization with 9 specialized agents covering the full sales lifecycle from prospecting to customer success, including PE/investor outreach for deal sourcing.

## Team Overview

SALES_TEAM is designed to support **any business model** (B2B, B2C, SaaS, e-commerce, services) with a complete sales operation including outbound prospecting, deal closing, sales analytics, and customer retention.

## Agents (9)

### 1. **PE Outreach Agent** (NEW)
- **Focus**: PE/Family Office investor outreach, relationship building, buy box discovery
- **Capabilities**: LinkedIn outreach, personalized message generation, investor tracking, buy box documentation, deal matching
- **Use Cases**: Building capital source relationships, earning finder's fees, matching sourced deals to investors
- **Special**: References active investor list (Google Sheet), uses templates from `pe_investor_outreach.json`

### 2. **SDR Agent** (Sales Development Representative)
- **Focus**: Prospecting, cold outreach, lead qualification, meeting booking
- **Capabilities**: Email sequences, cold calling, LinkedIn outreach, multi-channel campaigns, BANT/MEDDIC qualification
- **Use Cases**: Building pipeline, generating SQLs, booking discovery calls

### 3. **Account Executive**
- **Focus**: Full-cycle sales from discovery through close
- **Capabilities**: Discovery calls, demos, proposals, negotiations, objection handling, deal closing
- **Use Cases**: Closing deals, managing sales cycles, relationship building

### 4. **Sales Operations**
- **Focus**: CRM administration, process optimization, sales enablement
- **Capabilities**: CRM management, territory planning, quota setting, commission management, workflow automation
- **Use Cases**: Sales process design, data quality, reporting infrastructure

### 5. **Sales Analyst**
- **Focus**: Forecasting, pipeline analysis, performance metrics
- **Capabilities**: Sales forecasting, pipeline health tracking, win/loss analysis, KPI dashboards
- **Use Cases**: Revenue forecasting, pipeline optimization, performance benchmarking

### 6. **Proposal Specialist**
- **Focus**: Proposal writing, pricing, RFP responses
- **Capabilities**: Proposal creation, SOW development, pricing models, ROI calculations
- **Use Cases**: Complex proposals, RFP responses, pricing strategy

### 7. **Customer Success Manager**
- **Focus**: Onboarding, retention, expansion
- **Capabilities**: Customer onboarding, health scoring, churn prevention, upsell/cross-sell, renewal management
- **Use Cases**: Customer retention, expansion revenue, QBRs

### 8. **Outbound Specialist**
- **Focus**: High-volume cold outreach campaigns
- **Capabilities**: Cold calling, email cadences, multi-channel sequences, list building, A/B testing
- **Use Cases**: Outbound campaigns, lead generation, market penetration

### 9. **Sales Manager**
- **Focus**: Team coaching, pipeline management, forecasting
- **Capabilities**: 1-on-1 coaching, deal coaching, performance management, hiring/onboarding
- **Use Cases**: Team leadership, forecast accuracy, rep development

## Directory Structure

```
SALES_TEAM/
├── .claude/
│   ├── agents/              # 9 sales agent definitions
│   ├── commands/            # Custom slash commands
│   ├── skills/              # Custom skills
│   └── settings.json        # Team configuration
├── memory/                  # CRM configs, templates, target lists
├── outputs/                 # Proposals, sequences, reports
├── tools/                   # Custom Python tools
├── scripts/                 # Automation scripts
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

## Key Use Cases

### Pipeline Generation
- **SDR Agent**: Build target lists, execute outreach campaigns
- **Outbound Specialist**: High-volume cold calling and email
- **Sales Operations**: Optimize lead routing and qualification

### Deal Closing
- **Account Executive**: Run discovery, demos, negotiations
- **Proposal Specialist**: Create compelling proposals with ROI
- **Sales Manager**: Coach on deal strategy

### Revenue Forecasting
- **Sales Analyst**: Build forecasting models, track pipeline health
- **Sales Manager**: Review and commit to forecast
- **Sales Operations**: Provide data integrity

### Customer Retention & Expansion
- **Customer Success Manager**: Drive adoption, prevent churn
- **Account Executive**: Identify expansion opportunities
- **Sales Analyst**: Track NRR, expansion metrics

## MCP Integrations

- **google-workspace**: CRM data (Sheets), proposals (Docs/Slides), email automation
- **bright-data**: Lead generation, competitive intelligence, market research

## Getting Started

### 1. Configure Memory Files

Create these configuration files in `SALES_TEAM/memory/`:

**crm_config.json:**
```json
{
  "crm_type": "salesforce",
  "user_email": "your@email.com",
  "custom_fields": {
    "lead_source": "Lead Source",
    "industry": "Industry"
  }
}
```

**outreach_templates.json:**
```json
{
  "cold_email_1": "Subject: Quick question about [pain point]...",
  "follow_up_1": "Subject: Following up..."
}
```

**target_lists.json:**
```json
{
  "icp_criteria": {
    "company_size": "50-500 employees",
    "industry": ["SaaS", "Technology"],
    "location": ["USA", "Canada"]
  }
}
```

### 2. Invoke Agents

```bash
# Generate outbound campaign
@sdr-agent Create a 5-email sequence for SaaS companies

# Analyze pipeline
@sales-analyst What's our forecast accuracy this quarter?

# Coach on deal
@sales-manager Review the Acme Corp deal strategy

# Create proposal
@proposal-specialist Build a proposal for Beta Inc ($50k deal)
```

### 3. Team Workflows

**Weekly Pipeline Review:**
1. **Sales Analyst**: Generate pipeline report
2. **Sales Manager**: Review with team, identify at-risk deals
3. **Account Executive**: Update next steps on all deals

**Monthly Forecast:**
1. **Sales Analyst**: Build weighted pipeline forecast
2. **Sales Manager**: Review and commit to forecast
3. **Sales Operations**: Track accuracy month-over-month

**Quarterly Planning:**
1. **Sales Operations**: Set quotas and territories
2. **Sales Manager**: Communicate targets to team
3. **SDR Agent**: Build prospecting plan for next quarter

## Performance Metrics

Key metrics tracked by SALES_TEAM:

### Activity Metrics
- Calls/emails per day (SDR, Outbound)
- Meetings booked per week (SDR)
- Demos delivered per week (AE)

### Pipeline Metrics
- Pipeline coverage (3-5x quota)
- Pipeline velocity
- Stage conversion rates

### Revenue Metrics
- Quota attainment
- Win rate
- Average deal size
- Sales cycle length

### Retention Metrics
- Logo retention (>90%)
- Net revenue retention (>110%)
- Churn rate (<5%)

## Best Practices

1. **Always use absolute paths** for file operations
2. **Read memory configs** before starting work
3. **Update CRM religiously** (data integrity is critical)
4. **Multi-thread on deals** (engage 3+ stakeholders)
5. **Track forecast accuracy** (learn from variances)
6. **Coach continuously** (not just during 1-on-1s)

## Support

For issues or questions about SALES_TEAM agents:
- See [MULTI_AGENT_GUIDE.md](../MULTI_AGENT_GUIDE.md) for agent invocation patterns
- See [TOOL_REGISTRY.md](../TOOL_REGISTRY.md) for available tools and MCPs
- See individual agent files in `.claude/agents/` for detailed capabilities
