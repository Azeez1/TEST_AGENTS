# Financial Approval Gate
#
# PreToolUse hook for outbound financial deliverables:
#   - mcp__google-workspace__send_gmail_message  (emailing a valuation/deal/deck)
#   - Bash  (upload_to_drive.py of a financial artifact)
#   - mcp__google-workspace__create_drive_file
#
# A valuation, deal memo, board deck, term sheet, or forecast model must NOT
# leave the system without CFO sign-off. Enforces the FINANCIAL_TEAM approval
# rule that previously lived only as the dormant `financial-guard` skill.
#
# Override: human appends [[CFO-APPROVED]] once sign-off is real.
# Wired in .claude/settings.json under hooks.PreToolUse.

$ErrorActionPreference = "Stop"
$ENFORCE_MODE = $true

$VIOLATIONS_LOG = Join-Path $PSScriptRoot "..\..\LOGS\financial-approval.log"
$OVERRIDE_TOKEN = "[[CFO-APPROVED]]"

# Keywords that mark a financial deliverable (case-insensitive).
$FIN_PATTERNS = @(
    'valuation', 'dcf\b', 'discounted cash', 'deal memo', 'deal\s*model',
    'board\s*deck', 'board\s*presentation', 'term\s*sheet', 'cap\s*table',
    'forecast\s*model', 'lbo\b', 'precedent\s*transaction', 'comparable\s*compan',
    'purchase\s*price', 'investment\s*memo', 'fundrais', 'investor\s*deck'
)

try {
    $stdin = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($stdin)) { exit 0 }
    $payload = $stdin | ConvertFrom-Json
    $tool = $payload.tool_name

    $relevant = @("mcp__google-workspace__send_gmail_message",
                  "mcp__google-workspace__create_drive_file", "Bash")
    if ($relevant -notcontains $tool) { exit 0 }

    # Gather the text we should inspect, per tool shape.
    $text = ""
    if ($tool -eq "mcp__google-workspace__send_gmail_message") {
        $text = "$($payload.tool_input.subject) `n $($payload.tool_input.body) `n $($payload.tool_input.attachments)"
    }
    elseif ($tool -eq "mcp__google-workspace__create_drive_file") {
        $text = "$($payload.tool_input.file_name) `n $($payload.tool_input.name) `n $($payload.tool_input.content)"
    }
    elseif ($tool -eq "Bash") {
        $cmd = $payload.tool_input.command
        # Only care about Bash that uploads to Drive
        if (-not $cmd -or $cmd -notmatch 'upload_to_drive') { exit 0 }
        $text = $cmd
    }
    if ([string]::IsNullOrWhiteSpace($text)) { exit 0 }

    # Must look financial to be in scope.
    $matched = $false
    foreach ($p in $FIN_PATTERNS) {
        if ([regex]::IsMatch($text, $p, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)) { $matched = $true; break }
    }
    if (-not $matched) { exit 0 }

    $ts = (Get-Date).ToString("o")
    $logDir = Split-Path $VIOLATIONS_LOG -Parent
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

    $hasOverride = ($payload.tool_input | ConvertTo-Json -Depth 8 -Compress).Contains($OVERRIDE_TOKEN)
    $verdict = if ($hasOverride) { "OVERRIDE" } else { "BLOCK" }
    Add-Content -Path $VIOLATIONS_LOG -Value "[$ts] [$verdict] $tool | financial deliverable outbound"

    if ($hasOverride) {
        [Console]::Error.WriteLine("FINANCIAL_APPROVAL_GATE: CFO approval token present - allowing.")
        exit 0
    }
    [Console]::Error.WriteLine("FINANCIAL_APPROVAL_GATE: financial deliverable leaving the system without CFO sign-off.")
    [Console]::Error.WriteLine("  Valuations / deal models / board decks need a human CFO review first.")
    if ($ENFORCE_MODE) {
        [Console]::Error.WriteLine("  Get sign-off, then add $OVERRIDE_TOKEN to the subject/body/command and retry.")
        exit 2
    }
    exit 0
}
catch {
    [Console]::Error.WriteLine("FINANCIAL_APPROVAL_GATE: hook error (failing open): $($_.Exception.Message)")
    exit 0
}
