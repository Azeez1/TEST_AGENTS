import importlib
import json
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


def test_post_call_delivery_is_scheduled_once_on_socket_close(monkeypatch):
    call_id = "socket-close-delivery-test"
    bridge.CALL_UTTERANCES[call_id] = ["Can I leave Z a message?", "Please call me back at 301-448-9941."]
    bridge.CALL_AUTHORIZED[call_id] = False
    bridge.CALL_METADATA[call_id] = {"direction": "inbound"}
    bridge.CALL_LAST_CALLER_TEXT[call_id] = "please call me back"
    bridge.CALL_AUTH_ACKED[call_id] = True
    bridge.CALL_REMINDER_COUNT[call_id] = 2

    scheduled = []

    def fake_create_task(coro):
        scheduled.append(coro)
        coro.close()
        return object()

    monkeypatch.setattr(bridge.asyncio, "create_task", fake_create_task)

    bridge._schedule_post_call_delivery(call_id)
    bridge._schedule_post_call_delivery(call_id)

    assert len(scheduled) == 1
    assert call_id not in bridge.CALL_UTTERANCES
    assert call_id not in bridge.CALL_AUTHORIZED
    assert call_id not in bridge.CALL_METADATA
    assert call_id not in bridge.CALL_LAST_CALLER_TEXT
    assert call_id not in bridge.CALL_AUTH_ACKED
    assert call_id not in bridge.CALL_REMINDER_COUNT


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
