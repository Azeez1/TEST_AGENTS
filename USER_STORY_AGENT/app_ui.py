"""
User Story Agent - Web UI
Complete Streamlit interface for generating and managing user stories
"""

import streamlit as st
import os
import tempfile
import asyncio
from anthropic import Anthropic
from note_parser import extract_notes, extract_notes_from_multiple_files
from story_generator import StoryGenerator
from excel_handler import ExcelHandler, read_existing_stories, create_excel_output
from formatters import StoryFormatter, validate_stories
from ui_helpers import (
    display_story_card, display_story_summary, save_uploaded_file,
    show_success_message, show_error_message, show_warning_message, show_info_message,
    create_download_button, get_batch_operation_options
)
from dotenv import load_dotenv

# Import autonomous mode components
try:
    from autonomous_mode import AutonomousAgent, generate_stories_autonomous
    from conversation_memory import ConversationMemory, format_preferences_for_display
    from multi_file_processor import process_multiple_files
    AUTONOMOUS_MODE_AVAILABLE = True
except ImportError:
    AUTONOMOUS_MODE_AVAILABLE = False

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
if 'refine_working_stories' not in st.session_state:
    st.session_state.refine_working_stories = []
if 'refinement_history' not in st.session_state:
    st.session_state.refinement_history = []
if 'refine_excel_name' not in st.session_state:
    st.session_state.refine_excel_name = None

# Autonomous mode session state
if 'feedback_history' not in st.session_state:
    st.session_state.feedback_history = []
if 'autonomous_agent' not in st.session_state and AUTONOMOUS_MODE_AVAILABLE:
    st.session_state.autonomous_agent = AutonomousAgent()

# Initialize clients
client = Anthropic()
story_generator = StoryGenerator()
formatter = StoryFormatter()


def generate_stories_from_notes(notes_text: str, output_filename: str, append: bool, ac_format: str = "gherkin"):
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

        # Define AC format instructions
        if ac_format == "explicit":
            ac_example = """      "1. The Login Page displays:\\n   a. Email field (Required)\\n   b. Password field (Required)\\n      i. Show/hide password toggle\\n   c. \\"Remember Me\\" checkbox\\n   d. \\"Sign In\\" button\\n      i. Disabled if fields empty",
      "2. User States:\\n   a. Guest users: Form is displayed\\n   b. Already logged in: Redirect to Dashboard",
      "3. Validation:\\n   a. If email invalid format, display error: \\"Please enter valid email\\"\\n   b. If credentials incorrect, display error: \\"Invalid email or password\\"",
      "4. Successful Login:\\n   a. Redirect to Dashboard\\n   b. Set session cookie (expires in 30 days if \\"Remember Me\\" checked)",
      "Notes:\\n- Performance: Page loads within 2 seconds\\n- Security: HTTPS required, password encrypted\\n- Accessibility: Keyboard navigable, proper labels\\n- Analytics: Track login attempts, success/failure rates" """
            ac_requirement = """2. Include Explicit/Detailed acceptance criteria in this specific format:

   TARGET: 30-50 lines total (2,500-4,500 characters)
   STRUCTURE: 3-4 indentation levels max (1, a, i, 1), 4-7 main sections

   Universal Checklist - Cover ALL of these:
   ✅ Trigger/Entry Point: What initiates this functionality?
   ✅ Inputs: What data/information is required?
   ✅ Processing/Logic: What happens during execution?
   ✅ Outputs: What's produced?
   ✅ Validation Rules: What must be verified?
   ✅ Error Handling: What happens when things fail?
   ✅ Edge Cases: Unusual scenarios?
   ✅ Permissions: Who can access this?
   ✅ State Changes: What changes in the system?
   ✅ Success Criteria: How do we know it worked?

   INCLUDE:
   ✅ What displays on screen, user interactions, conditional logic (if/then)
   ✅ Validation and error messages with EXACT text
   ✅ Navigation flows, required vs optional fields
   ✅ User states (guest/logged in, empty states)
   ✅ Cross-references: (See [Story Name])

   AVOID:
   ❌ Design details, pixel-perfect specs, vague statements
   ❌ Exhaustive analytics/accessibility (put in Notes)

   REQUIRED: Always end with "Notes:" section covering:
   - Performance, Accessibility, Analytics, Future enhancements"""
        else:
            ac_example = """      "Given [context], when [action], then [expected outcome]",
      "Given [context], when [action], then [expected outcome]" """
            ac_requirement = "2. Include 4-6 detailed acceptance criteria per story in Gherkin format (Given/When/Then)"

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
{ac_example}
    ],
    "business_case": "Explanation of business value and impact",
    "relevant_pages": "Page/screen names affected"
  }}
]

Requirements:
1. Each story must follow the "As a..., I want..., so that..." format
{ac_requirement}
3. Each acceptance_criteria array element is a complete numbered section with \\n for line breaks and proper indentation (spaces)
4. Cover edge cases: errors, mobile responsiveness, accessibility, missing data
5. Business case should explain ROI, customer impact, or strategic value
6. Be specific about which pages/screens/areas are affected
7. Always include the "Notes:" section as the final element in acceptance_criteria array

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


def refine_single_story(story: dict, instruction: str, ac_format: str = "gherkin") -> dict:
    """Refine a specific story based on instruction"""
    try:
        prompt = story_generator.get_refinement_prompt(story, instruction, ac_format)

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
if AUTONOMOUS_MODE_AVAILABLE:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📝 Generate Stories",
        "✏️ Refine Stories",
        "➕ Add More Stories",
        "👁️ View Stories",
        "⚙️ Batch Operations",
        "🤖 Autonomous & Feedback"
    ])
else:
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
        # Check if autonomous mode available for multiple files
        if AUTONOMOUS_MODE_AVAILABLE:
            uploaded_notes = st.file_uploader(
                "Upload meeting notes or requirements (multiple files supported)",
                type=['pdf', 'txt', 'md', 'docx', 'xlsx', 'xls', 'json', 'csv', 'html', 'xml', 'png', 'jpg', 'jpeg'],
                accept_multiple_files=True,
                help="Supported: PDF, TXT, MD, DOCX, XLSX/XLS, JSON, CSV, HTML, XML, Images (with OCR)\n\nMultiple files will be combined automatically",
                key="gen_file_upload"
            )
        else:
            uploaded_notes = st.file_uploader(
                "Upload meeting notes or requirements",
                type=['pdf', 'txt', 'md', 'docx', 'xlsx', 'xls'],
                help="Supported formats: PDF, TXT, MD, DOCX (Word), XLSX/XLS (Excel)",
                key="gen_file_upload"
            )
            # Convert single file to list for consistency
            uploaded_notes = [uploaded_notes] if uploaded_notes else []

        if uploaded_notes:
            if len(uploaded_notes) == 1:
                temp_path = save_uploaded_file(uploaded_notes[0])
                notes_text = extract_notes(temp_path)
                st.success(f"✓ Loaded {len(notes_text)} characters from {uploaded_notes[0].name}")
            else:
                # Multiple files
                temp_paths = [save_uploaded_file(f) for f in uploaded_notes]
                notes_text = extract_notes_from_multiple_files(temp_paths)
                st.success(f"✓ Loaded {len(uploaded_notes)} files, {len(notes_text)} total characters")

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

    # AC Format Selection
    st.markdown("### Acceptance Criteria Format")
    ac_format = st.radio(
        "Choose AC format:",
        ["Gherkin (Given/When/Then)", "Explicit/Detailed"],
        horizontal=True,
        help="""Gherkin: Concise Given/When/Then format for testable criteria

Explicit/Detailed: Realistic format (30-50 lines, 2,500-4,500 chars)
• Hierarchical numbering (1, a, i, 1) with 4-7 main sections
• Includes: screen display, user interactions, validation, navigation, user states, responsive behavior
• Avoids: pixel-perfect design, exhaustive specs, non-critical timings
• Always includes Notes section: performance, accessibility, analytics, future enhancements

Focuses on functional requirements developers and QA need to implement/test.""",
        key="gen_ac_format"
    )
    ac_format_value = "gherkin" if ac_format == "Gherkin (Given/When/Then)" else "explicit"

    # Autonomous Mode Options (if available)
    browser_enabled = False
    browser_instructions = ""
    current_feedback = ""

    if AUTONOMOUS_MODE_AVAILABLE:
        st.markdown("---")
        st.markdown("### 🤖 Autonomous Mode (Optional)")

        # Show MCP Status
        if st.session_state.autonomous_agent:
            mcp_status = st.session_state.autonomous_agent.get_mcp_status()
            if mcp_status['configured']:
                st.success(f"🔌 MCP Configured | {mcp_status['tools_available']} Playwright tools available")
                if mcp_status['server_running']:
                    st.info("✅ MCP Server: Running")
                else:
                    st.info("⏸️ MCP Server: Will start when needed")
            else:
                st.warning("⚠️ MCP Not Configured - Using research-enhanced prompts only")
                with st.expander("How to enable MCP"):
                    st.markdown("""
                    To enable TRUE browser automation with Playwright:
                    1. Ensure `mcp_config.json` exists in the project folder
                    2. Install Playwright: `npm install -g @executeautomation/playwright-mcp-server`
                    3. Restart the app

                    Without MCP, the agent uses research-enhanced prompts (still effective!)
                    """)

        browser_enabled = st.checkbox(
            "Enable Browser & Research Mode",
            value=False,
            help="Agent will use Playwright MCP tools to actually browse websites and research best practices"
        )

        if browser_enabled:
            research_mode = st.radio(
                "Research Mode:",
                ["Autonomous (Agent decides)", "Guided (Provide instructions)"],
                horizontal=True
            )

            if research_mode == "Guided (Provide instructions)":
                browser_instructions = st.text_area(
                    "Browser Instructions",
                    placeholder="Examples:\n• Go to https://figma.com/file/xyz and extract design specs\n• Search for 'WCAG accessibility requirements checkout flow'\n• Browse https://design.company.com and learn button components",
                    height=120,
                    help="Tell the agent what to browse, search, or research"
                )

        # Feedback section
        st.markdown("### 💬 Feedback (Optional)")
        current_feedback = st.text_area(
            "Apply feedback from previous generation",
            placeholder="Examples:\n• Make ACs shorter (20-30 lines)\n• Use Button.Primary not 'primary button'\n• Always include mobile responsiveness\n• More user-focused, less technical",
            height=100,
            help="Agent will remember and apply this feedback to generation"
        )

    # Generate button
    if st.button("🚀 Generate User Stories", type="primary", use_container_width=True):
        if not notes_text:
            show_error_message("Please provide meeting notes (upload file or paste text)")
        else:
            # Use autonomous mode if enabled, otherwise use standard generation
            if AUTONOMOUS_MODE_AVAILABLE and (browser_enabled or current_feedback):
                # Autonomous generation
                spinner_text = "Generating with autonomous mode..."
                if browser_enabled:
                    spinner_text = "Researching and generating stories..."

                # Create activity log container
                activity_log = st.empty()
                log_lines = []

                def log_callback(message):
                    """Callback to capture and display logs"""
                    log_lines.append(message)
                    # Update the activity log display (latest 30 lines)
                    with activity_log.container():
                        st.markdown("### 🔴 Live Activity Log")
                        st.code("\n".join(log_lines[-30:]), language="")

                try:
                    # Show initial activity log
                    with activity_log.container():
                        st.markdown("### 🔴 Live Activity Log")
                        st.info("Starting autonomous generation...")

                    # Add feedback if provided
                    if current_feedback and st.session_state.autonomous_agent:
                        st.session_state.autonomous_agent.add_feedback(current_feedback, "Tab 1 Generation")
                        st.session_state.feedback_history.append(current_feedback)

                    # Save notes to temp file for autonomous mode
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8') as tmp:
                        tmp.write(notes_text)
                        temp_notes_path = tmp.name

                    # Create autonomous agent
                    agent = AutonomousAgent(output_file=output_filename, enable_browser=browser_enabled)

                    # Copy feedback from session if exists
                    if st.session_state.feedback_history:
                        for fb in st.session_state.feedback_history:
                            agent.add_feedback(fb)

                    # Generate with async support
                    import asyncio
                    success, stories, message = asyncio.run(
                        agent.generate_from_notes(
                            temp_notes_path,
                            ac_format=ac_format_value,
                            browser_instructions=browser_instructions,
                            append=append_mode
                        )
                    )

                    # Clean up temp file
                    try:
                        os.unlink(temp_notes_path)
                    except:
                        pass

                    # Clear activity log after completion
                    activity_log.empty()

                    if success:
                        st.session_state.generated_stories = stories
                        st.session_state.output_file_path = output_filename

                        show_success_message(f"Stories generated successfully! {message}", len(stories))

                        # Show research notice
                        if browser_enabled:
                            st.info("🌐 Agent performed web research to enhance story quality")

                        # Display summary
                        display_story_summary(stories)

                        # Display stories
                        st.markdown("### Generated Stories")
                        for i, story in enumerate(stories, 1):
                            display_story_card(story, i)

                        # Download button
                        st.markdown("---")
                        create_download_button(output_filename, "📥 Download Excel File", key="gen_download")
                    else:
                        show_error_message(message)

                except Exception as e:
                    activity_log.empty()
                    show_error_message(f"Autonomous generation error: {str(e)}")
            else:
                # Standard generation (original behavior)
                with st.spinner("Generating user stories with Claude AI..."):
                    try:
                        stories, output_path = generate_stories_from_notes(notes_text, output_filename, append_mode, ac_format_value)

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
    st.markdown("*Refine multiple stories in one session before downloading*")

    # Upload existing Excel
    uploaded_excel = st.file_uploader(
        "Upload existing user stories Excel file",
        type=['xlsx'],
        help="Upload the Excel file containing your user stories",
        key="refine_excel_upload"
    )

    if uploaded_excel:
        # Load stories into session state if new upload
        if st.session_state.refine_excel_name != uploaded_excel.name:
            temp_excel_path = save_uploaded_file(uploaded_excel)
            st.session_state.refine_working_stories = read_existing_stories(temp_excel_path)
            st.session_state.refine_excel_name = uploaded_excel.name
            st.session_state.refinement_history = []

        show_success_message(f"Loaded {len(st.session_state.refine_working_stories)} stories from {uploaded_excel.name}")

        # Show refinement history if any
        if st.session_state.refinement_history:
            st.markdown("### ✏️ Refinements Made This Session")
            for history_item in st.session_state.refinement_history:
                st.success(f"✓ Story {history_item['row']}: {history_item['instruction']}")

        st.markdown("---")

        # Display stories list
        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("### Select Story to Refine")

            # Story selector
            story_options = [f"Story {i+1}: {s['feature_epic']}" for i, s in enumerate(st.session_state.refine_working_stories)]
            selected_index = st.selectbox(
                "Choose a story:",
                range(len(story_options)),
                format_func=lambda x: story_options[x],
                key="refine_story_selector"
            )

        with col2:
            st.markdown("### Current Story")
            display_story_card(st.session_state.refine_working_stories[selected_index])

        st.markdown("---")

        # AC Format Selection (for AI Refinement)
        st.markdown("### Acceptance Criteria Format")
        refine_ac_format = st.radio(
            "Choose AC format:",
            ["Gherkin (Given/When/Then)", "Explicit/Detailed"],
            horizontal=True,
            help="""Gherkin: Concise Given/When/Then format for testable criteria

Explicit/Detailed: Realistic format (30-50 lines, 2,500-4,500 chars)
• Hierarchical numbering (1, a, i, 1) with 4-7 main sections
• Includes: screen display, user interactions, validation, navigation, user states, responsive behavior
• Avoids: pixel-perfect design, exhaustive specs, non-critical timings
• Always includes Notes section: performance, accessibility, analytics, future enhancements

Focuses on functional requirements developers and QA need to implement/test.""",
            key="refine_ac_format"
        )
        refine_ac_format_value = "gherkin" if refine_ac_format == "Gherkin (Given/When/Then)" else "explicit"

        st.markdown("---")

        # Two options: Manual Edit OR AI Refinement
        edit_mode = st.radio(
            "Choose editing mode:",
            ["✏️ Manual Edit", "🤖 AI Refinement"],
            horizontal=True,
            key="edit_mode_selector"
        )

        if edit_mode == "✏️ Manual Edit":
            st.markdown("### Manual Edit Story")
            st.markdown("*Edit the fields directly and save your changes*")

            # Get current story
            current_story = st.session_state.refine_working_stories[selected_index]

            # Manual edit fields
            manual_user_story = st.text_area(
                "User Story",
                value=current_story['user_story'],
                height=80,
                key=f"manual_user_story_{selected_index}"
            )

            manual_feature_epic = st.text_input(
                "Feature/Epic",
                value=current_story['feature_epic'],
                key=f"manual_feature_{selected_index}"
            )

            # Acceptance Criteria (each on separate line)
            st.markdown("**Acceptance Criteria** (one per line)")
            manual_ac_text = st.text_area(
                "Acceptance Criteria",
                value="\n".join(current_story['acceptance_criteria']),
                height=120,
                key=f"manual_ac_{selected_index}",
                help="Enter each acceptance criterion on a new line"
            )

            manual_business_case = st.text_area(
                "Rationale or Business Case",
                value=current_story['business_case'],
                height=80,
                key=f"manual_bc_{selected_index}"
            )

            manual_relevant_pages = st.text_input(
                "Relevant Page(s)",
                value=current_story['relevant_pages'],
                key=f"manual_pages_{selected_index}"
            )

            # Save button
            if st.button("💾 Save Manual Changes", type="primary", use_container_width=True):
                # Parse AC text into list
                ac_list = [line.strip() for line in manual_ac_text.split('\n') if line.strip()]

                # Create updated story
                updated_story = {
                    'user_story': manual_user_story.strip(),
                    'feature_epic': manual_feature_epic.strip(),
                    'acceptance_criteria': ac_list,
                    'business_case': manual_business_case.strip(),
                    'relevant_pages': manual_relevant_pages.strip()
                }

                # Update in working stories
                st.session_state.refine_working_stories[selected_index] = updated_story

                # Add to history
                st.session_state.refinement_history.append({
                    'row': selected_index + 1,
                    'feature': updated_story['feature_epic'],
                    'instruction': 'Manual edit'
                })

                show_success_message(f"Story {selected_index + 1} saved! You can edit more stories or download all changes.")
                st.rerun()

        else:  # AI Refinement mode
            st.markdown("### AI Refinement Instructions")
            st.markdown("*Describe what you want Claude to change*")

            refinement_instruction = st.text_area(
                "What changes do you want to make?",
                placeholder="Examples:\n- Add more acceptance criteria about error handling\n- Make the business case more specific\n- Add mobile responsiveness requirements\n- Change user type from 'customer' to 'administrator'",
                height=120,
                key="refine_instruction_input"
            )

            # Refine button
            if st.button("🤖 Refine with AI", type="primary", use_container_width=True):
                if not refinement_instruction:
                    show_warning_message("Please enter refinement instructions")
                else:
                    with st.spinner("Refining story with Claude AI..."):
                        try:
                            refined_story = refine_single_story(
                                st.session_state.refine_working_stories[selected_index],
                                refinement_instruction,
                                refine_ac_format_value
                            )

                            # Update in working stories
                            st.session_state.refine_working_stories[selected_index] = refined_story

                            # Add to history
                            st.session_state.refinement_history.append({
                                'row': selected_index + 1,
                                'feature': refined_story['feature_epic'],
                                'instruction': refinement_instruction
                            })

                            show_success_message(f"Story {selected_index + 1} refined! You can refine more stories or download all changes.")

                            # Force rerun to show updated state
                            st.rerun()

                        except Exception as e:
                            show_error_message(str(e))

        # Download button section
        st.markdown("---")

        # Download all changes button (only if refinements made)
        if st.session_state.refinement_history:
                try:
                    # Prepare download data
                    import tempfile
                    from excel_handler import ExcelHandler

                    def prepare_download_data():
                        """Prepare Excel data for download"""
                        # Create temp file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                            temp_path = tmp.name

                        # Write stories to temp file
                        excel_handler = ExcelHandler(temp_path)
                        excel_handler.write_stories(st.session_state.refine_working_stories, append=False)
                        excel_handler.close()

                        # Read the file
                        with open(temp_path, 'rb') as f:
                            data = f.read()

                        # Clean up temp file
                        import os
                        try:
                            os.unlink(temp_path)
                        except:
                            pass

                        return data

                    # Generate Excel data
                    excel_data = prepare_download_data()

                    # Direct download button
                    st.download_button(
                        label="📥 Download All Changes",
                        data=excel_data,
                        file_name=st.session_state.refine_excel_name or "refined_stories.xlsx",
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        use_container_width=True,
                        key="refine_download_all"
                    )

                    st.info(f"✓ {len(st.session_state.refinement_history)} refinements ready to download")

                except Exception as e:
                    show_error_message(f"Download error: {str(e)}")

        # Show refined story preview if just refined
        if st.session_state.refinement_history and st.session_state.refinement_history[-1]['row'] == selected_index + 1:
            st.markdown("---")
            st.markdown("### ✨ Refined Story Preview")
            display_story_card(st.session_state.refine_working_stories[selected_index])

# TAB 3: ADD MORE STORIES
with tab3:
    st.header("Add More Stories to Existing File")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Upload New Meeting Notes")
        new_notes_file = st.file_uploader(
            "Upload new meeting notes or requirements",
            type=['pdf', 'txt', 'md', 'docx', 'xlsx', 'xls'],
            help="Supported: PDF, TXT, MD, DOCX, XLSX/XLS",
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

        # AC Format Selection
        st.markdown("### Acceptance Criteria Format")
        append_ac_format = st.radio(
            "Choose AC format:",
            ["Gherkin (Given/When/Then)", "Explicit/Detailed"],
            horizontal=True,
            help="""Gherkin: Concise Given/When/Then format for testable criteria

Explicit/Detailed: Realistic format (30-50 lines, 2,500-4,500 chars)
• Hierarchical numbering (1, a, i, 1) with 4-7 main sections
• Includes: screen display, user interactions, validation, navigation, user states, responsive behavior
• Avoids: pixel-perfect design, exhaustive specs, non-critical timings
• Always includes Notes section: performance, accessibility, analytics, future enhancements

Focuses on functional requirements developers and QA need to implement/test.""",
            key="append_ac_format"
        )
        append_ac_format_value = "gherkin" if append_ac_format == "Gherkin (Given/When/Then)" else "explicit"

        # Add button
        if st.button("➕ Add New Stories", type="primary", use_container_width=True):
            with st.spinner("Generating and appending new stories..."):
                try:
                    new_stories, output_path = generate_stories_from_notes(
                        new_notes_text,
                        existing_excel_temp,
                        append=True,
                        ac_format=append_ac_format_value
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

# TAB 6: AUTONOMOUS & FEEDBACK (only if autonomous mode available)
if AUTONOMOUS_MODE_AVAILABLE:
    with tab6:
        st.header("🤖 Autonomous Mode & Feedback Management")
        st.markdown("Manage agent preferences and view feedback history")

        # Create tabs within tab6
        feedback_tab, preferences_tab, about_tab = st.tabs([
            "💬 Feedback History",
            "⚙️ Stored Preferences",
            "ℹ️ About Autonomous Mode"
        ])

        with feedback_tab:
            st.markdown("### Current Session Feedback")

            if st.session_state.feedback_history:
                st.info(f"📝 {len(st.session_state.feedback_history)} feedback items this session")

                for i, feedback in enumerate(st.session_state.feedback_history, 1):
                    with st.expander(f"Feedback {i}"):
                        st.write(feedback)

                if st.button("Clear Session Feedback", key="clear_session_feedback"):
                    st.session_state.feedback_history = []
                    st.success("Session feedback cleared")
                    st.rerun()
            else:
                st.info("No feedback in current session")

            st.markdown("---")
            st.markdown("### Add New Feedback")
            st.markdown("Add feedback that will be applied to all future generations")

            new_feedback = st.text_area(
                "Enter feedback:",
                placeholder="Examples:\n• Always include error handling in ACs\n• Use specific component names from our design system\n• Make stories more user-focused",
                height=120,
                key="new_feedback_input"
            )

            if st.button("💾 Save Feedback", type="primary"):
                if new_feedback:
                    st.session_state.feedback_history.append(new_feedback)
                    if st.session_state.autonomous_agent:
                        st.session_state.autonomous_agent.add_feedback(new_feedback, "Manual Entry")
                    st.success("Feedback saved! It will be applied to future generations.")
                    st.rerun()
                else:
                    st.warning("Please enter feedback first")

        with preferences_tab:
            st.markdown("### Stored Preferences")
            st.markdown("These preferences are saved permanently and applied across all sessions")

            if st.session_state.autonomous_agent:
                preferences = st.session_state.autonomous_agent.get_preferences()

                if preferences:
                    st.info(f"📚 {len(preferences)} stored preferences")

                    for i, pref in enumerate(preferences):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(f"**{i+1}.** {pref.get('preference', '')}")
                            st.caption(f"Added: {pref.get('timestamp', 'Unknown')[:10]}")
                        with col2:
                            if st.button("Delete", key=f"del_pref_{i}"):
                                st.session_state.autonomous_agent.remove_preference(i)
                                st.success("Preference removed")
                                st.rerun()

                    st.markdown("---")
                    if st.button("🗑️ Clear All Preferences", type="secondary"):
                        if st.session_state.autonomous_agent.memory:
                            st.session_state.autonomous_agent.memory.clear_all()
                            st.success("All preferences cleared")
                            st.rerun()
                else:
                    st.info("No stored preferences yet")
                    st.markdown("💡 **Tip:** Add feedback in the 'Feedback History' tab to create permanent preferences")
            else:
                st.info("Autonomous agent not initialized")

        with about_tab:
            st.markdown("### About Autonomous Mode")

            st.markdown("""
            **Autonomous Mode** enhances story generation with:

            #### 🌐 Browser & Research
            - **Web Search**: Agent searches for best practices, examples, and standards
            - **Site Browsing**: Can visit URLs you provide (Figma, design systems, docs)
            - **Autonomous Research**: Agent decides what to research based on notes
            - **Guided Research**: You provide specific instructions for browsing

            #### 💬 Feedback & Learning
            - **Session Feedback**: Applied to current session
            - **Stored Preferences**: Permanent, applied across all sessions
            - **Iterative Improvement**: Agent learns and improves over time
            - **Contextual Memory**: Remembers your preferences and style

            #### 📁 Enhanced File Support
            - **Multiple Files**: Upload and process multiple files at once
            - **More Formats**: JSON, CSV, HTML, XML, Images (with OCR)
            - **Automatic Combination**: Files are intelligently combined

            #### 🎯 Use Cases
            1. **Design System Integration**: Browse your design system and use exact component names
            2. **Standards Compliance**: Research WCAG, GDPR, or other standards automatically
            3. **Competitive Analysis**: Analyze competitor implementations
            4. **Style Learning**: Agent learns your team's story style over time
            5. **Domain Research**: Automatic research of domain-specific best practices

            #### 🚀 Getting Started
            1. Enable "Browser & Research Mode" in Tab 1
            2. Choose Autonomous or provide specific instructions
            3. Optionally add feedback for the agent to apply
            4. Generate stories - agent will research first
            5. Review and provide more feedback to improve future generations

            #### 💡 Tips
            - Start with autonomous mode to let agent explore
            - Provide specific URLs when you have resources to analyze
            - Use feedback to teach agent your preferences over time
            - Stored preferences persist across sessions
            - Combine multiple input files for comprehensive context
            """)

            st.markdown("---")
            st.markdown("### Configuration")

            mcp_available = os.path.exists("mcp_config.json")
            st.write(f"**MCP Configuration:** {'✅ Available' if mcp_available else '❌ Not found'}")

            if mcp_available:
                st.success("Playwright MCP is configured and ready")
            else:
                st.warning("MCP config not found. Browser features may be limited.")
                st.info("Create `mcp_config.json` to enable full browser capabilities")

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
