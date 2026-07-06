# run_intent_engine.ps1 - Windows Task Scheduler runner for the Dux Intent Signal Engine.
# Invokes ONLY python (run_intent_scan.py). It NEVER calls claude.exe, so a scheduled
# run can never bill the Anthropic API. ASCII-only, PowerShell 5.1 safe.
# Logs to LOGS\scheduled\intent-engine-<date>.log.
param(
    [int]$SinceDays = 7,
    [string]$ExtraArgs = ""
)

$repo = "C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS"
Set-Location $repo

$logDir = Join-Path $repo "LOGS\scheduled"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ("intent-engine-{0}.log" -f (Get-Date -Format 'yyyy-MM-dd'))

# Kill switch (same pattern as run_scheduled_claude.ps1): add 'intent-engine' to this
# list to make the scheduled task a no-op without unregistering it.
$disabledTasks = @()
if ($disabledTasks -contains 'intent-engine') {
    Add-Content -Path $log -Value ("=== {0} SKIPPED intent-engine - task disabled by operator ===" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
    exit 0
}

$python = "C:\Python314\python.exe"
if (-not (Test-Path $python)) { $python = "python" }
$script = Join-Path $repo "SALES_TEAM\tools\intent_engine\run_intent_scan.py"

$argList = @($script, "--scheduled", "--since-days", "$SinceDays")
if ($ExtraArgs -ne "") { $argList += ($ExtraArgs -split ' ') }

Add-Content -Path $log -Value ("=== {0} START intent scan (since-days={1}) ===" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $SinceDays)
& $python @argList *>> $log
$code = $LASTEXITCODE
Add-Content -Path $log -Value ("=== {0} END (exit {1}) ===" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $code)
exit $code
