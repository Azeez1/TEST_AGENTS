# Deploy Approval Gate
#
# PreToolUse hook for Bash|PowerShell.
# Infrastructure mutations (terraform apply, helm upgrade, kubectl apply,
# render/serverless deploy) provision real, billable, hard-to-undo resources.
# devops-engineer must not run them without a deliberate human approval.
#
# Override: append [[DEPLOY-APPROVED]] (optionally [[DEPLOY-APPROVED:prod]]).
# Wired in .claude/settings.json under hooks.PreToolUse.

$ErrorActionPreference = "Stop"
$ENFORCE_MODE = $true

$VIOLATIONS_LOG = Join-Path $PSScriptRoot "..\..\LOGS\deploy-approval.log"
$OVERRIDE_TOKEN = "[[DEPLOY-APPROVED"   # prefix match; allows [[DEPLOY-APPROVED]] or [[DEPLOY-APPROVED:env]]

$DEPLOY_PATTERNS = @(
    @{ rx = 'terraform\s+apply';            why = "terraform apply" },
    @{ rx = 'terraform\s+destroy';          why = "terraform destroy" },
    @{ rx = 'helm\s+(upgrade|install)';     why = "helm release" },
    @{ rx = 'kubectl\s+apply';              why = "kubectl apply" },
    @{ rx = 'kubectl\s+rollout';            why = "kubectl rollout" },
    @{ rx = 'serverless\s+deploy';          why = "serverless deploy" },
    @{ rx = '\brender\b.*deploy';           why = "Render deploy" },
    @{ rx = 'aws\s+cloudformation\s+(deploy|create-stack|update-stack)'; why = "CloudFormation deploy" },
    @{ rx = 'pulumi\s+up';                  why = "pulumi up" },
    @{ rx = 'gcloud\s+(run\s+deploy|app\s+deploy)'; why = "GCloud deploy" }
)

try {
    $stdin = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($stdin)) { exit 0 }
    $payload = $stdin | ConvertFrom-Json
    if (@("Bash", "PowerShell") -notcontains $payload.tool_name) { exit 0 }

    $cmd = $payload.tool_input.command
    if ([string]::IsNullOrWhiteSpace($cmd)) { exit 0 }

    $hits = @()
    foreach ($d in $DEPLOY_PATTERNS) {
        if ([regex]::IsMatch($cmd, $d.rx, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)) { $hits += $d.why }
    }
    if ($hits.Count -eq 0) { exit 0 }

    $ts = (Get-Date).ToString("o")
    $logDir = Split-Path $VIOLATIONS_LOG -Parent
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

    $hasOverride = $cmd.Contains($OVERRIDE_TOKEN)
    $verdict = if ($hasOverride) { "OVERRIDE" } else { "BLOCK" }
    Add-Content -Path $VIOLATIONS_LOG -Value "[$ts] [$verdict] $($hits -join '; ') | $cmd"

    if ($hasOverride) {
        [Console]::Error.WriteLine("DEPLOY_APPROVAL_GATE: deploy approval token present - allowing ($($hits -join '; ')).")
        exit 0
    }
    [Console]::Error.WriteLine("DEPLOY_APPROVAL_GATE: infrastructure deploy blocked ($($hits -join '; ')).")
    if ($ENFORCE_MODE) {
        [Console]::Error.WriteLine("  Confirm the target environment, then append [[DEPLOY-APPROVED]] (or [[DEPLOY-APPROVED:prod]]) and retry.")
        exit 2
    }
    exit 0
}
catch {
    [Console]::Error.WriteLine("DEPLOY_APPROVAL_GATE: hook error (failing open): $($_.Exception.Message)")
    exit 0
}
