# register_scheduled_claude.ps1 — (re)registers the DuxOS scheduled Claude jobs on THIS machine.
# Run once on the desktop (DESKTOP-B8JD7TL), in a normal PowerShell window:
#   powershell -ExecutionPolicy Bypass -File scripts\register_scheduled_claude.ps1
# Jobs run only while EZ is signed in and use the claude.ai subscription (see run_scheduled_claude.ps1).
# A missed run (PC asleep/off at the time) starts as soon as the PC is available again.

$repo = "C:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS"
$runner = Join-Path $repo "scripts\run_scheduled_claude.ps1"
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 1) -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

$jobs = @(
    @{ Task = 'DuxOS sync-memory daily'; Name = 'sync-memory'; Cmd = '/sync-memory'; Tools = 'Bash'
        Trigger = (New-ScheduledTaskTrigger -Daily -At 7:00am) },
    @{ Task = 'DuxOS agent-health weekly'; Name = 'agent-health'; Cmd = '/agent-health full generate-report'
        Tools = 'Read,Glob,Grep,Edit(ENGINEERING_TEAM/outputs/**),Bash(python tools/lint_agent_declarations.py),Bash(python tools/check_codex_drift.py),Bash(git status:*),Bash(git log:*)'
        Trigger = (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 8:00am) }
)

foreach ($j in $jobs) {
    $arg = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$runner`" -Command `"$($j.Cmd)`" -Name $($j.Name) -AllowedTools `"$($j.Tools)`""
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arg -WorkingDirectory $repo
    Register-ScheduledTask -TaskName $j.Task -Action $action -Trigger $j.Trigger -Settings $settings -Principal $principal `
        -Description "Headless Claude Code ($($j.Cmd)) on the claude.ai subscription. See .claude/OPERATOR_CHEATSHEET.md" -Force | Out-Null
}

Get-ScheduledTask "DuxOS*" | ForEach-Object { "{0} | {1} | next run {2}" -f $_.TaskName, $_.State, (Get-ScheduledTaskInfo $_).NextRunTime }
