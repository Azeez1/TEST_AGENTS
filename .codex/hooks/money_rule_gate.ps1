# Money Rule Gate
#
# PreToolUse hook for Bash|PowerShell|Write|Edit and known trade-execution
# MCP tools. Enforces the CLAUDE.md / DBAC "Money Rule": anything that places
# an order, executes a trade, or moves money requires explicit human approval.
#
# Today HEDGE_FUND ict-trader and FINANCIAL trading-optimizer declare
# "analyze-only / never execute" in PROSE ONLY. This makes it real: any
# execution path is blocked unless the human appends [[MONEY-APPROVED]].
#
# Wired in .claude/settings.json under hooks.PreToolUse.

$ErrorActionPreference = "Stop"
$ENFORCE_MODE = $true

$VIOLATIONS_LOG = Join-Path $PSScriptRoot "..\..\LOGS\money-rule.log"
$OVERRIDE_TOKEN = "[[MONEY-APPROVED]]"

# Tool names that ARE order execution (block outright unless approved).
$EXEC_TOOL_NAMES = @(
    "mcp__tradingview__replay_trade"   # placing a (replay) trade is execution-shaped; keep gated
)

# Content keywords (regex, case-insensitive) that indicate real money movement.
$MONEY_PATTERNS = @(
    @{ rx = '\bplace_order\b';            why = "place_order call" },
    @{ rx = '\bsubmit_order\b';           why = "submit_order call" },
    @{ rx = '\bcreate_order\b';           why = "create_order call" },
    @{ rx = '\bexecute_trade\b';          why = "execute_trade call" },
    @{ rx = '\blive_trading\s*=\s*True';  why = "live_trading enabled" },
    @{ rx = '\bsend_wire\b';              why = "wire transfer" },
    @{ rx = '\bwire_transfer\b';          why = "wire transfer" },
    @{ rx = '\binitiate_payout\b';        why = "payout" },
    @{ rx = '\btransfer_funds\b';         why = "funds transfer" },
    @{ rx = 'alpaca.*\b(order|buy|sell)\b'; why = "Alpaca order" },
    @{ rx = 'ib_insync';                  why = "Interactive Brokers order client" },
    @{ rx = '\bbroker\.(buy|sell|order|trade)\b'; why = "broker order method" },
    @{ rx = 'ccxt.*create_order';         why = "ccxt exchange order" }
)

try {
    $stdin = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($stdin)) { exit 0 }
    $payload = $stdin | ConvertFrom-Json

    $tool = $payload.tool_name
    $hits = @()

    if ($EXEC_TOOL_NAMES -contains $tool) {
        $hits += "execution tool: $tool"
    }

    # Scan command (Bash/PS) and content/new_string (Write/Edit)
    $text = ""
    if ($payload.tool_input.command)    { $text += "`n" + $payload.tool_input.command }
    if ($payload.tool_input.content)    { $text += "`n" + $payload.tool_input.content }
    if ($payload.tool_input.new_string) { $text += "`n" + $payload.tool_input.new_string }

    if (-not [string]::IsNullOrWhiteSpace($text)) {
        foreach ($p in $MONEY_PATTERNS) {
            if ([regex]::IsMatch($text, $p.rx, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)) {
                $hits += $p.why
            }
        }
    }

    if ($hits.Count -eq 0) { exit 0 }

    $ts = (Get-Date).ToString("o")
    $logDir = Split-Path $VIOLATIONS_LOG -Parent
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

    $blob = "$text $($payload.tool_input | ConvertTo-Json -Depth 6 -Compress)"
    $hasOverride = $blob.Contains($OVERRIDE_TOKEN)
    $verdict = if ($hasOverride) { "OVERRIDE" } else { "BLOCK" }
    Add-Content -Path $VIOLATIONS_LOG -Value "[$ts] [$verdict] $tool | $($hits -join '; ')"

    if ($hasOverride) {
        [Console]::Error.WriteLine("MONEY_RULE_GATE: human approval token present - allowing ($($hits -join '; '))")
        exit 0
    }

    [Console]::Error.WriteLine("MONEY_RULE_GATE: this action moves money / executes a trade")
    foreach ($h in $hits) { [Console]::Error.WriteLine("  - $h") }
    if ($ENFORCE_MODE) {
        [Console]::Error.WriteLine("  Money Rule: a human must approve. Get sign-off, then append $OVERRIDE_TOKEN to proceed.")
        exit 2
    }
    exit 0
}
catch {
    [Console]::Error.WriteLine("MONEY_RULE_GATE: hook error (failing open): $($_.Exception.Message)")
    exit 0
}
