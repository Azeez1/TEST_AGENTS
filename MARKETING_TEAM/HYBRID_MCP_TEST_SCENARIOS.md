# Marketing Team Hybrid MCP Implementation - Test Scenarios

**Date:** October 13, 2025
**Status:** ✅ All 15 agents updated with role-specific MCP tools
**Approach:** Hybrid (Custom tools + Root MCP tools)

---

## 🎯 What Was Implemented

### Hybrid Architecture

**Custom Tools (Preserved):**
- `send_gmail`, `create_gmail_draft`, `send_email_campaign` - Rate limiting & campaign logic
- `upload_to_google_drive` - Marketing folder structure
- `generate_image`, `generate_video` - OpenAI integration
- `generate_pdf`, `generate_powerpoint` - Document generation
- Router tools, platform formatters, brand voice tools

**MCP Tools (Added from Root):**
- **Google Workspace MCP:** Docs, Sheets, Calendar, Slides, Forms, Gmail (backup)
- **Playwright MCP:** Browser automation for research

---

## 📋 Test Scenarios

### Test 1: Copywriter + Google Docs ✍️

**Agent:** Copywriter
**New MCP Tools:** `mcp__google_workspace__create_doc`, `mcp__google_workspace__update_doc`

**Test Command:**
```
Use the copywriter subagent to write a 300-word blog introduction about "The Future of AI in Marketing" and save it directly to a Google Doc titled "AI Marketing Blog Intro"
```

**Expected Outcome:**
- ✅ Copywriter writes compelling 300-word intro
- ✅ Creates a Google Doc with proper formatting
- ✅ Returns Google Doc URL
- ✅ Content follows brand voice guidelines

**What to Verify:**
- [ ] Google Doc was created
- [ ] Content quality is high
- [ ] Formatting is clean (headings, paragraphs)
- [ ] No errors during creation

---

### Test 2: Analyst + Google Sheets 📊

**Agent:** Analyst
**New MCP Tools:** `mcp__google_workspace__create_sheet`, `mcp__google_workspace__update_sheet`, `mcp__google_workspace__read_sheet`

**Test Command:**
```
Use the analyst subagent to create a campaign metrics tracking dashboard in Google Sheets with the following KPIs: Impressions, Clicks, CTR, Conversions, Cost per Conversion, ROI. Include sample data for a week.
```

**Expected Outcome:**
- ✅ Creates Google Sheet with professional structure
- ✅ Headers: Date, Impressions, Clicks, CTR, Conversions, CPC, ROI
- ✅ Sample data for 7 days
- ✅ Formulas for calculated fields (CTR, ROI)
- ✅ Returns Google Sheets URL

**What to Verify:**
- [ ] Sheet was created successfully
- [ ] Headers are properly formatted
- [ ] Sample data looks realistic
- [ ] Formulas work correctly
- [ ] Professional layout

---

### Test 3: SEO Specialist + Playwright 🔍

**Agent:** SEO Specialist
**New MCP Tools:** `mcp__playwright__*`, `mcp__google_workspace__create_sheet`

**Test Command:**
```
Use the seo-specialist subagent to research "AI marketing automation" trends. Navigate to Google Trends or a marketing blog, extract key insights, and create a keyword tracking sheet in Google Sheets.
```

**Expected Outcome:**
- ✅ Uses Playwright to navigate to relevant websites
- ✅ Extracts trend data and keyword insights
- ✅ Creates Google Sheet with keyword tracking
- ✅ Provides actionable SEO recommendations

**What to Verify:**
- [ ] Browser automation worked
- [ ] Extracted real trend data
- [ ] Sheet contains keyword rankings
- [ ] Recommendations are actionable

---

### Test 4: Content Strategist + Calendar 📅

**Agent:** Content Strategist
**New MCP Tools:** `mcp__google_workspace__create_calendar_event`, `mcp__google_workspace__create_sheet`, `mcp__google_workspace__create_doc`

**Test Command:**
```
Use the content-strategist subagent to plan a product launch campaign for next Monday at 9am. Schedule the launch as a Google Calendar event and create a campaign tracking sheet.
```

**Expected Outcome:**
- ✅ Creates Google Calendar event titled "Product Launch Campaign"
- ✅ Scheduled for next Monday at 9:00 AM
- ✅ Creates campaign tracking sheet with timeline
- ✅ Provides campaign strategy overview

**What to Verify:**
- [ ] Calendar event was created
- [ ] Date/time are correct
- [ ] Event has proper description
- [ ] Tracking sheet was created
- [ ] Campaign plan is comprehensive

---

### Test 5: Gmail Agent + Custom Tools (Rate Limiting) 📧

**Agent:** Gmail Agent
**Tools:** Custom (PRIMARY) + MCP (BACKUP)

**Test Command:**
```
Use the gmail-agent subagent to send a test email to test@example.com with subject "MCP Integration Test" and body "Testing the hybrid MCP approach with custom rate limiting."
```

**Expected Outcome:**
- ✅ Uses CUSTOM `send_gmail` tool (not MCP)
- ✅ Email sent successfully
- ✅ Rate limit tracking updated
- ✅ Returns sent count and limit remaining

**What to Verify:**
- [ ] Email was sent
- [ ] Used custom tool (check logs for tool name)
- [ ] Rate limiting is active (shows "sent_today: X, limit_remaining: Y")
- [ ] NOT using MCP tool (custom is priority)

**Critical:** This test validates that custom tools are still primary!

---

### Test 6: Presentation Designer + Google Slides 📊

**Agent:** Presentation Designer
**New MCP Tools:** `mcp__google_workspace__create_slides`

**Test Command:**
```
Use the presentation-designer subagent to create a 3-slide Google Slides presentation about "Marketing ROI Metrics". Slides should be: (1) Title, (2) Key Metrics Overview, (3) ROI Formula.
```

**Expected Outcome:**
- ✅ Creates Google Slides presentation
- ✅ 3 slides with proper content
- ✅ Professional formatting
- ✅ Returns Google Slides URL

**What to Verify:**
- [ ] Slides presentation was created
- [ ] All 3 slides have content
- [ ] Formatting is professional
- [ ] Can be edited in Google Slides

---

### Test 7: Research Agent + Playwright + Docs 🔬

**Agent:** Research Agent
**New MCP Tools:** `mcp__playwright__*`, `mcp__google_workspace__create_doc`

**Test Command:**
```
Use the research-agent subagent to research "top marketing trends 2025" using browser automation, then document findings in a Google Doc titled "2025 Marketing Trends Research".
```

**Expected Outcome:**
- ✅ Uses Playwright to browse and extract data
- ✅ Comprehensive research with citations
- ✅ Creates Google Doc with formatted findings
- ✅ Returns Doc URL

**What to Verify:**
- [ ] Browser automation executed
- [ ] Research is thorough and cited
- [ ] Google Doc was created
- [ ] Findings are well-structured

---

### Test 8: Multi-Agent Coordination 🎭

**Agents:** Content Strategist → Copywriter → Analyst
**Test:** Full workflow with multiple MCP tools

**Test Command:**
```
Use the content-strategist subagent to create a mini marketing campaign:
1. Have the copywriter write a 400-word blog post in Google Docs
2. Have the analyst create a metrics tracking sheet
3. Schedule the campaign launch for next Friday at 10am in Google Calendar
```

**Expected Outcome:**
- ✅ Content Strategist coordinates all agents
- ✅ Copywriter creates Google Doc with blog post
- ✅ Analyst creates Google Sheets dashboard
- ✅ Calendar event scheduled for Friday 10am
- ✅ All deliverables returned with URLs

**What to Verify:**
- [ ] All 3 tasks completed successfully
- [ ] Agents were called in sequence
- [ ] All Google Workspace items created
- [ ] Campaign is cohesive and coordinated

---

## 🔧 Troubleshooting

### If Google Workspace MCP Tools Fail:

**Check 1: MCP Server Running**
```bash
# From TEST_AGENTS root:
python -m uv tool run workspace-mcp --tool-tier core
```
Should start server without errors.

**Check 2: OAuth Credentials**
- Verify `GOOGLE_OAUTH_CLIENT_ID` in `.env` or `.mcp.json`
- Verify `GOOGLE_OAUTH_CLIENT_SECRET` is correct
- Check `OAUTHLIB_INSECURE_TRANSPORT=1` is set

**Check 3: MCP Configuration**
- Verify `.mcp.json` at TEST_AGENTS root has `google_workspace` server
- Restart Claude Code to reload MCP servers

**Check 4: Agent Working Directory**
- Run agents from `TEST_AGENTS/` root (not `MARKETING_TEAM/` subdirectory)
- MCP config is at root level

### If Playwright MCP Tools Fail:

**Check 1: Playwright Installed**
```bash
npx playwright install
```

**Check 2: MCP Server Running**
```bash
npx -y @microsoft/playwright-mcp
```

### If Custom Tools Fail:

**Check 1: Credentials Missing**
```bash
cd MARKETING_TEAM
ls gmail_credentials.json   # Should exist
ls credentials.json         # Should exist
```

**Check 2: Python Dependencies**
```bash
cd MARKETING_TEAM
pip install -r requirements.txt
```

**Check 3: .env File**
Verify `MARKETING_TEAM/.env` contains:
- `OPENAI_API_KEY`
- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`

---

## ✅ Success Criteria

### For Each Test:
- [ ] Agent completes task without errors
- [ ] MCP tools are accessible and functional
- [ ] Custom tools still work as expected
- [ ] Output quality is high
- [ ] URLs are returned and accessible

### For Overall System:
- [ ] Hybrid approach works (custom + MCP)
- [ ] No conflicts between custom and MCP tools
- [ ] Gmail Agent prioritizes custom tools (rate limiting preserved)
- [ ] New capabilities work (Docs, Sheets, Calendar, Slides)
- [ ] Multi-agent coordination functions properly

---

## 📊 Test Results Template

Copy this for each test:

```
### Test X: [Test Name]
**Date/Time:** [timestamp]
**Agent:** [agent name]
**Status:** ✅ PASS / ❌ FAIL / ⚠️ PARTIAL

**What Worked:**
-

**What Failed:**
-

**Errors:**
```
[error messages if any]
```

**Notes:**
-

**Output URLs:**
- Google Doc:
- Google Sheet:
- Google Calendar:
- Google Slides:
```

---

## 🚀 Next Steps After Testing

### If All Tests Pass:
1. ✅ Document which tools are used most frequently
2. ✅ Create best practices guide for agents
3. ✅ Train team on hybrid approach
4. ✅ Monitor usage and optimize

### If Some Tests Fail:
1. 🔍 Identify root cause (MCP server, credentials, agent config)
2. 🔧 Fix issues one by one
3. 🔄 Re-test failed scenarios
4. 📝 Document solutions

### If MCP Tools Don't Work:
1. ⚡ Keep using custom tools (they're proven)
2. 🔧 Debug MCP configuration separately
3. 📖 Consult workspace-mcp documentation
4. 🤝 Consider alternative: expand custom tools instead

---

## 📚 Reference

### Agent Tool Summary

| Agent | Custom Tools | MCP Tools (New) |
|-------|-------------|----------------|
| Copywriter | brand_voice | create_doc, update_doc |
| Editor | brand_voice | create_doc, update_doc |
| Analyst | WebSearch, WebFetch | create_sheet, update_sheet, read_sheet |
| SEO Specialist | WebSearch, WebFetch | playwright__*, create_sheet |
| Social Media Manager | format_platform | (none - complete as-is) |
| Visual Designer | generate_image, brand_guidelines | upload_to_drive |
| Video Producer | generate_video, upload_drive | upload_to_drive |
| Email Specialist | brand_voice, save_content | create_doc |
| Gmail Agent | send_gmail, create_draft, campaign | send_email, create_draft (backup) |
| PDF Specialist | generate_pdf, upload_drive | upload_to_drive |
| Presentation Designer | generate_ppt, upload_drive | create_slides, upload_to_drive |
| Content Strategist | (coordination only) | create_calendar_event, create_sheet, create_doc |
| Research Agent | perplexity, WebSearch, WebFetch | playwright__*, create_doc |
| Router Agent | classify_intent, select_agents | (none - routing only) |

### MCP Tool Categories

**Google Workspace MCP Tools:**
- `mcp__google_workspace__create_doc`
- `mcp__google_workspace__update_doc`
- `mcp__google_workspace__create_sheet`
- `mcp__google_workspace__update_sheet`
- `mcp__google_workspace__read_sheet`
- `mcp__google_workspace__create_calendar_event`
- `mcp__google_workspace__create_slides`
- `mcp__google_workspace__upload_to_drive`
- `mcp__google_workspace__send_email` (backup)
- `mcp__google_workspace__create_draft` (backup)

**Playwright MCP Tools:**
- `mcp__playwright__navigate`
- `mcp__playwright__screenshot`
- `mcp__playwright__click`
- `mcp__playwright__fill`
- `mcp__playwright__get_visible_text`
- `mcp__playwright__evaluate`
- (and many more browser automation tools)

---

## 🎯 Implementation Complete!

**Status:** ✅ All 15 agents updated with role-specific MCP tools
**Next:** Run test scenarios above to validate functionality
**Goal:** Prove hybrid approach works (custom + MCP best of both worlds)

Good luck with testing! 🚀
