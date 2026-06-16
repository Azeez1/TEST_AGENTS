#!/usr/bin/env python3
"""Codex-native enforcement gate.

This hook is intentionally wired with matcher "*" in .codex/hooks.json. Codex
tool names differ from Claude-side tool names, so the gate classifies each tool
call itself and blocks with a Codex-compatible JSON error plus exit code 1.

Fail open on internal errors. A broken guardrail should not wedge the session.
"""
from __future__ import annotations

from datetime import date, datetime
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HOOK_DIR = Path(__file__).resolve().parent
LOG_DIR = Path.home() / ".codex" / "test_agents_hooks"
LOG = LOG_DIR / "codex-enforcement.log"
DO_NOT_EMAIL = HOOK_DIR / "config" / "do_not_email.txt"

DAILY_API_BUDGET = 50.0
WARN_API_SPEND_AT = 10.0
DAILY_EMAIL_LIMIT = 50

SHELL_TOOLS = {
    "bash",
    "shell",
    "shell_command",
    "powershell",
    "local_shell",
    "command_execution",
    "exec",
    "functions.shell_command",
    "container.exec",
}
WRITE_TOOLS = {
    "write",
    "edit",
    "multiedit",
    "notebookedit",
    "apply_patch",
    "functions.apply_patch",
}

DESTRUCTIVE = [
    (r"rm\s+(-[a-z]*r[a-z]*f|-[a-z]*f[a-z]*r|--recursive\s+--force)", "recursive force delete (rm -rf)"),
    (r"Remove-Item\b.*-Recurse\b.*-Force\b", "recursive force delete (Remove-Item)"),
    (r"Remove-Item\b.*-Force\b.*-Recurse\b", "recursive force delete (Remove-Item)"),
    (r"\brmdir\s+/s", "recursive directory delete (rmdir /s)"),
    (r"git\s+reset\s+--hard", "git reset --hard"),
    (r"git\s+push\b.*(--force\b|-f\b|--force-with-lease)", "git force-push"),
    (r"git\s+clean\s+-[a-z]*f", "git clean -f"),
    (r"\bDROP\s+(TABLE|DATABASE|SCHEMA)\b", "SQL DROP"),
    (r"\bTRUNCATE\s+TABLE\b", "SQL TRUNCATE"),
    (r"kubectl\s+delete\b", "kubectl delete"),
    (r"docker\s+(rm|rmi)\s+-[a-z]*f", "docker force remove"),
    (r"docker\s+system\s+prune", "docker system prune"),
    (r"\bmkfs", "mkfs"),
    (r"dd\s+if=", "dd raw disk write"),
]
MONEY = [
    (r"\bplace_order\b", "place_order"),
    (r"\bsubmit_order\b", "submit_order"),
    (r"\bcreate_order\b", "create_order"),
    (r"\bexecute_trade\b", "execute_trade"),
    (r"\blive_trading\s*=\s*True", "live_trading enabled"),
    (r"\bsend_wire\b", "wire transfer"),
    (r"\bwire_transfer\b", "wire transfer"),
    (r"\btransfer_funds\b", "funds transfer"),
    (r"\bbroker\.(buy|sell|order|trade)\b", "broker order method"),
    (r"ib_insync", "Interactive Brokers order client"),
    (r"ccxt.*create_order", "ccxt exchange order"),
    (r"alpaca.*\b(order|buy|sell)\b", "Alpaca order"),
]
DEPLOY = [
    (r"terraform\s+apply", "terraform apply"),
    (r"terraform\s+destroy", "terraform destroy"),
    (r"helm\s+(upgrade|install)", "helm release"),
    (r"kubectl\s+apply", "kubectl apply"),
    (r"kubectl\s+rollout", "kubectl rollout"),
    (r"serverless\s+deploy", "serverless deploy"),
    (r"\brender\b.*deploy", "Render deploy"),
    (r"pulumi\s+up", "pulumi up"),
    (r"gcloud\s+(run\s+deploy|app\s+deploy)", "gcloud deploy"),
    (r"aws\s+cloudformation\s+(deploy|create-stack|update-stack)", "CloudFormation deploy"),
]
VOICE_DEPLOY = [
    (r"cascading[_\s-]*deploy", "cascading deploy"),
    (r"deploy.*\bretell\b", "Retell deploy"),
    (r"\bretell\b.*deploy", "Retell deploy"),
    (r"voice[_\s-]*deploy", "voice deploy"),
    (r"deploy[_\s-]*voice", "voice deploy"),
    (r"publish[_\s-]*agent", "publish voice agent"),
    (r"phone_number.*(attach|assign|buy)", "attach/buy phone number"),
    (r"go[_\s-]*live", "go-live command"),
]
SECRETS = [
    (r"sk-[a-zA-Z0-9]{20,}", "OpenAI API key"),
    (r"pplx-[a-zA-Z0-9]{20,}", "Perplexity API key"),
    (r"GOCSPX-[a-zA-Z0-9_\-]+", "Google OAuth secret"),
    (r"eyJ[a-zA-Z0-9_\-]{30,}\.[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+", "JWT token"),
    (r"ghp_[a-zA-Z0-9]{36,}", "GitHub PAT"),
    (r"github_pat_[a-zA-Z0-9_]{20,}", "GitHub fine-grained PAT"),
    (r"xai-[a-zA-Z0-9]{20,}", "xAI API key"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key ID"),
    (r"AIza[0-9A-Za-z_\-]{35}", "Google API key"),
]
SAFE_SECRET_CONTEXT = [
    r"os\.getenv\(",
    r"process\.env\.",
    r"\$\{[A-Z_]+\}",
    r"\$env:",
    r"your[_\-].*[_\-]here",
    r"placeholder",
    r"example",
    r"xxxx",
]
PLACEHOLDERS = [
    r"\[PLACEHOLDER\]?",
    r"\[USER\s*VERIFY\]?",
    r"\bTKTK\b",
    r"<FILL[_\s-]*IN>",
    r"\bTBD\b",
    r"lorem\s+ipsum",
    r"\[INSERT[^\]]*\]",
    r"\bXXXX\b",
]
FINANCIAL_DELIVERABLES = [
    (r"valuation", "valuation"),
    (r"dcf\b", "DCF"),
    (r"discounted cash", "discounted cash flow"),
    (r"deal memo", "deal memo"),
    (r"deal\s*model", "deal model"),
    (r"board\s*deck", "board deck"),
    (r"board\s*presentation", "board presentation"),
    (r"term\s*sheet", "term sheet"),
    (r"cap\s*table", "cap table"),
    (r"forecast\s*model", "forecast model"),
    (r"lbo\b", "LBO"),
    (r"precedent\s*transaction", "precedent transaction"),
    (r"comparable\s*compan", "comparable company"),
    (r"purchase\s*price", "purchase price"),
    (r"investment\s*memo", "investment memo"),
    (r"fundrais", "fundraising"),
    (r"investor\s*deck", "investor deck"),
]
FORBIDDEN_VOICE_TERMS = [
    "retell",
    "retellai",
    "dashboard.retellai",
    "gpt-realtime",
    "openai-realtime",
    "11labs",
    "elevenlabs",
    "cartesia",
    "minimax",
    "deepgram",
    "twilio",
]
VOICE_REQUIRED_SECTIONS = ["Caller", "Incident", "Action Required"]
API_COST = {
    "mcp__marketing_tools__generate_sora_video": 8.0,
    "mcp__marketing_tools__generate_veo_ugc_from_image": 6.0,
    "mcp__marketing_tools__generate_veo_text_to_video": 6.0,
    "mcp__marketing_tools__generate_kling_video": 4.0,
    "mcp__marketing_tools__generate_seedance_video": 4.0,
    "mcp__marketing_tools__generate_video_with_fallback": 6.0,
    "mcp__marketing_tools__generate_gpt4o_image": 0.17,
    "mcp__marketing_tools__generate_nano_banana_image": 0.14,
    "mcp__marketing_tools__generate_nano_banana_2_image": 0.14,
    "mcp__marketing_tools__generate_image_with_fallback": 0.17,
}


def normalize_tool(tool: str) -> str:
    return tool.lower().replace("-", "_").replace(".", "__")


def is_shell(tool: str) -> bool:
    normalized = normalize_tool(tool)
    return normalized in SHELL_TOOLS or any(key in normalized for key in ("shell", "bash", "command", "exec"))


def is_write(tool: str) -> bool:
    normalized = normalize_tool(tool)
    return normalized in WRITE_TOOLS or any(key in normalized for key in ("write", "edit", "patch", "notebook"))


def is_gmail_send(tool: str) -> bool:
    normalized = normalize_tool(tool)
    return "send_gmail_message" in normalized or ("gmail" in normalized and "send" in normalized)


def is_drive_create(tool: str) -> bool:
    normalized = normalize_tool(tool)
    return (
        "create_drive_file" in normalized
        or ("upload" in normalized and "drive" in normalized)
        or "import_document" in normalized
        or "import_spreadsheet" in normalized
        or ("create_file" in normalized and ("drive" in normalized or "google" in normalized))
    )


def is_marketing_generation(tool: str) -> bool:
    return normalize_tool(tool).startswith("mcp__marketing_tools__generate_")


def first_match(text: str, table: list[tuple[str, str]]) -> str | None:
    for pattern, reason in table:
        if re.search(pattern, text, re.IGNORECASE):
            return reason
    return None


def iter_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        out: list[str] = []
        for item in value.values():
            out.extend(iter_strings(item))
        return out
    if isinstance(value, list):
        out = []
        for item in value:
            out.extend(iter_strings(item))
        return out
    return []


def input_text(value: Any) -> str:
    return "\n".join(iter_strings(value))


def safe_secret_context(blob: str, value: str) -> bool:
    idx = blob.find(value)
    if idx < 0:
        return False
    window = blob[max(0, idx - 60): idx + len(value) + 120]
    return any(re.search(pattern, window, re.IGNORECASE) for pattern in SAFE_SECRET_CONTEXT)


def append_log(path: Path, line: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line.rstrip() + "\n")
    except OSError:
        pass


def log(verdict: str, detail: str) -> None:
    append_log(LOG, f"[{verdict}] {detail}")


def block(token: str | None, reason: str) -> None:
    hint = f" To proceed, a human must add the token {token} to the command/content." if token else ""
    print(json.dumps({"error": f"Blocked by Codex enforcement gate: {reason}.{hint}"}))
    sys.exit(1)


def get_field(tool_input: dict[str, Any], *names: str) -> str:
    for name in names:
        value = tool_input.get(name)
        if value is None:
            continue
        if isinstance(value, list):
            return ", ".join(str(item) for item in value)
        return str(value)
    return ""


def load_do_not_email() -> list[str]:
    try:
        if not DO_NOT_EMAIL.exists():
            return []
        return [
            line.strip().lower()
            for line in DO_NOT_EMAIL.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
    except OSError:
        return []


def enforce_api_cost(tool: str, blob: str) -> None:
    if not is_marketing_generation(tool):
        return

    normalized = normalize_tool(tool)
    estimate = API_COST.get(normalized, 6.0 if "video" in normalized else 0.17)
    today = date.today().isoformat()
    spend_file = LOG_DIR / f"api-spend-{today}.total"
    spent = 0.0
    try:
        if spend_file.exists():
            spent = float(spend_file.read_text(encoding="utf-8").strip() or "0")
    except (OSError, ValueError):
        spent = 0.0

    projected = spent + estimate
    has_override = "[[SPEND-APPROVED]]" in blob
    ts = datetime.now().isoformat()
    if projected > DAILY_API_BUDGET and not has_override:
        append_log(LOG_DIR / "api-spend.log", f"[{ts}] [BLOCK] {normalized} est=${estimate} spent=${spent}")
        block("[[SPEND-APPROVED]]", f"paid generation would exceed today's ${DAILY_API_BUDGET:.0f} budget")

    try:
        spend_file.parent.mkdir(parents=True, exist_ok=True)
        spend_file.write_text(str(round(projected, 4)), encoding="utf-8")
    except OSError:
        pass
    tag = "OVERRIDE" if has_override else "OK"
    append_log(LOG_DIR / "api-spend.log", f"[{ts}] [{tag}] {normalized} est=${estimate} running=${round(projected, 2)}")
    if projected >= WARN_API_SPEND_AT:
        log("WARN", f"api spend is about ${round(projected, 2)} today")


def enforce_team_email(tool: str, tool_input: dict[str, Any], blob: str) -> None:
    if not is_gmail_send(tool):
        return

    to_value = get_field(tool_input, "to", "recipient", "recipients", "email")
    subject = get_field(tool_input, "subject")
    body = get_field(tool_input, "body", "message", "html", "text")
    ts = datetime.now().isoformat()

    lowered_to = to_value.lower()
    for blocked in load_do_not_email():
        if blocked and blocked in lowered_to:
            append_log(LOG_DIR / "team-email.log", f"[{ts}] [BLOCK] do-not-email match '{blocked}' -> {to_value}")
            block(None, f"recipient is on the Do-Not-Email list ({blocked})")

    if not subject.strip():
        append_log(LOG_DIR / "team-email.log", f"[{ts}] [BLOCK] empty subject -> {to_value}")
        block(None, "email send has an empty subject")

    today = date.today().isoformat()
    count_file = LOG_DIR / f"email-sends-{today}.count"
    count = 0
    try:
        if count_file.exists():
            count = int(count_file.read_text(encoding="utf-8").strip() or "0")
    except (OSError, ValueError):
        count = 0

    has_override = "[[BULK-APPROVED]]" in body or "[[BULK-APPROVED]]" in blob
    if count >= DAILY_EMAIL_LIMIT and not has_override:
        append_log(LOG_DIR / "team-email.log", f"[{ts}] [BLOCK] daily limit {DAILY_EMAIL_LIMIT} reached ({count}) -> {to_value}")
        block("[[BULK-APPROVED]]", f"daily send limit ({DAILY_EMAIL_LIMIT}) reached")

    try:
        count_file.parent.mkdir(parents=True, exist_ok=True)
        count_file.write_text(str(count + 1), encoding="utf-8")
    except OSError:
        pass


def is_voice_email(subject: str, body: str) -> bool:
    if not subject or not body:
        return False
    if not re.search(r"^\[[^\]]+\]", subject):
        return False
    lowered = body.lower()
    return any(term in lowered for term in ("ai intake", "voice receptionist", "ai receptionist", "inbound call", "new intake"))


def enforce_voice_email(tool: str, tool_input: dict[str, Any]) -> None:
    if not is_gmail_send(tool):
        return

    subject = get_field(tool_input, "subject")
    body = get_field(tool_input, "body", "message", "html", "text")
    if not is_voice_email(subject, body):
        return

    violations: list[str] = []
    combined = f"{subject}\n{body}".lower()
    for term in FORBIDDEN_VOICE_TERMS:
        if term in combined:
            violations.append(f"contains forbidden vendor term '{term}'")
            break
    for section in VOICE_REQUIRED_SECTIONS:
        if section.lower() not in body.lower():
            violations.append(f"body missing required section '{section}'")

    if violations:
        ts = datetime.now().isoformat()
        append_log(LOG_DIR / "voice-email-violations.log", f"[{ts}] [BLOCK] {subject} | {'; '.join(violations)}")
        block(None, "voice-team email violates white-label or required-section rules")


def enforce_financial_approval(tool: str, raw_input: Any, command: str, blob: str) -> None:
    outbound = is_gmail_send(tool) or is_drive_create(tool) or ("upload_to_drive" in command.lower())
    if not outbound:
        return

    reason = first_match(input_text(raw_input), FINANCIAL_DELIVERABLES)
    if not reason:
        return

    ts = datetime.now().isoformat()
    normalized = normalize_tool(tool)
    if "[[CFO-APPROVED]]" in blob:
        append_log(LOG_DIR / "financial-approval.log", f"[{ts}] [OVERRIDE] {normalized} | {reason}")
        return
    append_log(LOG_DIR / "financial-approval.log", f"[{ts}] [BLOCK] {normalized} | {reason}")
    block("[[CFO-APPROVED]]", f"financial deliverable is leaving the system without CFO sign-off ({reason})")


def extract_command(raw_input: Any, tool_input: dict[str, Any]) -> str:
    command = str(tool_input.get("command") or "")
    if not command and isinstance(raw_input, str):
        command = raw_input
    if not command:
        command = " ".join(iter_strings(raw_input))
    return command


def main() -> None:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        sys.exit(0)

    try:
        tool = str(payload.get("tool_name") or payload.get("tool") or "")
        raw_input = payload.get("tool_input")
        if raw_input is None:
            raw_input = payload.get("input") or {}
        tool_input = raw_input if isinstance(raw_input, dict) else {}
        blob = json.dumps(raw_input, default=str)
        command = extract_command(raw_input, tool_input)

        def has_token(token: str) -> bool:
            return token in blob

        enforce_api_cost(tool, blob)
        enforce_team_email(tool, tool_input, blob)
        enforce_voice_email(tool, tool_input)
        enforce_financial_approval(tool, raw_input, command, blob)

        if is_shell(tool):
            reason = first_match(command, DESTRUCTIVE)
            if reason:
                if has_token("[[CONFIRM-DESTRUCTIVE]]"):
                    log("OVERRIDE", f"destructive: {reason}")
                else:
                    log("BLOCK", f"destructive: {reason} | {command[:200]}")
                    block("[[CONFIRM-DESTRUCTIVE]]", f"destructive command ({reason})")

            reason = first_match(command, MONEY)
            if reason:
                if has_token("[[MONEY-APPROVED]]"):
                    log("OVERRIDE", f"money: {reason}")
                else:
                    log("BLOCK", f"money: {reason} | {command[:200]}")
                    block("[[MONEY-APPROVED]]", f"this moves money / executes a trade ({reason})")

            reason = first_match(command, VOICE_DEPLOY)
            if reason:
                if has_token("[[VOICE-DEPLOY-APPROVED]]"):
                    log("OVERRIDE", f"voice: {reason}")
                else:
                    log("BLOCK", f"voice: {reason} | {command[:200]}")
                    block("[[VOICE-DEPLOY-APPROVED]]", f"this puts a voice agent live ({reason})")

            reason = first_match(command, DEPLOY)
            if reason:
                if has_token("[[DEPLOY-APPROVED]]"):
                    log("OVERRIDE", f"deploy: {reason}")
                else:
                    log("BLOCK", f"deploy: {reason} | {command[:200]}")
                    block("[[DEPLOY-APPROVED]]", f"infrastructure deploy ({reason})")

        if is_write(tool):
            reason = first_match(input_text(raw_input), MONEY)
            if reason:
                if has_token("[[MONEY-APPROVED]]"):
                    log("OVERRIDE", f"money-write: {reason}")
                else:
                    log("BLOCK", f"money-write: {reason}")
                    block("[[MONEY-APPROVED]]", f"write contains money movement / trade execution code ({reason})")

            for pattern, label in SECRETS:
                for match in re.findall(pattern, blob):
                    value = match if isinstance(match, str) else (match[0] if match else "")
                    if value and not safe_secret_context(blob, value):
                        log("BLOCK", f"secret: {label}")
                        block(None, f"hardcoded {label} detected; put secrets in environment variables")

            path = str(tool_input.get("file_path") or tool_input.get("path") or "")
            norm_path = path.replace("\\", "/")
            is_final = "PROPOSAL_TEAM" in norm_path and (
                re.search(r"(?i)final|submit|deliverable", norm_path)
                or re.search(r"(?i)PROPOSAL_TEAM/outputs/.*proposal", norm_path)
            )
            if is_final and not has_token("[[DRAFT-OK]]"):
                reason = first_match(input_text(raw_input), [(pattern, pattern) for pattern in PLACEHOLDERS])
                if reason:
                    log("BLOCK", f"placeholder in final: {reason}")
                    block("[[DRAFT-OK]]", "final proposal still contains drafting markers")

    except SystemExit:
        raise
    except Exception as exc:
        log("ERROR", f"failing open: {exc}")

    sys.exit(0)


if __name__ == "__main__":
    main()
