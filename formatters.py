"""
Formatters Module
Utility functions for formatting user stories and acceptance criteria
"""

from typing import List, Dict
import json


class StoryFormatter:
    """Format user stories and acceptance criteria"""

    @staticmethod
    def format_gherkin_ac(ac: str) -> str:
        """
        Ensure acceptance criteria follows Gherkin format

        Args:
            ac: Acceptance criteria string

        Returns:
            Properly formatted Gherkin AC
        """
        ac = ac.strip()

        # Check if already in Gherkin format
        if ac.lower().startswith('given'):
            return ac

        # If not, it might need reformatting
        return ac

    @staticmethod
    def validate_story_format(story: str) -> bool:
        """
        Validate that a user story follows the standard format

        Args:
            story: User story string

        Returns:
            True if valid format
        """
        story_lower = story.lower()
        return (
            story_lower.startswith('as a') or
            story_lower.startswith('as an')
        ) and 'i want' in story_lower and 'so that' in story_lower

    @staticmethod
    def format_story_dict(story_data: Dict) -> Dict:
        """
        Format and validate a story dictionary

        Args:
            story_data: Raw story data from AI

        Returns:
            Validated and formatted story dictionary
        """
        formatted = {
            'user_story': story_data.get('user_story', '').strip(),
            'feature_epic': story_data.get('feature_epic', '').strip(),
            'acceptance_criteria': [],
            'business_case': story_data.get('business_case', '').strip(),
            'relevant_pages': story_data.get('relevant_pages', '').strip()
        }

        # Format acceptance criteria
        acs = story_data.get('acceptance_criteria', [])
        if isinstance(acs, str):
            # If ACs came as a string, split them
            acs = [ac.strip() for ac in acs.split('\n') if ac.strip()]

        for ac in acs:
            formatted_ac = StoryFormatter.format_gherkin_ac(ac)
            if formatted_ac:
                formatted['acceptance_criteria'].append(formatted_ac)

        return formatted

    @staticmethod
    def parse_ai_response(response: str) -> List[Dict]:
        """
        Parse AI response into story dictionaries

        Args:
            response: Raw AI response (expected to be JSON)

        Returns:
            List of story dictionaries
        """
        try:
            # Try to parse as JSON
            data = json.loads(response)

            # If it's a single object, wrap in list
            if isinstance(data, dict):
                data = [data]

            # Format each story
            return [StoryFormatter.format_story_dict(story) for story in data]

        except json.JSONDecodeError:
            # If not valid JSON, try to extract from markdown code blocks
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                json_str = response[json_start:json_end].strip()
                data = json.loads(json_str)

                if isinstance(data, dict):
                    data = [data]

                return [StoryFormatter.format_story_dict(story) for story in data]
            else:
                raise ValueError("Could not parse AI response as JSON")

    @staticmethod
    def stories_to_text(stories: List[Dict]) -> str:
        """
        Convert stories to readable text format

        Args:
            stories: List of story dictionaries

        Returns:
            Formatted text representation
        """
        output = []
        for i, story in enumerate(stories, 1):
            output.append(f"\n{'='*80}")
            output.append(f"Story #{i}")
            output.append(f"{'='*80}")
            output.append(f"\nUser Story: {story['user_story']}")
            output.append(f"\nFeature/Epic: {story['feature_epic']}")
            output.append(f"\nAcceptance Criteria:")
            for ac in story['acceptance_criteria']:
                output.append(f"  - {ac}")
            output.append(f"\nBusiness Case: {story['business_case']}")
            output.append(f"\nRelevant Pages: {story['relevant_pages']}")

        return '\n'.join(output)


def validate_stories(stories: List[Dict]) -> tuple[bool, List[str]]:
    """
    Validate a list of stories and return any issues

    Args:
        stories: List of story dictionaries

    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []

    for i, story in enumerate(stories, 1):
        # Check user story format
        if not StoryFormatter.validate_story_format(story.get('user_story', '')):
            issues.append(f"Story #{i}: User story doesn't follow standard format")

        # Check for acceptance criteria
        if not story.get('acceptance_criteria'):
            issues.append(f"Story #{i}: Missing acceptance criteria")

        # Check for business case
        if not story.get('business_case'):
            issues.append(f"Story #{i}: Missing business case")

        # Check for feature/epic
        if not story.get('feature_epic'):
            issues.append(f"Story #{i}: Missing feature/epic name")

    return (len(issues) == 0, issues)


def format_for_display(stories: List[Dict]) -> str:
    """
    Format stories for console display

    Args:
        stories: List of story dictionaries

    Returns:
        Formatted string for display
    """
    return StoryFormatter.stories_to_text(stories)
