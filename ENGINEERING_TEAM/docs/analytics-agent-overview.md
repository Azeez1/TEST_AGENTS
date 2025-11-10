# Analytics Agent - Complete Overview

**Created:** 2025-11-10
**Team:** ENGINEERING_TEAM
**Agent Type:** Data Analytics Specialist

---

## 🎯 Purpose

The **Analytics Agent** is a comprehensive data analytics specialist that can:
- Connect to multiple data sources (databases, APIs, files, cloud services)
- Perform advanced statistical analysis and predictive modeling
- Create interactive visualizations and dashboards
- Generate professional reports in multiple formats
- Provide actionable insights from complex datasets

---

## ✨ Key Capabilities

### 1. Multi-Source Data Integration

**Databases:**
- PostgreSQL
- MySQL/MariaDB
- MongoDB
- SQLite
- Redis

**APIs:**
- REST APIs (JSON, XML)
- GraphQL
- Third-party platforms (Stripe, Google Analytics, Mixpanel, Amplitude)

**Files:**
- CSV, JSON, Excel (.xlsx), Parquet
- TSV, XML
- Google Sheets (via MCP)

**Web Scraping:**
- Bright Data MCP for competitive intelligence
- Public data aggregation

### 2. Analytics & Statistics

- **Descriptive Statistics:** Mean, median, std dev, percentiles, distributions
- **Correlation Analysis:** Pearson, Spearman, heatmaps
- **Time Series Analysis:** Trends, seasonality, forecasting
- **Cohort Analysis:** Retention, LTV, churn analysis
- **A/B Testing:** Statistical significance, confidence intervals, winner determination
- **Predictive Modeling:** Classification, regression, clustering

### 3. Visualization & Dashboards

**Chart Types:**
- Line, bar, scatter, pie, area charts
- Histograms, box plots, violin plots
- Heatmaps, funnel charts
- Sankey diagrams, waterfall charts

**Interactive Features:**
- Hover tooltips
- Zoom and pan
- Date range selectors
- Dropdown filters
- Multi-axis support

**Dashboard Types:**
- HTML dashboards (Plotly, D3.js)
- React dashboards (using artifacts-builder skill)
- Excel dashboards (using xlsx skill)
- Google Data Studio (via MCP)

### 4. Report Generation

**Formats:**
- HTML (interactive, responsive)
- PDF (professional, printable)
- Excel (formulas, charts, pivot tables)
- Google Docs (collaborative)

**Report Sections:**
- Executive summaries
- KPI metrics cards
- Charts and visualizations
- Data tables
- Insights and recommendations

---

## 🛠️ Technical Stack

**Tools:**
- `connect_database` - Connect to PostgreSQL, MySQL, MongoDB, SQLite, Redis
- `query_database` - Execute SQL queries, return DataFrames
- `fetch_api_data` - Fetch from REST/GraphQL APIs
- `load_data_from_file` - Load CSV, JSON, Excel, Parquet, XML
- `transform_data` - ETL operations (merge, filter, aggregate, calculate)
- `analyze_data` - Statistical analysis (descriptive, correlation, time series)
- `analyze_ab_test` - A/B test statistical significance
- `create_chart` - Interactive charts (Plotly)
- `create_dashboard` - Multi-section dashboards (HTML, React)

**Skills:**
- `artifacts-builder` - Complex React dashboards
- `xlsx` - Excel file generation
- `pdf` - PDF report creation
- `filesystem` - File operations

**MCP Integrations:**
- `google-workspace` - Google Sheets, Docs, Drive
- `bright-data` - Web scraping for competitive data
- `sequential-thinking` - Structured problem-solving

**Python Libraries:**
- pandas, numpy - Data manipulation
- scipy - Statistical testing
- scikit-learn - Machine learning
- plotly - Interactive visualizations
- requests - API calls
- psycopg2, mysql-connector, pymongo - Database drivers

---

## 📊 Common Use Cases

### Use Case 1: Marketing Campaign ROI
```
User: "Use analytics-agent to analyze email campaign ROI from Mailchimp and our database"

Workflow:
1. Fetch campaign metrics from Mailchimp API
2. Query revenue data from PostgreSQL
3. Calculate ROI, ROAS, conversion rates
4. Create funnel visualization
5. Generate PDF report with recommendations
```

### Use Case 2: User Retention Dashboard
```
User: "Create a real-time user retention dashboard from our database"

Workflow:
1. Connect to PostgreSQL
2. Query user cohorts and retention data
3. Calculate retention rates by cohort
4. Create cohort retention heatmap
5. Build interactive dashboard with auto-refresh
6. Save to ENGINEERING_TEAM/outputs/dashboards/
```

### Use Case 3: A/B Test Analysis
```
User: "Analyze A/B test results for new checkout flow"

Workflow:
1. Load test data from CSV
2. Perform t-test for statistical significance
3. Calculate lift and confidence intervals
4. Create comparison chart
5. Generate report with winner recommendation
```

### Use Case 4: Predictive Churn Model
```
User: "Build a model to predict customer churn"

Workflow:
1. Extract customer features from database
2. Train Random Forest classification model
3. Evaluate model performance
4. Predict churn probability for active customers
5. Identify high-risk customers (>70% probability)
6. Export to CSV for customer success team
```

### Use Case 5: Multi-Source Dashboard
```
User: "Create dashboard combining Stripe, Google Analytics, and our database"

Workflow:
1. Fetch payment data from Stripe API
2. Fetch traffic data from Google Analytics API
3. Query user data from database
4. Merge datasets on user_id
5. Calculate metrics (revenue, conversion rate, CAC)
6. Build dashboard with KPI cards, charts, tables
7. Save as interactive HTML
```

---

## 🚀 Getting Started

### Step 1: Configure Data Sources

Create `/ENGINEERING_TEAM/memory/database_config.json`:

```json
{
  "databases": {
    "production_postgres": {
      "type": "postgresql",
      "host": "localhost",
      "port": 5432,
      "database": "app_production",
      "username": "analytics_user",
      "password": "YOUR_PASSWORD"
    }
  },
  "apis": {
    "stripe": {
      "base_url": "https://api.stripe.com/v1",
      "api_key": "sk_live_YOUR_KEY"
    }
  }
}
```

### Step 2: Invoke Analytics Agent

```
Use analytics-agent to analyze user signups from PostgreSQL and create a trend chart
```

### Step 3: View Outputs

Outputs are saved to:
- **Charts:** `ENGINEERING_TEAM/outputs/charts/`
- **Dashboards:** `ENGINEERING_TEAM/outputs/dashboards/`
- **Reports:** `ENGINEERING_TEAM/outputs/reports/`

---

## 📈 Example Workflows

See detailed examples in:
- **Workflows Guide:** `ENGINEERING_TEAM/outputs/examples/analytics_workflows.md`

Quick examples:

**Database Analysis:**
```python
from tools.analytics_tools import connect_database, query_database, create_chart

# Connect
conn = connect_database(db_type="postgresql", host="localhost", database="app_db")

# Query
df = query_database(conn, "SELECT date, revenue FROM daily_revenue")

# Visualize
chart = create_chart(df, chart_type="line", x="date", y="revenue", title="Revenue Trend")
```

**API Data Fetching:**
```python
from tools.analytics_tools import fetch_api_data

# Fetch from Stripe
data = fetch_api_data(
    url="https://api.stripe.com/v1/subscriptions",
    headers={"Authorization": "Bearer sk_live_..."}
)
```

**A/B Test Analysis:**
```python
from tools.analytics_tools import analyze_ab_test

results = analyze_ab_test(
    control_data=df[df['variant'] == 'A'],
    treatment_data=df[df['variant'] == 'B'],
    metric="conversion_rate",
    confidence_level=0.95
)

print(f"Winner: {results['recommendation']}")
print(f"Lift: {results['lift_percentage']:.1f}%")
print(f"P-value: {results['p_value']:.4f}")
```

---

## 🔒 Security & Best Practices

### Security
- **Never hardcode credentials** - Use `database_config.json`
- **Use secure connections** - SSL/TLS for databases
- **Anonymize PII** - Remove sensitive data before analysis
- **Read-only access** - Use read-only database users when possible

### Performance
- **Test queries first** - Use `LIMIT 100` for testing
- **Cache connections** - Connections are reused automatically
- **Optimize queries** - Use indexes, avoid SELECT *
- **Sample large datasets** - Random sampling for exploration

### Organization
- **Use absolute paths** - Always use workspace validation
- **Save outputs properly** - Use `ENGINEERING_TEAM/outputs/`
- **Version control** - Git commit significant analyses
- **Document assumptions** - Include methodology in reports

---

## 🤝 Integration with Other Agents

### CTO Coordination
```
CTO delegates: "Use analytics-agent to analyze system performance and create executive dashboard"
→ Analytics agent fetches from monitoring APIs
→ Creates comprehensive dashboard
→ CTO reviews and shares with leadership
```

### Marketing Team Collaboration
```
User: "Use analytics-agent to analyze MARKETING_TEAM campaign results"
→ Read campaign data from MARKETING_TEAM/outputs/
→ Analyze ROI, conversion rates
→ Create dashboard in ENGINEERING_TEAM/outputs/
→ Share findings with marketing team
```

### Database Architect Partnership
```
User: "Use analytics-agent to analyze query performance from database logs"
→ Database architect provides schema and connection
→ Analytics agent queries slow query logs
→ Identifies optimization opportunities
→ Creates performance dashboard
```

### Test Engineer Metrics
```
User: "Use analytics-agent to visualize test coverage trends"
→ Read test results from QA_TEAM
→ Calculate coverage metrics over time
→ Create trend charts
→ Dashboard for engineering team
```

---

## 📚 Additional Resources

**Files Created:**
- **Agent Definition:** `ENGINEERING_TEAM/.claude/agents/analytics-agent.md`
- **Tools Module:** `ENGINEERING_TEAM/tools/analytics_tools.py`
- **Config Template:** `ENGINEERING_TEAM/memory/database_config.example.json`
- **Workflows Guide:** `ENGINEERING_TEAM/outputs/examples/analytics_workflows.md`
- **This Overview:** `ENGINEERING_TEAM/docs/analytics-agent-overview.md`

**Dependencies:**
```bash
# Install required Python packages
pip install pandas numpy scipy scikit-learn plotly requests
pip install psycopg2-binary mysql-connector-python pymongo redis
```

**Configuration:**
1. Copy `database_config.example.json` to `database_config.json`
2. Fill in your credentials
3. Test connection with simple query

---

## 💡 Tips & Tricks

1. **Start simple** - Test with small queries before full datasets
2. **Visualize early** - Create quick charts to spot patterns
3. **Use descriptive analysis** - Run `analyze_data()` for initial insights
4. **Combine sources** - Merge database + API + file data for complete picture
5. **Save incrementally** - Save intermediate results, not just final output
6. **Document findings** - Include insights in all reports
7. **Automate recurring** - Create templates for weekly/monthly reports

---

## 🎯 When to Use Analytics Agent

**Use analytics-agent when you need to:**
- ✅ Connect to databases and pull data
- ✅ Fetch data from APIs
- ✅ Perform statistical analysis
- ✅ Create interactive visualizations
- ✅ Build dashboards
- ✅ Generate reports
- ✅ Analyze A/B tests
- ✅ Build predictive models
- ✅ Track KPIs and metrics
- ✅ Combine multiple data sources

**Don't use analytics-agent for:**
- ❌ Simple spreadsheet creation (use Google Sheets MCP)
- ❌ Marketing-only analysis (use MARKETING_TEAM analyst)
- ❌ Code analysis (use code-reviewer)
- ❌ Test generation (use test-orchestrator)

---

## 📞 Support

For questions or issues:
1. Check workflows guide: `analytics_workflows.md`
2. Review agent definition: `analytics-agent.md`
3. Inspect tools module: `analytics_tools.py`
4. Consult CTO for complex multi-agent workflows

---

**The analytics agent turns raw data into actionable insights - connecting any data source, analyzing with statistical rigor, and delivering beautiful visualizations that drive business decisions.**
