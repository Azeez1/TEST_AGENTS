"""
Marketing Tools MCP Server
Wraps all marketing tools as an in-process MCP server for Claude Code
"""

import sys
import os
import asyncio

# Add tools directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claude_agent_sdk import create_sdk_mcp_server

# Import all tools
from openai_gpt4o_image import generate_gpt4o_image
from platform_formatters import (
    format_twitter_post,
    format_linkedin_post,
    extract_hashtags,
    optimize_post_for_engagement,
    create_post_variations
)
from gmail_api import (
    send_gmail,
    create_gmail_draft,
    send_email_campaign
)
from router_tools import (
    classify_intent,
    get_agent_capabilities,
    list_available_agents,
    format_agent_response
)
from google_drive import upload_file_to_drive
from sora_video import generate_sora_video


def main():
    """Run the MCP server"""
    # Create server with all tools
    server = create_sdk_mcp_server(
        name="marketing-tools",
        version="1.0.0",
        tools=[
            # Image generation (1 tool)
            generate_gpt4o_image,

            # Social media formatters (5 tools)
            format_twitter_post,
            format_linkedin_post,
            extract_hashtags,
            optimize_post_for_engagement,
            create_post_variations,

            # Gmail operations (3 tools)
            send_gmail,
            create_gmail_draft,
            send_email_campaign,

            # Router coordination (4 tools)
            classify_intent,
            get_agent_capabilities,
            list_available_agents,
            format_agent_response,

            # Google Drive (1 tool)
            upload_file_to_drive,

            # Video generation (1 tool)
            generate_sora_video
        ]
    )

    # Run server (stdio mode for MCP)
    server.run()


if __name__ == "__main__":
    main()
