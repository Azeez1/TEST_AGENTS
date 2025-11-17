# PROPOSAL_TEAM Setup Instructions

This guide will help you set up the RFP Proposal Team agent on your local machine.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git

## Installation Steps

### 1. Navigate to the Project Directory

```bash
cd /home/user/TEST_AGENTS/PROPOSAL_TEAM/dux_rfp_agent
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- Core: `python-dotenv`, `pydantic`, `pyyaml`, `jsonschema`
- Document Processing: `PyPDF2`, `python-docx`, `docxtpl`, `pillow`
- LLM Providers: `openai`, `anthropic`
- Vector Database: `pinecone-client`
- API Framework: `fastapi`, `uvicorn`
- Development: `pytest`, `black`, `ruff`

### 3. Install the Package in Editable Mode

```bash
pip install -e .
```

This makes the `dux_rfp_agent` package importable and enables the `dux-rfp` CLI command.

### 4. Install MCP Package (for Claude Code Integration)

The MCP server requires the `mcp` package:

```bash
pip install mcp
```

### 5. Configure Environment Variables

**IMPORTANT: Never commit API keys to version control!**

1. Copy the example environment file:
   ```bash
   cd config
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```bash
   # Required: Choose your LLM provider
   LLM_PROVIDER=openai              # or "anthropic"
   LLM_MODEL_SMALL=gpt-4o-mini      # For parsing
   LLM_MODEL_STRONG=gpt-4o          # For writing
   OPENAI_API_KEY=sk-your-actual-key-here

   # OR for Anthropic:
   # LLM_PROVIDER=anthropic
   # LLM_MODEL_SMALL=claude-haiku-4
   # LLM_MODEL_STRONG=claude-sonnet-4
   # ANTHROPIC_API_KEY=sk-ant-your-actual-key-here

   # Optional: Knowledge Base (Pinecone)
   # PINECONE_API_KEY=your-pinecone-key
   # PINECONE_INDEX=rfp-knowledge-base
   # EMBEDDING_MODEL=text-embedding-3-small
   ```

3. The `.env` file is already in `.gitignore` and will not be committed to version control.

### 6. Verify Installation

Test that the package imports correctly:

```bash
python3 -c "import sys; sys.path.insert(0, 'src'); import dux_rfp_agent; print('✓ Package installed successfully')"
```

Test the CLI:

```bash
dux-rfp --help
```

### 7. (Optional) Set Up Knowledge Base

If you want to use the knowledge base features with Pinecone:

1. Add your `PINECONE_API_KEY` to `.env`
2. Create an index in Pinecone dashboard
3. Index your documents:
   ```bash
   python scripts/index_kb.py \
     --input ../kb/resumes \
     --type resume \
     --sector government
   ```

## Usage

### Via Slash Command (in Claude Code)

```bash
/rfp-process ./path/to/rfp.pdf --sector government --company "Acme Solutions"
```

### Via CLI

```bash
dux-rfp \
  --rfp ./path/to/rfp.pdf \
  --out ./output \
  --sector government \
  --company "Acme Solutions"
```

### Via Python API

```python
from dux_rfp_agent.pipeline import RFPPipeline
from pathlib import Path

pipeline = RFPPipeline(enable_kb=True)
result = pipeline.process_rfp(
    rfp_path=Path("rfp.pdf"),
    output_dir=Path("./output"),
    sector="government",
    company_name="Acme Corp"
)
```

## Running Tests

```bash
cd /home/user/TEST_AGENTS/PROPOSAL_TEAM/dux_rfp_agent

# Run all tests
pytest

# Run with coverage
pytest --cov=dux_rfp_agent --cov-report=html

# Run specific test
pytest tests/test_pipeline.py
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'dux_rfp_agent'"

**Solution**: Install the package in editable mode:
```bash
cd /home/user/TEST_AGENTS/PROPOSAL_TEAM/dux_rfp_agent
pip install -e .
```

### "ModuleNotFoundError: No module named 'jsonschema'"

**Solution**: Install missing dependencies:
```bash
pip install jsonschema>=4.17.0
```

### "ModuleNotFoundError: No module named 'mcp'"

**Solution**: Install the MCP package:
```bash
pip install mcp
```

### "LLM API key not found"

**Solution**:
1. Make sure you created `.env` file in `dux_rfp_agent/config/`
2. Add your `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
3. Verify the file is not empty and keys are valid

### "Pinecone not available"

**Solution**: Either:
- Add `PINECONE_API_KEY` to your `.env` file, OR
- Use `--no-kb` flag to disable knowledge base features:
  ```bash
  /rfp-process ./rfp.pdf --sector government --no-kb
  ```

### MCP Server Fails to Start

**Solution**:
1. Verify Python path in `.claude/settings.json` is correct
2. Check MCP server logs for errors
3. Test the server manually:
   ```bash
   python3 /home/user/TEST_AGENTS/PROPOSAL_TEAM/.claude/tools/rfp_mcp_server.py
   ```

## Security Best Practices

✅ **DO**:
- Keep API keys in `.env` files (already in `.gitignore`)
- Use environment variables for sensitive configuration
- Regularly rotate API keys
- Review `.gitignore` before committing

❌ **DON'T**:
- Commit `.env` files to version control
- Share API keys in chat, email, or documentation
- Hard-code API keys in source code
- Commit sensitive RFP documents to public repos

## Next Steps

1. Review the [README.md](dux_rfp_agent/README.md) for detailed usage
2. Check [COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md) for compliance features
3. Explore example RFPs in `examples/`
4. Customize prompts in `src/dux_rfp_agent/prompts/`
5. Add sector-specific templates in `src/dux_rfp_agent/templates/sectors/`

## Support

For issues or questions:
- Check the documentation in `dux_rfp_agent/README.md`
- Review troubleshooting section above
- Check existing issues in the repository
- Consult the RFP agent documentation at `.claude/agents/rfp-agent.md`
