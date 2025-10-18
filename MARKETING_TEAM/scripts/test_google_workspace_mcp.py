"""
Test script to verify Google Workspace MCP connectivity
"""
import subprocess
import json

def test_mcp_connection():
    """Test if Google Workspace MCP is accessible"""
    print("Testing Google Workspace MCP Connection...\n")

    try:
        # Run MCP list command
        result = subprocess.run(
            ["claude", "mcp", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )

        print("MCP Server Status:")
        print("-" * 50)
        print(result.stdout)

        # Check if google-workspace is in the output
        if "google-workspace" in result.stdout and "Connected" in result.stdout:
            print("\n[SUCCESS] Google Workspace MCP is connected!")
            print("\nAvailable capabilities:")
            print("  - Gmail integration")
            print("  - Google Drive file management")
            print("  - Google Docs creation")
            print("  - Google Sheets operations")
            print("  - Google Calendar access")
            return True
        else:
            print("\n[FAILED] Google Workspace MCP is not connected")
            return False

    except subprocess.TimeoutExpired:
        print("[ERROR] Command timed out")
        return False
    except FileNotFoundError:
        print("[ERROR] 'claude' command not found")
        print("Make sure Claude Code CLI is installed")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_workspace_mcp_executable():
    """Test if workspace-mcp.exe exists and is accessible"""
    print("\nTesting workspace-mcp.exe...\n")

    exe_path = r"C:\Users\sabaa\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\workspace-mcp.exe"

    try:
        result = subprocess.run(
            [exe_path, "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print("[SUCCESS] workspace-mcp.exe is accessible")
            print(f"Location: {exe_path}")
            return True
        else:
            print("[WARNING] workspace-mcp.exe returned an error")
            print(result.stderr)
            return False

    except FileNotFoundError:
        print(f"[ERROR] workspace-mcp.exe not found at: {exe_path}")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  Google Workspace MCP Connection Test")
    print("=" * 60)
    print()

    # Test 1: MCP connection
    mcp_connected = test_mcp_connection()

    # Test 2: Executable accessibility
    exe_accessible = test_workspace_mcp_executable()

    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    print(f"MCP Connection:    {'[PASS]' if mcp_connected else '[FAIL]'}")
    print(f"Executable Access: {'[PASS]' if exe_accessible else '[FAIL]'}")
    print()

    if mcp_connected and exe_accessible:
        print("[SUCCESS] All tests passed! Google Workspace MCP is ready to use.")
        print("\nTry these commands with Claude Code:")
        print('  "Send an email to [recipient]"')
        print('  "Create a Google Doc"')
        print('  "List my Gmail messages"')
    else:
        print("[WARNING] Some tests failed. Check the errors above.")
        print("\nTroubleshooting:")
        print("  1. Verify workspace-mcp is installed: pip install workspace-mcp")
        print("  2. Check .mcp.json configuration")
        print("  3. Ensure Google OAuth credentials are set up")
