"""
Feedback Handler Module
Processes user feedback and applies learned preferences to story generation
"""

import json
from typing import Dict, List, Optional
from datetime import datetime


class FeedbackHandler:
    """Handle user feedback and preference learning"""

    def __init__(self, memory_store=None):
        """
        Initialize feedback handler

        Args:
            memory_store: Optional ConversationMemory instance
        """
        self.memory = memory_store
        self.session_feedback = []

    def add_feedback(self, feedback: str, context: str = "") -> Dict:
        """
        Add user feedback

        Args:
            feedback: Feedback text from user
            context: Context where feedback was given

        Returns:
            Processed feedback dictionary
        """
        feedback_entry = {
            "feedback": feedback,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "applied": False
        }

        self.session_feedback.append(feedback_entry)

        # Store in memory if available
        if self.memory:
            self.memory.add_preference(feedback, context)

        return feedback_entry

    def get_all_feedback(self) -> List[Dict]:
        """
        Get all feedback from session

        Returns:
            List of feedback entries
        """
        return self.session_feedback

    def build_feedback_context(self) -> str:
        """
        Build context string from all feedback for prompts

        Returns:
            Formatted feedback context
        """
        if not self.session_feedback and (not self.memory or not self.memory.get_all_preferences()):
            return ""

        context_parts = ["\n=== USER PREFERENCES AND FEEDBACK ===\n"]
        context_parts.append("Apply these preferences to all generated stories:\n")

        # Add stored preferences from memory
        if self.memory:
            stored_prefs = self.memory.get_all_preferences()
            if stored_prefs:
                context_parts.append("\nLearned Preferences (from previous sessions):")
                for i, pref in enumerate(stored_prefs, 1):
                    context_parts.append(f"{i}. {pref.get('preference', '')}")

        # Add session feedback
        if self.session_feedback:
            context_parts.append("\nCurrent Session Feedback:")
            for i, fb in enumerate(self.session_feedback, 1):
                context_parts.append(f"{i}. {fb.get('feedback', '')}")

        context_parts.append("\n" + "="*50 + "\n")

        return "\n".join(context_parts)

    def analyze_feedback(self, feedback: str) -> Dict[str, any]:
        """
        Analyze feedback to extract actionable preferences

        Args:
            feedback: Raw feedback text

        Returns:
            Analysis dictionary with categorized feedback
        """
        feedback_lower = feedback.lower()

        analysis = {
            "original": feedback,
            "categories": [],
            "actionable": True
        }

        # Categorize feedback
        if any(word in feedback_lower for word in ["shorter", "longer", "concise", "detailed", "brief"]):
            analysis["categories"].append("length")

        if any(word in feedback_lower for word in ["technical", "simple", "user-focused", "developer"]):
            analysis["categories"].append("complexity")

        if any(word in feedback_lower for word in ["format", "structure", "style", "template"]):
            analysis["categories"].append("format")

        if any(word in feedback_lower for word in ["call", "name", "term", "use"]):
            analysis["categories"].append("terminology")

        if any(word in feedback_lower for word in ["include", "add", "always", "must", "should"]):
            analysis["categories"].append("requirements")

        if any(word in feedback_lower for word in ["remove", "don't", "avoid", "skip"]):
            analysis["categories"].append("exclusions")

        if not analysis["categories"]:
            analysis["categories"].append("general")

        return analysis

    def apply_feedback_to_prompt(self, base_prompt: str) -> str:
        """
        Apply accumulated feedback to a generation prompt

        Args:
            base_prompt: Original prompt

        Returns:
            Enhanced prompt with feedback context
        """
        feedback_context = self.build_feedback_context()

        if not feedback_context:
            return base_prompt

        # Insert feedback context before the main instructions
        return feedback_context + "\n" + base_prompt

    def get_feedback_summary(self) -> Dict[str, any]:
        """
        Get summary of all feedback

        Returns:
            Summary dictionary
        """
        total_count = len(self.session_feedback)
        stored_count = len(self.memory.get_all_preferences()) if self.memory else 0

        categories = {}
        for fb in self.session_feedback:
            analysis = self.analyze_feedback(fb.get("feedback", ""))
            for cat in analysis["categories"]:
                categories[cat] = categories.get(cat, 0) + 1

        return {
            "total_session_feedback": total_count,
            "total_stored_preferences": stored_count,
            "categories": categories,
            "recent_feedback": self.session_feedback[-5:] if self.session_feedback else []
        }

    def clear_session_feedback(self):
        """Clear session feedback (keeps stored preferences)"""
        self.session_feedback = []


class FeedbackPromptBuilder:
    """Build prompts enhanced with feedback"""

    @staticmethod
    def enhance_generation_prompt(base_prompt: str, feedback_handler: FeedbackHandler, ac_format: str = "gherkin") -> str:
        """
        Enhance a generation prompt with feedback

        Args:
            base_prompt: Original generation prompt
            feedback_handler: FeedbackHandler instance
            ac_format: AC format to use

        Returns:
            Enhanced prompt
        """
        # Get feedback context
        feedback_context = feedback_handler.build_feedback_context()

        # Add AC format instruction
        ac_instruction = ""
        if ac_format == "explicit":
            ac_instruction = """
ACCEPTANCE CRITERIA FORMAT: Use Explicit/Detailed format
- 30-50 lines total
- Structured with numbered sections (1, 2, 3) and subsections (a, b, c)
- Include: What displays, User interactions, Validation, Navigation, Responsive behavior
- Always include a Notes section at the end
"""
        else:
            ac_instruction = """
ACCEPTANCE CRITERIA FORMAT: Use Gherkin format (Given/When/Then)
- At least 4-6 acceptance criteria per story
- Format: "Given [context], when [action], then [expected outcome]"
"""

        # Combine all parts
        enhanced = []

        if feedback_context:
            enhanced.append(feedback_context)

        enhanced.append(ac_instruction)
        enhanced.append(base_prompt)

        return "\n".join(enhanced)

    @staticmethod
    def enhance_refinement_prompt(base_prompt: str, feedback: str) -> str:
        """
        Enhance a refinement prompt with specific feedback

        Args:
            base_prompt: Original refinement prompt
            feedback: Specific feedback for this refinement

        Returns:
            Enhanced prompt
        """
        return f"""{base_prompt}

ADDITIONAL FEEDBACK TO APPLY:
{feedback}

Ensure the refined story incorporates this feedback while maintaining quality.
"""


def create_feedback_handler(memory_store=None) -> FeedbackHandler:
    """
    Create a FeedbackHandler instance

    Args:
        memory_store: Optional memory store for persistent preferences

    Returns:
        FeedbackHandler instance
    """
    return FeedbackHandler(memory_store=memory_store)
