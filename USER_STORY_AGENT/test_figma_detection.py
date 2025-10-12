"""
Test script for Figma URL detection functionality
"""

import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from autonomous_mode import AutonomousAgent

def test_figma_detection():
    """Test various Figma URL detection scenarios"""

    agent = AutonomousAgent()

    # Test Case 1: Figma URL with password
    test_notes_1 = """
    Dashboard Requirements:
    - User analytics
    - Real-time charts
    - Export functionality

    Figma: https://www.figma.com/proto/ABC123XYZ?node-id=1%3A2
    Password: tower-film-great-letter
    """

    result_1 = agent._detect_figma_url(test_notes_1)
    print("Test 1 - Figma with password:")
    print(f"  Result: {result_1}")
    assert result_1 is not None, "Should detect Figma URL"
    assert result_1['password'] == "tower-film-great-letter", "Should extract password"
    print("  ✓ PASS\n")

    # Test Case 2: Figma URL without password
    test_notes_2 = """
    Login Page Requirements
    Figma prototype: https://figma.com/file/XYZ789/auth-flow
    """

    result_2 = agent._detect_figma_url(test_notes_2)
    print("Test 2 - Figma without password:")
    print(f"  Result: {result_2}")
    assert result_2 is not None, "Should detect Figma URL"
    assert result_2['password'] == "", "Password should be empty"
    print("  ✓ PASS\n")

    # Test Case 3: No Figma URL
    test_notes_3 = """
    General requirements:
    - User management
    - Role-based access
    """

    result_3 = agent._detect_figma_url(test_notes_3)
    print("Test 3 - No Figma URL:")
    print(f"  Result: {result_3}")
    assert result_3 is None, "Should return None when no Figma URL"
    print("  ✓ PASS\n")

    # Test Case 4: Excel-like format with Figma
    test_notes_4 = """
    === Sheet: Requirements ===
    [DETECTED: Structured Requirements Table]

    Requirement 1:
      Feature: Dashboard
      Description: Analytics dashboard with charts
      Figma Link: https://www.figma.com/proto/DASH123
      Pass: demo-2024
    """

    result_4 = agent._detect_figma_url(test_notes_4)
    print("Test 4 - Excel-like format:")
    print(f"  Result: {result_4}")
    assert result_4 is not None, "Should detect Figma in Excel format"
    assert "figma.com/proto/DASH123" in result_4['url'], "Should extract correct URL"
    assert result_4['password'] == "demo-2024", "Should extract password with 'Pass:' format"
    print("  ✓ PASS\n")

    # Test Case 5: Figma URL with various password formats
    test_notes_5 = """
    Prototype URL: https://figma.com/proto/TEST456
    pwd: secret123
    """

    result_5 = agent._detect_figma_url(test_notes_5)
    print("Test 5 - Alternative password format (pwd):")
    print(f"  Result: {result_5}")
    assert result_5 is not None, "Should detect Figma URL"
    assert result_5['password'] == "secret123", "Should extract password with 'pwd:' format"
    print("  ✓ PASS\n")

    print("=" * 60)
    print("🎉 All tests passed!")
    print("=" * 60)
    print("\nFigma detection is working correctly!")
    print("The agent will now automatically:")
    print("  1. Detect Figma URLs in Excel/notes")
    print("  2. Extract passwords if present")
    print("  3. Use specialized Figma navigation template")
    print("  4. Combine Excel requirements + Figma designs")

if __name__ == "__main__":
    test_figma_detection()
