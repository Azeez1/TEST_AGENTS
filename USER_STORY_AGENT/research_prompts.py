"""
Research Prompts Module
Templates and utilities for autonomous research prompts
"""

from typing import Dict, List, Optional


class ResearchPrompts:
    """Generate prompts for autonomous research"""

    @staticmethod
    def get_domain_research_prompt(notes: str, detected_domain: str = "") -> str:
        """
        Generate prompt for researching domain-specific best practices

        Args:
            notes: Meeting notes
            detected_domain: Detected domain (e.g., "e-commerce", "healthcare")

        Returns:
            Research prompt
        """
        domain_context = f" in the {detected_domain} domain" if detected_domain else ""

        return f"""You are an autonomous AI research agent with full browser control. Your mission: analyze meeting notes and generate expert-level user stories{domain_context}.

Meeting Notes:
{notes}

🤖 AUTONOMOUS MODE - You have complete freedom to navigate the web.

Like Perplexity or Manus, you decide:
- Which websites to visit
- What to search for
- Which links to click
- How deep to explore
- What patterns to extract

Available Tools (use efficiently):
- playwright_navigate - Go to any URL
- playwright_click - Click elements (CSS selectors)
- playwright_fill - Fill form inputs
- playwright_screenshot - Capture screens (use fullPage: true for complete pages)
- playwright_press_key - Keyboard input (ArrowRight, ArrowLeft, Enter, etc.)
- playwright_scroll_page - Scroll the page (directions: down, up, bottom, top)
- playwright_get_page_info - Get current page URL, title, and visible text
- playwright_evaluate - Execute JavaScript (useful for custom scrolling: window.scrollBy(0, 500))

Your Research Strategy (adapt as needed):
1. Analyze notes → identify features, domains, URLs mentioned
2. If Figma URL mentioned → navigate there, handle passwords, explore all screens
3. If domain clear (e.g., e-commerce) → search best practices, visit leaders (Shopify, Amazon)
4. If technical → look up standards (WCAG, GDPR, etc.)
5. Browse, click, scroll autonomously to gather comprehensive info
6. Synthesize findings into expert user stories

Be proactive:
- Follow interesting links
- Take screenshots of good examples
- Extract patterns from real sites
- Make autonomous decisions without asking
- If something doesn't work, try another approach

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

Return ONLY the JSON array, no additional text or commentary.
"""

    @staticmethod
    def get_guided_research_prompt(notes: str, instructions: str, ac_format: str = "gherkin") -> str:
        """
        Generate prompt with specific browsing instructions

        Args:
            notes: Meeting notes
            instructions: Specific browser instructions from user
            ac_format: AC format to use

        Returns:
            Research prompt
        """
        # Define AC format instructions
        if ac_format == "explicit":
            ac_format_desc = "Explicit/Detailed format (30-50 lines, structured with numbered sections and subsections)"
            ac_example = """      "1. The [Page] displays:\\n   a. Element 1\\n      i. Detail\\n   b. Element 2",
      "2. User States:\\n   a. Guest users: [behavior]\\n   b. Logged-in users: [behavior]",
      "3. Validation Rules:\\n   a. Field validation\\n      i. Error message: \\"text\\"",
      "Notes:\\n- Performance: [details]\\n- Accessibility: [details]\""""
        else:
            ac_format_desc = "Gherkin format (Given/When/Then)"
            ac_example = """      "Given [context], when [action], then [expected outcome]",
      "Given [context], when [action], then [expected outcome]",
      ..."""

        return f"""Follow these specific research instructions before generating user stories:

Research Instructions:
{instructions}

Meeting Notes:
{notes}

Steps:
1. Execute the research instructions above using your browser tools
2. Gather and analyze the information you find
3. Generate user stories that incorporate:
   - Information from the meeting notes
   - Context and patterns from your research
   - Any design specifications or standards you discovered

IMPORTANT: Use {ac_format_desc}

Generate user stories in this exact JSON format:
[
  {{
    "user_story": "As a [user type], I want [goal], so that [benefit]",
    "feature_epic": "Concise feature name",
    "acceptance_criteria": [
{ac_example}
    ],
    "business_case": "Explanation of business value and impact",
    "relevant_pages": "Page/screen names affected"
  }}
]

Requirements:
1. Each story must follow the "As a..., I want..., so that..." format
2. Include 4-6 detailed acceptance criteria per story in the specified format ({ac_format_desc})
3. Cover edge cases: errors, mobile responsiveness, accessibility, missing data
4. Business case should explain ROI, customer impact, or strategic value
5. Be specific about which pages/screens/areas are affected

Return ONLY the JSON array, no additional text or commentary.
"""

    @staticmethod
    def get_design_system_prompt(notes: str, design_system_url: str) -> str:
        """
        Generate prompt for learning from a design system

        Args:
            notes: Meeting notes
            design_system_url: URL of design system

        Returns:
            Research prompt
        """
        return f"""Research the design system and use it to generate user stories:

1. Navigate to: {design_system_url}
2. Browse the component library and documentation
3. Learn:
   - Component names and conventions (e.g., Button.Primary, Input.Text)
   - Available states and variants
   - Accessibility patterns
   - Usage guidelines

4. Generate user stories from these notes using the EXACT component names and patterns from the design system:

Meeting Notes:
{notes}

Important:
- Use the design system's component terminology
- Reference the design system's states and variants
- Follow the design system's patterns and guidelines
- Include references to design system components in acceptance criteria

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

Return ONLY the JSON array, no additional text or commentary.
"""

    @staticmethod
    def get_competitor_analysis_prompt(notes: str, competitor_urls: List[str]) -> str:
        """
        Generate prompt for analyzing competitor implementations

        Args:
            notes: Meeting notes
            competitor_urls: List of competitor URLs to analyze

        Returns:
            Research prompt
        """
        urls_list = "\n".join(f"   - {url}" for url in competitor_urls)

        return f"""Analyze competitor implementations to inform user stories:

1. Visit and analyze these competitor sites:
{urls_list}

2. For each site, observe:
   - How they implement similar features
   - UX patterns and flows
   - Error handling
   - Accessibility features
   - Mobile responsiveness

3. Generate user stories based on these notes, incorporating best practices from competitors:

Meeting Notes:
{notes}

Important:
- Learn from competitors but don't copy directly
- Identify patterns that work well
- Note innovative approaches
- Consider improvements over competitor implementations

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

Return ONLY the JSON array, no additional text or commentary.
"""

    @staticmethod
    def get_standards_lookup_prompt(notes: str, standards: List[str]) -> str:
        """
        Generate prompt for looking up technical standards

        Args:
            notes: Meeting notes
            standards: List of standards to look up (e.g., ["WCAG 2.1", "GDPR"])

        Returns:
            Research prompt
        """
        standards_list = "\n".join(f"   - {std}" for std in standards)

        return f"""Research technical standards and generate compliant user stories:

1. Look up these standards and their requirements:
{standards_list}

2. For each standard, identify:
   - Key requirements relevant to the features in the notes
   - Compliance criteria
   - Best practices for implementation

3. Generate user stories from these notes that include compliance requirements:

Meeting Notes:
{notes}

Important:
- Include standard-specific acceptance criteria
- Reference standards in business cases
- Ensure stories cover compliance requirements
- Include validation and testing criteria for compliance

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

Return ONLY the JSON array, no additional text or commentary.
"""

    @staticmethod
    def get_figma_prototype_prompt(notes: str, figma_url: str, password: str = "", ac_format: str = "gherkin") -> str:
        """
        Generate prompt for analyzing Figma prototypes

        Args:
            notes: Meeting notes
            figma_url: Figma prototype URL
            password: Optional password for password-protected prototypes
            ac_format: AC format to use

        Returns:
            Research prompt for Figma analysis
        """
        # Define AC format instructions
        if ac_format == "explicit":
            ac_format_desc = "Explicit/Detailed format (30-50 lines, structured with numbered sections and subsections)"
            ac_example = """      "1. The [Page] displays:\\n   a. Element 1\\n      i. Detail\\n   b. Element 2",
      "2. User States:\\n   a. Guest users: [behavior]\\n   b. Logged-in users: [behavior]",
      "3. Validation Rules:\\n   a. Field validation\\n      i. Error message: \\"text\\"",
      "Notes:\\n- Performance: [details]\\n- Accessibility: [details]\""""
        else:
            ac_format_desc = "Gherkin format (Given/When/Then)"
            ac_example = """      "Given [context], when [action], then [expected outcome]",
      "Given [context], when [action], then [expected outcome]",
      ..."""

        password_instruction = ""
        if password:
            password_instruction = f"""
2. If password prompt appears, authenticate:
   - Fill password field: playwright_fill with selector "input[type='password']" and value "{password}"
   - Click continue button: playwright_click with selector "button:has-text('Continue')"
"""

        return f"""Analyze this Figma prototype and intelligently combine it with the uploaded document to generate comprehensive user stories:

Figma URL: {figma_url}

IMPORTANT: Research efficiently to stay within tool iteration limits. Focus on KEY screens and comprehensive generation.

Steps to navigate the Figma prototype:
1. Navigate to the URL above{password_instruction}
{3 if password else 2}. Explore the prototype efficiently and autonomously:
   - Use ArrowRight/ArrowLeft keys to navigate between screens
   - Take screenshots of KEY screens that demonstrate important UI/UX patterns (use fullPage: true)
   - If you need to see more content on a long screen, scroll using JavaScript: window.scrollBy(0, 500)
   - Observe and mentally document: UI components, layouts, design patterns, colors, typography, spacing
   - Navigate through several representative screens (look for X/Y indicators at bottom to understand total screens)
   - Prioritize breadth over depth - see multiple screens rather than exhaustively documenting one

{4 if password else 3}. INTELLIGENTLY SYNTHESIZE both sources to generate user stories:

   **Your Uploaded Document/Excel Content:**
   {notes}

   **How to combine Figma + Document:**
   - If document has requirements → Use Figma to add UI/UX implementation details
   - If document has features → Use Figma to specify exact screens, components, flows
   - If document has business goals → Use Figma to describe visual implementation
   - Use your own intelligence to fill gaps where information is missing in either source
   - Enhance stories with design specs from Figma (colors, typography, spacing)
   - Add interaction patterns and flows observed in Figma
   - Include accessibility considerations based on visual design

   **Generate stories that:**
   - Start with the purpose/requirement from the document (if exists)
   - Add concrete implementation details from Figma screens
   - Use your judgment to create comprehensive, production-ready stories
   - Reference specific Figma screens and document sections where applicable

IMPORTANT: Use {ac_format_desc} for acceptance criteria.

Generate user stories in this exact JSON format:
[
  {{
    "user_story": "As a [user type], I want [goal], so that [benefit]",
    "feature_epic": "Concise feature name",
    "acceptance_criteria": [
{ac_example}
    ],
    "business_case": "Explanation of business value and impact",
    "relevant_pages": "Page/screen names from Figma prototype"
  }}
]

Requirements for Figma-based stories:
1. Each story must follow the "As a..., I want..., so that..." format
2. Include 4-6 detailed acceptance criteria per story in the specified format ({ac_format_desc})
3. Reference specific screens, components, and UI elements from the Figma prototype
4. Include visual design specifications (colors, typography, spacing) when relevant
5. Cover interaction patterns shown in the prototype
6. Include accessibility considerations based on the design
7. Specify which Figma screens each story relates to

Return ONLY the JSON array, no additional text or commentary.
"""

    @staticmethod
    def detect_domain_from_notes(notes: str) -> str:
        """
        Analyze notes to detect the domain/industry

        Args:
            notes: Meeting notes

        Returns:
            Detected domain string
        """
        notes_lower = notes.lower()

        domains = {
            "e-commerce": ["shop", "cart", "checkout", "product", "payment", "order", "inventory"],
            "healthcare": ["patient", "medical", "health", "diagnosis", "treatment", "hospital", "doctor"],
            "finance": ["account", "transaction", "banking", "payment", "investment", "loan"],
            "education": ["student", "course", "learning", "assignment", "grade", "teacher"],
            "social": ["post", "comment", "like", "share", "friend", "feed", "profile"],
            "saas": ["subscription", "dashboard", "analytics", "integration", "api", "tenant"],
        }

        domain_scores = {}
        for domain, keywords in domains.items():
            score = sum(1 for keyword in keywords if keyword in notes_lower)
            if score > 0:
                domain_scores[domain] = score

        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        return ""


def create_autonomous_research_plan(notes: str, browser_instructions: str = "") -> Dict[str, any]:
    """
    Create a research plan based on notes and instructions

    Args:
        notes: Meeting notes
        browser_instructions: Optional browser instructions

    Returns:
        Research plan dictionary
    """
    plan = {
        "has_specific_instructions": bool(browser_instructions),
        "detected_domain": ResearchPrompts.detect_domain_from_notes(notes),
        "research_type": "",
        "prompt": ""
    }

    if browser_instructions:
        # User provided specific instructions - use guided research
        plan["research_type"] = "guided"
        plan["prompt"] = browser_instructions
    elif plan["detected_domain"]:
        # Domain detected - do domain-specific research
        plan["research_type"] = "domain"
        plan["prompt"] = f"Research {plan['detected_domain']} best practices and examples"
    else:
        # Generic research
        plan["research_type"] = "generic"
        plan["prompt"] = "Research general best practices for the features mentioned"

    return plan
