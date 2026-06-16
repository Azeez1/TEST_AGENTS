# Proposal Tracker auto-trigger hook.
#
# Fires after Codex write-like tools when a .sbir_validation_<verdict> marker
# is created or modified. The Excel tracker is derived from proposal output
# files, so this hook refreshes it without blocking the tool call.

$ErrorActionPreference = "Stop"

$REPO_ROOT      = "C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS"
$TRACKER_LOG    = Join-Path $REPO_ROOT "LOGS\proposal-tracker.log"
$TRACKER_SCRIPT = Join-Path $REPO_ROOT "tools\proposal_tracker.py"

function Get-CandidatePath($payload) {
    $toolInput = $payload.tool_input
    if (-not $toolInput) { $toolInput = $payload.input }

    if ($toolInput -is [string]) {
        $m = [regex]::Match($toolInput, '(?m)^\*\*\* (?:Add|Update) File:\s+(.+?\.sbir_validation_(?:pass|conditional|fail))\s*$')
        if ($m.Success) { return $m.Groups[1].Value.Trim() }
        return ""
    }

    foreach ($field in @("file_path", "path", "target_path", "notebook_path")) {
        $value = [string]$toolInput.$field
        if (-not [string]::IsNullOrWhiteSpace($value)) { return $value }
    }

    return ""
}

try {
    $stdin = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($stdin)) { exit 0 }

    $payload = $stdin | ConvertFrom-Json
    $tool = [string]$payload.tool_name
    if (-not $tool) { $tool = [string]$payload.tool }
    $tool = $tool.ToLower()

    if ($tool -notmatch 'write|edit|patch|notebook') { exit 0 }

    $path = Get-CandidatePath $payload
    if ([string]::IsNullOrWhiteSpace($path)) { exit 0 }
    if ($path -notmatch '\.sbir_validation_(pass|conditional|fail)$') { exit 0 }

    $logDir = Split-Path $TRACKER_LOG -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    $ts = (Get-Date).ToString("o")
    Add-Content -Path $TRACKER_LOG -Value "[$ts] Validator marker write detected: $path"

    $output = & python $TRACKER_SCRIPT --quiet 2>&1
    $exit = $LASTEXITCODE

    Add-Content -Path $TRACKER_LOG -Value "[$ts] Tracker exit=$exit  $output"

    if ($exit -ne 0) {
        [Console]::Error.WriteLine("PROPOSAL_TRACKER: hook ran script but exit=$exit")
        [Console]::Error.WriteLine($output)
    }

    exit 0
}
catch {
    [Console]::Error.WriteLine("PROPOSAL_TRACKER hook error: $($_.Exception.Message)")
    exit 0
}
