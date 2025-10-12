# ⚡ Quick Test Guide - Excel + Figma Authentication

## 🎯 **Before You Test (30 seconds)**

Run these commands to verify fixes are in place:

```bash
# 1. Check tools are restored
grep -c "playwright_scroll_page\|playwright_get_page_info" USER_STORY_AGENT/research_prompts.py
# Expected: 2 (one for each tool)

# 2. Check password selectors are explicit
grep -c "input\[type='password'\]" USER_STORY_AGENT/research_prompts.py
# Expected: 1

# 3. Run detection tests
cd USER_STORY_AGENT && python test_figma_detection.py
# Expected: "🎉 All tests passed!"
```

**All pass?** ✅ You're ready to test!

---

## 📝 **Test Case (Copy/Paste Ready)**

### **Excel Content:**
Create an Excel file with this in cell A1:

```
Dashboard Requirements:
- User analytics with charts
- Real-time data updates
- Export to CSV/PDF

Design:
Figma: https://figma.com/proto/YOUR_FIGMA_ID
Password: your-password-here
```

*(Replace with your actual Figma URL and password)*

---

## 🚀 **Run the Test**

```bash
cd USER_STORY_AGENT
streamlit run app_ui.py
```

**In the UI:**
1. Upload your Excel file
2. ✅ Enable "Browser & Research Mode"
3. ✅ Select "Autonomous" mode
4. ✅ Click "Generate Stories"

---

## 👀 **What to Watch For**

### **✅ SUCCESS INDICATORS:**

You should see these logs in order:

```
🎨 Detected Figma prototype: https://figma.com/proto/...
🔐 Password detected: you*** (will auto-fill)
  → Using selector: input[type='password']
  → Continue button: button:has-text('Continue')
  → Using specialized Figma navigation template

🚀 Starting Playwright MCP server...
✓ MCP server ready!

🤖 Calling Claude API with MCP tool support...

🔧 Tool: playwright_navigate
  Input: {"url": "https://figma.com/proto/..."}
✓ Result: Navigated successfully

🔧 Tool: playwright_fill
  Input: {"selector": "input[type='password']", "value": "your-password"}
✓ Result: Filled input

🔧 Tool: playwright_click
  Input: {"selector": "button:has-text('Continue')"}
✓ Result: Clicked button

🔧 Tool: playwright_press_key
  Input: {"key": "ArrowRight"}
✓ Result: Pressed key

🔧 Tool: playwright_screenshot
  Input: {"name": "screen_1", "fullPage": true}
✓ Result: Screenshot captured

... [more screens] ...

✓ Task complete after 14 iteration(s)

🔧 Parsing JSON response...
✓ Successfully parsed 8 user stories!

💾 Writing to user_stories.xlsx...
✓ Successfully saved 8 stories to Excel!
```

---

### **❌ FAILURE INDICATORS:**

**If you see this:**
```
Error: Unknown tool: playwright_scroll_page
```
→ **Problem:** Tools not restored
→ **Fix:** Run `git status` and ensure research_prompts.py has the fixes

**If you see this:**
```
Error: Selector not found: [some random selector]
```
→ **Problem:** Using wrong selector for password
→ **Fix:** Verify research_prompts.py has `input[type='password']`

**If you see this:**
```
⚠️ Reached max iterations (20)
Total response: 0 characters
```
→ **Problem:** Still hitting iteration limit
→ **Check:** Are there "Unknown tool" errors above? Those waste iterations

---

## 📊 **Expected Results**

### **Performance Metrics:**
- ⏱️ **Time:** 30-60 seconds total
- 🔄 **Iterations:** 12-16 out of 20 (with buffer)
- 📝 **Stories:** 6-10 comprehensive stories
- 📄 **Response:** 8,000-12,000 characters
- ✅ **Success rate:** ~95%

### **Story Quality:**
Stories should include:
- ✅ Exact Figma screen references
- ✅ Component names (Button.Primary, Card.Metric)
- ✅ Design specs (colors: #2563EB, typography: 32px/40px)
- ✅ Visual details (spacing: 16px grid, border radius: 8px)
- ✅ Both Excel requirements AND Figma design specs

---

## 🔍 **Quick Debugging**

### **Issue: MCP server won't start**
```bash
# Test MCP server manually
npx -y @executeautomation/playwright-mcp-server
# Should start without errors (Ctrl+C to stop)
```

### **Issue: Password not detected**
```bash
# Check detection logic
cd USER_STORY_AGENT
python -c "
from autonomous_mode import AutonomousAgent
agent = AutonomousAgent()
notes = '''
Figma: https://figma.com/proto/ABC
Password: test123
'''
result = agent._detect_figma_url(notes)
print(result)
"
# Expected: {'url': '...', 'password': 'test123'}
```

### **Issue: Authentication fails**
**Check Figma URL manually:**
1. Open Figma URL in browser
2. Does it show password prompt?
3. Try entering password manually
4. Verify button text is "Continue" (not "Submit" or "Login")

---

## 🎬 **Step-by-Step Video of What Happens**

1. **Agent reads Excel** → Finds Figma URL and password
2. **Logs show detection** → "🔐 Password detected: xxx***"
3. **MCP server starts** → "✓ MCP server ready!"
4. **Navigate to Figma** → `playwright_navigate`
5. **Fill password field** → `playwright_fill` with `input[type='password']`
6. **Click Continue** → `playwright_click` with `button:has-text('Continue')`
7. **Navigate screens** → `playwright_press_key` with `ArrowRight`
8. **Take screenshots** → `playwright_screenshot` with `fullPage: true`
9. **Generate stories** → Combines Excel + Figma data
10. **Save to Excel** → Download ready!

---

## ✅ **Success Checklist**

After test, verify:

- [ ] No "Unknown tool" errors in logs
- [ ] Password was detected and logged (with masking)
- [ ] Explicit selectors shown in logs
- [ ] `playwright_fill` used for password
- [ ] `playwright_click` used for Continue button
- [ ] Multiple screens navigated (ArrowRight key presses)
- [ ] Screenshots captured
- [ ] Stories generated (not 0!)
- [ ] Stories reference Figma screens
- [ ] Excel file downloaded successfully

**All checked?** 🎉 **You're good to go!**

---

## 📚 **Full Documentation**

- **Quick overview:** This file
- **Detailed fixes:** [FIXES_SUMMARY.md](FIXES_SUMMARY.md)
- **Technical report:** [VALIDATION_REPORT.md](VALIDATION_REPORT.md)
- **Pre-flight checks:** [PRE_FLIGHT_CHECKLIST.md](PRE_FLIGHT_CHECKLIST.md)

---

## 🆘 **Still Having Issues?**

1. Check [VALIDATION_REPORT.md](VALIDATION_REPORT.md) - Section "Troubleshooting"
2. Review logs carefully - error messages are descriptive
3. Verify Figma URL is accessible (try in browser first)
4. Ensure password is correct (copy/paste to avoid typos)
5. Check MCP server logs for connection issues

---

## 🎯 **TL;DR**

**Before testing:**
```bash
grep "playwright_scroll_page" USER_STORY_AGENT/research_prompts.py  # Should find it
python USER_STORY_AGENT/test_figma_detection.py  # Should pass all
```

**During testing:**
- Watch for: "🔐 Password detected: xxx***"
- Watch for: "Using selector: input[type='password']"
- Watch for: "✓ Successfully parsed X user stories!"

**Success = No "Unknown tool" errors + Stories generated + Excel downloaded**

🚀 **You're ready to test!**
