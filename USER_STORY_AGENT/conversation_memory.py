"""
Conversation Memory Module
Stores and retrieves user preferences and feedback across sessions
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class ConversationMemory:
    """Store and retrieve conversation memory and preferences"""

    def __init__(self, storage_file: str = "preferences_store.json"):
        """
        Initialize conversation memory

        Args:
            storage_file: Path to JSON file for storing preferences
        """
        self.storage_file = storage_file
        self.preferences = []
        self.load()

    def load(self):
        """Load preferences from storage file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.preferences = data.get("preferences", [])
            except Exception as e:
                print(f"Warning: Could not load preferences: {e}")
                self.preferences = []
        else:
            self.preferences = []

    def save(self):
        """Save preferences to storage file"""
        try:
            data = {
                "preferences": self.preferences,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save preferences: {e}")

    def add_preference(self, preference: str, context: str = ""):
        """
        Add a new preference

        Args:
            preference: Preference text
            context: Context where preference was given
        """
        pref_entry = {
            "preference": preference,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "times_applied": 0
        }

        # Check if similar preference exists
        if not self._has_similar_preference(preference):
            self.preferences.append(pref_entry)
            self.save()

    def _has_similar_preference(self, preference: str) -> bool:
        """Check if a similar preference already exists"""
        pref_lower = preference.lower()
        for existing in self.preferences:
            if existing.get("preference", "").lower() == pref_lower:
                return True
        return False

    def get_all_preferences(self) -> List[Dict]:
        """
        Get all stored preferences

        Returns:
            List of preference dictionaries
        """
        return self.preferences

    def get_recent_preferences(self, count: int = 5) -> List[Dict]:
        """
        Get most recent preferences

        Args:
            count: Number of preferences to return

        Returns:
            List of recent preferences
        """
        return self.preferences[-count:] if self.preferences else []

    def remove_preference(self, index: int) -> bool:
        """
        Remove a preference by index

        Args:
            index: Index of preference to remove

        Returns:
            True if removed successfully
        """
        if 0 <= index < len(self.preferences):
            self.preferences.pop(index)
            self.save()
            return True
        return False

    def clear_all(self):
        """Clear all preferences"""
        self.preferences = []
        self.save()

    def increment_usage(self, preference: str):
        """
        Increment usage counter for a preference

        Args:
            preference: Preference text
        """
        for pref in self.preferences:
            if pref.get("preference") == preference:
                pref["times_applied"] = pref.get("times_applied", 0) + 1
                self.save()
                break

    def get_preference_summary(self) -> Dict:
        """
        Get summary of stored preferences

        Returns:
            Summary dictionary
        """
        return {
            "total_preferences": len(self.preferences),
            "most_recent": self.preferences[-1] if self.preferences else None,
            "preferences_list": [p.get("preference") for p in self.preferences]
        }

    def export_preferences(self, export_file: str):
        """
        Export preferences to a file

        Args:
            export_file: Path to export file
        """
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "preferences": self.preferences,
                    "exported_at": datetime.now().isoformat()
                }, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting preferences: {e}")
            return False

    def import_preferences(self, import_file: str):
        """
        Import preferences from a file

        Args:
            import_file: Path to import file
        """
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                imported_prefs = data.get("preferences", [])

                for pref in imported_prefs:
                    if not self._has_similar_preference(pref.get("preference", "")):
                        self.preferences.append(pref)

                self.save()
            return True
        except Exception as e:
            print(f"Error importing preferences: {e}")
            return False


def create_memory_store(storage_file: str = "preferences_store.json") -> ConversationMemory:
    """
    Create a ConversationMemory instance

    Args:
        storage_file: Path to storage file

    Returns:
        ConversationMemory instance
    """
    return ConversationMemory(storage_file=storage_file)


def format_preferences_for_display(preferences: List[Dict]) -> str:
    """
    Format preferences for display in UI

    Args:
        preferences: List of preference dictionaries

    Returns:
        Formatted string
    """
    if not preferences:
        return "No preferences stored yet."

    lines = []
    for i, pref in enumerate(preferences, 1):
        timestamp = pref.get("timestamp", "Unknown")
        times_applied = pref.get("times_applied", 0)
        preference_text = pref.get("preference", "")

        lines.append(f"{i}. {preference_text}")
        lines.append(f"   Applied {times_applied} times | Added: {timestamp[:10]}")
        lines.append("")

    return "\n".join(lines)
