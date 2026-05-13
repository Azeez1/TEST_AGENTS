# PE Diagnosis Validation Gate - Closed Loop (Lesson 5)
#
# PreToolUse hook that blocks Drive uploads of PE diagnosis PDFs unless:
#   (1) A matching .validation_pass file exists AND is newer than the PDF
#   (2) The PDF itself contains the required footer signature strings
#       (programmatic overflow-cutoff detection via pdftotext)
#
# CLOSED-LOOP BEHAVIOR (upgraded 2026-05-12):
#   - Tracks retry count per-PDF in .claude/hooks/.pe_retry_state/{basename}.count
#   - On each block (genuine validation failure, not parse error):
#       * Increment retry counter
#       * Include "RETRY N of 3" + specific failure context in stderr
#       * Exit 2 (block the upload)
#   - After 3 failed attempts on the same PDF:
#       * Reset counter, write escalation entry to LOGS/escalations.log
#       * Try to send a Telegram alert via telegram_notify.ps1 if it exists
#       * Continue to block (exit 2) - escalation is informational
#   - On PASS: reset the retry counter for that PDF
#
# Wired in .claude/settings.local.json under hooks.PreToolUse.

$ErrorActionPreference = "Stop"

$REQUIRED_FOOTER_MARKERS = @(
    "linkedin.com/in/azeez-oseni",
    "duxmachina.com"
)

$RETRY_BUDGET     = 3
$RETRY_STATE_DIR  = Join-Path $PSScriptRoot ".pe_retry_state"
$ESCALATION_LOG   = Join-Path $PSScriptRoot "..\..\LOGS\escalations.log"
$TELEGRAM_HELPER  = Join-Path $PSScriptRoot "telegram_notify.ps1"

# --- Retry state helpers ----------------------------------------------
function Get-RetryStatePath($pdfPath) {
    if (-not (Test-Path $RETRY_STATE_DIR)) {
        New-Item -ItemType Directory -Path $RETRY_STATE_DIR -Force | Out-Null
    }
    $base = [System.IO.Path]::GetFileNameWithoutExtension($pdfPath)
    # Sanitize basename for filesystem
    $base = $base -replace '[^A-Za-z0-9_\-\.]', '_'
    return Join-Path $RETRY_STATE_DIR "$base.count"
}

function Get-RetryCount($pdfPath) {
    $statePath = Get-RetryStatePath $pdfPath
    if (-not (Test-Path $statePath)) { return 0 }
    try { return [int](Get-Content $statePath -Raw).Trim() } catch { return 0 }
}

function Set-RetryCount($pdfPath, $count) {
    $statePath = Get-RetryStatePath $pdfPath
    Set-Content -Path $statePath -Value "$count" -NoNewline
}

function Reset-RetryCount($pdfPath) {
    $statePath = Get-RetryStatePath $pdfPath
    if (Test-Path $statePath) { Remove-Item $statePath -Force }
}

# --- Block helper: increments counter, escalates if budget exceeded ---
function Invoke-BlockWithRetry($pdfPath, $reason, $fixHint) {
    $count = (Get-RetryCount $pdfPath) + 1
    Set-RetryCount $pdfPath $count

    [Console]::Error.WriteLine("PE_GATE: BLOCKED [attempt $count of $RETRY_BUDGET]")
    [Console]::Error.WriteLine("  PDF: $pdfPath")
    [Console]::Error.WriteLine("  Reason: $reason")
    [Console]::Error.WriteLine("  Fix:    $fixHint")

    if ($count -ge $RETRY_BUDGET) {
        # Escalate
        [Console]::Error.WriteLine("")
        [Console]::Error.WriteLine("PE_GATE: RETRY BUDGET EXCEEDED ($count >= $RETRY_BUDGET).")
        [Console]::Error.WriteLine("Escalating. Resetting counter so subsequent attempts start fresh.")

        $escalationDir = Split-Path $ESCALATION_LOG -Parent
        if (-not (Test-Path $escalationDir)) {
            New-Item -ItemType Directory -Path $escalationDir -Force | Out-Null
        }
        $ts = (Get-Date).ToString("o")
        Add-Content -Path $ESCALATION_LOG -Value "[$ts] PE_GATE escalation: $pdfPath | reason=$reason | attempts=$count"

        # Best-effort Telegram notify
        if (Test-Path $TELEGRAM_HELPER) {
            try {
                & $TELEGRAM_HELPER "PE_GATE escalation: $pdfPath failed validation $count times. Reason: $reason"
            } catch {
                [Console]::Error.WriteLine("PE_GATE: telegram_notify failed: $($_.Exception.Message)")
            }
        }

        # Reset for next session
        Reset-RetryCount $pdfPath
    } else {
        $remaining = $RETRY_BUDGET - $count
        [Console]::Error.WriteLine("")
        [Console]::Error.WriteLine("PE_GATE: $remaining retries remaining. Fix the issue above and try again.")
    }

    exit 2
}

# --- Main -------------------------------------------------------------
try {
    $stdin = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($stdin)) { exit 0 }

    $payload = $stdin | ConvertFrom-Json

    if ($payload.tool_name -ne "Bash") { exit 0 }

    $command = $payload.tool_input.command
    if ([string]::IsNullOrWhiteSpace($command)) { exit 0 }

    $isUpload  = $command -match "upload_to_drive\.py"
    $isDiagPdf = $command -match "_diagnosis\.pdf"
    if (-not ($isUpload -and $isDiagPdf)) { exit 0 }

    $absPattern = "[A-Za-z]:[\\/][^ ""]+_diagnosis\.pdf"
    $relPattern = "[^ ""]+_diagnosis\.pdf"

    $pdfMatch = [regex]::Match($command, $absPattern)
    if (-not $pdfMatch.Success) {
        $pdfMatch = [regex]::Match($command, $relPattern)
    }
    if (-not $pdfMatch.Success) {
        # Parse errors are not the agent's fault - no retry tracking
        [Console]::Error.WriteLine("PE_GATE: Could not parse PDF path from upload command. Refusing.")
        exit 2
    }

    $pdfPath  = $pdfMatch.Value
    $passPath = $pdfPath -replace "\.pdf$", ".validation_pass"

    if (-not (Test-Path $pdfPath)) {
        Invoke-BlockWithRetry $pdfPath "PDF not found at expected path" "Render the diagnosis PDF before invoking upload"
    }

    # GATE 1: validation_pass file exists and is fresh
    if (-not (Test-Path $passPath)) {
        Invoke-BlockWithRetry $pdfPath "no .validation_pass file" "Run the pe-diagnosis-validator subagent on this PDF first. It writes the pass file on success."
    }

    $pdfTime  = (Get-Item $pdfPath).LastWriteTime
    $passTime = (Get-Item $passPath).LastWriteTime

    if ($passTime -lt $pdfTime) {
        Invoke-BlockWithRetry $pdfPath "validation pass file is STALE (PDF re-rendered after validation)" "Re-run pe-diagnosis-validator on the current PDF to refresh the pass file."
    }

    # GATE 2: PDF actually contains the footer signature (overflow-cutoff detection)
    $pdftotext = Get-Command pdftotext -ErrorAction SilentlyContinue
    if ($null -eq $pdftotext) {
        [Console]::Error.WriteLine("PE_GATE: WARNING - pdftotext not found on PATH. Skipping cutoff check.")
        [Console]::Error.WriteLine("Install poppler-utils for full PDF cutoff detection.")
        Write-Host "PE_GATE: PASS (pass file ok, cutoff check skipped) - $pdfPath"
        Reset-RetryCount $pdfPath
        exit 0
    }

    $extracted = & pdftotext -layout "$pdfPath" - 2>$null
    if (-not $extracted) {
        Invoke-BlockWithRetry $pdfPath "pdftotext returned no text - PDF may be corrupt or image-only" "Re-render via Chrome headless to produce a real text-bearing PDF."
    }

    $text = $extracted -join "`n"
    $missing = @()
    foreach ($marker in $REQUIRED_FOOTER_MARKERS) {
        if ($text -notmatch [regex]::Escape($marker)) {
            $missing += $marker
        }
    }

    if ($missing.Count -gt 0) {
        $hint = "Tighten CSS spacing on bottom-half elements (timeline, metrics, footer) and re-render. See tools/fix_diagnosis_pdfs.py. After re-rendering, you must re-run pe-diagnosis-validator (pass file will be stale)."
        Invoke-BlockWithRetry $pdfPath "PDF appears TRUNCATED - missing footer markers: $($missing -join ', ')" $hint
    }

    Write-Host "PE_GATE: PASS - $pdfPath (pass file + footer signature verified)"
    Reset-RetryCount $pdfPath
    exit 0
}
catch {
    [Console]::Error.WriteLine("PE_GATE: hook script error: $($_.Exception.Message)")
    exit 2
}
