"""
UI Helpers Module
Utility functions for formatting and displaying user stories in Streamlit
"""

import streamlit as st
from typing import List, Dict
import tempfile
import os


def display_story_card(story: Dict, index: int = None):
    """
    Display a single user story in an expandable card format

    Args:
        story: Story dictionary
        index: Optional story number for display
    """
    title = f"Story #{index}: {story.get('feature_epic', 'Untitled')}" if index else story.get('feature_epic', 'Untitled')

    with st.expander(title, expanded=False):
        st.markdown("### 📖 User Story")
        st.info(story.get('user_story', 'N/A'))

        st.markdown("### ✅ Acceptance Criteria")
        acs = story.get('acceptance_criteria', [])
        if acs:
            for ac in acs:
                st.markdown(f"- {ac}")
        else:
            st.warning("No acceptance criteria")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 💼 Business Case")
            st.write(story.get('business_case', 'N/A'))

        with col2:
            st.markdown("### 📄 Relevant Pages")
            st.write(story.get('relevant_pages', 'N/A'))


def display_story_summary(stories: List[Dict]):
    """
    Display summary metrics for a list of stories

    Args:
        stories: List of story dictionaries
    """
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Stories", len(stories))

    with col2:
        total_acs = sum(len(s.get('acceptance_criteria', [])) for s in stories)
        avg_acs = total_acs / len(stories) if stories else 0
        st.metric("Avg ACs per Story", f"{avg_acs:.1f}")

    with col3:
        features = set(s.get('feature_epic', 'Unknown') for s in stories)
        st.metric("Unique Features", len(features))


def save_uploaded_file(uploaded_file) -> str:
    """
    Save an uploaded file to a temporary location and return the path

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        Path to the saved temporary file
    """
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        return tmp_file.name


def format_story_for_display(story: Dict) -> str:
    """
    Format a story as markdown text

    Args:
        story: Story dictionary

    Returns:
        Formatted markdown string
    """
    md = f"**User Story:** {story.get('user_story', 'N/A')}\n\n"
    md += f"**Feature/Epic:** {story.get('feature_epic', 'N/A')}\n\n"
    md += f"**Acceptance Criteria:**\n"

    for ac in story.get('acceptance_criteria', []):
        md += f"- {ac}\n"

    md += f"\n**Business Case:** {story.get('business_case', 'N/A')}\n\n"
    md += f"**Relevant Pages:** {story.get('relevant_pages', 'N/A')}\n"

    return md


def show_success_message(message: str, stories_count: int = None):
    """
    Display a success message with optional story count

    Args:
        message: Success message text
        stories_count: Optional number of stories
    """
    if stories_count:
        st.success(f"✅ {message} ({stories_count} {'story' if stories_count == 1 else 'stories'})")
    else:
        st.success(f"✅ {message}")


def show_error_message(message: str):
    """
    Display an error message

    Args:
        message: Error message text
    """
    st.error(f"❌ {message}")


def show_warning_message(message: str):
    """
    Display a warning message

    Args:
        message: Warning message text
    """
    st.warning(f"⚠️ {message}")


def show_info_message(message: str):
    """
    Display an info message

    Args:
        message: Info message text
    """
    st.info(f"ℹ️ {message}")


def create_download_button(file_path: str, button_text: str = "Download Excel", key: str = None):
    """
    Create a download button for an Excel file

    Args:
        file_path: Path to the Excel file
        button_text: Text for the download button
        key: Unique key for the button
    """
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            st.download_button(
                label=button_text,
                data=f,
                file_name=os.path.basename(file_path),
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                key=key
            )
    else:
        show_error_message(f"File not found: {file_path}")


def get_batch_operation_options():
    """
    Get list of predefined batch operation options

    Returns:
        Dictionary of operation names to instructions
    """
    return {
        "Add mobile responsiveness ACs": "Add acceptance criteria about mobile responsiveness and touch-friendly interfaces to this story",
        "Add accessibility ACs": "Add acceptance criteria about screen reader compatibility, keyboard navigation, and WCAG compliance",
        "Add error handling ACs": "Add acceptance criteria about error states, validation, and graceful degradation",
        "Add performance ACs": "Add acceptance criteria about page load time, response time, and performance optimization",
        "Add security ACs": "Add acceptance criteria about data security, authentication, and authorization",
        "Custom instruction": "custom"  # Special marker for custom input
    }
