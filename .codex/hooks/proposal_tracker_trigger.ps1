# Proposal Tracker auto-trigger hook
#
# Fires on PostToolUse Write to any .sbir_validation_<verdict> marker file.
# Re-runs tools/proposal_tracker.py to refresh PROPOSAL_TRACKER.xlsx.
#
# Source of truth = .md files in each PROPOSAL_TEAM/outputs/<topic_id>/ folder.
# Excel is derived. This hook keeps the Excel in sync with the latest validator state.
#
# Wired in .claude/settings.local.json under hooks.PostToolUse.

$ErrorActionPreference = "Stop"

$REPO_ROOT     = "C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS"
$TRACKER_LOG   = Join-Path $REPO_ROOT "LOGS\proposal-tracker.log"
$TRACKER_SCRIPT = Join-Path $REPO_ROOT "tools\proposal_tracker.py"

try {
    $stdin = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($stdin)) { exit 0 }

    $payload = $stdin | ConvertFrom-Json

    # Only fire on Write to a validator marker file
    if ($payload.tool_name -ne "Write") { exit 0 }

    $path = $payload.tool_input.file_path
    if ([string]::IsNullOrWhiteSpace($path)) { exit 0 }
    if ($path -notmatch '\.sbir_validation_(pass|conditional|fail)$') { exit 0 }

    # Ensure log dir exists
    $logDir = Split-Path $TRACKER_LOG -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    $ts = (Get-Date).ToString("o")
    Add-Content -Path $TRACKER_LOG -Value "[$ts] Validator marker write detected: $path"

    # Run the tracker script (Python)
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
    # Hook errors must NEVER block the user's tool call - fail open.
    [Console]::Error.WriteLine("PROPOSAL_TRACKER hook error: $($_.Exception.Message)")
    exit 0
}
