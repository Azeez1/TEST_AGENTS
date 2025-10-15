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
            ac_format: Format for acceptance criteria ("gherkin", "explicit", or "functional")

        Returns:
            Prompt for generating user stories
        """
        existing_context = ""
        if existing_stories:
            existing_context = f"\n\nExisting stories (avoid duplicates):\n" + "\n".join(existing_stories)

        # Define AC format instructions
        if ac_format == "functional":
            ac_instructions = """2. Acceptance Criteria in Functional format

   TARGET LENGTH: 30-50 lines total (2,500-4,500 characters)

   STRUCTURE:
   - Use 3-4 levels max (1, a, i, 1)
   - Keep 4-7 main numbered sections
   - Focus on functional requirements ONLY

   LANGUAGE RULES - CRITICAL:

   ✅ PRIMARY PATTERN (Use This Most):
   - **"The user will be able to [action]"** ← MAIN PATTERN!
   - Example: "The user will be able to navigate through product images"
   - Example: "The user will be able to expand to full screen gallery mode"
   - Focus on USER CAPABILITIES and what user can DO

   ✅ SECONDARY PATTERNS (Supporting):
   - "The [element] will [verb]" - for automatic system behavior
   - "When user selects [X], [result]" - for user interactions
   - "The [page/section] will display [content]" - for what shows
   - "will be displayed", "will show", "displays"
   - Describe WHAT the system DOES

   ❌ AVOID ALL DESIGN LANGUAGE AND UI IMPLEMENTATION TERMS:

   Design Adjectives (NO):
   - NO "modern", "modernized", "streamlined", "clean", "clear"
   - NO "prominent", "prominently", "elevated", "intuitive", "seamless"
   - NO "visual hierarchy", "aesthetics", "polished", "sophisticated"

   UI Implementation Terms (NO):
   - NO "button" → USE "call-to-action" or "selectable option"
   - NO "dropdown" → USE "selection menu" or "options list"
   - NO "modal", "popup" → USE "overlay message" or "notification"
   - NO "accordion", "collapsible" → USE "expandable section"
   - NO "carousel", "slider" → USE "navigable images" or "image sequence"
   - NO "toggle", "switch" → USE "option to enable/disable"
   - NO "checkbox" → USE "selectable option"
   - NO "radio button" → USE "single-selection option"
   - NO "tab" → USE "section" or "area"
   - NO "icon" → USE "indicator" or "symbol"
   - NO "sidebar", "navbar" → USE "navigation area"

   Focus on FUNCTIONALITY, not implementation!

   FUNCTIONAL LANGUAGE PATTERNS TO USE:
   ✅ "call-to-action" (instead of button)
   ✅ "selectable option/component" (instead of checkbox, radio, toggle)
   ✅ "navigate to [page]" (instead of click button to go to)
   ✅ "expandable section" (instead of accordion, collapsible)
   ✅ "selection menu" or "options list" (instead of dropdown)
   ✅ "overlay message" or "notification" (instead of modal, popup)
   ✅ "option to enable/disable" (instead of toggle, switch)
   ✅ "single-selection option" (instead of radio button)
   ✅ "multiple-selection option" (instead of checkboxes)
   ✅ "navigable images" (instead of carousel, image slider)
   ✅ "navigation area" (instead of navbar, sidebar, menu bar)

   CONTENT TO INCLUDE:
   ✅ What displays/shows on screen (specific elements)
   ✅ User interactions and system responses
   ✅ Conditional logic (If/then statements)
   ✅ Data availability states (pending, unavailable, error)
   ✅ User states (guest users, logged-in users)
   ✅ Mobile responsive behavior
   ✅ Navigation flows (redirects, page changes)
   ✅ Field behaviors (required, optional, dynamic updates)

   CONTENT TO AVOID:
   ❌ Pixel-perfect design specs (fonts, colors, spacing)
   ❌ Subjective design descriptions
   ❌ Exhaustive analytics/accessibility details (summarize in Notes)
   ❌ A/B testing requirements
   ❌ CMS/admin implementation details

   EXAMPLE STRUCTURE:

   1. The [Page Name] will display [element/section] [location]
      a. [Specific element or information]
      b. [Another element]
         i. [Detail about element]
         ii. [Conditional behavior]
            1. [Further nested detail]
      c. [Another element with behavior]

   2. User State-Specific Content:
      a. Logged-in users see:
         i. [Specific content]
         ii. [Specific features]
      b. Guest users see:
         i. [Different content]
         ii. [Different features]

   3. If [condition], [the system/section] will display [specific outcome]
      a. [Sub-condition or detail]

   4. The user will be able to [action]
      a. When user selects [element], they will be navigated to [destination]
      b. [Result or feedback]

   5. The [feature/section] will be mobile responsive

   EXAMPLE (Based on Real Postal Store Story #5 - Using Functional Language):

   1. The user will be able to navigate through product images within the product detail page
       a. The product image will dynamically change once user selects a different image
   2. The user will be able to expand to full screen view, showing multiple product angles and images
       a. The user will be able to exit full screen view and navigate back to product detail page
   3. The user will be able to view photos in full-size resolution

   Notice: NO "button", "modal", "carousel" - just functional descriptions!

   ADDITIONAL EXAMPLE (Story #1 - System Display Pattern):

   1. The Product Details Page will display a 'How it Works' section below the product information
   2. The 'How it Works' section will display the following information
       a. Definition of the product
       b. Hyperlink to related section for additional information
   3. If the 'How it Works' section is pending or under maintenance, the section will display placeholder messaging
   4. The 'How it Works' section will be mobile responsive

   NOTES SECTION (always include):
   Add a "Notes" section after ACs covering:
   - Performance considerations
   - Accessibility summary
   - Analytics overview
   - Future enhancements
   - Technical hints
   - Open questions"""
            ac_format_note = "with functional language only (no design adjectives)"
        elif ac_format == "explicit":
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
            ac_format: Format for acceptance criteria ("gherkin", "explicit", or "functional")

        Returns:
            Prompt for refining the story
        """
        # Define AC format reminder
        if ac_format == "functional":
            ac_format_reminder = """
CRITICAL: Use Functional AC format with the following COMPLETE GUIDELINES:

## 🎯 FUNCTIONAL FORMAT (DEFAULT - Use This 95% of the Time)

**TARGET:** 30-50 lines total, 2,500-4,500 characters
**STRUCTURE:** 3-4 indentation levels max (1, a, i, 1)
**SECTIONS:** 4-7 main numbered sections
**FOCUS:** Pure functional requirements ONLY

### LANGUAGE RULES - ABSOLUTELY CRITICAL:

✅ PRIMARY PATTERN (Use This Most):
- **"The user will be able to [action]"** ← MAIN PATTERN!
- Example: "The user will be able to navigate through product images"
- Example: "The user will be able to expand to full screen gallery mode"
- Focus on USER CAPABILITIES and what user can DO

✅ SECONDARY PATTERNS (Supporting):
- "The [element] will [verb]" - for automatic system behavior
- "When user selects [X], [result]" - for user interactions
- "The [page/section] will display [content]" - for what shows
- "will be displayed", "will show", "displays"
- Describe WHAT the system DOES, not HOW it looks

❌ AVOID ALL DESIGN LANGUAGE AND UI IMPLEMENTATION TERMS (THIS IS CRITICAL):

Design Adjectives (NO):
- NO "modern", "modernized", "streamlined", "clean", "clear"
- NO "prominent", "prominently", "elevated", "intuitive", "seamless"
- NO "visual hierarchy", "aesthetics", "polished", "sophisticated"

UI Implementation Terms (NO):
- NO "button" → USE "call-to-action" or "selectable option"
- NO "dropdown" → USE "selection menu" or "options list"
- NO "modal", "popup" → USE "overlay message" or "notification"
- NO "accordion", "collapsible" → USE "expandable section"
- NO "carousel", "slider" → USE "navigable images"
- NO "toggle", "switch" → USE "option to enable/disable"
- NO "checkbox" → USE "selectable option"
- NO "radio button" → USE "single-selection option"
- NO "tab" → USE "section" or "area"
- NO "icon" → USE "indicator" or "symbol"
- NO "sidebar", "navbar" → USE "navigation area"

FUNCTIONAL LANGUAGE TO USE:
✅ "call-to-action" (not button)
✅ "selectable option/component" (not checkbox/radio/toggle)
✅ "navigate to [page]" (not click button)
✅ "expandable section" (not accordion/collapsible)
✅ "selection menu" (not dropdown)
✅ "overlay message" (not modal/popup)
✅ "option to enable/disable" (not toggle/switch)

Focus on FUNCTIONALITY ONLY - NO design or implementation words!

### Content Checklist - Every AC Must Cover:
✅ Trigger/Entry Point: What initiates this functionality?
✅ What Displays: Specific elements that show on screen
✅ User Interactions: What user can do and system responses
✅ Conditional Logic: If/then statements
✅ Data States: What happens with pending, missing, or error data
✅ User States: Guest vs logged-in users
✅ Navigation: Where user is redirected/navigated
✅ Field Behaviors: Required, optional, dynamic updates
✅ Mobile Responsive: How it behaves on mobile

### What to INCLUDE:
✅ Specific screen elements that display
✅ User interactions and system responses
✅ Conditional logic (If/then statements)
✅ Data availability (pending, unavailable, error messaging)
✅ User state differences (guest/logged-in)
✅ Navigation flows (redirects to specific pages)
✅ Field behaviors (required, optional, auto-populate, dynamic)
✅ Mobile responsive statement

### What to AVOID:
❌ Design adjectives ("modern", "clean", "prominent", etc.)
❌ Subjective visual descriptions
❌ Pixel-perfect design specs
❌ Exhaustive analytics details (summarize in Notes)
❌ Detailed accessibility specs (summarize in Notes)

### REQUIRED NOTES SECTION:
Always include a "Notes:" section at the end covering:
- Performance: Target load times
- Accessibility: Screen reader, keyboard navigation summary
- Analytics: Key events to track
- Future Enhancements: Planned features
- Technical Hints: API, caching considerations

### Example Structure (Use As Template):

1. The [Page/Feature Name] will display [element] [location]
   a. [Specific element or information]
   b. [Another element]
      i. [Detail about the element]
      ii. [Conditional behavior]
         1. [Further nested detail if needed]
   c. [Element with specific behavior]

2. User State-Specific Content:
   a. Logged-in users see:
      i. [Specific content]
      ii. [Specific features or information]
   b. Guest users see:
      i. [Different content]
      ii. [Different features]

3. If [condition], [the system/page/section] will display [specific outcome]
   a. [Sub-condition or additional detail]
   b. [Another outcome]

4. The user will be able to [action]
   a. When user selects [element], they will be navigated to [destination page]
   b. [Resulting behavior or feedback]

5. The [feature/section/page] will be mobile responsive

Notes:
- Performance: [target metrics]
- Accessibility: [keyboard navigation, screen readers]
- Analytics: [key events to track]
- Future: [planned enhancements]

### REAL EXAMPLE FROM POSTAL STORE (Story #5 - Functional Language Only):

1. The user will be able to navigate through product images within the product detail page
    a. The product image will dynamically change once user selects a different image
2. The user will be able to expand to full screen view, showing multiple product angles and images
    a. The user will be able to exit full screen view and navigate back to product detail page
3. The user will be able to view photos in full-size resolution

Notice: Uses "full screen view" not "modal", "selects" not "clicks button"

Notes:
- Performance: Images load progressively, full-size available on demand
- Accessibility: Image navigation keyboard accessible, alt text on all images
- Future: Add zoom functionality, image comparison feature

### ADDITIONAL EXAMPLE (Story #1 - System Display Pattern):

1. The Product Details Page will display a 'How it Works' section below the product information
2. The 'How it Works' section will display the following information
    a. Definition of the product
    b. Hyperlink to related section for additional information
3. If the 'How it Works' section is pending or under maintenance, the section will display placeholder messaging
4. The 'How it Works' section will be mobile responsive

Notes:
- Performance: Section loads with page, no additional requests
- Accessibility: Links have descriptive text, section has proper heading
- Future: Expand to additional product categories

---

REMEMBER: NO design language. Only describe FUNCTIONALITY and BEHAVIOR."""
        elif ac_format == "explicit":
            ac_format_reminder = """
CRITICAL: Use Explicit/Detailed AC format with the following COMPLETE GUIDELINES:

## 🎯 KEEP IT SIMPLE (DEFAULT - Use This 95% of the Time)

**TARGET:** 30-50 lines total, 2,500-4,500 characters
**STRUCTURE:** 3-4 indentation levels max (1, a, i, 1)
**SECTIONS:** 4-7 main numbered sections
**FOCUS:** Core functionality only

### Universal Checklist - Every AC Must Cover:
✅ Trigger/Entry Point: What initiates this functionality?
✅ Inputs: What data/information is required?
✅ Processing/Logic: What happens during execution?
✅ Outputs: What's produced? (screen, data, notification, file)
✅ Validation Rules: What must be verified/checked?
✅ Error Handling: What happens when things fail?
✅ Edge Cases: Unusual scenarios covered?
✅ Permissions: Who can access this? (roles, authentication)
✅ State Changes: What changes in the system?
✅ Success Criteria: How do we know it worked?

### What to INCLUDE:
✅ What displays/happens on screen
✅ User interactions and results
✅ Conditional logic (if/then statements)
✅ Validation and error messages with exact text
✅ Navigation flows and redirects
✅ Required vs optional fields (mark explicitly)
✅ User states (guest/logged in, empty states)
✅ Tooltips and modals
✅ Pre-populated data
✅ Cross-references to related stories: (See [Story Name])
✅ Responsive behavior summary (desktop/mobile differences if important)

### What to AVOID:
❌ Design implementation details ("swipe left" → use "option to access")
❌ Vague statements ("manage items" → use "Copy, Delete, or Select")
❌ Pixel-perfect design specs (fonts, colors, exact spacing)
❌ Exhaustive analytics event lists
❌ Detailed accessibility specs (summarize in Notes)
❌ CMS/admin implementation details
❌ A/B testing requirements
❌ Social features (unless core to story)
❌ Specific timings (unless critical - say "loads quickly")

### REQUIRED NOTES SECTION:
Always include a "Notes:" section at the end covering:
- Performance: Target load times, optimization notes
- Accessibility: Screen reader, keyboard navigation summary
- Analytics: Key events to track (high-level)
- Future Enhancements: v2 features, nice-to-haves
- Technical Hints: Caching, API considerations
- Open Questions: Items needing clarification

### Example Structure (Use As Template):

1. The [Page/Feature Name] displays:
   a. [UI Element/Section Name]
      i. [Field name] (Required)
      ii. [Field name] (Optional)
      iii. [Behavior or condition]
         1. If [condition], then [result]
         2. Error message: "[exact text]"
   b. [Next UI Element]
      i. [Details...]
   c. [Button/Action]
      i. Disabled if [condition]
      ii. Selecting will redirect to [Destination]

2. User States:
   a. Guest users: [behavior]
   b. Logged-in users: [behavior]
   c. Empty state: Display message "[text]"

3. Validation Rules:
   a. [Field] validation
      i. If [invalid condition], display error: "[message]"
   b. Form submission
      i. All Required fields must be completed

4. Navigation:
   a. Success: Redirect to [Page]
   b. Cancel: Return to [Previous Page] (See [Story Name])
   c. Back button: Navigate to [Page]

5. Responsive Behavior:
   a. Desktop: [key differences]
   b. Mobile: [key differences if significant]

Notes:
- Performance: [target metrics]
- Accessibility: [keyboard navigation, screen readers]
- Analytics: [key events to track]
- Future: [planned enhancements]

### Common Patterns to Use:

**For Validation:**
i. If the user does not [required action] they will receive an error message informing them that [specific error text]

**For Navigation:**
i. Selecting will redirect the user to [Destination] ([URL]) to [purpose]

**For Conditionals:**
a. If [condition], then:
   i. [Outcome 1]
   ii. [Outcome 2]

**For Cross-References:**
ii. [Action] (See [Related User Story Name])

**For Modals:**
d. Tool Tip
   i. Selecting will display a modal that [describes purpose]
      1. [Content element]
      2. [Button/Link]
         a. Selecting will [action]

**For Pre-population:**
i. [Field name] will pre-populate with [data source/default value]

**For Permissions:**
a. User must be [authenticated/have role] to access this feature
b. If user does not have permission:
   i. User sees: [error message OR redirect to login]

---

REMEMBER: Default to SIMPLE (30-50 lines). Only write comprehensive 100+ line ACs if this is mission-critical, compliance-heavy, or explicitly required."""
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

Return the refined story in the same JSON format with acceptance_criteria as an ARRAY OF STRINGS where each string is one complete acceptance criterion section:
{{
    "user_story": "...",
    "feature_epic": "...",
    "acceptance_criteria": [
        "1. The [Page] displays:\\n   a. Element 1\\n      i. Detail\\n   b. Element 2",
        "2. User States:\\n   a. Guest users: [behavior]\\n   b. Logged-in users: [behavior]",
        "3. Validation Rules:\\n   a. Field validation\\n      i. Error message: \\"text\\"",
        "Notes:\\n- Performance: [details]\\n- Accessibility: [details]"
    ],
    "business_case": "...",
    "relevant_pages": "..."
}}

IMPORTANT: Each array element should be a complete numbered section (including subsections with proper indentation using \\n for line breaks). The ACs should total 30-50 lines when formatted. Always include the Notes section as the final array element.

Maintain the quality and detail level while implementing the requested changes."""

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
