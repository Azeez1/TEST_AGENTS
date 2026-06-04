# API Cost Gate
#
# PreToolUse hook for paid media-generation MCP tools (marketing-tools video +
# image generators). Tracks a running daily spend estimate and hard-blocks once
# the day's budget would be exceeded. Prevents a single session from running up
# $100+ in Sora/Veo/image calls with no ceiling.
#
# Override for an approved big render day: add [[SPEND-APPROVED]] to any string
# field of the tool input (e.g. the prompt).
# Wired in .claude/settings.json under hooks.PreToolUse.

$ErrorActionPreference = "Stop"
$ENFORCE_MODE = $true

$DAILY_BUDGET   = 50.0     # USD per day across all paid generations
$WARN_AT        = 10.0     # informational threshold
$VIOLATIONS_LOG = Join-Path $PSScriptRoot "..\..\LOGS\api-spend.log"
$SPEND_DIR      = Join-Path $PSScriptRoot "..\..\LOGS"
$OVERRIDE_TOKEN = "[[SPEND-APPROVED]]"

# Rough per-call cost estimate (USD). Video >> image. Conservative/high side.
$COST = @{
    "mcp__marketing-tools__generate_sora_video"        = 8.0
    "mcp__marketing-tools__generate_veo_ugc_from_image"= 6.0
    "mcp__marketing-tools__generate_veo_text_to_video" = 6.0
    "mcp__marketing-tools__generate_kling_video"       = 4.0
    "mcp__marketing-tools__generate_seedance_video"    = 4.0
    "mcp__marketing-tools__generate_video_with_fallback"= 6.0
    "mcp__marketing-tools__generate_gpt4o_image"       = 0.17
    "mcp__marketing-tools__generate_nano_banana_image" = 0.14
    "mcp__marketing-tools__generate_nano_banana_2_image"= 0.14
    "mcp__marketing-tools__generate_image_with_fallback"= 0.17
}

try {
    $stdin = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($stdin)) { exit 0 }
    $payload = $stdin | ConvertFrom-Json
    $tool = $payload.tool_name
    if (-not $COST.ContainsKey($tool)) { exit 0 }

    $est = [double]$COST[$tool]
    $today = (Get-Date).ToString("yyyy-MM-dd")
    $spendFile = Join-Path $SPEND_DIR "api-spend-$today.total"
    $spent = 0.0
    if (Test-Path $spendFile) { $spent = [double](Get-Content $spendFile -Raw).Trim() }
    $projected = $spent + $est

    $logDir = Split-Path $VIOLATIONS_LOG -Parent
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
    $ts = (Get-Date).ToString("o")

    $blob = $payload.tool_input | ConvertTo-Json -Depth 8 -Compress
    $hasOverride = $blob.Contains($OVERRIDE_TOKEN)

    if ($projected -gt $DAILY_BUDGET -and -not $hasOverride) {
        Add-Content -Path $VIOLATIONS_LOG -Value "[$ts] [BLOCK] $tool est=`$$est spent=`$$spent budget=`$$DAILY_BUDGET"
        [Console]::Error.WriteLine("API_COST_GATE: paid generation would exceed today's `$$DAILY_BUDGET budget.")
        [Console]::Error.WriteLine("  Spent so far: `$$([math]::Round($spent,2)) | this call ~`$$est | projected `$$([math]::Round($projected,2)).")
        [Console]::Error.WriteLine("  For an approved render day, add $OVERRIDE_TOKEN to the prompt and retry.")
        if ($ENFORCE_MODE) { exit 2 }
        exit 0
    }

    # Allowed - record spend.
    Set-Content -Path $spendFile -Value ([string]([math]::Round($projected, 4)))
    $tag = if ($hasOverride) { "OVERRIDE" } else { "OK" }
    Add-Content -Path $VIOLATIONS_LOG -Value "[$ts] [$tag] $tool est=`$$est running=`$$([math]::Round($projected,2))"
    if ($projected -ge $WARN_AT) {
        [Console]::Error.WriteLine("API_COST_GATE: heads up - today's generation spend is ~`$$([math]::Round($projected,2)).")
    }
    exit 0
}
catch {
    [Console]::Error.WriteLine("API_COST_GATE: hook error (failing open): $($_.Exception.Message)")
    exit 0
}
