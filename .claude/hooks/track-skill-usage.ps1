# track-skill-usage.ps1
# PreToolUse hook that logs skill invocations to JSONL
# Always approves — this is a logging-only hook, never blocks

$input_data = [Console]::In.ReadToEnd()

try {
    $json = $input_data | ConvertFrom-Json

    $skill_name = ""
    $skill_args = ""

    if ($json.tool_input.skill) {
        $skill_name = $json.tool_input.skill
    }
    if ($json.tool_input.args) {
        $skill_args = $json.tool_input.args
    }

    if ($skill_name -ne "") {
        $log_entry = @{
            timestamp  = (Get-Date -Format "o")
            skill      = $skill_name
            args       = $skill_args
            session_id = if ($env:CLAUDE_SESSION_ID) { $env:CLAUDE_SESSION_ID } else { "unknown" }
        } | ConvertTo-Json -Compress

        $log_path = Join-Path $PSScriptRoot "skill-usage.jsonl"
        Add-Content -Path $log_path -Value $log_entry -Encoding UTF8
    }
} catch {
    # Silently ignore errors — never block the tool
}

Write-Output '{"decision":"approve"}'
