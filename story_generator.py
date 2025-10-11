"""
Story Generator Module
Contains prompts and logic for generating user stories and acceptance criteria
"""

from typing import Dict, List


class StoryGenerator:
    """Generate user stories and acceptance criteria from meeting notes"""

    @staticmethod
    def get_analysis_prompt(notes: str) -> str:
        """
        Create prompt for analyzing notes and extracting structured information

        Args:
            notes: Raw meeting notes text

        Returns:
            Prompt for Claude to analyze notes
        """
        return f"""Analyze the following meeting notes and extract structured information for creating user stories.

Meeting Notes:
{notes}

Please extract and identify:
1. Features or functionality mentioned
2. User goals and pain points
3. Business value or rationale
4. Relevant pages/screens/areas affected
5. Any constraints or specific requirements

Return the analysis in a structured format that will help generate user stories."""

    @staticmethod
    def get_story_generation_prompt(analysis: str, existing_stories: List[str] = None, ac_format: str = "gherkin") -> str:
        """
        Create prompt for generating user stories from analysis

        Args:
            analysis: Structured analysis from notes
            existing_stories: List of existing user stories (to avoid duplicates)
            ac_format: Format for acceptance criteria ("gherkin" or "explicit")

        Returns:
            Prompt for generating user stories
        """
        existing_context = ""
        if existing_stories:
            existing_context = f"\n\nExisting stories (avoid duplicates):\n" + "\n".join(existing_stories)

        # Define AC format instructions
        if ac_format == "explicit":
            ac_instructions = """2. Acceptance Criteria in Explicit/Detailed format

   TARGET LENGTH: 30-50 lines total (2,500-4,500 characters)

   STRUCTURE:
   - Use 3-4 levels max (1, a, i, 1)
   - Keep 4-7 main numbered sections
   - Focus on functional requirements only

   INCLUDE:
   ✅ What displays/happens on screen
   ✅ User interactions and results
   ✅ Conditional logic (if/then statements)
   ✅ Validation and error messages
   ✅ Navigation flows
   ✅ Required vs optional fields
   ✅ User states (guest/logged in, empty states)
   ✅ Responsive behavior summary (desktop/tablet/mobile)
   ✅ Cross-references to related stories

   AVOID:
   ❌ Specific timings (say "loads quickly" or "within X seconds" only if critical)
   ❌ Detailed analytics event lists (summarize in Notes)
   ❌ Pixel-perfect design specs (fonts, colors, exact spacing)
   ❌ Exhaustive accessibility specs (summarize in Notes)
   ❌ CMS/admin implementation details
   ❌ A/B testing requirements
   ❌ Social features (unless core to story)

   EXAMPLE STRUCTURE:

   1. Page Display
      a. Primary content/form elements
         i. Field Name (Required)
         ii. Field Name (Optional)
      b. User interactions
         i. Button/link behavior
         ii. If [condition], then [result]
      c. Error handling
         i. Error message: "[exact text]"

   2. User States
      a. Guest users: [behavior]
      b. Logged-in users: [behavior]
      c. Empty state: [what displays]

   3. Validation Rules
      a. Field validation
         i. If [invalid condition], show error: "[message]"
      b. Form submission
         i. Required fields must be completed

   4. Navigation
      a. Success: Redirect to [destination]
      b. Cancel: Return to [previous page]
      c. Cross-reference: (See [Related Story])

   5. Responsive Behavior
      a. Desktop: [key differences]
      b. Mobile: [key differences]

   NOTES SECTION (always include):
   Add a "Notes" section after ACs covering:
   - Performance considerations (e.g., "loads within 2 seconds")
   - Accessibility summary (e.g., "screen reader compatible, keyboard navigation")
   - Analytics overview (e.g., "track button clicks, form submissions")
   - Future enhancements (e.g., "v2: add filtering")
   - Technical hints (e.g., "use caching for performance")
   - Open questions (e.g., "confirm error message wording with UX")"""
            ac_format_note = "with realistic length (30-50 lines) and practical focus"
        else:
            ac_instructions = """2. Detailed Acceptance Criteria in Gherkin format (Given/When/Then)
   - Include at least 4-6 acceptance criteria per story
   - Cover happy path, edge cases, error handling, mobile responsiveness, and accessibility
   - Each AC should be specific and testable
   - Follow this pattern: "Given [context], when [action], then [expected outcome]" """
            ac_format_note = "each in Given/When/Then format"

        return f"""Based on the following analysis, generate comprehensive user stories in the standard format:
"As a [user type], I want [goal], so that [benefit]"

Analysis:
{analysis}
{existing_context}

For each user story, also provide:
1. Feature/Epic name (concise feature title)
{ac_instructions}
3. Rationale or Business Case (explain the business value and impact)
4. Relevant Page(s) (which pages/screens/areas this affects)

Format the output as a JSON array with objects containing:
- user_story: The user story text
- feature_epic: The feature/epic name
- acceptance_criteria: Array of acceptance criteria strings ({ac_format_note})
- business_case: The rationale/business case
- relevant_pages: The relevant pages/screens

Consider edge cases like:
- Missing or invalid data
- Mobile/tablet responsiveness
- Accessibility (screen readers, keyboard navigation)
- Error states and recovery
- Performance considerations
- Cross-browser compatibility (if web-based)"""

    @staticmethod
    def get_refinement_prompt(story: Dict, instruction: str, ac_format: str = "gherkin") -> str:
        """
        Create prompt for refining an existing story

        Args:
            story: Existing story dictionary
            instruction: User's refinement instruction
            ac_format: Format for acceptance criteria ("gherkin" or "explicit")

        Returns:
            Prompt for refining the story
        """
        # Define AC format reminder
        if ac_format == "explicit":
            ac_format_reminder = """
IMPORTANT: Maintain the Explicit/Detailed AC format.

TARGET LENGTH: 30-50 lines (2,500-4,500 characters)

STRUCTURE: Use 3-4 levels max (1, a, i, 1), keep 4-7 main sections

INCLUDE:
✅ What displays/happens on screen
✅ User interactions and conditional logic (if/then)
✅ Validation and error messages
✅ Navigation flows and cross-references
✅ User states (guest/logged in, empty state)
✅ Responsive behavior summary

AVOID:
❌ Specific timings, detailed analytics, pixel-perfect design
❌ Exhaustive accessibility, CMS details, A/B testing
❌ Social features (unless core)

NOTES SECTION: Always include performance, accessibility, analytics, future enhancements, technical hints, open questions"""
        else:
            ac_format_reminder = "\nIMPORTANT: Maintain the Gherkin format (Given/When/Then) for all acceptance criteria."

        return f"""Refine the following user story based on the instruction provided.

Current Story:
User Story: {story.get('user_story', '')}
Feature/Epic: {story.get('feature_epic', '')}
Acceptance Criteria:
{chr(10).join('- ' + ac for ac in story.get('acceptance_criteria', []))}
Business Case: {story.get('business_case', '')}
Relevant Pages: {story.get('relevant_pages', '')}

Refinement Instruction:
{instruction}
{ac_format_reminder}

Return the refined story in the same JSON format:
{{
    "user_story": "...",
    "feature_epic": "...",
    "acceptance_criteria": ["...", "..."],
    "business_case": "...",
    "relevant_pages": "..."
}}

Maintain the quality and detail level of the original story while implementing the requested changes."""

    @staticmethod
    def get_batch_update_prompt(stories: List[Dict], instruction: str) -> str:
        """
        Create prompt for batch updating multiple stories

        Args:
            stories: List of story dictionaries
            instruction: Batch update instruction

        Returns:
            Prompt for batch updates
        """
        stories_text = "\n\n".join([
            f"Story {i+1}:\n{story.get('user_story', '')}"
            for i, story in enumerate(stories)
        ])

        return f"""Apply the following update to all user stories below:

Update Instruction: {instruction}

Stories to Update:
{stories_text}

Return the updated stories as a JSON array, maintaining all original fields while implementing the requested changes.
Each story should have: user_story, feature_epic, acceptance_criteria (array), business_case, relevant_pages"""


def create_story_prompt(notes: str, context: str = "") -> str:
    """
    Helper function to create a complete story generation prompt

    Args:
        notes: Raw meeting notes
        context: Optional context about the project

    Returns:
        Complete prompt for story generation
    """
    generator = StoryGenerator()
    return generator.get_story_generation_prompt(notes)
