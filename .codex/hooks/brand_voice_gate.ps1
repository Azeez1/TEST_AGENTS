# Brand Voice Gate
#
# PreToolUse hook for Claude-in-Chrome `computer` typing (mcp__claude-in-chrome__computer, action=type).
# Hard-blocks SOCIAL POST text that violates EZ's brand-voice rules so nothing
# off-brand ever gets published under @EZdaArchitect / his LinkedIn:
#   - em dash / en dash   (EZ's explicit rule; an AI tell)
#   - hashtags (#word)    (EZ uses none)
#   - a tight list of AI-tells (delve, tapestry, game-changer, etc.)
#
# The daily-social-round skill self-checks first; this is the deterministic backstop.
# Only fires on post-like text (>= 40 chars) so it never blocks short search/field typing.
# Fails open (a buggy hook never freezes the system). Wired in .claude/settings.json.
# NOTE: dash chars are built from codepoints at runtime so this source stays pure
# ASCII and never breaks under PowerShell 5.1 codepage decoding.

$ErrorActionPreference = "Stop"
$ENFORCE_MODE = $true
try { [Console]::InputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$VIOLATIONS_LOG = Join-Path $PSScriptRoot "..\..\LOGS\brand-voice.log"
$MIN_LEN = 40

$EMDASH = [string][char]0x2014
$ENDASH = [string][char]0x2013

# Pattern + reason. Case-insensitive. Patterns are .NET regex.
$BANNED = @(
    @{ rx = $EMDASH;             why = "em dash (use commas or periods)" },
    @{ rx = $ENDASH;             why = "en dash (use commas or periods)" },
    @{ rx = '#[A-Za-z]\w+';      why = "hashtag (EZ uses none)" },
    @{ rx = '\bdelve\b';         why = "AI-tell: delve" },
    @{ rx = '\btapestry\b';      why = "AI-tell: tapestry" },
    @{ rx = 'game-?changer';     why = "AI-tell: game-changer" },
    @{ rx = 'fast-paced world';  why = "AI-tell: fast-paced world" },
    @{ rx = '\bunleash\b';       why = "AI-tell: unleash" }
)

try {
    $stdin = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($stdin)) { exit 0 }
    $payload = $stdin | ConvertFrom-Json

    if ($payload.tool_name -ne "mcp__claude-in-chrome__computer") { exit 0 }
    if ($payload.tool_input.action -ne "type") { exit 0 }

    $text = [string]$payload.tool_input.text
    if ([string]::IsNullOrWhiteSpace($text)) { exit 0 }
    if ($text.Length -lt $MIN_LEN) { exit 0 }

    $hits = @()
    foreach ($b in $BANNED) {
        if ([regex]::IsMatch($text, $b.rx, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)) {
            $hits += $b.why
        }
    }
    if ($hits.Count -eq 0) { exit 0 }

    $ts = (Get-Date).ToString("o")
    $logDir = Split-Path $VIOLATIONS_LOG -Parent
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
    $snippet = $text.Substring(0, [Math]::Min(120, $text.Length))
    Add-Content -Path $VIOLATIONS_LOG -Value "[$ts] [BLOCK] $($hits -join '; ') | $snippet"

    [Console]::Error.WriteLine("BRAND_VOICE_GATE: off-brand pattern in a social post blocked")
    foreach ($h in $hits) { [Console]::Error.WriteLine("  - $h") }
    if ($ENFORCE_MODE) {
        [Console]::Error.WriteLine("  Rewrite without these (no em or en dashes, no hashtags, no AI-tells) and retry.")
        exit 2
    }
    exit 0
}
catch {
    [Console]::Error.WriteLine("BRAND_VOICE_GATE: hook error (failing open): $($_.Exception.Message)")
    exit 0
}
