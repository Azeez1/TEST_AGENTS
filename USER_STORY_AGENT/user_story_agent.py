"""
User Story Agent
Main agent using Claude Agent SDK to generate user stories from meeting notes
"""

import asyncio
import argparse
import sys
import os
from anthropic import Anthropic
from note_parser import extract_notes
from story_generator import StoryGenerator
from excel_handler import ExcelHandler, read_existing_stories
from formatters import StoryFormatter, validate_stories, format_for_display
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class UserStoryAgent:
    """Main agent for generating user stories"""

    def __init__(self, output_file: str = "user_stories.xlsx"):
        self.output_file = output_file
        self.story_generator = StoryGenerator()
        self.formatter = StoryFormatter()
        self.excel_handler = ExcelHandler(output_file)
        self.client = Anthropic()  # Initialize Anthropic client

    async def generate_from_notes(self, notes_input: str, append: bool = True):
        """
        Generate user stories from meeting notes

        Args:
            notes_input: File path or raw text notes
            append: Whether to append to existing Excel or create new
        """
        print("📝 Extracting notes...")
        notes = extract_notes(notes_input)

        if not notes:
            print("❌ No notes found or file is empty")
            return

        print(f"✓ Extracted {len(notes)} characters of notes\n")

        # Check for existing stories
        existing_stories = []
        if append and self.excel_handler.file_exists():
            print("📚 Reading existing stories...")
            existing_stories = read_existing_stories(self.output_file)
            print(f"✓ Found {len(existing_stories)} existing stories\n")

        # Generate stories using Claude
        print("🤖 Generating user stories with Claude API...\n")

        prompt = self._build_generation_prompt(notes, existing_stories)

        # Call Claude API
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract response text
        response_text = response.content[0].text

        print("✓ Generation complete!\n")

        # Parse and format stories
        print("📋 Parsing and formatting stories...")
        try:
            stories = self.formatter.parse_ai_response(response_text)
            print(f"✓ Parsed {len(stories)} user stories\n")

            # Validate stories
            is_valid, issues = validate_stories(stories)
            if not is_valid:
                print("⚠️  Validation warnings:")
                for issue in issues:
                    print(f"  - {issue}")
                print()

            # Display stories
            print(format_for_display(stories))
            print()

            # Write to Excel
            print(f"💾 Writing to {self.output_file}...")
            self.excel_handler.write_stories(stories, append=append)
            self.excel_handler.close()
            print(f"✓ Successfully saved {len(stories)} stories to Excel!\n")

            # Summary
            print("="*80)
            print("📊 SUMMARY")
            print("="*80)
            print(f"Total stories generated: {len(stories)}")
            print(f"Output file: {os.path.abspath(self.output_file)}")
            print(f"Mode: {'Append' if append else 'New file'}")
            if existing_stories:
                print(f"Previous stories: {len(existing_stories)}")
                print(f"Total stories now: {len(existing_stories) + len(stories)}")

        except Exception as e:
            print(f"❌ Error processing stories: {str(e)}")
            print("\nRaw response:")
            print(response_text)

    async def refine_story(self, row_num: int, instruction: str):
        """
        Refine a specific story based on user instruction

        Args:
            row_num: Row number to refine (1-indexed)
            instruction: Refinement instruction
        """
        print(f"🔍 Loading story from row {row_num}...")

        existing_stories = read_existing_stories(self.output_file)
        if row_num < 1 or row_num > len(existing_stories):
            print(f"❌ Invalid row number. File has {len(existing_stories)} stories.")
            return

        story_to_refine = existing_stories[row_num - 1]
        print(f"✓ Loaded story: {story_to_refine['user_story'][:80]}...\n")

        print("🤖 Refining story with Claude API...\n")

        prompt = self.story_generator.get_refinement_prompt(story_to_refine, instruction)

        # Call Claude API
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract response text
        response_text = response.content[0].text

        print("✓ Refinement complete!\n")

        # Parse refined story
        try:
            refined_stories = self.formatter.parse_ai_response(response_text)
            if refined_stories:
                refined_story = refined_stories[0]

                # Display changes
                print("📋 Refined Story:")
                print(format_for_display([refined_story]))
                print()

                # Update Excel
                print(f"💾 Updating row {row_num} in {self.output_file}...")
                self.excel_handler.update_story(row_num, refined_story)
                self.excel_handler.close()
                print("✓ Story updated successfully!\n")

        except Exception as e:
            print(f"❌ Error processing refined story: {str(e)}")

    async def interactive_mode(self):
        """Interactive mode for conversational refinement"""
        print("="*80)
        print("🤖 USER STORY AGENT - Interactive Mode")
        print("="*80)
        print("\nCommands:")
        print("  generate <file>  - Generate stories from notes file")
        print("  refine <row>     - Refine a specific story row")
        print("  view             - View all existing stories")
        print("  exit             - Exit interactive mode")
        print()

        while True:
            try:
                command = input("\n> ").strip()

                if not command:
                    continue

                if command == "exit":
                    print("👋 Goodbye!")
                    break

                elif command == "view":
                    stories = read_existing_stories(self.output_file)
                    if stories:
                        print(format_for_display(stories))
                    else:
                        print("📭 No stories found in the file.")

                elif command.startswith("generate "):
                    file_path = command[9:].strip()
                    await self.generate_from_notes(file_path, append=True)

                elif command.startswith("refine "):
                    row_num = int(command[7:].strip())
                    instruction = input("Refinement instruction: ").strip()
                    await self.refine_story(row_num, instruction)

                else:
                    print("❌ Unknown command. Try: generate, refine, view, or exit")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

    def _build_generation_prompt(self, notes: str, existing_stories: list = None) -> str:
        """Build the complete prompt for story generation"""

        existing_context = ""
        if existing_stories:
            existing_list = [s['user_story'] for s in existing_stories[:5]]  # Show first 5
            existing_context = "\n\nExisting stories (avoid duplicates):\n" + "\n".join(existing_list)

        return f"""You are a user story generation expert. Generate comprehensive, backlog-ready user stories from the following meeting notes.

Meeting Notes:
{notes}
{existing_context}

Generate user stories in this exact JSON format:
[
  {{
    "user_story": "As a [user type], I want [goal], so that [benefit]",
    "feature_epic": "Concise feature name",
    "acceptance_criteria": [
      "Given [context], when [action], then [expected outcome]",
      "Given [context], when [action], then [expected outcome]",
      ...
    ],
    "business_case": "Explanation of business value and impact",
    "relevant_pages": "Page/screen names affected"
  }}
]

Requirements:
1. Each story must follow the "As a..., I want..., so that..." format
2. Include 4-6 detailed acceptance criteria per story in Gherkin format (Given/When/Then)
3. Cover edge cases: errors, mobile responsiveness, accessibility, missing data
4. Business case should explain ROI, customer impact, or strategic value
5. Be specific about which pages/screens/areas are affected

Return ONLY the JSON array, no additional text."""


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="User Story Agent - Generate backlog-ready user stories from meeting notes")

    parser.add_argument('--notes', type=str, help='Path to meeting notes file or raw text')
    parser.add_argument('--output', type=str, default='user_stories.xlsx', help='Output Excel file path')
    parser.add_argument('--append', action='store_true', default=True, help='Append to existing file (default: True)')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing file instead of appending')
    parser.add_argument('--refine', type=int, help='Row number to refine')
    parser.add_argument('--instruction', type=str, help='Refinement instruction (use with --refine)')
    parser.add_argument('--interactive', action='store_true', help='Start interactive mode')

    args = parser.parse_args()

    # Create agent
    agent = UserStoryAgent(output_file=args.output)

    # Interactive mode
    if args.interactive:
        await agent.interactive_mode()
        return

    # Refine mode
    if args.refine:
        if not args.instruction:
            print("❌ --instruction required when using --refine")
            return
        await agent.refine_story(args.refine, args.instruction)
        return

    # Generate mode
    if args.notes:
        append = not args.overwrite
        await agent.generate_from_notes(args.notes, append=append)
        return

    # No arguments - show help
    parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
