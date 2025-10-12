# Figma Prototype Navigation Guide

**Date:** October 12, 2025
**Version:** 2.0 - Enhanced with Full Scrolling & Keyboard Navigation

---

## Overview

The USER_STORY_AGENT now has **enhanced Figma prototype navigation capabilities** including:
- ✅ Password-protected prototype access
- ✅ Keyboard navigation (arrow keys, restart)
- ✅ Full page scrolling to capture entire screens
- ✅ Screenshot capture with fullPage option
- ✅ Automatic screen exploration
- ✅ Design-to-user-story generation

---

## New Playwright Tools (3 Added)

### 1. `playwright_press_key`
**Purpose:** Press keyboard keys for navigation

**Use Cases:**
- Navigate Figma prototypes (→ next, ← previous, r restart)
- Navigate image carousels
- Navigate presentations
- Interactive prototypes
- Keyboard-only interfaces

**Parameters:**
- `key` (required): Key to press
  - `ArrowRight` - Next screen/slide
  - `ArrowLeft` - Previous screen/slide
  - `ArrowUp` - Scroll up
  - `ArrowDown` - Scroll down
  - `Enter` - Confirm/submit
  - `Escape` - Cancel/close
  - `r` - Restart
  - Any other key

**Example:**
```json
{
  "name": "playwright_press_key",
  "input": {
    "key": "ArrowRight"
  }
}
```

---

### 2. `playwright_scroll_page`
**Purpose:** Scroll entire page to capture full content

**Use Cases:**
- Long pages with scrollable content
- Dashboards with hidden content
- Detailed design screens
- Content below the fold
- Infinite scroll pages

**Parameters:**
- `direction` (required): Direction to scroll
  - `"down"` - Scroll down
  - `"up"` - Scroll up
  - `"bottom"` - Scroll to page bottom
  - `"top"` - Scroll to page top
- `amount` (optional): Pixels to scroll (default varies by direction)

**Examples:**
```json
{
  "name": "playwright_scroll_page",
  "input": {
    "direction": "down",
    "amount": 800
  }
}
```

```json
{
  "name": "playwright_scroll_page",
  "input": {
    "direction": "bottom"
  }
}
```

---

### 3. `playwright_get_page_info`
**Purpose:** Get current page information

**Returns:**
- Current URL
- Page title
- Visible text content

**Parameters:**
None required

**Example:**
```json
{
  "name": "playwright_get_page_info",
  "input": {}
}
```

---

## How to Use with Figma Prototypes

### Method 1: Via UI (Tab 1 - Generate Stories)

1. **Upload or paste meeting notes**

2. **Enable Browser & Research Mode**
   - Check the "Enable Browser & Research Mode" checkbox
   - Select "Guided (Provide instructions)"

3. **Enter Figma instructions:**
```
Navigate to https://www.figma.com/proto/[your-proto-id]
Password: your-password-here
Explore all screens using arrow keys
Take screenshots with fullPage: true
Scroll each screen to see all content
Generate stories for each screen
```

4. **Click "Generate User Stories"**

5. **Watch the live activity log** showing:
   - Browser launching
   - Password entry
   - Screen navigation
   - Screenshots captured
   - Content extraction

---

### Method 2: Programmatically

```python
from research_prompts import ResearchPrompts
from autonomous_mode import AutonomousAgent

# Generate Figma-specific prompt
prompt = ResearchPrompts.get_figma_prototype_prompt(
    notes="Meeting notes about authentication flow",
    figma_url="https://www.figma.com/proto/...",
    password="tower-film-great-letter",
    ac_format="gherkin"  # or "explicit"
)

# Create autonomous agent
agent = AutonomousAgent(
    output_file="figma_stories.xlsx",
    enable_browser=True
)

# Generate stories
success, stories, message = await agent.generate_from_notes(
    notes_input="notes.txt",
    ac_format="gherkin",
    browser_instructions=prompt
)
```

---

### Method 3: Direct Browser Automation

```python
from mcp_client import PlaywrightMCPClient

client = PlaywrightMCPClient()
await client.start_server()

# Navigate to Figma
await client.call_with_tools("""
Navigate to https://www.figma.com/proto/[id]
Fill password field with: your-password
Click Continue button
Press ArrowRight to go to next screen
Scroll page to bottom
Take fullPage screenshot
""")

await client.stop_server()
```

---

## Complete Figma Navigation Workflow

### Step-by-Step Process

**1. Initial Navigation**
```
playwright_navigate → Figma prototype URL
```

**2. Password Entry (if needed)**
```
playwright_fill → input[type="password"], "your-password"
playwright_click → button:has-text("Continue")
```

**3. Screen Exploration Loop**
```
For each screen (1 to N):
  1. playwright_get_page_info → Get current screen info
  2. playwright_screenshot → Capture initial view (fullPage: false)
  3. playwright_scroll_page → direction: "bottom"
  4. playwright_screenshot → Capture full scroll (fullPage: true)
  5. playwright_press_key → "ArrowRight" (next screen)
```

**4. Analysis & Generation**
- Extract design elements from screenshots
- Document UI components and patterns
- Generate user stories with design specifications

---

## Figma-Specific Prompt Template

The `get_figma_prototype_prompt()` method generates prompts with:

### Included Instructions:
1. URL navigation with password entry
2. Keyboard navigation guide (←/→/r)
3. Screenshot capture (with fullPage option)
4. Full page scrolling directives
5. Screen counter awareness (X / Y indicator)
6. Component documentation requirements
7. JSON format specifications
8. AC format selection (Gherkin or Explicit/Detailed)

### Generated Stories Include:
- Screen-by-screen breakdown
- User flows through prototype
- UI component specifications
- Visual design patterns
- Color schemes and typography
- Interaction patterns
- Accessibility considerations
- References to specific Figma screens

---

## Best Practices

### For Password-Protected Prototypes:
1. Always provide password in the instructions
2. Wait for page load after password entry
3. Check for success before proceeding

### For Multi-Screen Prototypes:
1. Start at screen 1/N
2. Navigate sequentially with ArrowRight
3. Take screenshots before AND after scrolling
4. Track screen numbers
5. Press 'r' to restart if needed

### For Full Content Capture:
1. Take initial screenshot (visible area)
2. Scroll to bottom
3. Take fullPage screenshot
4. Compare both to ensure no missed content

### For Complex Designs:
1. Document component hierarchy
2. Note colors, fonts, spacing
3. Capture interaction states (hover, active, disabled)
4. Document responsive behaviors
5. Note animations or transitions

---

## Troubleshooting

### Issue: "Can't click Continue button"
**Solution:** Use keyboard entry instead:
```python
playwright_press_key → "Enter"
```

### Issue: "Screen content cut off"
**Solution:** Use fullPage screenshot:
```json
{
  "fullPage": true
}
```

### Issue: "Can't navigate to next screen"
**Solution:** Use keyboard instead of clicking:
```python
playwright_press_key → "ArrowRight"
```

### Issue: "iframe content not visible"
**Solution:** Figma prototypes are in iframes - keyboard navigation works better than direct clicks

### Issue: "Content below fold not captured"
**Solution:** Scroll before screenshot:
```python
playwright_scroll_page → direction: "bottom"
playwright_screenshot → fullPage: true
```

---

## Examples

### Example 1: Simple Figma Exploration

**Input:**
```
Navigate to https://www.figma.com/proto/abc123
Password: demo-password
Explore all 4 screens
Generate stories
```

**Agent Actions:**
1. Opens browser
2. Navigates to URL
3. Enters password
4. Presses ArrowRight 4 times
5. Takes screenshots of each screen
6. Extracts UI elements
7. Generates 4 user stories (one per screen)

---

### Example 2: Detailed Design Analysis

**Input:**
```
Navigate to https://www.figma.com/proto/xyz789
Password: secure-pass-123
For each screen:
  - Take fullPage screenshot
  - Scroll entire page
  - Document all buttons, inputs, and components
  - Note color schemes
  - Check for accessibility features
Generate comprehensive stories with design specs
```

**Agent Actions:**
1. Opens browser
2. Navigates + enters password
3. For each screen:
   - Screenshots initial view
   - Scrolls to bottom
   - Screenshots full page
   - Extracts visible text and elements
   - Documents color, typography, spacing
4. Generates detailed stories with:
   - Component specifications
   - Visual design references
   - Accessibility requirements
   - Interaction patterns

---

### Example 3: Comparison with Notes

**Notes:**
```
Authentication flow design
- Login screen
- Two-factor auth
- Success state
- Error handling
```

**Figma URL:** https://www.figma.com/proto/auth-flow
**Password:** auth-demo

**Result:**
- 4 user stories matching the 4 screens
- Each story references Figma components
- Design specifications included in ACs
- Visual patterns documented

---

## Tool Count

**Total Playwright Tools:** 8
1. playwright_navigate
2. playwright_screenshot
3. playwright_click
4. playwright_fill
5. playwright_evaluate
6. **playwright_press_key** ← NEW
7. **playwright_scroll_page** ← NEW
8. **playwright_get_page_info** ← NEW

---

## Configuration

### Enable in MCP Config

`.mcp.json`:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server"]
    }
  }
}
```

### Enable in Settings

`.claude/settings.local.json`:
```json
{
  "enabledMcpjsonServers": ["playwright"],
  "permissions": {
    "allow": [
      "Bash(npx @executeautomation/playwright-mcp-server:*)"
    ]
  }
}
```

---

## Testing

Run the test suite:
```bash
python test_figma_navigation.py
```

**Expected Output:**
```
✓ Navigate instruction
✓ Password instruction
✓ Keyboard navigation (ArrowRight)
✓ Keyboard navigation (ArrowLeft)
✓ Screenshot instruction
✓ Scroll instruction
✓ Full page capture
✓ Page info extraction
✓ JSON format requirement

✅ ALL CHECKS PASSED
```

---

## Real-World Use Cases

### 1. **Design Handoff**
- Designer shares Figma prototype
- Product manager provides meeting notes
- Agent generates implementation-ready stories
- Stories include exact component names from design system

### 2. **Sprint Planning**
- Team reviews Figma designs
- Agent explores all screens
- Generates stories for each feature
- Estimates based on design complexity

### 3. **QA Test Case Generation**
- Agent analyzes Figma prototype
- Documents all states and interactions
- Generates test scenarios
- Creates visual regression test baseline

### 4. **Accessibility Audit**
- Agent reviews Figma designs
- Documents UI patterns
- Identifies accessibility gaps
- Generates accessibility-focused stories

---

## Limitations

### Current Limitations:
1. **Interactive Prototypes:** May not capture all hover states automatically
2. **Animations:** Screenshots capture static states only
3. **Complex Interactions:** Drag-and-drop may require custom instructions
4. **Private Prototypes:** Must have password access
5. **Large Prototypes:** May take time to explore 20+ screens

### Workarounds:
1. Provide specific hover/interaction instructions
2. Use multiple screenshots per screen
3. Document interaction patterns in notes
4. Always provide passwords in instructions
5. Use autonomous mode for large prototypes

---

## Future Enhancements

Planned improvements:
- [ ] Video recording of Figma navigation
- [ ] Component extraction API integration
- [ ] Design token parsing
- [ ] Automatic interaction detection
- [ ] Multi-page Figma file support
- [ ] Design system integration
- [ ] Figma API direct access (no browser needed)

---

## Support

**Issues:** Create issue at https://github.com/Azeez1/TEST_AGENTS/issues

**Documentation:** See README.md and TEST_RESULTS.md

**MCP Setup:** See Playwright MCP docs at https://github.com/executeautomation/playwright-mcp-server

---

*Built with Playwright MCP and Claude Code*
