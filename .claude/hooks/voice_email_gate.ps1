# Voice Email Gate
#
# PreToolUse hook for mcp__google-workspace__send_gmail_message.
# Blocks any email send if the subject or body contains forbidden vendor terms
# OR if a voice-agent intake email is missing required structural sections.
#
# Rationale:
#   - VOICE_TEAM emails are white-labelled as the firm's own intake system.
#   - Any leak of vendor names (Retell, openai-realtime, gpt-realtime-X,
#     ElevenLabs, etc.) breaks the white-label and weakens pricing leverage.
#   - Missing structural sections (Caller, Incident, Recording, Calendar,
#     Action Required) produce low-trust intake emails that the firm will
#     ignore — fail closed instead.
#
# Wired in .claude/settings.json under hooks.PreToolUse with matcher for
# the Gmail send tool.

$ErrorActionPreference = "Stop"

# --- TOGGLE -----------------------------------------------------------
# $true  = block violating sends with exit 2
# $false = WARN-only (log + stderr, allow)
$ENFORCE_MODE = $true

# --- Paths ------------------------------------------------------------
$VIOLATIONS_LOG = Join-Path $PSScriptRoot "..\..\LOGS\voice-email-violations.log"

# --- Forbidden term sets ----------------------------------------------
# Case-insensitive substrings. If any appear in subject or body, BLOCK.
$FORBIDDEN_VENDOR_TERMS = @(
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
    "twilio"
)

# Subject regex requirement. Voice-team emails MUST start with "[<FirmName>]".
$SUBJECT_PREFIX_PATTERN = '^\[[^\]]+\]'

# Required structural sections for a voice-intake summary email.
# These are markers we expect to see in the body. If any are missing, WARN
# (or BLOCK in enforce mode). Adjust per template evolution.
$REQUIRED_SECTIONS = @(
    "Caller",
    "Incident",
    "Action Required"
)

# --- Helpers ----------------------------------------------------------
function Find-ForbiddenTerm($text) {
    if (-not $text) { return $null }
    $low = $text.ToLower()
    foreach ($term in $FORBIDDEN_VENDOR_TERMS) {
        if ($low.Contains($term)) { return $term }
    }
    return $null
}

function Test-IsVoiceTeamEmail($subject, $body) {
    # Heuristic: subject starts with [SomeName] AND body looks like a
    # voice-intake template (mentions "AI Intake" or "Voice Receptionist" or
    # "Inbound call" in the body). Non-voice emails skip this gate entirely.
    if (-not $subject -or -not $body) { return $false }
    if ($subject -notmatch $SUBJECT_PREFIX_PATTERN) { return $false }
    $patterns = @("ai intake", "voice receptionist", "ai receptionist", "inbound call", "new intake")
    foreach ($p in $patterns) {
        if ($body.ToLower().Contains($p)) { return $true }
    }
    return $false
}

# --- Main -------------------------------------------------------------
try {
    $stdin = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($stdin)) { exit 0 }

    $payload = $stdin | ConvertFrom-Json

    # Only inspect the Gmail send tool
    if ($payload.tool_name -ne "mcp__google-workspace__send_gmail_message") { exit 0 }

    $subject = $payload.tool_input.subject
    $body    = $payload.tool_input.body

    # If it's not a voice-team intake email, this hook doesn't apply
    if (-not (Test-IsVoiceTeamEmail $subject $body)) { exit 0 }

    $violations = @()

    # Check 1: forbidden vendor terms in subject
    $vSubject = Find-ForbiddenTerm $subject
    if ($vSubject) {
        $violations += "Subject contains forbidden vendor term: '$vSubject'"
    }

    # Check 2: forbidden vendor terms in body
    $vBody = Find-ForbiddenTerm $body
    if ($vBody) {
        $violations += "Body contains forbidden vendor term: '$vBody' (breaks white-label)"
    }

    # Check 3: subject prefix
    if ($subject -notmatch $SUBJECT_PREFIX_PATTERN) {
        $violations += "Subject must start with '[<Firm Name>]' prefix. Got: '$subject'"
    }

    # Check 4: required sections present in body
    foreach ($section in $REQUIRED_SECTIONS) {
        if (-not $body.ToLower().Contains($section.ToLower())) {
            $violations += "Body missing required section: '$section'"
        }
    }

    if ($violations.Count -eq 0) { exit 0 }

    # Log + report
    $ts = (Get-Date).ToString("o")
    $logDir = Split-Path $VIOLATIONS_LOG -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    $verdictLabel = if ($ENFORCE_MODE) { "BLOCK" } else { "WARN" }
    $logEntry = "[$ts] [$verdictLabel] send_gmail_message subject='$subject'`n"
    foreach ($v in $violations) { $logEntry += "    - $v`n" }
    Add-Content -Path $VIOLATIONS_LOG -Value $logEntry

    [Console]::Error.WriteLine("VOICE_EMAIL_GATE: [$verdictLabel] $($violations.Count) violation(s)")
    foreach ($v in $violations) {
        [Console]::Error.WriteLine("  - $v")
    }

    if ($ENFORCE_MODE) {
        [Console]::Error.WriteLine("VOICE_EMAIL_GATE: ENFORCE_MODE is ON - blocking this send.")
        [Console]::Error.WriteLine("  Fix the email body / subject and retry. See LOGS/voice-email-violations.log for history.")
        exit 2
    }

    [Console]::Error.WriteLine("  (WARN-only mode - send allowed. Set `$ENFORCE_MODE to `$true to block.)")
    exit 0
}
catch {
    # Hook errors must never block the user. Fail open.
    [Console]::Error.WriteLine("VOICE_EMAIL_GATE: hook script error: $($_.Exception.Message)")
    exit 0
}
