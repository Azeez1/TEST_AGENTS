# analyze-skill-usage.ps1
# Reads skill-usage.jsonl and produces usage analytics

$log_path = Join-Path $PSScriptRoot "skill-usage.jsonl"

if (-not (Test-Path $log_path)) {
    Write-Host "No skill usage data found at $log_path"
    Write-Host "The tracking hook needs to be active before analysis is meaningful."
    Write-Host ""
    Write-Host "To enable tracking, add this to your settings.json hooks:"
    Write-Host '  "PreToolUse": [{"matcher": "Skill", "hook_command": "powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/track-skill-usage.ps1"}]'
    exit
}

$lines = Get-Content $log_path -Encoding UTF8
$entries = @()
foreach ($line in $lines) {
    if ($line.Trim() -ne "") {
        try {
            $entries += ($line | ConvertFrom-Json)
        } catch {}
    }
}

if ($entries.Count -eq 0) {
    Write-Host "Log file exists but contains no valid entries."
    exit
}

$now = Get-Date
$seven_days_ago = $now.AddDays(-7)
$thirty_days_ago = $now.AddDays(-30)

# Count by skill
$all_time = @{}
$last_7d = @{}
$last_30d = @{}

foreach ($e in $entries) {
    $skill = $e.skill
    $ts = [DateTime]::Parse($e.timestamp)

    if (-not $all_time.ContainsKey($skill)) { $all_time[$skill] = 0 }
    if (-not $last_7d.ContainsKey($skill)) { $last_7d[$skill] = 0 }
    if (-not $last_30d.ContainsKey($skill)) { $last_30d[$skill] = 0 }

    $all_time[$skill]++
    if ($ts -ge $thirty_days_ago) { $last_30d[$skill]++ }
    if ($ts -ge $seven_days_ago) { $last_7d[$skill]++ }
}

# Known skills list
$known_skills = @(
    "algorithmic-art", "artifacts-builder", "brand-guidelines", "canvas-design",
    "careful", "excalidraw-diagrams", "financial-guard", "flow-diagram",
    "freeze", "frontend-design", "infographic-creator", "internal-comms",
    "mcp-builder", "n8n-code-javascript", "n8n-code-python",
    "n8n-expression-syntax", "n8n-mcp-tools-expert", "n8n-node-configuration",
    "n8n-validation-expert", "n8n-workflow-patterns", "remotion-video",
    "skill-creator", "slack-gif-creator", "spec-driven-dev", "theme-factory",
    "last30days"
)

Write-Host ""
Write-Host "========================================="
Write-Host "  SKILL USAGE ANALYTICS"
Write-Host "  Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
Write-Host "  Total invocations: $($entries.Count)"
Write-Host "========================================="
Write-Host ""

# Table header
Write-Host ("{0,-25} {1,8} {2,8} {3,8} {4,8}" -f "SKILL", "ALL", "30D", "7D", "TREND")
Write-Host ("{0,-25} {1,8} {2,8} {3,8} {4,8}" -f "-------------------------", "--------", "--------", "--------", "--------")

$sorted = $all_time.GetEnumerator() | Sort-Object Value -Descending
foreach ($s in $sorted) {
    $skill = $s.Key
    $total = $s.Value
    $d30 = if ($last_30d.ContainsKey($skill)) { $last_30d[$skill] } else { 0 }
    $d7 = if ($last_7d.ContainsKey($skill)) { $last_7d[$skill] } else { 0 }

    # Trend calculation
    $trend = "STABLE"
    if ($d30 -gt 0) {
        $weekly_rate_30d = $d30 / 4.0
        if ($d7 -gt ($weekly_rate_30d * 1.5)) { $trend = "UP" }
        elseif ($d7 -lt ($weekly_rate_30d * 0.5)) { $trend = "DOWN" }
    }
    if ($d30 -eq 0 -and $total -gt 0) { $trend = "STALE" }

    Write-Host ("{0,-25} {1,8} {2,8} {3,8} {4,8}" -f $skill, $total, $d30, $d7, $trend)
}

# Find unused known skills
Write-Host ""
Write-Host "--- NEVER USED (candidates for review) ---"
$unused = $known_skills | Where-Object { -not $all_time.ContainsKey($_) }
if ($unused.Count -gt 0) {
    foreach ($u in $unused) { Write-Host "  - $u" }
} else {
    Write-Host "  (all known skills have been used at least once)"
}

Write-Host ""
Write-Host "--- RECOMMENDATIONS ---"
$top = @($sorted | Select-Object -First 3 | ForEach-Object { $_.Key })
if ($top.Count -gt 0) {
    Write-Host "  Invest in quality: $($top -join ', ') (most used)"
}
$stale_skills = @($sorted | Where-Object { (-not $last_30d.ContainsKey($_.Key)) -or ($last_30d[$_.Key] -eq 0) } | Where-Object { $_.Value -gt 0 } | ForEach-Object { $_.Key })
if ($stale_skills.Count -gt 0) {
    Write-Host "  Review/remove: $($stale_skills -join ', ') (no recent usage)"
}
Write-Host ""
