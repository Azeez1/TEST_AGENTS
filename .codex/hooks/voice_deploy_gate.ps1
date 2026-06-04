# Voice Deploy Gate
#
# PreToolUse hook for Bash|PowerShell.
# Putting a voice agent LIVE means real callers and real telephony spend.
# voice-deployer must not flip a firm to production without a human go-ahead.
#
# Detects voice deploy commands (Retell deploy, cascading deploy scripts) and
# blocks unless the human appends [[VOICE-DEPLOY-APPROVED]].
#
# Wired in .claude/settings.json under hooks.PreToolUse.

$ErrorActionPreference = "Stop"
$ENFORCE_MODE = $true

$VIOLATIONS_LOG = Join-Path $PSScriptRoot "..\..\LOGS\voice-deploy.log"
$OVERRIDE_TOKEN = "[[VOICE-DEPLOY-APPROVED]]"

# Command shapes that mean "go live" (case-insensitive).
$DEPLOY_PATTERNS = @(
    @{ rx = 'cascading[_\s-]*deploy';            why = "cascading deploy script" },
    @{ rx = 'deploy.*\bretell\b';                why = "Retell deploy" },
    @{ rx = '\bretell\b.*deploy';                why = "Retell deploy" },
    @{ rx = 'voice[_\s-]*deploy';                why = "voice deploy" },
    @{ rx = 'deploy[_\s-]*voice';                why = "voice deploy" },
    @{ rx = 'publish[_\s-]*agent';               why = "publish voice agent" },
    @{ rx = 'phone_number.*(attach|assign|buy)'; why = "attach/buy phone number" },
    @{ rx = 'go[_\s-]*live';                     why = "go-live command" }
)

try {
    $stdin = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($stdin)) { exit 0 }
    $payload = $stdin | ConvertFrom-Json
    if (@("Bash", "PowerShell") -notcontains $payload.tool_name) { exit 0 }

    $cmd = $payload.tool_input.command
    if ([string]::IsNullOrWhiteSpace($cmd)) { exit 0 }

    $hits = @()
    foreach ($d in $DEPLOY_PATTERNS) {
        if ([regex]::IsMatch($cmd, $d.rx, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)) { $hits += $d.why }
    }
    if ($hits.Count -eq 0) { exit 0 }

    $ts = (Get-Date).ToString("o")
    $logDir = Split-Path $VIOLATIONS_LOG -Parent
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

    $hasOverride = $cmd.Contains($OVERRIDE_TOKEN)
    $verdict = if ($hasOverride) { "OVERRIDE" } else { "BLOCK" }
    Add-Content -Path $VIOLATIONS_LOG -Value "[$ts] [$verdict] $($hits -join '; ') | $cmd"

    if ($hasOverride) {
        [Console]::Error.WriteLine("VOICE_DEPLOY_GATE: deploy approval token present - allowing.")
        exit 0
    }
    [Console]::Error.WriteLine("VOICE_DEPLOY_GATE: this puts a voice agent LIVE (real callers + telephony cost).")
    foreach ($h in $hits) { [Console]::Error.WriteLine("  - $h") }
    if ($ENFORCE_MODE) {
        [Console]::Error.WriteLine("  Confirm the firm config is tested, then add $OVERRIDE_TOKEN to the command and retry.")
        exit 2
    }
    exit 0
}
catch {
    [Console]::Error.WriteLine("VOICE_DEPLOY_GATE: hook error (failing open): $($_.Exception.Message)")
    exit 0
}
