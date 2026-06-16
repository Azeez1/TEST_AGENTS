# run_scheduled_claude.ps1 — Windows Task Scheduler runner for headless Claude Code slash commands.
# Each task passes ONLY the tools its command needs via -AllowedTools (comma-separated);
# everything else stays permission-gated (and auto-denies in headless mode).
# The hard-block hooks in .claude/settings.json apply on top regardless.
# Logs to LOGS\scheduled\<name>-<date>.log.
param(
    [Parameter(Mandatory = $true)][string]$Command,
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][string]$AllowedTools
)

$repo = "C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS"
Set-Location $repo

$logDir = Join-Path $repo "LOGS\scheduled"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ("{0}-{1}.log" -f $Name, (Get-Date -Format 'yyyy-MM-dd'))

Add-Content -Path $log -Value ("=== {0} START {1} ===" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Command)
& "C:\Users\sabaa\.local\bin\claude.exe" -p $Command --allowedTools $AllowedTools *>> $log
Add-Content -Path $log -Value ("=== {0} END (exit {1}) ===" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $LASTEXITCODE)
