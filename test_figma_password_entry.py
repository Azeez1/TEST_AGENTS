"""
Test Figma password entry specifically
"""
import asyncio
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'USER_STORY_AGENT'))

from mcp_client import PlaywrightMCPClient

async def test_password_entry():
    """Test password entry into Figma"""
    print("="*60)
    print("Testing Figma Password Entry")
    print("="*60)
    print()

    client = PlaywrightMCPClient()

    print("Starting MCP server...")
    await client.start_server()
    print()

    figma_url = "https://www.figma.com/proto/39gOKzK7GqtY60mSFl99zn/High-Fidelity-Prototype-for-User-Stories?page-id=0%3A1&node-id=11-7168&viewport=536%2C292%2C0.11&t=kGOA8ietRAZjo9eS-1&scaling=scale-down&content-scaling=responsive"
    password = "tower-film-great-letter"

    # Simple prompt that should enter password
    prompt = f"""
Navigate to this URL: {figma_url}

Then:
1. Wait 2 seconds for page to load
2. Fill the password input field with: {password}
3. Click the Continue button
4. Wait 2 seconds
5. Take a screenshot

Be explicit with each step.
"""

    print("Sending prompt to agent...")
    print()

    result = await client.call_with_tools(
        prompt=prompt,
        max_tokens=4096,
        log_callback=lambda msg: print(msg)
    )

    print()
    print("="*60)
    print("RESULT:")
    print("="*60)
    print(result[:500] if result else "No result")
    print()

    await client.stop_server()

if __name__ == "__main__":
    asyncio.run(test_password_entry())
