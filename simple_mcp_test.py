"""
Simple direct test of MCP Playwright integration
"""
import asyncio
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add USER_STORY_AGENT to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'USER_STORY_AGENT'))

from mcp_client import PlaywrightMCPClient

async def test_mcp_directly():
    """Direct test of Playwright MCP client"""
    print("="*60)
    print("Direct MCP Playwright Test")
    print("="*60)
    print()

    # Create client
    client = PlaywrightMCPClient()

    # Check if configured
    print(f"MCP Configured: {client.is_available()}")
    print(f"Available Tools: {len(client.get_playwright_tools())}")
    print()

    # Start MCP server
    print("Starting MCP server...")
    server_started = await client.start_server()

    if not server_started:
        print("Failed to start MCP server!")
        return False

    print()
    print("Testing browser automation with MCP...")
    print()

    # Test with a simple research prompt
    test_prompt = """
    Please research USPS package tracking by:
    1. Navigate to usps.com
    2. Take a screenshot
    3. Look for tracking features

    Then summarize what you found in 2-3 sentences.
    """

    try:
        result = await client.call_with_tools(
            prompt=test_prompt,
            max_tokens=2048
        )

        print()
        print("="*60)
        print("RESULT:")
        print("="*60)
        print(result)
        print()

        # Stop server
        await client.stop_server()

        # Check if it actually used the browser
        if "[SIMULATED]" in result:
            print("⚠️  MCP fell back to simulation - browser may not be available")
            return False
        else:
            print("✅ MCP used REAL browser automation!")
            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        await client.stop_server()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_directly())
    print()
    print("="*60)
    if success:
        print("✅ MCP Browser Automation WORKING!")
    else:
        print("⚠️  MCP Browser May Need Configuration")
    print("="*60)
