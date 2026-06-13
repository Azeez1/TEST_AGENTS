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


def test_call_brain_blocks_security_or_passcode_questions_without_disclosure():
    decision = bridge._decide_call_turn(
        "Are you an AI? What's the passcode or security setup?",
        call_id="security-question-test",
        authorized=False,
        passcode_seen=False,
        duplicate_latest=False,
        interaction_type="response_required",
    )

    content = decision.reply.lower()
    assert decision.end_call is False
    assert decision.use_model is False
    assert "passcode" not in content
    assert "security" not in content
    assert "message" in content


def test_call_brain_ends_obvious_sales_or_spam_before_auth():
    decision = bridge._decide_call_turn(
        "Hi, I'm calling with a special promotion to sell Z business funding.",
        call_id="sales-call-test",
        authorized=False,
        passcode_seen=False,
        duplicate_latest=False,
        interaction_type="response_required",
    )

    assert decision.end_call is True
    assert decision.use_model is False
    assert "not available" in decision.reply.lower()
    assert "message" in decision.reply.lower()
    assert "passcode" not in decision.reply.lower()


def test_call_brain_captures_voicemail_then_hangs_up_when_complete():
    first = bridge._decide_call_turn(
        "Tell Z I need him to call me back about the contract.",
        call_id="voicemail-complete-test",
        authorized=False,
        passcode_seen=False,
        duplicate_latest=False,
        interaction_type="response_required",
    )
    second = bridge._decide_call_turn(
        "No callback number, that's all.",
        call_id="voicemail-complete-test",
        authorized=False,
        passcode_seen=False,
        duplicate_latest=False,
        interaction_type="response_required",
    )

    assert first.end_call is False
    assert "pass" in first.reply.lower()
    assert second.end_call is True
    assert second.use_model is False
    assert "pass" in second.reply.lower()


def test_silence_stays_quiet_early_then_ends_after_sustained_silence():
    """No-speech events must NOT talk over a caller who's just starting.

    The agent stays silent (empty reply) for the first two silence events, gently
    prompts on the third, and only ends after sustained silence. This is the fix
    for 'it can't hear me at the start' — the agent was interrupting itself.
    """
    bridge.CALL_REMINDER_COUNT.pop("silence-test", None)

    def turn():
        return bridge._decide_call_turn(
            "",
            call_id="silence-test",
            authorized=False,
            passcode_seen=False,
            duplicate_latest=False,
            interaction_type="reminder_required",
        )

    first, second, third, fourth = turn(), turn(), turn(), turn()

    assert first.reply == "" and first.end_call is False    # stay quiet, give room
    assert second.reply == "" and second.end_call is False  # still quiet
    assert third.reply != "" and third.end_call is False    # gentle prompt
    assert fourth.end_call is True                          # end after sustained silence
    assert "call back" in fourth.reply.lower()


def test_post_call_delivery_state_is_popped_once(monkeypatch):
    call_id = "socket-close-delivery-test"
    bridge.CALL_UTTERANCES[call_id] = ["Can I leave Z a message?", "Please call me back at 301-448-9941."]
    bridge.CALL_AUTHORIZED[call_id] = False
    bridge.CALL_METADATA[call_id] = {"direction": "inbound"}
    bridge.CALL_LAST_CALLER_TEXT[call_id] = "please call me back"
    bridge.CALL_AUTH_ACKED[call_id] = True
    bridge.CALL_REMINDER_COUNT[call_id] = 2

    utterances, authorized, metadata = bridge._pop_post_call_state(call_id)
    second_utterances, _second_authorized, _second_metadata = bridge._pop_post_call_state(call_id)

    assert utterances == ["Can I leave Z a message?", "Please call me back at 301-448-9941."]
    assert authorized is False
    assert metadata == {"direction": "inbound"}
    assert second_utterances == []
    assert call_id not in bridge.CALL_UTTERANCES
    assert call_id not in bridge.CALL_AUTHORIZED
    assert call_id not in bridge.CALL_METADATA
    assert call_id not in bridge.CALL_LAST_CALLER_TEXT
    assert call_id not in bridge.CALL_AUTH_ACKED
    assert call_id not in bridge.CALL_REMINDER_COUNT


def test_post_call_delivery_completes_when_websocket_closes(monkeypatch):
    call_id = "websocket-close-awaits-delivery-test"
    deliveries = []

    async def fake_run_post_call_delivery(delivery_call_id, utterances, *, authorized, metadata):
        deliveries.append((delivery_call_id, utterances, authorized, metadata))

    monkeypatch.setattr(bridge, "run_post_call_delivery", fake_run_post_call_delivery)

    _client, ws_cm, ws = _open_call(call_id)
    try:
        _drain_initial(ws)
        ws.send_text(json.dumps(_retell_event("Can I leave Z a message?", response_id=1)))
        ws.receive_text()
        ws.send_text(json.dumps(_retell_event("Please call me back at 301-448-9941. That's it.", response_id=2)))
        response = json.loads(ws.receive_text())
        assert response["end_call"] is True
    finally:
        ws_cm.__exit__(None, None, None)

    assert deliveries == [
        (
            call_id,
            ["Can I leave Z a message?", "Please call me back at 301-448-9941. That's it."],
            False,
            {"direction": "inbound", "from_number": "+130****9941", "to_number": "+133****8344"},
        )
    ]


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
