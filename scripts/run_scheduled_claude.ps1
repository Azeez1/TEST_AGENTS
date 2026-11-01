# run_scheduled_claude.ps1 — Windows Task Scheduler runner for headless Claude Code slash commands.
# Each task passes ONLY the tools its command needs via -AllowedTools (comma-separated);
# everything else stays permission-gated (and auto-denies in headless mode).
# The hard-block hooks in .claude/settings.json apply on top regardless.
# Logs to LOGS\scheduled\<name>-<date>.log (UTF-8).
param(
    [Parameter(Mandatory = $true)][string]$Command,
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][string]$AllowedTools
)

$repo = "C:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS"
Set-Location $repo

$logDir = Join-Path $repo "LOGS\scheduled"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ("{0}-{1}.log" -f $Name, (Get-Date -Format 'yyyy-MM-dd'))
function Write-Log([string]$msg) {
    Add-Content -Path $log -Encoding utf8 -Value ("=== {0} {1} ===" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg)
}

# 2026-11-01: runs ONLY on the desktop, ONLY on the claude.ai subscription.
# History: 2026-07-01 lead-gen-pm + brand-check retired (were billing API credits).
# 2026-10-12 everything paused: the other machine's tasks had ANTHROPIC_API_KEY set, which beats the
# claude.ai login, so they billed the API ("Credit balance is too low"). This script is OneDrive-synced,
# so the host guard below turns the other machine's Task Scheduler entries into no-ops.
$runHost = 'DESKTOP-B8JD7TL'
$disabledTasks = @('lead-gen-pm', 'brand-check')
if ($env:COMPUTERNAME -ne $runHost) {
    Write-Log ("SKIPPED '{0}' on {1} - scheduled runs only on {2}, no API call made" -f $Name, $env:COMPUTERNAME, $runHost)
    exit 0
}
if ($disabledTasks -contains $Name) {
    Write-Log ("SKIPPED '{0}' - task retired by operator, no API call made" -f $Name)
    exit 0
}

# Any of these makes claude.exe bill the API (or another provider) instead of the subscription.
foreach ($var in 'ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN', 'CLAUDE_CODE_OAUTH_TOKEN', 'ANTHROPIC_BASE_URL',
    'CLAUDE_CODE_USE_BEDROCK', 'CLAUDE_CODE_USE_VERTEX', 'CLAUDE_CODE_USE_FOUNDRY') {
    Remove-Item -Path "Env:$var" -ErrorAction SilentlyContinue
}

$claude = Join-Path $env:APPDATA "npm\node_modules\@anthropic-ai\claude-code\bin\claude.exe"
if (-not (Test-Path $claude)) {
    $found = Get-Command claude.exe, claude.cmd -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $found) { Write-Log "FAILED '$Name' - claude not found"; exit 1 }
    $claude = $found.Source
}

# Preflight: refuse to run unless logged in to the claude.ai subscription.
$auth = $null
try { $auth = (& $claude auth status 2>$null | Out-String) | ConvertFrom-Json } catch {}
if (-not $auth -or -not $auth.loggedIn -or $auth.authMethod -ne 'claude.ai') {
    Write-Log ("FAILED '{0}' - not on subscription auth (authMethod={1}); run 'claude auth login --claudeai'" -f $Name, $auth.authMethod)
    exit 1
}

Write-Log ("START {0} (auth {1}, {2})" -f $Command, $auth.authMethod, $auth.subscriptionType)
& $claude -p $Command --allowedTools $AllowedTools 2>&1 | ForEach-Object { "$_" } | Out-File -FilePath $log -Append -Encoding utf8
Write-Log ("END (exit {0})" -f $LASTEXITCODE)
