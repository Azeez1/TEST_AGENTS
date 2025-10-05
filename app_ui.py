"""
User Story Agent - Web UI
Complete Streamlit interface for generating and managing user stories
"""

import streamlit as st
import os
import tempfile
from anthropic import Anthropic
from note_parser import extract_notes
from story_generator import StoryGenerator
from excel_handler import ExcelHandler, read_existing_stories, create_excel_output
from formatters import StoryFormatter, validate_stories
from ui_helpers import (
    display_story_card, display_story_summary, save_uploaded_file,
    show_success_message, show_error_message, show_warning_message, show_info_message,
    create_download_button, get_batch_operation_options
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="User Story Agent",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'generated_stories' not in st.session_state:
    st.session_state.generated_stories = []
if 'output_file_path' not in st.session_state:
    st.session_state.output_file_path = None

# Initialize clients
client = Anthropic()
story_generator = StoryGenerator()
formatter = StoryFormatter()


def generate_stories_from_notes(notes_text: str, output_filename: str, append: bool):
    """Generate user stories from meeting notes"""
    try:
        # Build prompt
        existing_stories = []
        if append and os.path.exists(output_filename):
            existing_stories = read_existing_stories(output_filename)

        existing_context = ""
        if existing_stories:
            existing_list = [s['user_story'] for s in existing_stories[:5]]
            existing_context = "\n\nExisting stories (avoid duplicates):\n" + "\n".join(existing_list)

        prompt = f"""You are a user story generation expert. Generate comprehensive, backlog-ready user stories from the following meeting notes.

Meeting Notes:
{notes_text}
{existing_context}

Generate user stories in this exact JSON format:
[
  {{
    "user_story": "As a [user type], I want [goal], so that [benefit]",
    "feature_epic": "Concise feature name",
    "acceptance_criteria": [
      "Given [context], when [action], then [expected outcome]",
      "Given [context], when [action], then [expected outcome]"
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

        # Call Claude API
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text

        # Parse response
        stories = formatter.parse_ai_response(response_text)

        # Save to Excel
        excel_handler = ExcelHandler(output_filename)
        excel_handler.write_stories(stories, append=append)
        excel_handler.close()

        return stories, output_filename

    except Exception as e:
        raise Exception(f"Error generating stories: {str(e)}")


def refine_single_story(story: dict, instruction: str) -> dict:
    """Refine a specific story based on instruction"""
    try:
        prompt = story_generator.get_refinement_prompt(story, instruction)

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text
        refined_stories = formatter.parse_ai_response(response_text)

        if refined_stories:
            return refined_stories[0]
        else:
            raise Exception("Failed to parse refined story")

    except Exception as e:
        raise Exception(f"Error refining story: {str(e)}")


# Header
st.title("📝 User Story Agent")
st.markdown("Generate backlog-ready user stories from meeting notes with AI")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("About")
    st.info(
        """
        **User Story Agent** uses Claude AI to transform raw meeting notes
        into professional user stories with detailed acceptance criteria.

        **Features:**
        - Generate from notes
        - Refine existing stories
        - Append new stories
        - View & search stories
        - Batch operations
        """
    )
    st.markdown("---")
    st.markdown("**Powered by Claude Sonnet 4**")

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Generate Stories",
    "✏️ Refine Stories",
    "➕ Add More Stories",
    "👁️ View Stories",
    "⚙️ Batch Operations"
])

# TAB 1: GENERATE STORIES
with tab1:
    st.header("Generate User Stories from Notes")

    # Input method selection
    input_method = st.radio("Choose input method:", ["Upload File", "Paste Text"], horizontal=True)

    notes_text = None

    if input_method == "Upload File":
        uploaded_notes = st.file_uploader(
            "Upload meeting notes",
            type=['pdf', 'txt', 'md'],
            help="Supported formats: PDF, TXT, MD",
            key="gen_file_upload"
        )

        if uploaded_notes:
            temp_path = save_uploaded_file(uploaded_notes)
            notes_text = extract_notes(temp_path)
            st.success(f"✓ Loaded {len(notes_text)} characters from {uploaded_notes.name}")

            with st.expander("Preview notes"):
                st.text_area("Notes content", notes_text, height=200, disabled=True)

    else:
        notes_text = st.text_area(
            "Paste your meeting notes here:",
            height=300,
            placeholder="Meeting Notes - Project Name\n\nFeatures discussed:\n1. Feature A\n2. Feature B\n..."
        )

    # Output settings
    st.markdown("### Output Settings")
    col1, col2 = st.columns(2)

    with col1:
        output_filename = st.text_input(
            "Output filename",
            value="user_stories.xlsx",
            help="Name of the Excel file to create"
        )

    with col2:
        file_mode = st.radio(
            "File mode:",
            ["Create new file", "Append to existing"],
            horizontal=True
        )
        append_mode = (file_mode == "Append to existing")

    # Generate button
    if st.button("🚀 Generate User Stories", type="primary", use_container_width=True):
        if not notes_text:
            show_error_message("Please provide meeting notes (upload file or paste text)")
        else:
            with st.spinner("Generating user stories with Claude AI..."):
                try:
                    stories, output_path = generate_stories_from_notes(notes_text, output_filename, append_mode)

                    st.session_state.generated_stories = stories
                    st.session_state.output_file_path = output_path

                    show_success_message("Stories generated successfully", len(stories))

                    # Display summary
                    display_story_summary(stories)

                    # Display stories
                    st.markdown("### Generated Stories")
                    for i, story in enumerate(stories, 1):
                        display_story_card(story, i)

                    # Download button
                    st.markdown("---")
                    create_download_button(output_path, "📥 Download Excel File", key="gen_download")

                except Exception as e:
                    show_error_message(str(e))

# TAB 2: REFINE STORIES
with tab2:
    st.header("Refine Existing Stories")

    # Upload existing Excel
    uploaded_excel = st.file_uploader(
        "Upload existing user stories Excel file",
        type=['xlsx'],
        help="Upload the Excel file containing your user stories",
        key="refine_excel_upload"
    )

    if uploaded_excel:
        temp_excel_path = save_uploaded_file(uploaded_excel)

        try:
            existing_stories = read_existing_stories(temp_excel_path)

            show_success_message(f"Loaded {len(existing_stories)} stories from {uploaded_excel.name}")

            # Display stories list
            st.markdown("### Select Story to Refine")

            # Story selector
            story_options = [f"Story {i+1}: {s['feature_epic']}" for i, s in enumerate(existing_stories)]
            selected_index = st.selectbox("Choose a story:", range(len(story_options)), format_func=lambda x: story_options[x])

            # Display selected story
            st.markdown("#### Current Story")
            display_story_card(existing_stories[selected_index])

            # Refinement instruction
            st.markdown("#### Refinement Instructions")
            refinement_instruction = st.text_area(
                "What changes do you want to make?",
                placeholder="Examples:\n- Add more acceptance criteria about error handling\n- Make the business case more specific\n- Add mobile responsiveness requirements\n- Change user type from 'customer' to 'administrator'",
                height=150
            )

            # Refine button
            if st.button("✏️ Refine Story", type="primary", use_container_width=True):
                if not refinement_instruction:
                    show_warning_message("Please enter refinement instructions")
                else:
                    with st.spinner("Refining story with Claude AI..."):
                        try:
                            refined_story = refine_single_story(existing_stories[selected_index], refinement_instruction)

                            st.markdown("#### Refined Story")
                            display_story_card(refined_story)

                            # Update in Excel
                            excel_handler = ExcelHandler(temp_excel_path)
                            excel_handler.update_story(selected_index + 1, refined_story)
                            excel_handler.close()

                            show_success_message("Story refined and updated in Excel")

                            # Download button
                            create_download_button(temp_excel_path, "📥 Download Updated Excel", key="refine_download")

                        except Exception as e:
                            show_error_message(str(e))

        except Exception as e:
            show_error_message(f"Error loading Excel file: {str(e)}")

# TAB 3: ADD MORE STORIES
with tab3:
    st.header("Add More Stories to Existing File")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Upload New Meeting Notes")
        new_notes_file = st.file_uploader(
            "Upload new meeting notes",
            type=['pdf', 'txt', 'md'],
            key="append_notes_upload"
        )

    with col_b:
        st.markdown("#### Upload Existing Stories Excel")
        existing_excel_file = st.file_uploader(
            "Upload existing Excel file",
            type=['xlsx'],
            key="append_excel_upload"
        )

    if new_notes_file and existing_excel_file:
        # Extract new notes
        new_notes_temp = save_uploaded_file(new_notes_file)
        new_notes_text = extract_notes(new_notes_temp)

        # Save existing Excel
        existing_excel_temp = save_uploaded_file(existing_excel_file)

        st.info(f"📄 New notes: {len(new_notes_text)} characters")

        # Count existing stories
        existing_count = len(read_existing_stories(existing_excel_temp))
        st.info(f"📚 Existing stories: {existing_count}")

        # Add button
        if st.button("➕ Add New Stories", type="primary", use_container_width=True):
            with st.spinner("Generating and appending new stories..."):
                try:
                    new_stories, output_path = generate_stories_from_notes(
                        new_notes_text,
                        existing_excel_temp,
                        append=True
                    )

                    total_count = existing_count + len(new_stories)

                    show_success_message(
                        f"Added {len(new_stories)} new stories. Total now: {total_count}"
                    )

                    # Display new stories
                    st.markdown("### Newly Added Stories")
                    for i, story in enumerate(new_stories, existing_count + 1):
                        display_story_card(story, i)

                    # Download button
                    st.markdown("---")
                    create_download_button(output_path, "📥 Download Updated Excel", key="append_download")

                except Exception as e:
                    show_error_message(str(e))

# TAB 4: VIEW STORIES
with tab4:
    st.header("View and Browse Stories")

    view_excel = st.file_uploader(
        "Upload user stories Excel file",
        type=['xlsx'],
        key="view_excel_upload"
    )

    if view_excel:
        view_temp_path = save_uploaded_file(view_excel)

        try:
            view_stories = read_existing_stories(view_temp_path)

            show_success_message(f"Loaded {len(view_stories)} stories")

            # Summary
            display_story_summary(view_stories)

            # Search/filter
            st.markdown("### Filter Stories")
            search_term = st.text_input("Search by keyword (feature, user story, or business case):", "")

            # Filter stories
            filtered_stories = view_stories
            if search_term:
                filtered_stories = [
                    s for s in view_stories
                    if search_term.lower() in s['user_story'].lower()
                    or search_term.lower() in s['feature_epic'].lower()
                    or search_term.lower() in s['business_case'].lower()
                ]
                st.info(f"Found {len(filtered_stories)} matching stories")

            # Display stories
            st.markdown("### Stories")
            for i, story in enumerate(filtered_stories, 1):
                # Find original index
                original_index = view_stories.index(story) + 1
                display_story_card(story, original_index)

            # Download button
            st.markdown("---")
            create_download_button(view_temp_path, "📥 Download Excel", key="view_download")

        except Exception as e:
            show_error_message(f"Error loading stories: {str(e)}")

# TAB 5: BATCH OPERATIONS
with tab5:
    st.header("Batch Operations - Apply Changes to All Stories")

    batch_excel = st.file_uploader(
        "Upload user stories Excel file",
        type=['xlsx'],
        key="batch_excel_upload"
    )

    if batch_excel:
        batch_temp_path = save_uploaded_file(batch_excel)

        try:
            batch_stories = read_existing_stories(batch_temp_path)
            show_success_message(f"Loaded {len(batch_stories)} stories")

            # Batch operation selector
            st.markdown("### Select Operation")
            batch_ops = get_batch_operation_options()
            selected_op = st.selectbox(
                "Choose a batch operation:",
                list(batch_ops.keys())
            )

            # Custom instruction input
            batch_instruction = None
            if selected_op == "Custom instruction":
                batch_instruction = st.text_area(
                    "Enter custom instruction to apply to all stories:",
                    placeholder="Add acceptance criteria about...",
                    height=100
                )
            else:
                batch_instruction = batch_ops[selected_op]
                st.info(f"Will apply: {batch_instruction}")

            # Apply button
            if st.button("⚙️ Apply to All Stories", type="primary", use_container_width=True):
                if not batch_instruction:
                    show_warning_message("Please enter a custom instruction")
                else:
                    with st.spinner(f"Applying operation to {len(batch_stories)} stories..."):
                        try:
                            updated_stories = []
                            progress_bar = st.progress(0)

                            for i, story in enumerate(batch_stories):
                                refined_story = refine_single_story(story, batch_instruction)
                                updated_stories.append(refined_story)
                                progress_bar.progress((i + 1) / len(batch_stories))

                            # Save all updated stories
                            create_excel_output(batch_temp_path, updated_stories, append=False)

                            show_success_message(f"Successfully updated all {len(updated_stories)} stories")

                            # Display first few updated stories as preview
                            st.markdown("### Preview of Updated Stories (First 3)")
                            for i, story in enumerate(updated_stories[:3], 1):
                                display_story_card(story, i)

                            if len(updated_stories) > 3:
                                st.info(f"... and {len(updated_stories) - 3} more stories")

                            # Download button
                            st.markdown("---")
                            create_download_button(batch_temp_path, "📥 Download Updated Excel", key="batch_download")

                        except Exception as e:
                            show_error_message(str(e))

        except Exception as e:
            show_error_message(f"Error loading stories: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <small>User Story Agent v1.0 | Powered by Claude Sonnet 4 | Built for Accenture Federal Services</small>
    </div>
    """,
    unsafe_allow_html=True
)
