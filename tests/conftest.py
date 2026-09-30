"""Root tests run offline and isolate voice delivery from real accounts/state."""
import ipaddress
import socket
import sys

import pytest


@pytest.fixture(autouse=True)
def isolate_external_effects(monkeypatch, tmp_path):
    original_connect = socket.socket.connect
    def local_only(sock, address):
        try:
            loopback = isinstance(address, tuple) and ipaddress.ip_address(address[0]).is_loopback
        except ValueError:
            loopback = False
        if loopback:
            return original_connect(sock, address)
        raise RuntimeError("External networking is disabled in root tests")
    monkeypatch.setattr(socket.socket, "connect", local_only)
    # Patch already-collected module instances, including the webhook's short import.
    for name in ("VOICE_TEAM.webhook.phone_bridge_direct", "phone_bridge_direct"):
        bridge = sys.modules.get(name)
        if bridge:
            monkeypatch.setattr(bridge, "_send_telegram_direct", lambda *a, **kw: "skipped:offline-test")
            monkeypatch.setattr(bridge, "_write_call_record", lambda *a, **kw: tmp_path / "record.json")
            monkeypatch.setattr(bridge, "PHONE_LINE_VOICEMAIL_EMAIL", "")
