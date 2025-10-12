# MCP Browser Automation Setup & Usage

Complete guide for autonomous browser research with USER_STORY_AGENT.

---

## Quick Start

### 1. Install MCP Server
```bash
npm install -g @executeautomation/playwright-mcp-server
npx playwright install chromium
```

### 2. Configuration Files

Already configured in `.mcp.json` and `.claude.json`:
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

### 3. Verify Setup
```bash
claude mcp list
# Should show: playwright: ✓ Connected
```

---

## Autonomous Browser Research

### How It Works

The agent autonomously:
1. Analyzes your meeting notes
2. Decides which websites to visit
3. Navigates, clicks, scrolls as needed
4. Takes screenshots of valuable content
5. Synthesizes findings into user stories

**Like Perplexity or Manus** - the agent makes its own decisions!

### Usage in UI

1. Upload/paste meeting notes in Tab 1
2. Enable "Browser & Research Mode"
3. Select "Autonomous" (agent decides) or "Guided" (you provide hints)
4. Generate stories

The agent will:
- Search for best practices
- Navigate to relevant sites
- Extract design patterns
- Reference real examples in stories

---

## Special Cases

### Figma Prototypes

If notes mention Figma:
```
Meeting notes about auth flow
Figma: https://www.figma.com/proto/[id]
Password: tower-film-great-letter
```

Agent will:
- Navigate to Figma
- Enter password automatically
- Navigate all screens with arrow keys
- Scroll to see full designs
- Generate stories with design specs

### Design Systems

If notes mention design system URL:
```
Use components from https://design.company.com
```

Agent will:
- Browse component library
- Learn component names
- Use exact terminology in stories

---

## Available Browser Tools

- `playwright_navigate` - Go to URLs
- `playwright_click` - Click elements
- `playwright_fill` - Fill forms
- `playwright_screenshot` - Capture screens
- `playwright_press_key` - Use keyboard (arrows, Enter)
- `playwright_scroll_page` - Scroll up/down/top/bottom
- `playwright_evaluate` - Run JavaScript
- `playwright_get_page_info` - Get page context

---

## Troubleshooting

**Browser doesn't launch:**
```bash
npx playwright install chromium
```

**MCP not connected:**
```bash
claude mcp list
# If not showing, restart Claude Code
```

**Agent stops after navigation:**
- Now fixed with multi-iteration loop (up to 10 steps)

---

## Examples

### Example 1: Autonomous Research
```
Input: "E-commerce cart and checkout flow"

Agent autonomously:
- Searches "e-commerce checkout best practices"
- Visits Shopify, Amazon examples
- Takes screenshots of cart UIs
- Generates stories with industry patterns
```

### Example 2: Figma Analysis
```
Input:
Meeting notes: Authentication flow redesign
Figma: https://www.figma.com/proto/[id]
Password: demo-123

Agent autonomously:
- Navigates to Figma
- Enters password
- Uses arrow keys to explore all 4 screens
- Scrolls each screen fully
- Generates stories with component specs from designs
```

---

## Testing

Test autonomous navigation:
```python
from autonomous_mode import AutonomousAgent

agent = AutonomousAgent(enable_browser=True)
success, stories, msg = await agent.generate_from_notes(
    "Meeting notes about checkout flow",
    ac_format="gherkin"
)
# Agent decides what to research on its own!
```

---

For more details, see:
- [README.md](USER_STORY_AGENT/README.md) - Full application guide
- [.mcp.json](.mcp.json) - MCP configuration
- [mcp_client.py](USER_STORY_AGENT/mcp_client.py) - Implementation
