import base64
from email import message_from_bytes
import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
bridge = importlib.import_module("VOICE_TEAM.webhook.phone_bridge_direct")


def _open_call(call_id="test-call"):
    client = TestClient(bridge.app)
    ws_cm = client.websocket_connect(f"/retell/llm/{call_id}")
    ws = ws_cm.__enter__()
    return client, ws_cm, ws


def _drain_initial(ws):
    config = json.loads(ws.receive_text())
    greeting = json.loads(ws.receive_text())
    return config, greeting


def _retell_event(text, response_id=1, interaction_type="response_required"):
    return {
        "interaction_type": interaction_type,
        "response_id": response_id,
        "transcript": [{"role": "user", "content": text}],
        "call": {"from_number": "+130****9941", "to_number": "+133****8344", "direction": "inbound"},
    }


def test_initial_greeting_is_receptionist_not_rules_bot():
    _client, ws_cm, ws = _open_call("greeting-test")
    try:
        config, greeting = _drain_initial(ws)
        assert config["response_type"] == "config"
        content = greeting["content"]
        assert "Oshun for Z" in content
        assert "take a message" in content
        assert "who" in content.lower()
        assert "passcode" not in content.lower()
        assert "authenticate" not in content.lower()
    finally:
        ws_cm.__exit__(None, None, None)


def test_unauthenticated_private_request_offers_message_without_passcode():
    _client, ws_cm, ws = _open_call("private-request-test")
    try:
        _drain_initial(ws)
        ws.send_text(json.dumps(_retell_event("Can you check Z's Gmail?")))
        response = json.loads(ws.receive_text())
        content = response["content"].lower()
        assert response["end_call"] is False
        assert "private" in content
        assert "message" in content
        assert "passcode" not in content
        assert "authenticate" not in content
    finally:
        ws_cm.__exit__(None, None, None)


def test_unauthenticated_caller_can_leave_message_without_passcode():
    _client, ws_cm, ws = _open_call("voicemail-ack-test")
    try:
        _drain_initial(ws)
        ws.send_text(json.dumps(_retell_event("Can I leave Z a message?")))
        response = json.loads(ws.receive_text())
        content = response["content"]
        assert response["end_call"] is False
        assert "take a message" in content
        assert "What should I tell him" in content
        assert "passcode" not in content.lower()
    finally:
        ws_cm.__exit__(None, None, None)


def test_done_thanks_is_treated_as_end_call_intent():
    assert bridge._should_end_call("I'm good. Thank you.", "response_required", "done-thanks") is True


def test_voicemail_email_uses_google_token_file_when_refresh_env_missing(tmp_path, monkeypatch):
    token_file = tmp_path / "google_token.json"
    token_file.write_text(
        json.dumps(
            {
                "token": "valid-access-token",
                "refresh_token": "refresh-token-from-file",
                "client_id": "client-id-from-file",
                "client_secret": "client-secret-from-file",
                "expiry": "2999-01-01T00:00:00Z",
                "type": "authorized_user",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("GOOGLE_TOKEN_FILE", str(token_file))
    monkeypatch.delenv("GOOGLE_OAUTH_REFRESH_TOKEN", raising=False)
    monkeypatch.setattr(bridge, "GOOGLE_API_SCRIPT", "")
    monkeypatch.setattr(bridge, "PHONE_LINE_VOICEMAIL_EMAIL", "z@example.com")

    sent_requests = []

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    def fake_post(url, **kwargs):
        sent_requests.append((url, kwargs))
        assert url == "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
        assert kwargs["headers"]["Authorization"] == "Bearer valid-access-token"
        return FakeResponse({"id": "gmail-message-id"})

    monkeypatch.setattr(bridge.httpx, "post", fake_post)

    status = bridge.send_voicemail_email("call_test", "- Please call me back", {"direction": "inbound"})

    assert status == "sent:gmail-message-id"
    assert len(sent_requests) == 1
    raw_message = base64.urlsafe_b64decode(sent_requests[0][1]["json"]["raw"].encode("ascii"))
    parsed = message_from_bytes(raw_message)
    assert parsed.get_content_type() == "multipart/alternative"
    html_parts = [part for part in parsed.walk() if part.get_content_type() == "text/html"]
    plain_parts = [part for part in parsed.walk() if part.get_content_type() == "text/plain"]
    assert html_parts
    assert plain_parts
    html_payload = html_parts[0].get_payload(decode=True).decode("utf-8")
    assert "Please call me back" in html_payload
    assert "No actions were executed" in html_payload


def test_voicemail_email_google_workspace_helper_sends_html(tmp_path, monkeypatch):
    gapi_script = tmp_path / "google_api.py"
    gapi_script.write_text("# fake helper", encoding="utf-8")
    monkeypatch.setattr(bridge, "GOOGLE_API_SCRIPT", str(gapi_script))
    monkeypatch.setattr(bridge, "PHONE_LINE_VOICEMAIL_EMAIL", "z@example.com")

    calls = []

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps({"id": "gapi-message-id"}), stderr="")

    monkeypatch.setattr(bridge.subprocess, "run", fake_run)

    status = bridge.send_voicemail_email("call_html", "- HTML body please", {"direction": "inbound"})

    assert status == "sent:gapi-message-id"
    cmd = calls[0][0]
    assert cmd[-1] == "--html"
    html_body = cmd[cmd.index("--body") + 1]
    assert "<html" in html_body.lower()
    assert "HTML body please" in html_body
