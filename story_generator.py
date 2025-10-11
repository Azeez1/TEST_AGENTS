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

   CRITICAL: Choose the appropriate template based on story type. Use hierarchical numbering (1, a, i, 1, a) for ALL templates.

   === UNIVERSAL CHECKLIST (Apply to ALL Stories) ===
   Before writing ACs, verify you've addressed:
   - Trigger/Entry Point: What initiates this?
   - Inputs: What data is required?
   - Processing/Logic: What happens during execution?
   - Outputs: What's produced?
   - Validation Rules: What's verified?
   - Error Handling: What happens when it fails?
   - Edge Cases: Unusual scenarios?
   - Permissions: Who can access?
   - State Changes: What changes in the system?
   - Success Criteria: How do we know it worked?

   === TEMPLATE SELECTION GUIDE ===

   Template 1 - UI/Form Stories: Forms, data entry, wizards, screen flows
   Template 2 - Dashboard/List Views: Dashboards, tables, summary pages
   Template 3 - Backend/API: System integrations, APIs, data sync
   Template 4 - Notifications: Alerts, push notifications, emails
   Template 5 - Business Logic: Calculations, pricing, rules, eligibility
   Template 6 - Reports/Exports: Data exports, file generation, downloads
   Template 7 - Search/Filter: Search functionality, filtering, queries

   === TEMPLATE 1: UI/FORM STORIES ===
   Structure:
   1. The [Page Name] page displays the following:
      a. [UI Element/Section]:
         i. [Field] (Required) OR (If Applicable)
         ii. If the user does not [condition] they will receive an error message informing them that [exact error text]
      b. [Tooltips/Modals]:
         i. Tool Tip
            1. Selecting will display a modal that [describes content]
            2. [Action button/link]
               a. Selecting will redirect the user to [URL]
      c. Progress Bar is displayed [if multi-step]
      d. Cancel (See [Related Story])
      e. Option to navigate back to [Previous Page]
      f. Continue
         i. If the user does not [condition] they will not have the option to continue

   === TEMPLATE 2: DASHBOARD/LIST STORIES ===
   Structure:
   1. [User Type/State] Users:
      a. [Behavior for this state]
   2. [Alternative State]:
      a. [Alternative behavior]
   3. The [Dashboard] displays the following:
      a. [Section Name]:
         i. Display [quantity limit] of [items]
         ii. Sort by [criteria]
         iii. Each item shows:
            1. [Data point 1]
            2. [Data point 2]
         iv. User actions:
            1. [Action] (See [Related Story])

   === TEMPLATE 3: BACKEND/API STORIES ===
   Structure:
   1. When [trigger] occurs:
      a. System initiates [process]
   2. System sends/receives data:
      a. Endpoint: [URL]
      b. Authentication: [method]
      c. Request payload includes:
         i. [Field]: [type/format]
      d. System receives response:
         i. Success (HTTP 200):
            1. Contains: [data]
            2. System updates: [database/state]
            3. User sees: [result]
         ii. Error (HTTP [code]):
            1. System logs: [error details]
            2. System retries: [logic OR does not retry]
            3. User sees: [error message]
   3. Timeout handling:
      a. If no response within [X] seconds:
         i. System [action]

   === TEMPLATE 4: NOTIFICATION STORIES ===
   Structure:
   1. Notification triggers when:
      a. [Condition 1]
      b. [Condition 2]
   2. Notification eligibility:
      a. User has [permission/setting]
   3. Notification content includes:
      a. [Content element 1]
      b. [Action button]: [destination]
   4. Notification delivery:
      a. Channel: [Push/Email/SMS]
      b. Timing: [Immediate/Scheduled]
   5. Notification behavior:
      a. Displays in [location]
      b. User can [interact/dismiss]
   6. Opt-out mechanism:
      a. User can disable via [method]

   === TEMPLATE 5: BUSINESS LOGIC/CALCULATION STORIES ===
   Structure:
   1. System calculates [output] based on:
      a. Input: [source] - [description]
      b. Business rule: [rule]
   2. Calculation logic:
      a. If [condition], then:
         i. [Formula/rule]
         ii. Result: [output]
      b. If [edge case], then:
         i. [Alternative logic]
   3. Validation:
      a. System validates [criteria]
      b. If validation fails:
         i. System [action]
         ii. User notified: [message]
   4. Output:
      a. System returns: [format]
      b. User sees: [display format]

   === TEMPLATE 6: REPORT/EXPORT STORIES ===
   Structure:
   1. Report triggered by: [action]
   2. Report filters/parameters:
      a. [Filter 1]: [options]
         i. Default: [value]
         ii. Required: [Yes/No]
   3. Report data includes:
      a. Column 1: [name] - [source]
      b. Total records: [limit]
      c. Sort order: [default]
   4. Report format:
      a. File type: [CSV/PDF/Excel]
      b. File naming: [pattern]
   5. Report delivery:
      a. [Download/Email/Saved to location]
   6. Empty state:
      a. If no data:
         i. System [action]
         ii. User notified: [message]

   === TEMPLATE 7: SEARCH/FILTER STORIES ===
   Structure:
   1. The [Search Feature] displays:
      a. Search input:
         i. Accepts: [input types]
         ii. Validation: [rules]
      b. Search trigger:
         i. Initiates when [action]
         ii. Minimum characters: [number]
   2. Filter options:
      a. [Filter name]:
         i. Type: [dropdown/checkbox]
         ii. Options: [list]
   3. Search behavior:
      a. Looks for matches in:
         i. [Field 1]
      b. Case sensitive: [Yes/No]
      c. Partial matches: [Allowed/Not allowed]
   4. Search results:
      a. Display [X] per page
      b. Each result shows:
         i. [Data point]
   5. No results:
      a. Display message: [text]
      b. Suggestions: [alternatives]

   === COMMON PATTERNS (Reusable) ===

   Validation:
   i. If the user does not [action] they will receive an error message informing them that [exact error text]

   Navigation:
   i. Selecting will redirect the user to [Destination] ([URL]) to [purpose]

   Cross-reference:
   ii. [Action] (See [Related Story Name])

   Pre-population:
   i. [Field] will pre-populate with [source]

   Permissions:
   a. User must be [authenticated/role] to access
   b. If no permission:
      i. User sees: [message OR redirect]

   === WHAT TO AVOID ===
   ❌ Design details ("swipe left")
   ❌ Vague statements ("manage items")
   ❌ Ambiguous requirements
   ❌ Missing error scenarios"""
            ac_format_note = "using appropriate template with hierarchical numbering and implementation-level detail"
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
IMPORTANT: Maintain the Explicit/Detailed AC format. Choose the appropriate template based on story type.

Use hierarchical numbering (1, a, i, 1, a) for ALL templates.

Template Selection:
- UI/Form: Use Template 1 (forms, data entry, wizards, screen flows)
- Dashboard/List: Use Template 2 (dashboards, tables, summary pages)
- Backend/API: Use Template 3 (system integrations, APIs, data sync)
- Notifications: Use Template 4 (alerts, push, emails)
- Business Logic: Use Template 5 (calculations, pricing, rules)
- Reports: Use Template 6 (data exports, file generation)
- Search: Use Template 7 (search, filtering, queries)

Universal Requirements (ALL stories must address):
✓ Trigger/Entry Point
✓ Inputs required
✓ Processing/Logic
✓ Outputs produced
✓ Validation Rules
✓ Error Handling
✓ Edge Cases
✓ Permissions
✓ State Changes
✓ Success Criteria

Common Patterns to Use:
- Validation: "If the user does not [action] they will receive an error message informing them that [exact text]"
- Navigation: "Selecting will redirect the user to [Destination] ([URL]) to [purpose]"
- Cross-reference: "[Action] (See [Related Story Name])"
- Pre-population: "[Field] will pre-populate with [source]"
- Permissions: "User must be [authenticated/role] to access"

What to Avoid:
❌ Design details ("swipe left")
❌ Vague statements ("manage items")
❌ Ambiguous requirements
❌ Missing error scenarios"""
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
