# claude_p_logged.ps1 - logging wrapper around `claude -p`
#
# Purpose: capture programmatic Claude invocations to LOGS/claude-p-runs.jsonl
# so you can measure spend / volume BEFORE June 15 2026 when programmatic usage
# moves to its own dedicated budget (separate from Claude Code subscription).
#
# Usage:
#     .\tools\claude_p_logged.ps1 "your prompt here"
#     .\tools\claude_p_logged.ps1 "your prompt" -Model "claude-sonnet-4-6"
#
# Set $env:CLAUDE_P_CALLER before invoking to tag the caller (e.g. "pe-diagnosis.ps1"):
#     $env:CLAUDE_P_CALLER = "pe-diagnosis.ps1"
#     .\tools\claude_p_logged.ps1 "..."
#
# Output: writes claude -p's stdout to stdout transparently.
#         Adds one JSONL line per invocation to LOGS/claude-p-runs.jsonl.
#
# Per ADR-0001 absolute paths discipline. Per ADR-0002 ASCII-only.

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Prompt,

    [Parameter(Mandatory=$false)]
    [string]$Model = "",

    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$ExtraArgs
)

$ErrorActionPreference = "Stop"

$REPO_ROOT = "C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS"
$LOG_PATH  = Join-Path $REPO_ROOT "LOGS\claude-p-runs.jsonl"

# --- Helpers ----------------------------------------------------------
function Get-ShortHash($s) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($s)
    $hash = $sha.ComputeHash($bytes)
    return ([System.BitConverter]::ToString($hash) -replace '-','').Substring(0,16).ToLower()
}

# --- Ensure log dir exists --------------------------------------------
$logDir = Split-Path $LOG_PATH -Parent
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# --- Build claude command ---------------------------------------------
$cmdArgs = @("-p", $Prompt)
if ($Model -ne "") {
    $cmdArgs += "--model"
    $cmdArgs += $Model
}
if ($ExtraArgs) {
    $cmdArgs += $ExtraArgs
}

# --- Time + execute ---------------------------------------------------
$startTime = Get-Date
$startTimeIso = $startTime.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

$output = ""
$exitCode = 0
$errorMsg = ""

try {
    # Capture stdout. Allow stderr to pass through.
    $output = & claude @cmdArgs 2>&1 | Out-String
    $exitCode = $LASTEXITCODE
} catch {
    $exitCode = -1
    $errorMsg = $_.Exception.Message
}

$endTime = Get-Date
$durationMs = [int]($endTime - $startTime).TotalMilliseconds

# --- Compute rough token estimates (chars / 4 ~ tokens for English) --
$promptChars = $Prompt.Length
$outputChars = $output.Length
$approxInputTokens = [int]($promptChars / 4)
$approxOutputTokens = [int]($outputChars / 4)

# --- Build JSONL record -----------------------------------------------
$record = [ordered]@{
    ts                    = $startTimeIso
    duration_ms           = $durationMs
    exit_code             = $exitCode
    prompt_chars          = $promptChars
    prompt_hash           = Get-ShortHash $Prompt
    output_chars          = $outputChars
    approx_input_tokens   = $approxInputTokens
    approx_output_tokens  = $approxOutputTokens
    model                 = if ($Model -ne "") { $Model } else { "default" }
    cwd                   = (Get-Location).Path
    caller                = if ($env:CLAUDE_P_CALLER) { $env:CLAUDE_P_CALLER } else { "" }
}
if ($errorMsg -ne "") { $record["error"] = $errorMsg }

# --- Append to log (one compact JSONL line) ---------------------------
$jsonLine = $record | ConvertTo-Json -Compress -Depth 4
Add-Content -Path $LOG_PATH -Value $jsonLine -Encoding utf8

# --- Emit claude's output to stdout transparently ---------------------
Write-Output $output

exit $exitCode
