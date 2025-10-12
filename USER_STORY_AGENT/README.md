# User Story Agent

Transform meeting notes into backlog-ready user stories with AI-powered generation.

## Quick Start

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
Create `.env` file:
```
ANTHROPIC_API_KEY=your_api_key_here
```

### 3. Launch
```bash
start_ui.bat
```
Or: `streamlit run app_ui.py`

App opens at `http://localhost:8501`

## Features

- **Generate Stories** - Upload notes → Generate → Download Excel
- **Refine Stories** - Edit existing stories manually or with AI
- **Multiple AC Formats** - Gherkin (Given/When/Then) or Explicit/Detailed (30-50 lines)
- **Multi-File Support** - PDF, DOCX, TXT, Excel, Markdown, JSON, CSV, HTML, images
- **Browser Research** (Optional) - AI browses web for best practices
- **Feedback Learning** - Agent remembers preferences across sessions
- **🆕 Auto Figma Detection** - Automatically detects Figma URLs in Excel/notes and navigates designs

## Browser Research (Optional)

Enhance story generation with web research:

```bash
# Install Playwright MCP
npm install -g @executeautomation/playwright-mcp-server

# Install browsers
npx playwright install chromium
```

Then enable "Browser & Research Mode" in Tab 1.

## File Types Supported

- Documents: PDF, DOCX, TXT, MD
- Spreadsheets: XLSX, XLS
- Data: JSON, CSV, XML, HTML
- Images: PNG, JPG, GIF (with OCR)

## How to Use

### Generate Stories (Tab 1)
1. Upload notes or paste text
2. Choose AC format
3. Optionally enable browser research
4. Click "Generate User Stories"
5. Download Excel

### Refine Stories (Tab 2)
1. Upload existing Excel
2. Select story
3. Edit manually or use AI refinement
4. Download changes

### Browser Research
Provide instructions like:
- "Navigate to https://design.company.com and extract button styles"
- "Search for WCAG accessibility requirements for forms"
- "Browse Shopify cart and analyze their UX patterns"

### 🆕 Excel + Figma Workflow (Automatic)
**NEW:** Agent automatically detects Figma URLs in your Excel/notes!

**Simple workflow:**
1. Add Figma URL to Excel cell: `Figma: https://figma.com/proto/ABC123 Password: demo`
2. Upload Excel and enable "Browser & Research Mode"
3. Agent auto-detects, navigates Figma, extracts design specs
4. Combines Excel requirements + Figma designs into comprehensive stories

**See:** [EXCEL_FIGMA_WORKFLOW.md](EXCEL_FIGMA_WORKFLOW.md) for complete guide

## AC Formats

**Gherkin** (3-5 criteria):
```
Given [context]
When [action]
Then [outcome]
```

**Explicit/Detailed** (30-50 lines):
```
1. Screen Display
   a. Element details
2. User Actions
   a. Interaction details
...
Notes: Performance, accessibility, etc.
```

## Configuration

Edit `mcp_config.json` for browser automation settings.

## Troubleshooting

**JSON parsing error**: Check notes formatting, regenerate if needed

**Browser not working**: Install Playwright MCP and Chromium (see above)

**OCR not working**: Install Tesseract OCR (optional)

## Requirements

- Python 3.8+
- Anthropic API key
- Node.js + npm (optional, for browser research)

## Project Structure

```
app_ui.py                 # Main Streamlit UI (6 tabs)
autonomous_mode.py        # Browser automation agent with MCP
story_generator.py        # Prompt templates for generation
formatters.py            # JSON parsing with 4 fallback strategies
excel_handler.py         # Excel read/write operations
note_parser.py           # Multi-format file parsing
file_handlers.py         # Extended file format support
multi_file_processor.py  # Multi-file processing
ocr_handler.py           # OCR for images with pytesseract
mcp_client.py            # MCP stdio client with tool execution
research_prompts.py      # Autonomous research prompt templates
feedback_handler.py      # Feedback learning system
conversation_memory.py   # Persistent preferences storage
browser_helper.py        # Browser utilities (stub - unused)
mcp_config.json         # MCP configuration
requirements.txt        # Python dependencies
```

## License

Uses Anthropic Claude API. See Anthropic's terms of service.
