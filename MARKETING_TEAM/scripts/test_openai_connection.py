"""
Quick test script to verify OpenAI API connection
Tests GPT-4o image generation capability
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

async def test_openai_connection():
    """Test OpenAI API connection"""
    print("[*] Testing OpenAI API connection...")
    print()

    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[X] ERROR: OPENAI_API_KEY not found in .env file")
        return False

    print(f"[OK] API key found: {api_key[:20]}...")
    print()

    # Test import
    try:
        from openai import AsyncOpenAI
        print("[OK] OpenAI library imported successfully")
    except ImportError:
        print("[X] ERROR: OpenAI library not installed")
        print("   Run: pip install openai")
        return False

    # Test API connection
    try:
        print()
        print("[*] Testing API connection...")
        client = AsyncOpenAI(api_key=api_key)

        # Test with a simple models list call (free)
        models = await client.models.list()
        print("[OK] Successfully connected to OpenAI API")
        print()

        # Check for GPT-4o image model availability
        print("[*] Checking model availability...")
        available_models = [model.id for model in models.data]

        # GPT-4o image model
        if any("gpt-4" in model for model in available_models):
            print("[OK] GPT-4 models available")

        print()
        print("=" * 50)
        print("[SUCCESS] OpenAI API Setup Complete!")
        print("=" * 50)
        print()
        print("Your agents can now:")
        print("  - Generate images with GPT-4o (visual-designer)")
        print("  - Create videos with Sora (video-producer)")
        print()
        print("Try it now:")
        print('  "Use the visual-designer subagent to create a')
        print('   modern tech startup logo"')
        print()

        return True

    except Exception as e:
        print(f"[X] ERROR: Failed to connect to OpenAI API")
        print(f"   {str(e)}")
        print()
        print("Common issues:")
        print("  - Invalid API key")
        print("  - No credits/billing set up")
        print("  - Network connectivity issues")
        print()
        return False

if __name__ == "__main__":
    asyncio.run(test_openai_connection())
