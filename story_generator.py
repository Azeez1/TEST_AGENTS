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
            ac_instructions = """2. Detailed Acceptance Criteria in Explicit/Detailed format

   IMPORTANT: Write ACs that are detailed, prescriptive, and implementation-focused. Describe exactly what appears on each screen/page and how each element behaves.

   Structure Guidelines:
   - Use hierarchical numbering: 1, a, i, 1, a, etc.
   - Start with: "1. The [Page/Feature Name] page displays the following:"
   - List ALL UI elements (buttons, fields, checkboxes, links, tooltips, modals, progress indicators, error messages)
   - Mark required fields: "First Name (Required)" or "Company Name (If Applicable)"
   - Specify ALL validation rules, character limits, date ranges, allowed formats
   - Use "If...then" statements for conditional logic
   - Include exact URLs for redirects
   - Reference related user stories: "(See [Related Story Name])"
   - Define quantity limits and default behaviors

   Standard Template for Multi-Step Flows:
   ```
   1. The [Page Name] page displays the following:
      a. [Primary content/form fields]
         i. [Field name] (Required)
         ii. If the user does not [condition] they will receive an error message informing them that [error message]
      b. [Secondary elements - tooltips, help text]
         i. Tool Tip
            1. Selecting will display a modal that [describes content]
            2. Redirect link to [Destination]
               a. Selecting will redirect the user to [URL]
      c. Progress Bar is displayed
      d. Cancel (See [Save for Later User Story])
      e. Option to navigate back to the [Previous Page]
      f. Continue
         i. If the user does not [complete required action] they will not have the option to continue
   ```

   What to Include:
   - All UI elements on the page
   - Required vs optional fields clearly marked
   - All validation rules and error messages
   - Navigation flows (where each button/link goes)
   - Edge cases (guest users, empty states, errors)
   - Conditional logic with If...then statements
   - Cross-references to related user stories
   - Default/pre-populated values
   - Quantity limits and constraints
   - Tool tips and modal content descriptions

   What NOT to Include:
   - Design implementation details (e.g., "swipe left")
   - Vague statements (e.g., "User can manage labels")
   - Unclear requirements

   Example AC:
   ```
   1. The Package Weight page displays the following:
      a. Weight entry fields (Required):
         i. Pounds (lbs.)
         ii. Ounces (oz)
         iii. If the user does not input pounds or ounces greater than 0 they will receive an error message informing them that at least one field must be greater than 0
         iv. If the user inputs pounds greater than 70 they will receive an error message informing them that the pounds must be less than or equal to 70
      b. Note recommending the user to use a scale to input the exact weight of the package
      c. Progress Bar is displayed
      d. Cancel (See Save for Later User Story)
      e. Option to navigate back to the Select Packaging Type page
      f. Continue
         i. If the user does not meet the weight entry requirements they will not have the option to continue
   ```"""
            ac_format_note = "each in hierarchical explicit format with implementation-level detail"
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
IMPORTANT: Maintain the Explicit/Detailed AC format with hierarchical numbering and implementation-level detail.

Structure Requirements:
- Use hierarchical numbering: 1, a, i, 1, a
- Start with: "1. The [Page Name] page displays the following:"
- List ALL UI elements on the page
- Mark required fields: "(Required)" or "(If Applicable)"
- Use "If...then" statements for all conditional logic
- Include exact error messages
- Specify navigation destinations and URLs
- Reference related user stories: "(See [Story Name])"
- Include Progress Bar, Cancel, Back, and Continue sections for multi-step flows

Example Format:
1. The [Page] page displays the following:
   a. [Section/Element]:
      i. [Field] (Required)
      ii. If the user does not [condition] they will receive an error message informing them that [message]
   b. Progress Bar is displayed
   c. Cancel (See [Related Story])
   d. Option to navigate back to [Previous Page]
   e. Continue
      i. If the user does not [condition] they will not have the option to continue"""
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
