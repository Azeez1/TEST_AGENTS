---
globs:
  - "**/*.py"
  - "**/*.json"
  - "**/*.env"
  - "**/*.md"
description: Prevent API key exposure and credential leaks
---

# Security Rules

## Never Hardcode Secrets
- NEVER write API keys, tokens, passwords, or credentials directly in source files
- In Python: always use `os.getenv("KEY_NAME")` for secrets
- In JSON examples: use placeholder values like `"your_key_here"` or `"sk-your-key"`
- In .env.example files: show structure without real values

## Secret Patterns to Watch For
If you see ANY of these patterns in code being written or edited, STOP and warn the user:
- `sk-` followed by 20+ alphanumeric characters (OpenAI keys)
- `pplx-` followed by 20+ characters (Perplexity keys)
- `GOCSPX-` followed by characters (Google OAuth secrets)
- `eyJ...` JWT token patterns (base64-encoded tokens)
- `password = "..."` or `password: "..."` with actual values
- Any `API_KEY = "actual_value"` pattern

## Protected Files (Never Commit)
These files contain real credentials and are gitignored — never recreate them in tracked locations:
- `.env`, `.mcp.json`, `.claude.json` — contain real API keys
- `credentials.json`, `token.pickle` — OAuth tokens for Google services
- `.claude/settings.local.json` — local config with permissions

## Safe Patterns
- Reading from `.env` via `dotenv` or `os.getenv()` is correct
- Using `${VAR}` expansion in `.mcp.json` config is correct
- Template files (`.env.example`, `.mcp.json.example`) with placeholders are correct
