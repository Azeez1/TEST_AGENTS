# Excel + Figma Autonomous Workflow Guide

## 🎯 **Overview**

The USER_STORY_AGENT now **automatically detects Figma URLs** in your uploaded files and seamlessly combines:
- **Excel requirements** (functional specifications)
- **Figma designs** (visual specifications, components, screens)
- **Autonomous research** (best practices, standards)

into comprehensive, production-ready user stories.

---

## ✨ **New Capabilities**

### **Automatic Figma Detection**
- ✅ Detects Figma URLs in Excel cells, meeting notes, or text
- ✅ Auto-extracts passwords if provided
- ✅ Uses specialized Figma navigation template
- ✅ No manual browser instructions needed!

### **Smart Routing**
**Priority Order:**
1. **Figma URL detected** → Use Figma template
2. **Manual instructions provided** → Use guided mode
3. **Domain detected** → Use domain research
4. **Fallback** → Use general autonomous research

---

## 📝 **How to Use**

### **Step 1: Prepare Your Excel File**

Create an Excel file with requirements. **Include Figma URL anywhere:**

**Example: requirements.xlsx**

| Feature | Requirements | Figma | Notes |
|---------|-------------|-------|-------|
| User Dashboard | Analytics charts, filters, export | https://figma.com/proto/ABC123 | Password: demo-pass |
| Login Page | Email/password, remember me, SSO | https://figma.com/file/XYZ789 | |

**Alternative format (free-form in single cell):**
```
Dashboard Requirements:
- Real-time analytics charts
- Date range filtering
- Export to CSV/PDF

Figma prototype: https://www.figma.com/proto/ABC123XYZ
Password: tower-film-great-letter
```

### **Step 2: Upload to USER_STORY_AGENT**

1. Open Streamlit app: `streamlit run app_ui.py`
2. Go to **Tab 1: Generate Stories**
3. Choose: **Upload File**
4. Select your Excel file
5. Enable: **Browser & Research Mode** ✓
6. Select: **Autonomous (Agent decides)**
7. Click: **Generate User Stories**

### **Step 3: Agent Works Automatically**

**What the agent does (no intervention needed):**

```
🔍 Parsing Excel → Extract requirements
🎨 Detected Figma prototype: https://figma.com/proto/ABC123...
🔐 Password detected (will auto-fill)
🌐 Starting Playwright MCP server...
🚀 Navigating to Figma...
🔐 Entering password: demo-pass
⌨️ Pressing ArrowRight to navigate screens...
📸 Taking screenshots of Screen 1/5...
📋 Extracting design components...
⌨️ Navigating to Screen 2/5...
📸 Taking screenshots...
✨ Combining Excel requirements + Figma designs...
📝 Generating comprehensive user stories...
✓ Generated 8 stories successfully!
```

### **Step 4: Review Generated Stories**

**Stories will include:**
- ✅ Exact component names from Figma (e.g., "Button.Primary", "Card.Metric")
- ✅ Design specs (colors, spacing, typography)
- ✅ Functional requirements from Excel
- ✅ Screen references ("Figma Screen 1-3")
- ✅ Visual design patterns observed
- ✅ Interaction patterns from prototype

---

## 💡 **Example Workflows**

### **Workflow 1: Dashboard Feature**

**Input: Excel Cell**
```
Feature: Analytics Dashboard
Requirements:
- Line chart showing user growth
- Bar chart for feature usage
- Date range filter (7d, 30d, custom)
- Export button (CSV, PDF)

Figma: https://figma.com/proto/DASH2024
Password: analytics-demo
```

**Agent Actions:**
1. Detects Figma URL and password
2. Navigates to Figma prototype
3. Enters password automatically
4. Explores all 4 dashboard screens
5. Takes screenshots of each screen
6. Extracts component names:
   - "DatePicker.Range"
   - "Card.Metric" (used 4 times)
   - "Chart.Line"
   - "Chart.Bar"
   - "Button.Export"
7. Notes colors: Primary #2563EB, Success #10B981
8. Combines with Excel requirements
9. Generates stories

**Generated Story Example:**
```json
{
  "user_story": "As a data analyst, I want to view analytics dashboard with interactive charts, so that I can track user behavior trends",
  "feature_epic": "Analytics Dashboard",
  "acceptance_criteria": [
    "1. Dashboard Page displays (Figma Screen 1):\n   a. Header: 'Analytics Dashboard' (Typography: Heading.H1)\n   b. Date Range Filter (Component: DatePicker.Range)\n      i. Default selection: Last 30 days\n      ii. Quick options: Today, 7 days, 30 days, Custom range\n      iii. Color scheme: Primary blue #2563EB\n   c. Four Metric Cards (Component: Card.Metric, repeated 4x):\n      i. Total Users (with +12% trend indicator in green)\n      ii. Active Sessions (with percentage change)\n      iii. Conversion Rate (color-coded: green if >5%, red if <2%)\n      iv. Revenue (formatted as currency)",
    "2. Interactive Charts (Figma Screens 2-3):\n   a. Line Chart: User growth over time (Component: Chart.Line)\n      i. Hover tooltip shows exact values and date\n      ii. Click data point to drill down to detailed view\n   b. Bar Chart: Feature usage comparison (Component: Chart.Bar)\n      i. Bars use gradient from light to dark blue\n      ii. Horizontal axis labels rotated 45° for readability",
    "3. Export Functionality (Figma Screen 4):\n   a. Export Button (Component: Button.Export, top right corner)\n      i. Style: Secondary button, icon: download\n      ii. Clicking opens modal with format options: CSV, PDF, Excel\n      iii. Downloaded file includes all visible data for selected date range",
    "Notes:\n- Performance: Dashboard loads within 2 seconds, charts animate smoothly (300ms transitions)\n- Design: Follows Figma design system exactly - Primary: #2563EB, Success: #10B981, spacing: 16px grid\n- Accessibility: Charts have ARIA labels, keyboard navigable, screen reader compatible\n- Responsive: Mobile view stacks cards vertically, charts adapt to screen width"
  ],
  "business_case": "Analytics dashboard enables data-driven decision making by providing real-time insights into user behavior, improving product strategy and increasing ROI by 25%",
  "relevant_pages": "Dashboard.Analytics, Dashboard.Main (Figma Screens 1-4)"
}
```

---

### **Workflow 2: Multi-File Context**

**Upload Multiple Files:**
1. `requirements.xlsx` - Functional specs
2. `user_research.pdf` - User interview findings
3. `meeting_notes.txt` - Contains Figma URL

**Meeting Notes (meeting_notes.txt):**
```
Product Team Meeting - 2024-01-15

Discussed new onboarding flow
- Need to reduce signup friction
- Add social login options
- Tooltips for first-time users

Design mockups ready: https://figma.com/proto/ONBOARD2024?password=signup-flow

Reference existing apps:
- Notion's onboarding
- Slack's guided tour
```

**Agent Actions:**
1. Combines all 3 files into unified context
2. Detects Figma URL in meeting notes
3. Extracts password: "signup-flow"
4. Navigates Figma onboarding flow (5 screens)
5. Researches Notion and Slack onboarding (mentioned in notes)
6. Combines:
   - Excel requirements (functional specs)
   - PDF research (user insights)
   - Meeting notes (context)
   - Figma designs (visual specs)
   - Competitive research (best practices)
7. Generates comprehensive stories

---

## 🔍 **Supported Formats**

### **Figma URL Formats**
```
✅ https://www.figma.com/proto/ABC123...
✅ https://figma.com/proto/XYZ789...
✅ https://www.figma.com/file/FILE123...
✅ http://figma.com/proto/... (auto-upgraded to HTTPS)
```

### **Password Formats**
The agent detects passwords in various formats:

```
✅ Password: demo-pass
✅ password: secret123
✅ Pass: mypass
✅ Pwd: test456
✅ pw: abc123
```

**Context-aware:** Looks within 200 characters before/after Figma URL

---

## 📊 **What Gets Generated**

### **From Excel:**
- Functional requirements
- Business logic
- Validation rules
- User workflows

### **From Figma:**
- Exact component names
- Design tokens (colors, typography, spacing)
- Screen layouts
- Interaction patterns
- Visual hierarchy
- Responsive behavior observed

### **Combined Result:**
- **Comprehensive stories** with both functional and visual specs
- **Exact component references** for developers
- **Design specifications** for QA testing
- **Screen mappings** for easy navigation

---

## 🛠️ **Troubleshooting**

### **Issue: Figma URL not detected**

**Check:**
- ✅ URL starts with `http://` or `https://`
- ✅ URL contains `figma.com/proto/` or `figma.com/file/`
- ✅ No extra characters breaking the URL

**Test with:**
```python
python test_figma_detection.py
```

### **Issue: Password not extracted**

**Ensure password is within 200 characters of Figma URL:**
```
# ✅ Good
Figma: https://figma.com/proto/ABC
Password: demo

# ❌ Too far (>200 chars apart)
Figma: https://figma.com/proto/ABC
[200+ characters of other text]
Password: demo
```

### **Issue: Agent doesn't navigate Figma**

**Verify:**
1. MCP server installed: `npm install -g @executeautomation/playwright-mcp-server`
2. Chromium installed: `npx playwright install chromium`
3. Browser mode enabled in UI
4. Check activity log for errors

---

## 🎯 **Best Practices**

### **1. Organize Excel Clearly**
```
Feature Column | Requirements Column | Figma Column | Password Column
```

### **2. Include Context**
Add meeting notes, user research, or background info in Excel cells

### **3. Test Figma Access**
Verify Figma URL is accessible and password works before running

### **4. Use Descriptive Feature Names**
Helps agent understand what to look for in Figma designs

### **5. Multiple Figma Links**
If you have multiple Figma files, put them in separate Excel rows with associated requirements

---

## 🚀 **Advanced Usage**

### **Combine with Feedback**
Add feedback to teach agent your preferences:

**Tab 6: Autonomous & Feedback → Add Feedback:**
```
Always reference exact Figma component names
Include color hex codes in acceptance criteria
Specify font sizes from design system
Mention responsive breakpoints
```

**Result:** All future generations will apply these preferences!

### **Guided Mode Override**
If you want manual control despite Figma detection:

1. Enable "Guided (Provide instructions)"
2. Enter specific instructions
3. Agent follows your instructions instead of auto-Figma template

---

## 📈 **Results You Can Expect**

### **Before Enhancement:**
```
User Story: As a user, I want to view dashboard

Acceptance Criteria:
- Display analytics charts
- Show user metrics
- Allow filtering by date
```

### **After Enhancement (Excel + Figma):**
```
User Story: As a data analyst, I want to view analytics dashboard with interactive charts, so that I can track user behavior trends

Acceptance Criteria:
1. Dashboard Page displays (Figma Screen 1):
   a. Header: "Analytics Dashboard" (Typography: Heading.H1, Color: #1E293B)
   b. Date Range Filter (Component: DatePicker.Range)
      i. Default selection: Last 30 days
      ii. Quick options: Today, 7 days, 30 days, Custom range (Figma Screen 1)
      iii. Styling: Primary blue #2563EB, border-radius: 8px
   c. Four Metric Cards (Component: Card.Metric, Grid: 2x2)
      i. Total Users: 12,543 (+12% trend indicator, Color: Success #10B981)
      ii. Active Sessions: 3,421 (Figma Screen 1, Card position: top-right)
      iii. Conversion Rate: 4.2% (conditional coloring: green >5%, red <2%)
      iv. Revenue: $45,123 (formatted with currency symbol and commas)

2. Interactive Charts (Figma Screens 2-3):
   a. Line Chart: User growth over time (Component: Chart.Line, Height: 400px)
      i. Hover tooltip shows: {date}, {value}, {change %}
      ii. Click data point opens drill-down modal (Figma Screen 3)
      iii. Gradient fill: from Primary #2563EB to transparent
   b. Bar Chart: Feature usage comparison (Component: Chart.Bar)
      i. Bars use gradient: light to dark blue (#60A5FA to #2563EB)
      ii. X-axis labels rotated 45° for readability
      iii. Animated on load: bars grow from 0 to value (300ms duration)

3. Export Functionality (Figma Screen 4):
   a. Export Button (Component: Button.Export, Position: top-right corner)
      i. Style: Secondary button style, Icon: download-icon (16x16px)
      ii. Hover state: background changes to #EFF6FF (from Figma)
      iii. Clicking opens export modal (Component: Modal.Export, Figma Screen 4)
         1. Format options: Radio buttons for CSV, PDF, Excel
         2. Date range: Pre-populated with current filter selection
         3. Download button: Primary style, full-width in modal
      iv. Downloaded file naming: "analytics-dashboard-{date}-{format}"

4. Responsive Behavior (Figma responsive variants observed):
   a. Desktop (>1024px): Cards in 2x2 grid, charts side-by-side
   b. Tablet (768-1023px): Cards in 2x2 grid, charts stacked
   c. Mobile (<768px): Cards stacked vertically, charts full-width

Notes:
- Performance: Dashboard loads within 2 seconds (target from Excel), charts animate smoothly (300ms transitions from Figma)
- Design Tokens: Follows Figma design system exactly
  * Colors: Primary #2563EB, Success #10B981, Neutral #64748B
  * Typography: Heading.H1 (32px/40px), Body.Regular (16px/24px)
  * Spacing: 16px base grid (from Figma spacing system)
  * Border Radius: 8px for cards/buttons (from Figma components)
- Accessibility: All charts have ARIA labels, keyboard navigable (tab order matches Figma layout), screen reader compatible
- Analytics: Track dashboard views, export downloads, chart interactions, filter changes
```

**Improvement:**
- ✅ **10x more specific** with exact component names
- ✅ **Design specs included** (colors, spacing, typography)
- ✅ **Screen references** for easy navigation
- ✅ **Visual details** for pixel-perfect implementation
- ✅ **Ready for developers** - no ambiguity

---

## 🎉 **Summary**

**You can now:**
1. ✅ Upload Excel with requirements + Figma URL
2. ✅ Enable autonomous mode
3. ✅ Agent auto-detects Figma, navigates automatically
4. ✅ Combines Excel functional specs + Figma visual specs
5. ✅ Generates comprehensive, implementation-ready stories

**No manual browser instructions needed!** 🚀

---

## 📞 **Support**

**Test your setup:**
```bash
python test_figma_detection.py
```

**Check MCP status:**
- Open app → Tab 6 → About Autonomous Mode → Configuration section

**Report issues:**
- GitHub: [Your repo]/issues
- Include: Excel sample, Figma URL (public test URL), error logs
