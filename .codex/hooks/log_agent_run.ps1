# Append one JSONL line per Stop event to LOGS/agent-runs.jsonl.
# Reads JSON event payload from stdin (Claude Code hook contract).
# Phase A note: original target path is .claude/hooks/log_agent_run.ps1.proposed,
# but write permission was denied there. Move this file to:
#   C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\.claude\hooks\log_agent_run.ps1
# after review, then wire into settings.json under hooks.Stop.

$ErrorActionPreference = 'SilentlyContinue'

$logDir  = Join-Path $PSScriptRoot '..\LOGS'
if (-not (Test-Path $logDir)) {
    # Fallback when this script lives in .claude/hooks/
    $logDir = Join-Path $PSScriptRoot '..\..\LOGS'
}
$logFile = Join-Path $logDir 'agent-runs.jsonl'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Force -Path $logDir | Out-Null }

# Read hook payload from stdin
$raw = [Console]::In.ReadToEnd()
$payload = $null
try { $payload = $raw | ConvertFrom-Json } catch { $payload = $null }

$record = [ordered]@{
    ts          = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    agent       = if ($payload.agent_name)  { $payload.agent_name }  else { $env:CLAUDE_AGENT_NAME }
    status      = if ($payload.status)      { $payload.status }      else { 'ok' }
    duration_ms = if ($payload.duration_ms) { [int]$payload.duration_ms } else { $null }
    cost_usd    = if ($payload.cost_usd)    { [double]$payload.cost_usd } else { $null }
    model       = if ($payload.model)       { $payload.model }       else { $env:CLAUDE_MODEL }
    session_id  = if ($payload.session_id)  { $payload.session_id }  else { $env:CLAUDE_SESSION_ID }
    cwd         = (Get-Location).Path
}

# Strip nulls so the JSONL stays compact
$clean = @{}
foreach ($k in $record.Keys) { if ($null -ne $record[$k] -and $record[$k] -ne '') { $clean[$k] = $record[$k] } }

$line = ($clean | ConvertTo-Json -Compress -Depth 4)
Add-Content -Path $logFile -Value $line -Encoding utf8
