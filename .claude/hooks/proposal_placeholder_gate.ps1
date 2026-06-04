# Proposal Placeholder Gate
#
# PreToolUse hook for Write|Edit.
# A government/RFP deliverable must never ship with internal scaffolding still
# in it: [PLACEHOLDER], [USER VERIFY], TKTK, TODO, <FILL IN>, lorem ipsum.
# rfp-agent writes these as drafting markers; this blocks them from surviving
# into a file named like a final deliverable inside PROPOSAL_TEAM.
#
# Wired in .claude/settings.json under hooks.PreToolUse.

$ErrorActionPreference = "Stop"
$ENFORCE_MODE = $true

$VIOLATIONS_LOG = Join-Path $PSScriptRoot "..\..\LOGS\proposal-placeholder.log"
$OVERRIDE_TOKEN = "[[DRAFT-OK]]"   # use when intentionally saving a work-in-progress draft

# Marker patterns that must not survive to a final deliverable.
$MARKERS = @(
    '\[PLACEHOLDER\]?', '\[USER\s*VERIFY\]?', '\bTKTK\b', '<FILL[_\s-]*IN>',
    '\bTBD\b', 'lorem\s+ipsum', '\[INSERT[^\]]*\]', '\bXXXX\b'
)

# Only gate files that look like a FINAL deliverable inside PROPOSAL_TEAM.
function Test-FinalDeliverable($path) {
    if (-not $path) { return $false }
    $p = $path -replace '\\', '/'
    if ($p -notmatch 'PROPOSAL_TEAM') { return $false }
    # final-looking name OR a proposal section/body file under outputs
    if ($p -match '(?i)final|submit|deliverable') { return $true }
    if ($p -match '(?i)PROPOSAL_TEAM/outputs/.*proposal') { return $true }
    return $false
}

try {
    $stdin = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($stdin)) { exit 0 }
    $payload = $stdin | ConvertFrom-Json
    if (@("Write", "Edit", "MultiEdit") -notcontains $payload.tool_name) { exit 0 }

    $path = $payload.tool_input.file_path
    if (-not (Test-FinalDeliverable $path)) { exit 0 }

    $content = ""
    if ($payload.tool_input.content)    { $content += $payload.tool_input.content }
    if ($payload.tool_input.new_string) { $content += "`n" + $payload.tool_input.new_string }
    if ([string]::IsNullOrWhiteSpace($content)) { exit 0 }

    if ($content.Contains($OVERRIDE_TOKEN)) { exit 0 }

    $hits = @()
    foreach ($m in $MARKERS) {
        if ([regex]::IsMatch($content, $m, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)) { $hits += $m }
    }
    if ($hits.Count -eq 0) { exit 0 }

    $ts = (Get-Date).ToString("o")
    $logDir = Split-Path $VIOLATIONS_LOG -Parent
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
    Add-Content -Path $VIOLATIONS_LOG -Value "[$ts] [BLOCK] $path | unresolved markers: $($hits -join ', ')"

    [Console]::Error.WriteLine("PROPOSAL_PLACEHOLDER_GATE: final deliverable still contains drafting markers:")
    foreach ($h in $hits) { [Console]::Error.WriteLine("  - $h") }
    if ($ENFORCE_MODE) {
        [Console]::Error.WriteLine("  Resolve every marker before saving the final. To save an intentional draft, add $OVERRIDE_TOKEN.")
        exit 2
    }
    exit 0
}
catch {
    [Console]::Error.WriteLine("PROPOSAL_PLACEHOLDER_GATE: hook error (failing open): $($_.Exception.Message)")
    exit 0
}
