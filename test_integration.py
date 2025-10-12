"""
Integration test for USER_STORY_AGENT with real MCP browser automation
"""
import asyncio
import sys
import os

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add USER_STORY_AGENT to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'USER_STORY_AGENT'))

from autonomous_mode import AutonomousAgent

async def test_mcp_integration():
    """Test that MCP is properly configured and can generate stories with research"""
    print("=" * 60)
    print("USER_STORY_AGENT + MCP Integration Test")
    print("=" * 60)
    print()

    # Initialize agent
    agent = AutonomousAgent()

    # Check MCP status
    mcp_status = agent.get_mcp_status()
    print("📋 MCP Status:")
    print(f"  - Configured: {mcp_status['configured']}")
    print(f"  - Server Running: {mcp_status['server_running']}")
    print(f"  - Connection Type: {mcp_status.get('connection_type', 'Unknown')}")
    print(f"  - Tools Available: {mcp_status['tools_available']}")
    print()

    if not mcp_status['configured']:
        print("❌ MCP is not configured!")
        return False

    print("✅ MCP is properly configured!")
    print()

    # Test with a simple note that would benefit from research
    test_note = """
    Meeting Notes - USPS Package Tracking Feature

    - Users want to track their packages
    - Need to check delivery status
    - Want notifications when package is delivered
    - Should work on mobile and desktop
    """

    print("📝 Test Note:")
    print(test_note)
    print()

    print("🚀 Starting story generation with research mode...")
    print("   (This will test the real MCP browser automation)")
    print()

    try:
        # Generate stories with research enabled
        success, stories, error = await agent.generate_from_notes(
            notes_input=test_note,
            ac_format="gherkin",
            browser_instructions="Research USPS package tracking features",
            append=False
        )

        if success:
            print("✅ Story generation with research SUCCEEDED!")
            print()
            print(f"📊 Generated {len(stories)} stories")
            print()

            # Show first story as example
            if stories:
                story = stories[0]
                print("Example Story:")
                print(f"  Title: {story.get('user_story', 'N/A')}")
                print(f"  Epic: {story.get('feature_epic', 'N/A')}")
                print(f"  ACs: {len(story.get('acceptance_criteria', []))} criteria")
                print()

            return True
        else:
            print(f"❌ Story generation FAILED: {error}")
            return False

    except Exception as e:
        print(f"❌ Exception during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_integration())
    print()
    print("=" * 60)
    if success:
        print("✅ ALL TESTS PASSED - MCP Integration Working!")
    else:
        print("❌ TESTS FAILED - Check errors above")
    print("=" * 60)
    sys.exit(0 if success else 1)
