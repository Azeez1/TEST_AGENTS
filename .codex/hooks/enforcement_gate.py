#!/usr/bin/env python3
"""Codex-native enforcement gate — the Codex twin of the Claude Code guardrails.

WHY THIS EXISTS
Claude Code runs 9 separate PowerShell gates keyed to tool names like "Bash"
and "Write", blocking with `exit 2`. Codex is different on three axes:
  1. Tool names — Codex calls shells `command_execution`/`local_shell` and edits
     `apply_patch`, NOT "Bash"/"Write". So tool-name matchers from Claude do not
     match in Codex.
  2. Block contract — Codex blocks with `print({"error": ...})` + `exit 1`
     (see claude_boundary_gate.py), not `exit 2`.
  3. Wiring — this gate is registered with matcher "*" so it sees every tool
     call and classifies it itself (same approach as claude_boundary_gate.py).

So instead of porting 9 PowerShell files that would never fire, we consolidate
the SAME rules + the SAME override tokens into this one Codex-native gate.

COVERAGE vs the Claude gates:
  - secret_scan, destructive_bash, money_rule, deploy_approval, voice_deploy,
    proposal_placeholder  -> enforced here.
  - financial_approval, team_email, api_cost -> NOT here. Those gate specific
    MCP tools (Gmail send, Drive upload, marketing-tools generate_*) that do not
    exist in the Codex runtime, so there is nothing to gate.

Fail OPEN on any internal error (a broken gate must never wedge Codex).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "LOGS" / "codex-enforcement.log"

# --- tool classification -----------------------------------------------------
SHELL_TOOLS = {
    "bash", "shell", "shell_command", "powershell", "local_shell",
    "command_execution", "exec", "functions.shell_command", "container.exec",
}
WRITE_TOOLS = {
    "write", "edit", "multiedit", "notebookedit",
    "apply_patch", "functions.apply_patch",
}


def is_shell(tool: str) -> bool:
    return tool in SHELL_TOOLS or any(k in tool for k in ("shell", "bash", "command", "exec"))


def is_write(tool: str) -> bool:
    return tool in WRITE_TOOLS or any(k in tool for k in ("write", "edit", "patch", "notebook"))


# --- rule tables (regex, reason). Case-insensitive. --------------------------
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
    (r"\bmkfs", "mkfs (formats a filesystem)"),
    (r"dd\s+if=", "dd (raw disk write)"),
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
VOICE = [
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
SAFE = [
    r"os\.getenv\(", r"process\.env\.", r"\$\{[A-Z_]+\}", r"\$env:",
    r"your[_\-].*[_\-]here", r"placeholder", r"example", r"xxxx",
]
PLACEHOLDERS = [
    r"\[PLACEHOLDER\]?", r"\[USER\s*VERIFY\]?", r"\bTKTK\b", r"<FILL[_\s-]*IN>",
    r"\bTBD\b", r"lorem\s+ipsum", r"\[INSERT[^\]]*\]", r"\bXXXX\b",
]


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


def safe_context(blob: str, value: str) -> bool:
    idx = blob.find(value)
    if idx < 0:
        return False
    window = blob[max(0, idx - 60): idx + len(value) + 120]
    return any(re.search(s, window, re.IGNORECASE) for s in SAFE)


def log(verdict: str, detail: str) -> None:
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(f"[{verdict}] {detail}\n")
    except OSError:
        pass


def block(token: str | None, reason: str) -> None:
    hint = f" To proceed, a human must add the token {token} to the command/content." if token else ""
    print(json.dumps({"error": f"Blocked by Codex enforcement gate: {reason}.{hint}"}))
    sys.exit(1)


def main() -> None:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        sys.exit(0)

    tool = str(payload.get("tool_name") or payload.get("tool") or "").lower()
    raw_input = payload.get("tool_input")
    if raw_input is None:
        raw_input = payload.get("input") or {}
    tool_input = raw_input if isinstance(raw_input, dict) else {}

    blob = json.dumps(raw_input, default=str)

    def has_token(token: str) -> bool:
        return token in blob

    # ---- shell-like tools: destructive / money / deploy / voice ----
    if is_shell(tool):
        command = str(tool_input.get("command") or "")
        if not command and isinstance(raw_input, str):
            command = raw_input
        if not command:
            command = " ".join(iter_strings(raw_input))

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

        reason = first_match(command, VOICE)
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

    # ---- write-like tools: secrets / proposal placeholders ----
    if is_write(tool):
        # secret scan over the whole input blob
        for pattern, label in SECRETS:
            for m in re.findall(pattern, blob):
                value = m if isinstance(m, str) else (m[0] if m else "")
                if value and not safe_context(blob, value):
                    log("BLOCK", f"secret: {label}")
                    block(None, f"hardcoded {label} detected — put secrets in .env / env vars")

        # proposal placeholder scan on final PROPOSAL_TEAM deliverables
        path = str(tool_input.get("file_path") or tool_input.get("path") or "")
        norm = path.replace("\\", "/")
        is_final = "PROPOSAL_TEAM" in norm and (
            re.search(r"(?i)final|submit|deliverable", norm)
            or re.search(r"(?i)PROPOSAL_TEAM/outputs/.*proposal", norm)
        )
        if is_final and not has_token("[[DRAFT-OK]]"):
            content = " ".join(iter_strings(raw_input))
            reason = first_match(content, [(p, p) for p in PLACEHOLDERS])
            if reason:
                log("BLOCK", f"placeholder in final: {reason}")
                block("[[DRAFT-OK]]", "final proposal still contains drafting markers (e.g. [PLACEHOLDER])")

    sys.exit(0)


if __name__ == "__main__":
    main()
