# Destructive Bash Gate
#
# PreToolUse hook for Bash|PowerShell.
# Hard-blocks irreversible shell commands (data loss / history rewrite) unless
# the human consciously appends the override token [[CONFIRM-DESTRUCTIVE]] to
# the command. Every override is logged for an audit trail.
#
# Replaces the OPTIONAL `careful` skill (which nobody activates) with a wired,
# always-on gate. Covers ENGINEERING_TEAM + QA_TEAM Bash.
#
# Wired in .claude/settings.json under hooks.PreToolUse.

$ErrorActionPreference = "Stop"
$ENFORCE_MODE = $true

$VIOLATIONS_LOG = Join-Path $PSScriptRoot "..\..\LOGS\destructive-bash.log"
$OVERRIDE_TOKEN = "[[CONFIRM-DESTRUCTIVE]]"

# Pattern + reason. Case-insensitive.
$DANGER = @(
    @{ rx = 'rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r|--recursive\s+--force)'; why = "recursive force delete (rm -rf)" },
    @{ rx = 'Remove-Item\b.*-Recurse\b.*-Force\b';                  why = "recursive force delete (Remove-Item)" },
    @{ rx = 'Remove-Item\b.*-Force\b.*-Recurse\b';                  why = "recursive force delete (Remove-Item)" },
    @{ rx = '\brmdir\s+/s';                                         why = "recursive directory delete (rmdir /s)" },
    @{ rx = '\bdel\s+/[a-zA-Z]*s';                                  why = "recursive file delete (del /s)" },
    @{ rx = 'git\s+reset\s+--hard';                                why = "git reset --hard (discards uncommitted work)" },
    @{ rx = 'git\s+push\b.*(--force\b|-f\b|--force-with-lease)';   why = "git force-push (rewrites remote history)" },
    @{ rx = 'git\s+clean\s+-[a-zA-Z]*f';                           why = "git clean -f (deletes untracked files)" },
    @{ rx = 'git\s+checkout\s+--\s+\.';                            why = "git checkout -- . (discards all local changes)" },
    @{ rx = '\bDROP\s+(TABLE|DATABASE|SCHEMA)\b';                  why = "SQL DROP (destroys data)" },
    @{ rx = '\bTRUNCATE\s+TABLE\b';                                why = "SQL TRUNCATE (empties a table)" },
    @{ rx = '\bDELETE\s+FROM\b(?!.*\bWHERE\b)';                    why = "SQL DELETE without WHERE (wipes a table)" },
    @{ rx = 'kubectl\s+delete\b';                                  why = "kubectl delete (removes live resources)" },
    @{ rx = 'docker\s+(rm|rmi)\s+-[a-zA-Z]*f';                     why = "docker force remove" },
    @{ rx = 'docker\s+system\s+prune';                            why = "docker system prune (mass cleanup)" },
    @{ rx = '\bmkfs';                                              why = "mkfs (formats a filesystem)" },
    @{ rx = 'dd\s+if=';                                           why = "dd (raw disk write)" },
    @{ rx = '>\s*/dev/sd';                                        why = "write to raw disk device" }
)

try {
    $stdin = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($stdin)) { exit 0 }
    $payload = $stdin | ConvertFrom-Json

    if (@("Bash", "PowerShell") -notcontains $payload.tool_name) { exit 0 }

    $cmd = $payload.tool_input.command
    if ([string]::IsNullOrWhiteSpace($cmd)) { exit 0 }

    $hits = @()
    foreach ($d in $DANGER) {
        if ([regex]::IsMatch($cmd, $d.rx, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)) {
            $hits += $d.why
        }
    }
    if ($hits.Count -eq 0) { exit 0 }

    $ts = (Get-Date).ToString("o")
    $logDir = Split-Path $VIOLATIONS_LOG -Parent
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

    $hasOverride = $cmd.Contains($OVERRIDE_TOKEN)
    $verdict = if ($hasOverride) { "OVERRIDE" } else { "BLOCK" }
    Add-Content -Path $VIOLATIONS_LOG -Value "[$ts] [$verdict] $($hits -join '; ') | $cmd"

    if ($hasOverride) {
        [Console]::Error.WriteLine("DESTRUCTIVE_BASH_GATE: override token present - allowing ($($hits -join '; '))")
        exit 0
    }

    [Console]::Error.WriteLine("DESTRUCTIVE_BASH_GATE: destructive command blocked")
    foreach ($h in $hits) { [Console]::Error.WriteLine("  - $h") }
    if ($ENFORCE_MODE) {
        [Console]::Error.WriteLine("  This is irreversible. If you truly intend it, append the token $OVERRIDE_TOKEN to the command and retry.")
        exit 2
    }
    exit 0
}
catch {
    [Console]::Error.WriteLine("DESTRUCTIVE_BASH_GATE: hook error (failing open): $($_.Exception.Message)")
    exit 0
}
