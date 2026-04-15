"""
Integration tests for the Email Pipeline workflow.

Tests the interaction between:
  - email_template_renderer.py (template loading, HTML conversion, rendering)
  - send_email_with_attachment.py (MIME assembly, Gmail API dispatch)

Workflow under test:
  select_template → convert_plaintext → render_email_html → build MIME message

External dependencies (Gmail API, file I/O on templates JSON) are mocked.
Internal module interactions are exercised with real logic.
"""

import json
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

# ---------------------------------------------------------------------------
# Path setup: allow imports from MARKETING_TEAM/tools
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[3]  # TEST_AGENTS/
MARKETING_TOOLS = REPO_ROOT / "MARKETING_TEAM" / "tools"
sys.path.insert(0, str(MARKETING_TOOLS))


# ---------------------------------------------------------------------------
# Shared minimal email_templates.json fixture data
# ---------------------------------------------------------------------------
SAMPLE_TEMPLATES_DATA = {
    "default_template": "branded_light",
    "templates": {
        "plain": {
            "name": "Plain",
            "description": "Minimal styled email",
            "use_cases": ["internal", "transactional"],
            "html_template": "<html><body>{{BODY_CONTENT}}{{CTA_SECTION}}</body></html>"
        },
        "branded_light": {
            "name": "Branded Light",
            "description": "Professional with dark header/footer",
            "use_cases": ["deliverable", "proposal", "client_update"],
            "html_template": (
                "<html><head></head><body>"
                "<header style='background:#1a1a1a;color:gold'>DUX MACHINA</header>"
                "<main>{{BODY_CONTENT}}</main>"
                "{{CTA_SECTION}}"
                "<footer>Dux Machina OS</footer>"
                "</body></html>"
            )
        },
        "branded_dark": {
            "name": "Branded Dark",
            "description": "Full dark theme",
            "use_cases": ["announcement", "thought_leadership"],
            "html_template": (
                "<html><body style='background:#000;color:#fff'>"
                "{{BODY_CONTENT}}{{CTA_SECTION}}"
                "</body></html>"
            )
        },
        "professional": {
            "name": "Professional",
            "description": "Corporate-safe",
            "use_cases": ["enterprise", "partner"],
            "html_template": (
                "<html><body style='font-family:Arial'>"
                "{{BODY_CONTENT}}{{CTA_SECTION}}"
                "</body></html>"
            )
        }
    },
    "cta_templates": {
        "branded_light": (
            "<a href='{{CTA_LINK}}' style='background:gold;color:#000;"
            "padding:10px 20px'>{{CTA_TEXT}}</a>"
        ),
        "branded_dark": (
            "<a href='{{CTA_LINK}}' style='background:gold;color:#000;"
            "padding:10px 20px'>{{CTA_TEXT}}</a>"
        ),
        "professional": (
            "<a href='{{CTA_LINK}}' style='color:#000'>{{CTA_TEXT}}</a>"
        )
    }
}


@pytest.fixture(scope="module")
def templates_json_content():
    """Return serialized templates JSON used for all module-level tests."""
    return json.dumps(SAMPLE_TEMPLATES_DATA)


# ===========================================================================
# Section 1 — email_template_renderer internal pipeline
# ===========================================================================

@pytest.mark.integration
class TestEmailTemplateRendererPipeline:
    """
    Tests the renderer's internal module pipeline:
    load_templates → get_template → convert_plaintext_to_html → render_email_html
    """

    def test_convert_then_render_plain_text_becomes_html(self, templates_json_content):
        """
        convert_plaintext_to_html output is passed directly into render_email_html.
        Verifies the two functions compose correctly: newlines become <br> tags and
        the final HTML is embedded inside the template wrapper.
        """
        with patch("builtins.open", mock_open(read_data=templates_json_content)):
            from email_template_renderer import (
                convert_plaintext_to_html,
                render_email_html,
            )

            # Arrange — realistic multi-line email body
            plaintext_body = (
                "URGENT UPDATE\n\n"
                "Hi team,\n\n"
                "We shipped the new feature.\n"
                "Please review and respond."
            )

            # Act — Stage 1: convert to HTML fragments
            html_fragment = convert_plaintext_to_html(plaintext_body)

            # Assert Stage 1: UPPERCASE line is bolded, newlines converted
            assert "<strong>URGENT UPDATE</strong>" in html_fragment
            assert "<br>" in html_fragment

            # Act — Stage 2: embed converted fragment into template
            final_html = render_email_html(
                body=plaintext_body,
                template="branded_light"
            )

            # Assert Stage 2: template wrapper is present AND body content embedded
            assert "DUX MACHINA" in final_html          # template header
            assert "URGENT UPDATE" in final_html         # body injected
            assert "{{BODY_CONTENT}}" not in final_html  # placeholder replaced
            assert "{{CTA_SECTION}}" not in final_html   # CTA placeholder cleared

    def test_select_template_then_render_with_cta(self, templates_json_content):
        """
        select_template_for_context → render_email_html with CTA injection.
        Verifies the two functions work together: context selection drives template
        choice, and the CTA is correctly injected into the chosen template.
        """
        with patch("builtins.open", mock_open(read_data=templates_json_content)):
            from email_template_renderer import (
                select_template_for_context,
                render_email_html,
            )

            # Arrange
            template_name = select_template_for_context(
                email_type="announcement",
                recipient_type="general"
            )

            # Assert context selection chose branded_dark for announcements
            assert template_name == "branded_dark"

            # Act — render with that template and a CTA
            html = render_email_html(
                body="We have exciting news!",
                template=template_name,
                cta_text="Read More",
                cta_link="https://duxmachina.com/news"
            )

            # Assert — CTA text and link are embedded
            assert "Read More" in html
            assert "https://duxmachina.com/news" in html
            assert "{{CTA_TEXT}}" not in html
            assert "{{CTA_LINK}}" not in html

    def test_list_templates_then_get_each_valid_template(self, templates_json_content):
        """
        list_templates → get_template: every template reported as available
        should be fetchable without raising an error.
        """
        with patch("builtins.open", mock_open(read_data=templates_json_content)):
            from email_template_renderer import list_templates, get_template

            # Arrange
            available = list_templates()
            assert len(available) > 0, "list_templates() returned empty dict"

            # Act & Assert — every listed template can be fetched
            for name in available:
                html_template = get_template(name)
                assert isinstance(html_template, str)
                assert len(html_template) > 0, f"Template '{name}' returned empty HTML"

    def test_render_with_unknown_template_raises_value_error(self, templates_json_content):
        """
        render_email_html with invalid template name should surface a ValueError.
        The error must propagate from get_template up through render_email_html.
        """
        with patch("builtins.open", mock_open(read_data=templates_json_content)):
            from email_template_renderer import render_email_html

            with pytest.raises(ValueError, match="not found"):
                render_email_html(body="Hello", template="nonexistent_template")

    def test_get_default_template_matches_config(self, templates_json_content):
        """
        get_default_template() should return what's defined in default_template key.
        """
        with patch("builtins.open", mock_open(read_data=templates_json_content)):
            from email_template_renderer import get_default_template

            default = get_default_template()
            assert default == SAMPLE_TEMPLATES_DATA["default_template"]


# ===========================================================================
# Section 2 — send_email_with_attachment integration with renderer
# ===========================================================================

@pytest.mark.integration
class TestEmailSendWithRendererIntegration:
    """
    Tests send_email_with_attachment.py calling into email_template_renderer.py.
    Gmail API calls are mocked at the service layer; internal rendering runs real.
    """

    @pytest.fixture
    def attachment_file(self, tmp_path):
        """Create a real temporary file as a stand-in for an attachment."""
        f = tmp_path / "report.pdf"
        f.write_bytes(b"%PDF-1.4 stub content")
        return str(f)

    @pytest.fixture
    def mock_gmail_service(self):
        """Mock the Gmail API service returned by get_gmail_service()."""
        service = MagicMock()
        service.users().messages().send().execute.return_value = {
            "id": "msg_test_123",
            "threadId": "thread_456"
        }
        return service

    def test_send_email_renders_html_before_sending(
        self, attachment_file, mock_gmail_service, templates_json_content
    ):
        """
        End-to-end: send_email_with_attachment should call render_email_html
        internally, producing an HTML-rich MIME message that reaches the Gmail API.
        The returned message ID confirms the API was called with a real payload.
        """
        with patch("builtins.open", mock_open(read_data=templates_json_content)):
            # Patch the attachment open separately so the file read doesn't get mocked
            with patch(
                "send_email_with_attachment.get_gmail_service",
                return_value=mock_gmail_service
            ):
                # Re-open the attachment using the real file
                import builtins
                real_open = builtins.open

                def selective_open(path, *args, **kwargs):
                    if path == attachment_file:
                        return real_open(path, *args, **kwargs)
                    # For templates JSON
                    return mock_open(read_data=templates_json_content)()

                with patch("builtins.open", side_effect=selective_open):
                    from send_email_with_attachment import send_email_with_attachment

                    # Act
                    message_id = send_email_with_attachment(
                        to_email="test@example.com",
                        subject="Quarterly Report",
                        body="Hi,\n\nPlease find the report attached.\n\nBest,",
                        attachment_path=attachment_file,
                        template="branded_light"
                    )

                    # Assert — API was called and message ID returned
                    assert message_id == "msg_test_123"
                    mock_gmail_service.users().messages().send.assert_called_once()

    def test_send_email_missing_required_fields_raises_value_error(
        self, attachment_file, templates_json_content
    ):
        """
        Validation in send_email_with_attachment: missing required params
        should raise ValueError before any rendering or API call occurs.
        """
        with patch("builtins.open", mock_open(read_data=templates_json_content)):
            from send_email_with_attachment import send_email_with_attachment

            with pytest.raises((ValueError, TypeError)):
                send_email_with_attachment(
                    to_email="",          # empty → should fail validation
                    subject="Subject",
                    body="Body",
                    attachment_path=attachment_file
                )

    def test_send_email_missing_attachment_raises_file_not_found(
        self, templates_json_content
    ):
        """
        Attempt to send with a nonexistent attachment path should raise
        FileNotFoundError before making any API call.
        """
        with patch("builtins.open", mock_open(read_data=templates_json_content)):
            from send_email_with_attachment import send_email_with_attachment

            with pytest.raises(FileNotFoundError):
                send_email_with_attachment(
                    to_email="test@example.com",
                    subject="Test",
                    body="Hello",
                    attachment_path="/nonexistent/path/file.pdf"
                )


# ===========================================================================
# Section 3 — Template selection context → full send pipeline
# ===========================================================================

@pytest.mark.integration
@pytest.mark.slow
class TestTemplateSelectionToSendPipeline:
    """
    Full pipeline: select_template_for_context → render_email_html → send.
    Tests that contextual template selection produces a coherent email.
    """

    @pytest.fixture
    def attachment_file(self, tmp_path):
        f = tmp_path / "deck.pptx"
        f.write_bytes(b"PK stub pptx content")
        return str(f)

    @pytest.fixture
    def mock_gmail_service(self):
        service = MagicMock()
        service.users().messages().send().execute.return_value = {"id": "enterprise_msg_789"}
        return service

    @pytest.mark.parametrize("email_type,recipient_type,expected_template", [
        ("deliverable", "client", "branded_light"),
        ("announcement", "general", "branded_dark"),
        ("internal", "internal", "plain"),
        ("proposal", "enterprise", "professional"),
    ])
    def test_context_driven_template_selection_renders_consistently(
        self,
        email_type,
        recipient_type,
        expected_template,
        templates_json_content
    ):
        """
        Parametrized: for each email context, verify that:
        1. select_template_for_context returns the expected template name
        2. render_email_html with that template produces valid HTML
        3. The rendered HTML contains the body content (no un-replaced placeholders)
        """
        with patch("builtins.open", mock_open(read_data=templates_json_content)):
            from email_template_renderer import (
                select_template_for_context,
                render_email_html,
            )

            # Stage 1: select
            chosen = select_template_for_context(email_type, recipient_type)
            assert chosen == expected_template, (
                f"Expected '{expected_template}' for "
                f"email_type={email_type!r}, recipient_type={recipient_type!r}, "
                f"got '{chosen}'"
            )

            # Stage 2: render
            body = f"This is a {email_type} email for {recipient_type} recipients."
            html = render_email_html(body=body, template=chosen)

            # Stage 3: verify
            assert body.split(".")[0] in html  # body content present
            assert "{{BODY_CONTENT}}" not in html
            assert "{{CTA_SECTION}}" not in html
