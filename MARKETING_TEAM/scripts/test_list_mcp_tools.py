"""
Test that MCP server lists all tools correctly including new analyze_ugc_image
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server import app

async def test_list_tools():
    """Test that all tools are registered"""
    print("=" * 60)
    print("TESTING MCP TOOL REGISTRATION")
    print("=" * 60)

    # Get the list_tools handler
    handlers = app.request_handlers.get("tools/list", [])
    if not handlers:
        print("ERROR: No tool list handler found!")
        return

    # Call the handler
    handler = handlers[0]
    tools = await handler()

    print(f"\nFound {len(tools)} registered tools\n")

    # Expected tools
    expected_tools = {
        'analyze_ugc_image',
        'generate_gpt4o_image',
        'generate_nano_banana_image',
        'generate_sora_video',
        'generate_veo_text_to_video',
        'generate_veo_ugc_from_image'
    }

    tool_names = {t.name for t in tools}

    print("Tool Verification:")
    for tool in sorted(expected_tools):
        status = "YES" if tool in tool_names else "NO"
        print(f"  {tool}: {status}")

    # Check for new optional parameters
    print("\nParameter Verification:")

    ugc_tool = next((t for t in tools if t.name == 'generate_veo_ugc_from_image'), None)
    if ugc_tool:
        props = ugc_tool.inputSchema.get('properties', {})
        print("  generate_veo_ugc_from_image optional params:")
        print(f"    - icp: {'YES' if 'icp' in props else 'NO'}")
        print(f"    - product_features: {'YES' if 'product_features' in props else 'NO'}")
        print(f"    - video_setting: {'YES' if 'video_setting' in props else 'NO'}")
        print(f"    - reference_image_description: {'YES' if 'reference_image_description' in props else 'NO'}")

    veo_text_tool = next((t for t in tools if t.name == 'generate_veo_text_to_video'), None)
    if veo_text_tool:
        props = veo_text_tool.inputSchema.get('properties', {})
        print("  generate_veo_text_to_video optional params:")
        print(f"    - icp: {'YES' if 'icp' in props else 'NO'}")
        print(f"    - product_features: {'YES' if 'product_features' in props else 'NO'}")
        print(f"    - video_setting: {'YES' if 'video_setting' in props else 'NO'}")

    # Verify all expected tools are present
    missing_tools = expected_tools - tool_names
    if missing_tools:
        print(f"\nERROR: Missing tools: {missing_tools}")
        return False

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_list_tools())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
