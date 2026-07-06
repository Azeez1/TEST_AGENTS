# register_intent_task.ps1 - ONE-TIME registration of the weekly intent engine scan.
# Run manually (EZ only): powershell -ExecutionPolicy Bypass -File scripts\register_intent_task.ps1
# Creates task 'DuxOS intent-engine weekly': Mondays 07:00, StartWhenAvailable so a
# missed Monday (machine asleep) runs at next boot. ASCII-only, PowerShell 5.1 safe.

$taskName = "DuxOS intent-engine weekly"
$runner = "C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\scripts\run_intent_engine.ps1"

if (-not (Test-Path $runner)) {
    Write-Host "ERROR: runner not found at $runner"
    exit 1
}

$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Task '$taskName' already exists. Unregister it first if you want to recreate:"
    Write-Host "  Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false"
    exit 1
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$runner`" -SinceDays 7"

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 7:00am

$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
    -Settings $settings -Description "Dux Intent Signal Engine weekly scan (python only, no claude.exe)" | Out-Null

Write-Host "Registered '$taskName' (Mondays 07:00, StartWhenAvailable)."
Write-Host "Logs: LOGS\scheduled\intent-engine-<date>.log"
Write-Host "Kill switch: add 'intent-engine' to `$disabledTasks in run_intent_engine.ps1"
