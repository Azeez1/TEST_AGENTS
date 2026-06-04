# Team Email Gate
#
# PreToolUse hook for mcp__google-workspace__send_gmail_message.
# Covers MARKETING_TEAM + SALES_TEAM outreach (voice_email_gate only covers
# VOICE_TEAM). Three protections:
#   1. Do-Not-Email blocklist  (.claude/hooks/config/do_not_email.txt)  -> hard block
#   2. Daily send rate limit                                            -> hard block over cap
#   3. Empty-subject guard (low-trust / accidental send)                -> hard block
#
# Override for an intentional bulk run: add [[BULK-APPROVED]] to the body.
# Co-runs with voice_email_gate; both fire on the same tool.
# Wired in .claude/settings.json under hooks.PreToolUse.

$ErrorActionPreference = "Stop"
$ENFORCE_MODE = $true

$DAILY_LIMIT    = 50
$BLOCKLIST_FILE = Join-Path $PSScriptRoot "config\do_not_email.txt"
$VIOLATIONS_LOG = Join-Path $PSScriptRoot "..\..\LOGS\team-email.log"
$COUNT_DIR      = Join-Path $PSScriptRoot "..\..\LOGS"
$OVERRIDE_TOKEN = "[[BULK-APPROVED]]"

try {
    $stdin = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($stdin)) { exit 0 }
    $payload = $stdin | ConvertFrom-Json
    if ($payload.tool_name -ne "mcp__google-workspace__send_gmail_message") { exit 0 }

    $to      = "$($payload.tool_input.to)"
    $subject = "$($payload.tool_input.subject)"
    $body    = "$($payload.tool_input.body)"
    $hasOverride = $body.Contains($OVERRIDE_TOKEN)

    $logDir = Split-Path $VIOLATIONS_LOG -Parent
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
    $ts = (Get-Date).ToString("o")

    # --- 1. Blocklist (never overridable) ---
    if (Test-Path $BLOCKLIST_FILE) {
        $entries = Get-Content $BLOCKLIST_FILE | Where-Object { $_ -and -not $_.StartsWith("#") }
        foreach ($e in $entries) {
            $needle = $e.Trim().ToLower()
            if ($needle -and $to.ToLower().Contains($needle)) {
                Add-Content -Path $VIOLATIONS_LOG -Value "[$ts] [BLOCK] do-not-email match '$needle' -> $to"
                [Console]::Error.WriteLine("TEAM_EMAIL_GATE: recipient '$to' is on the Do-Not-Email list ('$needle').")
                [Console]::Error.WriteLine("  This block cannot be overridden. Remove them from the campaign.")
                if ($ENFORCE_MODE) { exit 2 } else { exit 0 }
            }
        }
    }

    # --- 2. Empty subject guard ---
    if ([string]::IsNullOrWhiteSpace($subject)) {
        Add-Content -Path $VIOLATIONS_LOG -Value "[$ts] [BLOCK] empty subject -> $to"
        [Console]::Error.WriteLine("TEAM_EMAIL_GATE: empty subject line. Add a real subject before sending.")
        if ($ENFORCE_MODE) { exit 2 } else { exit 0 }
    }

    # --- 3. Daily rate limit ---
    $today = (Get-Date).ToString("yyyy-MM-dd")
    $countFile = Join-Path $COUNT_DIR "email-sends-$today.count"
    $count = 0
    if (Test-Path $countFile) { $count = [int](Get-Content $countFile -Raw).Trim() }

    if ($count -ge $DAILY_LIMIT -and -not $hasOverride) {
        Add-Content -Path $VIOLATIONS_LOG -Value "[$ts] [BLOCK] daily limit $DAILY_LIMIT reached ($count) -> $to"
        [Console]::Error.WriteLine("TEAM_EMAIL_GATE: daily send limit ($DAILY_LIMIT) reached for $today.")
        [Console]::Error.WriteLine("  Protects domain reputation. For an approved bulk run, add $OVERRIDE_TOKEN to the body.")
        if ($ENFORCE_MODE) { exit 2 } else { exit 0 }
    }

    # Allowed - record the send.
    Set-Content -Path $countFile -Value ([string]($count + 1))
    if ($hasOverride -and $count -ge $DAILY_LIMIT) {
        Add-Content -Path $VIOLATIONS_LOG -Value "[$ts] [OVERRIDE] bulk approved past limit ($count) -> $to"
    }
    exit 0
}
catch {
    [Console]::Error.WriteLine("TEAM_EMAIL_GATE: hook error (failing open): $($_.Exception.Message)")
    exit 0
}
