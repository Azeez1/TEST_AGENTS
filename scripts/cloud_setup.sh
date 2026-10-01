#!/bin/bash
# Cloud environment setup script (Claude Code on the web).
# Paste into the environment's "Setup script" box; it runs before Claude Code
# starts, so the MCP servers in .mcp.json load in the very first session.
# See MCP_SETUP.md "Cloud Sessions".
cd /home/user/TEST_AGENTS 2>/dev/null || exit 0
VENV="$HOME/.cache/test_agents/marketing-tools-venv"
mkdir -p "$HOME/.cache/test_agents"
# All servers; ${VAR} placeholders are filled from env vars when the session starts
cp config/mcp.cloud.json .mcp.json
touch "$HOME/.cache/test_agents/mcp_cloud_generated"
echo '{"enableAllProjectMcpServers": true}' > .claude/settings.local.json
# Python packages for marketing-tools (mcp<2: the 2.x SDK dropped the decorator API it uses)
uv venv --quiet --allow-existing "$VENV"
uv pip install --quiet --python "$VENV/bin/python" "mcp<2" openai httpx tenacity loguru python-dotenv google-genai
sed -i "s#\"command\": \"python3\"#\"command\": \"$VENV/bin/python\"#" .mcp.json
