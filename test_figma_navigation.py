"""
Test Figma prototype navigation with scrolling and keyboard controls
"""
import asyncio
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add USER_STORY_AGENT to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'USER_STORY_AGENT'))

from research_prompts import ResearchPrompts

async def test_figma_navigation():
    """Test Figma prototype navigation"""
    print("="*60)
    print("Figma Prototype Navigation Test")
    print("="*60)
    print()

    # Test parameters
    figma_url = "https://www.figma.com/proto/39gOKzK7GqtY60mSFl99zn/High-Fidelity-Prototype-for-User-Stories?page-id=0%3A1&node-id=11-7168&viewport=536%2C292%2C0.11&t=kGOA8ietRAZjo9eS-1&scaling=scale-down&content-scaling=responsive"
    password = "tower-film-great-letter"
    notes = "User authentication and login flow design"

    print("Test Configuration:")
    print(f"  Figma URL: {figma_url[:80]}...")
    print(f"  Password: {password}")
    print(f"  Notes: {notes}")
    print()

    # Generate Figma-specific prompt
    print("Generating Figma research prompt...")
    prompt = ResearchPrompts.get_figma_prototype_prompt(
        notes=notes,
        figma_url=figma_url,
        password=password,
        ac_format="gherkin"
    )

    print("✓ Prompt generated!")
    print()
    print("Prompt Preview (first 500 chars):")
    print("-" * 60)
    print(prompt[:500])
    print("...")
    print("-" * 60)
    print()

    # Check for key instructions
    checks = [
        ("Navigate instruction", "Navigate to the URL" in prompt),
        ("Password instruction", password in prompt),
        ("Keyboard navigation (ArrowRight)", "ArrowRight" in prompt),
        ("Keyboard navigation (ArrowLeft)", "ArrowLeft" in prompt),
        ("Screenshot instruction", "playwright_screenshot" in prompt),
        ("Scroll instruction", "playwright_scroll_page" in prompt),
        ("Full page capture", "fullPage: true" in prompt),
        ("Page info extraction", "playwright_get_page_info" in prompt),
        ("JSON format requirement", "JSON" in prompt and "array" in prompt),
    ]

    print("Validation Checks:")
    all_passed = True
    for check_name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False

    print()
    print("="*60)
    if all_passed:
        print("✅ ALL CHECKS PASSED")
        print()
        print("The Figma navigation prompt includes:")
        print("  • URL navigation with password entry")
        print("  • Keyboard navigation (arrow keys)")
        print("  • Full page scrolling")
        print("  • Screenshot capture with fullPage option")
        print("  • Page info extraction")
        print("  • Complete screen exploration instructions")
    else:
        print("❌ SOME CHECKS FAILED")

    print("="*60)
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(test_figma_navigation())
    sys.exit(0 if success else 1)
