

# --- Cross-service post-call execution (added 2026-06-11) -------------------
# The public TEST_AGENTS web service handles LIVE call turns (fast persona
# layer) and hands authorized POST-CALL execution here, where the full Hermes
# (memories, skills, Telegram delivery) lives. Secured by the shared secret.

from fastapi import Request  # late import; header imports left untouched


def _read_secret_file() -> str:
    try:
        return Path("/opt/data/phone_line/.secret").read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def _execute_post_call_job(call_id: str, transcript: str, metadata: dict[str, Any]) -> None:
    _write_call_record(call_id, transcript, authorized=True, metadata=metadata)
    ask_hermes(transcript, call_id, post_call=True, authorized=True)


@app.post("/post-call")
async def post_call_exec(req: Request):
    provided = req.headers.get("x-phone-line-secret", "")
    expected = PHONE_LINE_SHARED_SECRET or _read_secret_file()
    if not expected or provided != expected:
        return JSONResponse({"status": "unauthorized"}, status_code=401)
    body = await req.json()
    call_id = str(body.get("call_id") or "unknown")
    transcript = str(body.get("transcript") or "").strip()
    metadata = body.get("metadata") or {}
    if not body.get("authorized"):
        # Voicemail/untrusted content stays on the web service; this endpoint
        # only executes trusted, passcode-authorized instructions. 403 makes the
        # caller fall back to its own (sandboxed) local handling.
        return JSONResponse({"status": "rejected_unauthorized_content"}, status_code=403)
    if not transcript:
        return {"status": "empty"}
    asyncio.create_task(asyncio.to_thread(_execute_post_call_job, call_id, transcript, metadata))
    return {"status": "accepted"}
