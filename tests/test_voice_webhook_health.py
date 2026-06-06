import importlib
import sys
from pathlib import Path

from fastapi.testclient import TestClient


WEBHOOK_DIR = Path(__file__).resolve().parents[1] / "VOICE_TEAM" / "webhook"
sys.path.insert(0, str(WEBHOOK_DIR))
main = importlib.import_module("main")


def test_public_health_exposes_redacted_phone_voicemail_delivery_status():
    client = TestClient(main.app)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["phone_line_direct_ready"] is True
    diagnostics = payload["phone_line_voicemail_delivery"]
    assert "email_recipient_configured" in diagnostics
    assert "google_refresh_env_configured" in diagnostics
    assert "google_token_file_present" in diagnostics
    assert "last_post_call_delivery" in diagnostics
    # Health may expose readiness/status, never credential material.
    assert "token" not in str(diagnostics).lower().replace("google_token_file_present", "")
    assert "secret" not in str(diagnostics).lower().replace("google_client_env_configured", "")
