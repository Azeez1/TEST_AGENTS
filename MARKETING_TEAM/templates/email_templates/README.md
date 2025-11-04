# Email Templates for Gmail Agent

This folder contains professional HTML email templates for the gmail-agent to use when sending formatted reports.

## Available Templates

### 1. Client Research Report Template
**File:** `client_research_report_template.html`

**Purpose:** Professional HTML email report for client research and fit assessments

**Use Cases:**
- Client prospect research reports
- Fit analysis and recommendations
- Lead qualification reports
- Partnership opportunity assessments

**Theme Features:**
- ✅ Clean, professional design with Dux Machina brand colors
- ✅ Color-coded recommendation badges (YES/MAYBE/NO)
- ✅ Responsive layout (mobile-friendly)
- ✅ Stats cards, profile tables, two-column pros/cons
- ✅ Approach cards with investment details
- ✅ Numbered next steps timeline
- ✅ Bottom line decision framework

---

## How to Use the Template

### Step 1: Copy the Template
```python
# Read the template file
with open('MARKETING_TEAM/templates/email_templates/client_research_report_template.html', 'r') as f:
    template = f.read()
```

### Step 2: Replace Variables

The template uses `{{VARIABLE_NAME}}` placeholders. Replace them with actual data:

**Required Variables:**

| Variable | Example Value | Description |
|----------|--------------|-------------|
| `{{PROSPECT_NAME}}` | "Miguel Otero Pedrido" | Full name of prospect |
| `{{REPORT_DATE}}` | "November 3, 2025" | Date of report generation |
| `{{RECOMMENDATION}}` | "MAYBE" | YES / MAYBE / NO |
| `{{RECOMMENDATION_CLASS}}` | "maybe" | yes / maybe / no (lowercase for CSS) |
| `{{RECOMMENDATION_ICON}}` | "⚠️" | ✅ / ⚠️ / ❌ |
| `{{RECOMMENDATION_SUBTITLE}}` | "Conditional Engagement Required" | Short description |
| `{{FIT_SCORE}}` | "6.0" | Score out of 10 |
| `{{FIT_LABEL}}` | "Borderline Fit - Needs Repositioning" | Score interpretation |

**Content Sections (HTML Blocks):**

| Variable | Content Type | Example |
|----------|--------------|---------|
| `{{SUMMARY_POINTS}}` | List items (`<li>`) | 3-4 key bullet points |
| `{{STATS_CARDS}}` | Stat card divs | LinkedIn followers, revenue, etc. |
| `{{PROFILE_ROWS}}` | Table rows (`<tr>`) | Current role, location, expertise, etc. |
| `{{NEGATIVE_POINTS}}` | List items (`<li>`) | Why NOT a perfect fit |
| `{{POSITIVE_POINTS}}` | List items (`<li>`) | Why there's still potential |
| `{{OPTION1_TITLE}}` | Text | "Option 1: Client" |
| `{{OPTION1_ICON}}` | Emoji | "💻" |
| `{{OPTION1_BADGE}}` | Text | "Platform Automation" |
| `{{OPTION1_FOCUS}}` | Text | One-line focus statement |
| `{{OPTION1_BULLETS}}` | List items (`<li>`) | Approach details |
| `{{OPTION1_INVESTMENT}}` | Text | "€15K-25K \| 6-8 weeks" |
| `{{OPTION2_*}}` | Same as Option 1 | Second recommended approach |
| `{{NEXT_STEPS_LIST}}` | List items (`<li>`) | Numbered timeline steps |
| `{{BOTTOM_LINE_CONTENT}}` | HTML paragraphs | Final recommendation and decision framework |

**Footer Variables:**

| Variable | Example Value |
|----------|--------------|
| `{{REPORT_FILES_LOCATION}}` | "MARKETING_TEAM/outputs/research/..." |
| `{{TEAM_EMAIL}}` | "sabaazeez12@gmail.com" |
| `{{PROSPECT_LINKEDIN}}` | "https://linkedin.com/in/..." |
| `{{PROSPECT_EMAIL}}` | "prospect@example.com" |

### Step 3: Example Replacement Code

```python
template = template.replace('{{PROSPECT_NAME}}', 'Miguel Otero Pedrido')
template = template.replace('{{REPORT_DATE}}', 'November 3, 2025')
template = template.replace('{{RECOMMENDATION}}', 'MAYBE')
template = template.replace('{{RECOMMENDATION_CLASS}}', 'maybe')
template = template.replace('{{RECOMMENDATION_ICON}}', '⚠️')
template = template.replace('{{FIT_SCORE}}', '6.0')

# Summary points (HTML list items)
summary_points = '''
<li><strong>Miguel Otero Pedrido</strong> is the founder of The Neural Maze...</li>
<li>Top 1% LinkedIn influencer with <strong>56,000 followers</strong>...</li>
<li>8+ years production ML experience...</li>
'''
template = template.replace('{{SUMMARY_POINTS}}', summary_points)

# Stats cards
stats_cards = '''
<div class="stat-card">
    <div class="number">56K</div>
    <div class="label">LinkedIn Followers</div>
</div>
<div class="stat-card">
    <div class="number">9K</div>
    <div class="label">Substack Subscribers</div>
</div>
<div class="stat-card">
    <div class="number">€150K-300K</div>
    <div class="label">Annual Revenue</div>
</div>
'''
template = template.replace('{{STATS_CARDS}}', stats_cards)

# Continue for all variables...
```

### Step 4: Send via Gmail API

```python
from send_email_with_attachment import send_email

send_email(
    to="sabaazeez12@gmail.com",
    cc="aoseni@duxvitaecapital.com",
    subject="Client Research Report: Miguel Otero Pedrido - MAYBE (6/10 Fit)",
    body=template,
    is_html=True
)
```

---

## Color Theme Reference

### Recommendation Badge Colors

**YES (Emerald Green):**
```css
.recommendation-badge.yes {
    background: #d1fae5;
    border-left: 6px solid #10b981;
}
```

**MAYBE (Amber):**
```css
.recommendation-badge.maybe {
    background: #fef3c7;
    border-left: 6px solid #f59e0b;
}
```

**NO (Red):**
```css
.recommendation-badge.no {
    background: #fee2e2;
    border-left: 6px solid #ef4444;
}
```

### Brand Colors

**Professional Navy/Blue Theme:**
- **Primary Navy:** `#1e3a8a` (header, next steps background)
- **Slate:** `#334155` (gradients, secondary backgrounds)
- **Blue:** `#3b82f6` (accents, links, borders, table headers)
- **Success:** `#10b981` (emerald green - YES recommendations)
- **Warning:** `#f59e0b` (amber - MAYBE recommendations)
- **Danger:** `#ef4444` (red - NO recommendations)
- **Dark Text:** `#1e293b` (headers, important text)
- **Gray Text:** `#636e72` (secondary text)
- **Footer:** `#1e293b` (dark slate)

---

## Template Components

### 1. Header
- Navy to slate gradient background (#1e3a8a → #334155)
- Report title, subtitle, date
- Centered text with text shadow

### 2. Recommendation Badge
- Large, prominent badge
- Color-coded by recommendation (YES/MAYBE/NO)
  - YES: Emerald green (#10b981)
  - MAYBE: Amber (#f59e0b)
  - NO: Red (#ef4444)
- Fit score display (X/10)
- Interpretation label

### 3. Executive Summary
- Light gray background box (#f8f9fa)
- Bullet points with blue arrow icons (#3b82f6)
- 3-4 key takeaways

### 4. Stats Grid
- 3-column grid (responsive: 1 column on mobile)
- Blue gradient cards (#3b82f6 → #1d4ed8)
- Large numbers with labels
- Professional blue shadow

### 5. Profile Table
- Blue header row (#3b82f6)
- Hover effects on rows
- Clean, organized data presentation
- Blue links (#3b82f6)

### 6. Fit Assessment (Two-Column)
- Red card: Why NOT a perfect fit (❌ icons, #ef4444 border)
- Green card: Why there's STILL potential (✅ icons, #10b981 border)
- Side-by-side comparison

### 7. Approach Cards
- Two options: Primary (blue border #3b82f6) and Secondary (green border #10b981)
- Icon + title + badge
- Bullet points with blue bullets (#3b82f6)
- Investment details

### 8. Next Steps Timeline
- Navy to slate gradient background (#1e3a8a → #334155)
- Numbered steps with circular white badges (blue numbers #3b82f6)
- Timeline format

### 9. Bottom Line
- Amber warning box (#fff3cd with #ffc107 border)
- Decision framework
- Risk assessment
- Blue highlight for strong text (#3b82f6)

### 10. Footer
- Dark slate background (#1e293b)
- Blue contact links (#60a5fa)
- Report file locations
- Copyright notice

---

## Responsive Design

The template automatically adjusts for mobile devices:

- **Desktop (>768px):** Two-column layouts, full stats grid
- **Mobile (≤768px):** Single column, stacked cards, full-width

---

## Best Practices

### 1. Keep Summary Concise
- 3-4 bullet points maximum
- Lead with most important information
- Use bold for emphasis on key terms

### 2. Use Appropriate Icons
- ✅ for positive signals
- ❌ for negative signals
- ⚠️ for warnings/maybes
- 💼 for business-related
- 🎯 for goals/targets
- 📊 for data/analytics
- 🚀 for growth/next steps

### 3. Recommendation Guidelines
- **YES (8-10/10):** Ideal client, pursue aggressively
- **MAYBE (6-7/10):** Qualified lead, needs nurturing/repositioning
- **NO (1-5/10):** Poor fit, decline or refer elsewhere

### 4. Investment Formatting
Use clear, scannable format:
```
💰 Investment: €15K-25K | ⏱️ Timeline: 6-8 weeks
📈 ROI: Free up 20 hours/week = €10K/week value
```

### 5. Next Steps Timeline
Use this format:
```html
<li><strong>Week 1:</strong> Action item with specific details</li>
<li><strong>Week 2-3:</strong> Follow-up action with context</li>
```

---

## Creating New Email Templates

When creating new themed templates:

1. **Copy this template as a starting point**
2. **Update the variables** to match your new use case
3. **Maintain responsive design** (use CSS grid with mobile breakpoints)
4. **Test on multiple devices** (desktop, tablet, mobile)
5. **Keep brand colors consistent** (purple gradient, success/warning/danger colors)
6. **Add clear instructions** in this README for the new template

---

## Example Templates to Create

Future templates for gmail-agent:

- **Campaign Performance Report** - Monthly/quarterly marketing metrics
- **Content Calendar Summary** - Upcoming content schedule
- **Lead Generation Report** - Weekly lead generation results
- **Social Media Analytics** - Platform-by-platform performance
- **Email Campaign Results** - Open rates, click rates, conversions
- **Partnership Proposal** - Outreach to potential partners
- **Event Invitation** - Professional event invites
- **Quarterly Business Review** - Executive summary for clients

---

## Support

For questions about using these templates, contact the MARKETING_TEAM research team or refer to the gmail-agent documentation:

- **Agent Definition:** `MARKETING_TEAM/.claude/agents/gmail-agent.md`
- **Tools:** `MARKETING_TEAM/tools/send_email_with_attachment.py`
- **Memory Config:** `MARKETING_TEAM/memory/email_config.json`

---

**Last Updated:** November 3, 2025
**Template Version:** 1.0
**Compatible With:** gmail-agent v1.0+