"""
Autonomous Mode Module
MCP-enabled agent with browser and research capabilities
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from anthropic import Anthropic
from note_parser import extract_notes, extract_notes_from_multiple_files
from story_generator import StoryGenerator
from formatters import StoryFormatter, validate_stories
from excel_handler import ExcelHandler, read_existing_stories
from feedback_handler import FeedbackHandler, FeedbackPromptBuilder
from conversation_memory import ConversationMemory
from research_prompts import ResearchPrompts, create_autonomous_research_plan
from mcp_client import PlaywrightMCPClient
import asyncio


class AutonomousAgent:
    """
    Autonomous user story agent with browser and research capabilities
    Enhanced version of UserStoryAgent with MCP integration
    """

    def __init__(self, output_file: str = "user_stories.xlsx", enable_browser: bool = False):
        """
        Initialize autonomous agent

        Args:
            output_file: Output Excel file path
            enable_browser: Enable browser/research mode
        """
        self.output_file = output_file
        self.enable_browser = enable_browser

        # Core components (from original agent)
        self.story_generator = StoryGenerator()
        self.formatter = StoryFormatter()
        self.excel_handler = ExcelHandler(output_file)
        self.client = Anthropic()

        # New autonomous components
        self.memory = ConversationMemory("preferences_store.json")
        self.feedback_handler = FeedbackHandler(memory_store=self.memory)

        # MCP Client
        self.mcp_client = PlaywrightMCPClient()
        self.mcp_enabled = self.mcp_client.is_available()
        self.mcp_server_started = False

    def _check_mcp_available(self) -> bool:
        """Check if MCP config exists"""
        return self.mcp_client.is_available()

    def get_mcp_status(self) -> Dict:
        """Get MCP connection status"""
        return self.mcp_client.get_status()

    async def generate_from_notes(
        self,
        notes_input: str,
        ac_format: str = "gherkin",
        browser_instructions: str = "",
        append: bool = True
    ) -> Tuple[bool, List[Dict], str]:
        """
        Generate user stories from notes with optional browser research

        Args:
            notes_input: File path or raw text notes
            ac_format: AC format ("gherkin" or "explicit")
            browser_instructions: Optional browser instructions for research
            append: Whether to append to existing Excel

        Returns:
            Tuple of (success, stories, message)
        """
        try:
            # Extract notes
            print("📝 Extracting notes...")
            notes = extract_notes(notes_input)

            if not notes:
                return False, [], "No notes found or file is empty"

            print(f"✓ Extracted {len(notes)} characters of notes\n")

            # Check for existing stories
            existing_stories = []
            if append and self.excel_handler.file_exists():
                print("📚 Reading existing stories...")
                existing_stories = read_existing_stories(self.output_file)
                print(f"✓ Found {len(existing_stories)} existing stories\n")

            # Generate stories (with or without browser research)
            if self.enable_browser and self.mcp_enabled:
                stories = await self._generate_with_research(
                    notes,
                    existing_stories,
                    ac_format,
                    browser_instructions
                )
            else:
                stories = await self._generate_standard(
                    notes,
                    existing_stories,
                    ac_format
                )

            if not stories:
                return False, [], "Failed to generate stories"

            # Validate stories
            is_valid, issues = validate_stories(stories)
            if not is_valid:
                print("⚠️  Validation warnings:")
                for issue in issues:
                    print(f"  - {issue}")
                print()

            # Write to Excel
            print(f"💾 Writing to {self.output_file}...")
            self.excel_handler.write_stories(stories, append=append)
            self.excel_handler.close()
            print(f"✓ Successfully saved {len(stories)} stories to Excel!\n")

            return True, stories, f"Generated {len(stories)} stories successfully"

        except Exception as e:
            return False, [], f"Error generating stories: {str(e)}"

    async def _generate_standard(
        self,
        notes: str,
        existing_stories: List[Dict],
        ac_format: str
    ) -> List[Dict]:
        """
        Standard generation without browser research (original behavior)

        Args:
            notes: Meeting notes
            existing_stories: Existing stories to avoid duplicates
            ac_format: AC format to use

        Returns:
            List of generated stories
        """
        print("🤖 Generating user stories with Claude API...\n")

        # Build prompt with feedback
        base_prompt = self._build_generation_prompt(notes, existing_stories, ac_format)
        enhanced_prompt = FeedbackPromptBuilder.enhance_generation_prompt(
            base_prompt,
            self.feedback_handler,
            ac_format
        )

        # Call Claude API
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": enhanced_prompt}]
        )

        response_text = response.content[0].text
        print("✓ Generation complete!\n")

        # Parse stories
        stories = self.formatter.parse_ai_response(response_text)
        print(f"✓ Parsed {len(stories)} user stories\n")

        return stories

    async def _generate_with_research(
        self,
        notes: str,
        existing_stories: List[Dict],
        ac_format: str,
        browser_instructions: str = "",
        stream_callback = None
    ) -> List[Dict]:
        """
        Generate stories with browser research enabled

        Args:
            notes: Meeting notes
            existing_stories: Existing stories
            ac_format: AC format to use
            browser_instructions: Optional browser instructions
            stream_callback: Optional callback for streaming updates

        Returns:
            List of generated stories
        """
        def _log(message: str, emoji: str = ""):
            """Helper to print and optionally stream to UI"""
            output = f"{emoji} {message}" if emoji else message
            print(output)
            if stream_callback:
                stream_callback(output)

        _log("Autonomous Research Mode Enabled\n", "🌐")

        # Create research plan
        research_plan = create_autonomous_research_plan(notes, browser_instructions)
        detected_domain = research_plan.get("detected_domain", "")

        if detected_domain:
            _log(f"Detected domain: {detected_domain}\n", "🎯")

        # Build research-enhanced prompt
        if browser_instructions:
            _log("Following your research instructions...", "📋")
            _log(f"Instructions: {browser_instructions[:100]}...\n", "  →")
            research_prompt = ResearchPrompts.get_guided_research_prompt(
                notes,
                browser_instructions,
                ac_format
            )
        else:
            _log("Performing autonomous research...", "🔍")
            _log(f"Will research: {detected_domain or 'general'} best practices\n", "  →")
            research_prompt = ResearchPrompts.get_domain_research_prompt(
                notes,
                detected_domain
            )

        # Add existing stories context
        if existing_stories:
            existing_list = [s['user_story'] for s in existing_stories[:5]]
            research_prompt += "\n\nExisting stories (avoid duplicates):\n" + "\n".join(existing_list)
            _log(f"Loaded {len(existing_stories)} existing stories to avoid duplicates", "📚")

        # Enhance with feedback
        enhanced_prompt = FeedbackPromptBuilder.enhance_generation_prompt(
            research_prompt,
            self.feedback_handler,
            ac_format
        )

        feedback_count = len(self.feedback_handler.session_feedback)
        if feedback_count > 0:
            _log(f"Applied {feedback_count} feedback item(s)\n", "💡")

        # Start MCP server if not already started
        if not self.mcp_server_started:
            _log("Starting Playwright MCP server...", "🚀")
            server_started = await self.mcp_client.start_server()
            if server_started:
                self.mcp_server_started = True
                _log("MCP server ready!\n", "✓")
            else:
                _log("Warning: MCP server failed to start, using prompt-only mode\n", "⚠️")

        # Call Claude with MCP tools
        _log("Calling Claude API with MCP tool support...", "🤖")
        prompt_size = len(enhanced_prompt)
        _log(f"Prompt size: {prompt_size:,} characters", "  →")
        _log(f"Available MCP tools: {len(self.mcp_client.get_playwright_tools())}\n", "  →")

        # Use MCP client for tool-enabled API call
        response_text = await self.mcp_client.call_with_tools(
            enhanced_prompt,
            max_tokens=8192,
            log_callback=lambda msg: _log(msg, "")
        )

        _log("\n" + "─" * 60, "")
        _log("Response complete!", "✓")
        response_length = len(response_text)
        _log(f"Total response: {response_length:,} characters\n", "  →")

        # Parse stories
        _log("Parsing JSON response...", "🔧")
        stories = self.formatter.parse_ai_response(response_text)
        _log(f"Successfully parsed {len(stories)} user stories!\n", "✓")

        return stories

    def _build_generation_prompt(
        self,
        notes: str,
        existing_stories: List[Dict],
        ac_format: str
    ) -> str:
        """
        Build generation prompt (same as original agent)

        Args:
            notes: Meeting notes
            existing_stories: Existing stories
            ac_format: AC format

        Returns:
            Prompt string
        """
        existing_context = ""
        if existing_stories:
            existing_list = [s['user_story'] for s in existing_stories[:5]]
            existing_context = "\n\nExisting stories (avoid duplicates):\n" + "\n".join(existing_list)

        # Use story generator's prompts
        if ac_format == "explicit":
            return self.story_generator.get_story_generation_prompt(
                notes,
                [s['user_story'] for s in existing_stories] if existing_stories else None,
                ac_format="explicit"
            )
        else:
            return self.story_generator.get_story_generation_prompt(
                notes,
                [s['user_story'] for s in existing_stories] if existing_stories else None,
                ac_format="gherkin"
            )

    def add_feedback(self, feedback: str, context: str = ""):
        """
        Add user feedback for future generations

        Args:
            feedback: Feedback text
            context: Context where feedback was given
        """
        self.feedback_handler.add_feedback(feedback, context)
        print(f"✓ Feedback saved: {feedback[:50]}...")

    def get_feedback_summary(self) -> Dict:
        """
        Get summary of all feedback

        Returns:
            Summary dictionary
        """
        return self.feedback_handler.get_feedback_summary()

    def clear_feedback(self):
        """Clear session feedback (keeps stored preferences)"""
        self.feedback_handler.clear_session_feedback()

    def get_preferences(self) -> List[Dict]:
        """
        Get all stored preferences

        Returns:
            List of preference dictionaries
        """
        return self.memory.get_all_preferences()

    def remove_preference(self, index: int) -> bool:
        """
        Remove a stored preference

        Args:
            index: Index of preference to remove

        Returns:
            True if removed successfully
        """
        return self.memory.remove_preference(index)

    async def cleanup(self):
        """Clean up resources (stop MCP server)"""
        if self.mcp_server_started:
            await self.mcp_client.stop_server()
            self.mcp_server_started = False


async def generate_stories_autonomous(
    notes_path: str,
    output_file: str = "user_stories.xlsx",
    ac_format: str = "gherkin",
    enable_browser: bool = False,
    browser_instructions: str = "",
    feedback: str = ""
) -> Tuple[bool, List[Dict], str]:
    """
    Main entry point for autonomous story generation

    Args:
        notes_path: Path to notes file
        output_file: Output Excel file
        ac_format: AC format ("gherkin" or "explicit")
        enable_browser: Enable browser research
        browser_instructions: Optional browser instructions
        feedback: Optional feedback to apply

    Returns:
        Tuple of (success, stories, message)
    """
    agent = AutonomousAgent(output_file=output_file, enable_browser=enable_browser)

    # Add feedback if provided
    if feedback:
        agent.add_feedback(feedback)

    # Generate stories
    success, stories, message = await agent.generate_from_notes(
        notes_path,
        ac_format=ac_format,
        browser_instructions=browser_instructions,
        append=True
    )

    return success, stories, message
