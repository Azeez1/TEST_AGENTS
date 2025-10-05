# User Story Agent 🤖

An autonomous AI agent that converts raw meeting notes into backlog-ready user stories with detailed acceptance criteria in Excel format.

## ✨ Features

- **Web UI**: Simple, intuitive Streamlit interface - no command line needed!
- **Domain-Agnostic**: Works with meeting notes from ANY project (e-commerce, finance, healthcare, etc.)
- **Intelligent Parsing**: Handles messy, unstructured notes - bullet points, paragraphs, whatever you have
- **Complete User Stories**: Generates stories in standard format with detailed Gherkin acceptance criteria
- **Excel Output**: Creates properly formatted Excel files with your exact column structure
- **Append Mode**: Automatically detects and appends to existing Excel files
- **Iterative Refinement**: Refine specific stories conversationally based on feedback
- **Batch Operations**: Apply changes to all stories at once

## 📋 Output Format

The agent generates Excel files with these columns:

| User Stories | Feature/Epic | Acceptance Criteria | Rationale or Business Case | Relevant Page(s) |
|--------------|--------------|---------------------|----------------------------|------------------|
| As a [user], I want [goal], so that [benefit] | Feature name | - Given... when... then...<br>- Given... when... then... | Business value explanation | Affected pages |

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=your-api-key-here
```

### 3. Launch the Web UI

```bash
streamlit run app_ui.py
```

This opens the web interface in your browser at `http://localhost:8501`

### 4. Use the Web Interface

- **Tab 1: Generate Stories** - Upload notes → Generate → Download Excel
- **Tab 2: Refine Stories** - Upload Excel → Select story → Refine → Download
- **Tab 3: Add More Stories** - Upload notes + Excel → Append → Download
- **Tab 4: View Stories** - Upload Excel → Browse/search stories
- **Tab 5: Batch Operations** - Upload Excel → Apply to all → Download

## 🖥️ Command Line Usage (Alternative)

If you prefer the command line interface:

### Generate User Stories from Notes

```bash
python user_story_agent.py --notes "meeting_notes.pdf" --output "user_stories.xlsx"
```

### Append More Stories

```bash
python user_story_agent.py --notes "week2_meeting.txt" --output "user_stories.xlsx"
```

The agent automatically detects the existing file and appends new stories.

## 💻 Usage Examples

### Basic Generation

```bash
# From a PDF file
python user_story_agent.py --notes "meeting_notes.pdf" --output "stories.xlsx"

# From a text file
python user_story_agent.py --notes "notes.txt" --output "stories.xlsx"
```

### Append to Existing File

```bash
# Automatically appends if file exists
python user_story_agent.py --notes "new_notes.pdf" --output "stories.xlsx"
```

### Overwrite Instead of Append

```bash
python user_story_agent.py --notes "notes.pdf" --output "stories.xlsx" --overwrite
```

### Refine a Specific Story

```bash
# Refine story in row 3
python user_story_agent.py --refine 3 --instruction "Add more error handling acceptance criteria" --output "stories.xlsx"
```

### Interactive Mode

```bash
python user_story_agent.py --interactive --output "stories.xlsx"
```

In interactive mode:
- `generate <file>` - Generate stories from a file
- `refine <row>` - Refine a specific story
- `view` - View all existing stories
- `exit` - Exit

## 📁 Project Structure

```
TEST_AGENTS/
├── user_story_agent.py       # Main agent (Claude SDK)
├── note_parser.py             # Parse PDFs and text files
├── story_generator.py         # Story generation prompts
├── excel_handler.py           # Excel read/write operations
├── formatters.py              # Format and validate stories
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── examples/
    ├── sample_notes.txt       # Example meeting notes
    └── output_example.xlsx    # Expected output format
```

## 🎯 How It Works

1. **Parse Notes**: Extracts text from PDF, text files, or raw input
2. **Analyze Context**: Claude understands the domain and extracts features, goals, pain points
3. **Generate Stories**: Creates user stories in standard format with detailed acceptance criteria
4. **Format for Excel**: Structures data with proper formatting (multiple ACs in one cell with bullets)
5. **Write/Append**: Creates new Excel or appends to existing file intelligently

## 🧠 What Makes This Powerful

### Autonomous AI Agent
Built on Claude Agent SDK, this isn't just a script - it's an autonomous agent that:
- Understands context across different domains
- Makes intelligent decisions about story structure
- Handles iteration and refinement conversationally
- Maintains consistency with existing backlog

### Domain-Agnostic Intelligence
The agent adapts to ANY project:
- **E-commerce** → Generates stories about products, checkout, shipping
- **Banking** → Generates stories about transactions, security, accounts
- **Healthcare** → Generates stories about patient data, HIPAA, appointments
- **Your project** → Learns from your notes automatically

### Quality Acceptance Criteria
Each story includes 4-6 detailed Gherkin-format ACs covering:
- Happy path scenarios
- Edge cases and error handling
- Mobile responsiveness
- Accessibility (screen readers, keyboard navigation)
- Data validation
- Performance considerations

## 🔧 Advanced Features

### Batch Updates
```bash
python user_story_agent.py --refine-all --instruction "Add mobile accessibility ACs to all stories"
```

### Custom Output Location
```bash
python user_story_agent.py --notes "notes.pdf" --output "backlog/sprint_5.xlsx"
```

### View Existing Stories
```bash
python user_story_agent.py --output "stories.xlsx" --interactive
> view
```

## 📊 Example Input → Output

### Input (Meeting Notes):
```
talked about how it works section - customers confused about products
needs to be on product page with hyperlinks
also mentioned we need better images, more angles
comparison table just for shipping supplies
```

### Output (Excel):

**User Story**: As a customer, I want to understand how to use products available on The Postal Store so that I can make sure I'm buying the right thing for my needs

**Feature/Epic**: Addition of How It Works section

**Acceptance Criteria**:
- Given a user is viewing a product details page, when they scroll to the "How It Works" section, then detailed usage instructions should appear
- Given the section is visible, when the user clicks a hyperlink, then it opens a relevant USPS guide
- Given a product has multiple variations, when a user changes the variation, then the "How It Works" content updates accordingly
- Given the user is on mobile, when they view the section, then it displays cleanly and remains legible
- Given a user with a screen reader, when they navigate to the section, then all content is properly announced

**Business Case**: Reduces customer confusion about product usage, helps customers choose appropriate products for their needs, thereby reducing buying mistakes and returns, and improving trust in the website and brand

**Relevant Pages**: Product Details Page

## 🎁 Benefits

- **Save 70-80% time** on user story writing
- **Consistent quality** across all stories
- **Works with any project** at your organization
- **Iterate quickly** based on stakeholder feedback
- **Production-ready output** for JIRA, Azure DevOps, etc.

## 🔮 Future Enhancements (v2)

- JIRA integration (auto-create tickets)
- Story point estimation sub-agent
- Test case generation
- Confluence documentation generation
- Multi-agent orchestration for complex workflows

## 📝 Notes

- The agent uses Claude Agent SDK for autonomous decision-making
- All stories follow industry-standard format (As a..., I want..., so that...)
- Acceptance criteria use Gherkin format (Given/When/Then)
- Excel formatting includes wrapped text, proper column widths, header styling

## 🤝 Contributing

This is a v1 framework designed to be extended. Ideas for improvements:
- Add support for Word documents (.docx)
- Integration with project management tools
- Story point estimation
- Custom templates per project type
- Version control for story iterations

## 📄 License

Built for Accenture Federal Services internal use.

---

**Built with [Claude Agent SDK](https://docs.claude.com/en/api/agent-sdk/overview)** 🤖
