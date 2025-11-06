"""
Quick test to verify MCP tools are registered correctly
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server import app

async def test_list_tools():
    """Test that all tools are registered"""
    print("Testing MCP Tool Registration...\n")

    # Get the list_tools handler
    handlers = app.request_handlers.get("tools/list", [])
    if not handlers:
        print("ERROR: No tool list handler found!")
        return

    # Call the handler
    handler = handlers[0]
    tools = await handler()

    print(f"Found {len(tools)} registered tools:\n")

    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool.name}")
        print(f"   Description: {tool.description[:80]}...")
        required = tool.inputSchema.get('required', [])
        optional_count = len(tool.inputSchema.get('properties', {})) - len(required)
        print(f"   Parameters: {len(required)} required, {optional_count} optional")
        print()

    # Check for our new tool
    tool_names = [t.name for t in tools]

    print("\nVerification:")
    print(f"  analyze_ugc_image: {'YES' if 'analyze_ugc_image' in tool_names else 'NO'}")
    print(f"  generate_veo_ugc_from_image: {'YES' if 'generate_veo_ugc_from_image' in tool_names else 'NO'}")
    print(f"  generate_veo_text_to_video: {'YES' if 'generate_veo_text_to_video' in tool_names else 'NO'}")
    print(f"  generate_nano_banana_image: {'YES' if 'generate_nano_banana_image' in tool_names else 'NO'}")

    # Check optional parameters on generate_veo_ugc_from_image
    ugc_tool = next((t for t in tools if t.name == 'generate_veo_ugc_from_image'), None)
    if ugc_tool:
        props = ugc_tool.inputSchema.get('properties', {})
        print("\n  generate_veo_ugc_from_image parameters:")
        print(f"     - icp: {'YES' if 'icp' in props else 'NO'}")
        print(f"     - product_features: {'YES' if 'product_features' in props else 'NO'}")
        print(f"     - video_setting: {'YES' if 'video_setting' in props else 'NO'}")
        print(f"     - reference_image_description: {'YES' if 'reference_image_description' in props else 'NO'}")

if __name__ == "__main__":
    asyncio.run(test_list_tools())
