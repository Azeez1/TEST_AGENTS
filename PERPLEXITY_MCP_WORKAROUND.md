# Perplexity MCP Workaround - Schema Bug Fix

## Problem

**Issue:** Perplexity MCP server has a known bug where `create_chat_completions` tool uses `oneOf/allOf/anyOf` at the top level of its schema, which Claude's API doesn't support.

**Error Message:**
```
API Error: 400 {"type":"error","error":{"type":"invalid_request_error","message":"tools.16.input_schema: input_schema does not support oneOf, allOf, or anyOf at the top level"},"request_id":"req_011CUdpfV7JkopjcXZ4SvL6f"}
```

**Reported Issues:**
- GitHub: https://github.com/perplexityai/modelcontextprotocol/issues/57
- Affects ALL Claude models (not just Claude Code)

## Solution

Disable the `create_chat_completions` tool while keeping the other 3 working tools.

### Configuration Changes

**File: `.mcp.json`**
```json
"perplexity": {
  "type": "stdio",
  "command": "npx",
  "args": [
    "-y",
    "@perplexity-ai/mcp-server",
    "--client",
    "claude-code",
    "--no-tool",
    "create_chat_completions"
  ],
  "env": {
    "PERPLEXITY_API_KEY": "your-key-here",
    "PERPLEXITY_TIMEOUT_MS": "600000"
  }
}
```

**File: `C:\Users\sabaa\AppData\Roaming\Claude\claude_desktop_config.json`**
```json
"perplexity": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@perplexity-ai/mcp-server", "--client", "claude-code", "--no-tool", "create_chat_completions"],
  "env": {
    "PERPLEXITY_API_KEY": "your-key-here",
    "PERPLEXITY_TIMEOUT_MS": "600000"
  }
}
```

## What Still Works

✅ **Perplexity MCP Tools (3/4):**
1. `perplexity_search` - Web search with SERP results
2. `perplexity_ask` - Conversational Q&A
3. `perplexity_reason` - Advanced reasoning

❌ **Disabled:**
- `create_chat_completions` - Has the schema bug

✅ **Custom Python Tools (100% working):**
All your custom Perplexity tools in `tools/perplexity_research_tool.py` work perfectly:
1. `conduct_research()` - Comprehensive research (sonar-pro)
2. `quick_research()` - Fast facts (sonar)
3. `strategic_analysis()` - Deep reasoning (sonar-reasoning)

## Impact

**No impact on your workflows!**

You don't use `create_chat_completions` - your agents use:
- Custom Python tools for comprehensive research
- MCP `perplexity_search` for web/SERP results
- MCP `perplexity_ask` and `perplexity_reason` as backups

## When to Remove This Workaround

Monitor the GitHub issue: https://github.com/perplexityai/modelcontextprotocol/issues/57

When Perplexity fixes the schema bug:
1. Remove `"--no-tool", "create_chat_completions"` from both config files
2. Restart Claude Code
3. Test that all 4 tools work without errors

## Testing

**Verify the fix works:**
1. Restart Claude Code
2. Check MCP Status - should show all 7 servers
3. No API errors about tool schemas
4. Test: `"Use research-agent to search for AI marketing trends"`

---

**Fixed:** 2025-01-30
**Root Cause:** Perplexity MCP `create_chat_completions` uses unsupported schema patterns
**Workaround:** Disable problematic tool, keep 3 working tools
**Status:** Permanent fix until Perplexity patches the bug
