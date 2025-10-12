"""
MCP Client Module
Handles connection to MCP servers (like Playwright MCP)
"""

import os
import json
import subprocess
import asyncio
from typing import Dict, List, Optional, Any
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """Client for connecting to MCP servers"""

    def __init__(self, config_path: str = "mcp_config.json"):
        """
        Initialize MCP client

        Args:
            config_path: Path to MCP configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.servers = {}
        self.anthropic_client = Anthropic()

    def _load_config(self) -> Dict:
        """Load MCP configuration"""
        if not os.path.exists(self.config_path):
            return {"mcpServers": {}}

        with open(self.config_path, 'r') as f:
            return json.load(f)

    def is_available(self) -> bool:
        """Check if MCP servers are configured"""
        return bool(self.config.get("mcpServers"))

    def get_playwright_tools(self) -> List[Dict]:
        """
        Get Playwright MCP tool definitions for Anthropic API

        Returns:
            List of tool definition dictionaries
        """
        return [
            {
                "name": "playwright_navigate",
                "description": "Navigate to a URL in the browser",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL to navigate to"
                        }
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "playwright_screenshot",
                "description": "Take a screenshot of the current page",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name for the screenshot file"
                        },
                        "fullPage": {
                            "type": "boolean",
                            "description": "Capture full scrollable page"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "playwright_click",
                "description": "Click an element on the page",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector for the element to click"
                        }
                    },
                    "required": ["selector"]
                }
            },
            {
                "name": "playwright_fill",
                "description": "Fill a form input field",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector for the input field"
                        },
                        "value": {
                            "type": "string",
                            "description": "Value to fill"
                        }
                    },
                    "required": ["selector", "value"]
                }
            },
            {
                "name": "playwright_evaluate",
                "description": "Execute JavaScript in the browser and return result",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "script": {
                            "type": "string",
                            "description": "JavaScript code to execute"
                        }
                    },
                    "required": ["script"]
                }
            },
            {
                "name": "playwright_press_key",
                "description": "Press a keyboard key (useful for Figma prototypes, image carousels, presentations). Use ArrowRight for next, ArrowLeft for previous, r for restart.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "Key to press: ArrowRight, ArrowLeft, ArrowUp, ArrowDown, Enter, Escape, r, etc."
                        }
                    },
                    "required": ["key"]
                }
            },
            {
                "name": "playwright_scroll_page",
                "description": "Scroll the entire page to capture full content. Use for long pages, dashboards, or detailed designs.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "direction": {
                            "type": "string",
                            "description": "Direction to scroll: 'down', 'up', 'bottom', 'top'",
                            "enum": ["down", "up", "bottom", "top"]
                        },
                        "amount": {
                            "type": "number",
                            "description": "Pixels to scroll (optional, default varies by direction)"
                        }
                    },
                    "required": ["direction"]
                }
            },
            {
                "name": "playwright_get_page_info",
                "description": "Get current page information including URL, title, and visible text",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

    async def call_with_tools(
        self,
        prompt: str,
        max_tokens: int = 8192,
        tools: Optional[List[Dict]] = None,
        log_callback = None,
        max_iterations: int = 10
    ) -> str:
        """
        Call Claude with tool support - allows MULTIPLE tool iterations

        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens for response
            tools: Tool definitions (defaults to Playwright tools)
            log_callback: Optional callback for logging activity
            max_iterations: Maximum number of tool-use iterations (default: 10)

        Returns:
            Final response text
        """
        if tools is None:
            tools = self.get_playwright_tools()

        def _log(message: str, emoji: str = ""):
            """Helper for logging"""
            output = f"{emoji} {message}" if emoji else message
            print(output)
            if log_callback:
                log_callback(output)

        _log("Calling Claude with tool support...", "🔧")
        _log(f"Available tools: {len(tools)}", "  →")
        _log(f"Max iterations: {max_iterations}", "  →")

        # Build initial messages
        messages = [{"role": "user", "content": prompt}]

        # Allow multiple iterations of tool use
        for iteration in range(max_iterations):
            # API call with tools
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                tools=tools,
                messages=messages
            )

            # Check stop reason
            if response.stop_reason == "end_turn":
                # Claude is done, extract final response
                _log(f"\n✓ Task complete after {iteration + 1} iteration(s)\n", "")
                response_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        response_text += block.text
                return response_text

            elif response.stop_reason == "tool_use":
                if iteration == 0:
                    _log("\n🔧 Claude is using tools!\n", "")
                else:
                    _log(f"\n🔧 Tool iteration {iteration + 1}/{max_iterations}\n", "")

                # Process tool uses
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        _log(f"Tool: {block.name}", "🔧")
                        _log(f"  Input: {json.dumps(block.input, indent=2)}", "")

                        # Execute tool via REAL MCP if session available, else simulate
                        if hasattr(self, 'mcp_session') and self.mcp_session:
                            result = await self._execute_tool_real(block.name, block.input, self.mcp_session, _log)
                        else:
                            result = await self._simulate_tool_execution(block.name, block.input, _log)

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })

                        _log(f"  Result: {result[:200]}...\n", "✓")

                # Add assistant response and tool results to messages
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})

                # Continue to next iteration
                _log("Continuing to next step...", "🤖")

            elif response.stop_reason == "max_tokens":
                _log("⚠️  Reached max tokens", "")
                response_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        response_text += block.text
                return response_text

            else:
                # Unknown stop reason
                _log(f"Unexpected stop reason: {response.stop_reason}", "  →")
                response_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        response_text += block.text
                return response_text

        # Reached max iterations
        _log(f"⚠️  Reached max iterations ({max_iterations})", "")
        response_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                response_text += block.text
        return response_text

    async def _execute_tool_real(
        self,
        tool_name: str,
        tool_input: Dict,
        mcp_session: ClientSession,
        log_callback
    ) -> str:
        """
        Execute tool via REAL MCP stdio connection

        Args:
            tool_name: Name of the tool
            tool_input: Tool input parameters
            mcp_session: Active MCP session
            log_callback: Logging function

        Returns:
            Real tool result from Playwright MCP server
        """
        try:
            log_callback(f"  → Executing tool via MCP server...", "")

            # Call the tool through MCP session
            result = await mcp_session.call_tool(tool_name, arguments=tool_input)

            # Extract result content
            if hasattr(result, 'content') and result.content:
                # MCP returns content as list of TextContent or ImageContent
                result_text = ""
                for content in result.content:
                    if hasattr(content, 'text'):
                        result_text += content.text
                    elif hasattr(content, 'data'):
                        # For images/binary data
                        result_text += f"[Binary data: {len(content.data)} bytes]"

                return result_text if result_text else str(result)
            else:
                return str(result)

        except Exception as e:
            log_callback(f"  ⚠️  MCP tool execution error: {e}", "")
            # Fallback to simulation if MCP fails
            return await self._simulate_tool_execution(tool_name, tool_input, log_callback)

    async def _simulate_tool_execution(
        self,
        tool_name: str,
        tool_input: Dict,
        log_callback
    ) -> str:
        """
        Fallback: Simulate tool execution if MCP fails

        Args:
            tool_name: Name of the tool
            tool_input: Tool input parameters
            log_callback: Logging function

        Returns:
            Simulated tool result
        """
        await asyncio.sleep(0.3)

        if tool_name == "playwright_navigate":
            url = tool_input.get("url", "")
            return f"[SIMULATED] Successfully navigated to {url}. Page loaded with 200 OK status."

        elif tool_name == "playwright_screenshot":
            name = tool_input.get("name", "screenshot.png")
            return f"[SIMULATED] Screenshot saved as {name}. Size: 1920x1080."

        elif tool_name == "playwright_click":
            selector = tool_input.get("selector", "")
            return f"[SIMULATED] Clicked element: {selector}"

        elif tool_name == "playwright_fill":
            selector = tool_input.get("selector", "")
            value = tool_input.get("value", "")
            return f"[SIMULATED] Filled {selector} with: {value}"

        elif tool_name == "playwright_evaluate":
            script = tool_input.get("script", "")
            return f"[SIMULATED] Executed JavaScript: {script[:100]}..."

        elif tool_name == "playwright_press_key":
            key = tool_input.get("key", "")
            return f"[SIMULATED] Pressed key: {key}"

        elif tool_name == "playwright_scroll_page":
            direction = tool_input.get("direction", "down")
            amount = tool_input.get("amount", 800)
            return f"[SIMULATED] Scrolled page {direction} by {amount}px"

        elif tool_name == "playwright_get_page_info":
            return f"[SIMULATED] Page info: URL: https://example.com, Title: Example Page"

        else:
            return f"[SIMULATED] Tool {tool_name} executed"


class PlaywrightMCPClient(MCPClient):
    """Specialized MCP client for Playwright with REAL MCP stdio connection"""

    def __init__(self, config_path: str = "mcp_config.json"):
        super().__init__(config_path)
        self.mcp_session = None
        self.stdio_context = None

    async def start_server(self) -> bool:
        """
        Start Playwright MCP server and establish stdio connection

        Returns:
            True if server started and connected successfully
        """
        try:
            print("🚀 Starting Playwright MCP server...")

            # Get server config
            server_config = self.config.get("mcpServers", {}).get("playwright", {})
            command = server_config.get("command", "npx")
            args = server_config.get("args", ["-y", "@executeautomation/playwright-mcp-server"])
            env = server_config.get("env", {})

            # Create server parameters for MCP SDK
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=env if env else None
            )

            # Establish stdio connection using MCP SDK
            print("🔌 Establishing MCP stdio connection...")
            self.stdio_context = stdio_client(server_params)
            read, write = await self.stdio_context.__aenter__()

            # Create MCP session
            self.mcp_session = ClientSession(read, write)
            await self.mcp_session.__aenter__()

            # Initialize the connection
            await self.mcp_session.initialize()

            print("✓ Playwright MCP server connected via stdio!\n")
            return True

        except Exception as e:
            print(f"✗ Error starting MCP server: {e}")
            print(f"  → Make sure Playwright MCP is installed: npm install -g @executeautomation/playwright-mcp-server\n")
            return False

    async def stop_server(self):
        """Stop Playwright MCP server and close connection"""
        try:
            if self.mcp_session:
                print("⏹️  Closing MCP session...")
                await self.mcp_session.__aexit__(None, None, None)
                self.mcp_session = None

            if self.stdio_context:
                await self.stdio_context.__aexit__(None, None, None)
                self.stdio_context = None

            print("✓ MCP connection closed\n")
        except Exception as e:
            print(f"Warning: Error closing MCP connection: {e}\n")

    def get_status(self) -> Dict[str, Any]:
        """
        Get MCP client status

        Returns:
            Status dictionary
        """
        return {
            "configured": self.is_available(),
            "server_running": self.mcp_session is not None,
            "session_active": self.mcp_session is not None,
            "tools_available": len(self.get_playwright_tools()),
            "config_path": self.config_path,
            "connection_type": "REAL MCP stdio" if self.mcp_session else "Not connected"
        }
