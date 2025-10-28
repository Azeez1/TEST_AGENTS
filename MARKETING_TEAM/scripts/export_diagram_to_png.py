"""
Export OBO Mind Map HTML to high-quality PNG using Playwright
"""
from playwright.sync_api import sync_playwright
import sys
from pathlib import Path

# Paths
HTML_FILE = Path(r"C:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS\MARKETING_TEAM\outputs\diagrams\OBO_MindMap_Final_Fixed.html")
OUTPUT_PNG = Path(r"C:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS\MARKETING_TEAM\outputs\diagrams\OBO_MindMap.png")

def export_to_png():
    """Capture the mind map as PNG"""
    print(f"Loading HTML file: {HTML_FILE}")

    if not HTML_FILE.exists():
        print(f"ERROR: HTML file not found at {HTML_FILE}")
        return False

    try:
        with sync_playwright() as p:
            print("Launching browser...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 3840, 'height': 2160})  # 4K resolution

            print("Loading diagram...")
            page.goto(f"file:///{HTML_FILE.as_posix()}")

            # Wait for Mermaid to render
            print("Waiting for diagram to render...")
            page.wait_for_selector('.mermaid svg', timeout=10000)
            page.wait_for_timeout(2000)  # Extra time for animations

            # Get the diagram element
            diagram = page.locator('#diagram-wrapper')

            print(f"Capturing screenshot to: {OUTPUT_PNG}")
            diagram.screenshot(path=str(OUTPUT_PNG))

            browser.close()
            print(f"\n✅ SUCCESS! PNG saved to: {OUTPUT_PNG}")
            print(f"   File size: {OUTPUT_PNG.stat().st_size / 1024:.1f} KB")
            return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTry using browser screenshot instead:")
        print("  1. Open the HTML file in your browser")
        print("  2. Press Windows Key + Shift + S")
        print("  3. Select the diagram area")
        print("  4. Paste into Paint/PowerPoint and save")
        return False

if __name__ == "__main__":
    success = export_to_png()
    sys.exit(0 if success else 1)
