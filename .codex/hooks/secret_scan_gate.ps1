# Secret Scan Gate
#
# PreToolUse hook for Write|Edit|MultiEdit|NotebookEdit.
# Blocks any write whose content contains a real (non-placeholder) secret:
# API keys, OAuth secrets, JWTs, PATs. Patterns are self-contained here.
# (Supersedes the former lib/security_gate.py, which was never wired AND blocked
# with exit 1 — which Claude Code does not treat as a block. Removed 2026-06-02.)
#
# security-rules.md is prose; this is its enforcement.
#
# Wired in .claude/settings.json under hooks.PreToolUse.

$ErrorActionPreference = "Stop"

# --- TOGGLE -----------------------------------------------------------
$ENFORCE_MODE = $true

# --- Paths ------------------------------------------------------------
$VIOLATIONS_LOG = Join-Path $PSScriptRoot "..\..\LOGS\secret-violations.log"

# --- Secret patterns (ported from lib/security_gate.py) ---------------
# Each: regex + human label.
$SECRET_PATTERNS = @(
    @{ rx = 'sk-[a-zA-Z0-9]{20,}';                                              label = "OpenAI API key" },
    @{ rx = 'pplx-[a-zA-Z0-9]{20,}';                                            label = "Perplexity API key" },
    @{ rx = 'GOCSPX-[a-zA-Z0-9_\-]+';                                           label = "Google OAuth secret" },
    @{ rx = 'eyJ[a-zA-Z0-9_\-]{30,}\.[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+';         label = "JWT token" },
    @{ rx = 'ghp_[a-zA-Z0-9]{36,}';                                             label = "GitHub personal access token" },
    @{ rx = 'gho_[a-zA-Z0-9]{36,}';                                             label = "GitHub OAuth token" },
    @{ rx = 'github_pat_[a-zA-Z0-9_]{20,}';                                     label = "GitHub fine-grained PAT" },
    @{ rx = 'xai-[a-zA-Z0-9]{20,}';                                             label = "xAI API key" },
    @{ rx = 'AKIA[0-9A-Z]{16}';                                                 label = "AWS access key ID" },
    @{ rx = 'AIza[0-9A-Za-z_\-]{35}';                                           label = "Google API key" }
)

# --- Safe context (placeholders / env reads) --------------------------
# If a match sits next to one of these, it's a template/example, not a leak.
$SAFE_PATTERNS = @(
    'os\.getenv\(',
    'process\.env\.',
    '\$\{[A-Z_]+\}',
    '\$env:',
    'your[_\-].*[_\-]here',
    'sk-your-key',
    'your_key_here',
    'placeholder',
    'example',
    'xxxx'
)

function Test-SafeContext($content, $matchValue) {
    $idx = $content.IndexOf($matchValue)
    if ($idx -lt 0) { return $false }
    $start = [Math]::Max(0, $idx - 60)
    $len = [Math]::Min($content.Length - $start, $matchValue.Length + 120)
    $window = $content.Substring($start, $len)
    foreach ($safe in $SAFE_PATTERNS) {
        if ($window -match $safe) { return $true }
    }
    return $false
}

# --- Main -------------------------------------------------------------
try {
    $stdin = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($stdin)) { exit 0 }

    $payload = $stdin | ConvertFrom-Json

    $relevantTools = @("Write", "Edit", "MultiEdit", "NotebookEdit")
    if ($relevantTools -notcontains $payload.tool_name) { exit 0 }

    # Serialize the whole tool_input so we catch content, new_string, edits[], etc.
    $content = $payload.tool_input | ConvertTo-Json -Depth 12 -Compress
    if ([string]::IsNullOrWhiteSpace($content)) { exit 0 }

    $hits = @()
    foreach ($p in $SECRET_PATTERNS) {
        $found = [regex]::Matches($content, $p.rx)
        foreach ($m in $found) {
            if (-not (Test-SafeContext $content $m.Value)) {
                $hits += $p.label
                break
            }
        }
    }

    if ($hits.Count -eq 0) { exit 0 }

    $ts = (Get-Date).ToString("o")
    $logDir = Split-Path $VIOLATIONS_LOG -Parent
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
    $path = $payload.tool_input.file_path
    Add-Content -Path $VIOLATIONS_LOG -Value "[$ts] [BLOCK] $($payload.tool_name) -> $path | $($hits -join ', ')"

    [Console]::Error.WriteLine("SECRET_SCAN_GATE: hardcoded secret detected ($($hits -join ', '))")
    [Console]::Error.WriteLine("  Secrets must live in .env and be read via os.getenv()/`$env:. Never write them to tracked files.")

    if ($ENFORCE_MODE) {
        [Console]::Error.WriteLine("  BLOCKED. Move the secret to .env, reference it indirectly, and retry.")
        exit 2
    }
    [Console]::Error.WriteLine("  (WARN-only mode - write allowed.)")
    exit 0
}
catch {
    [Console]::Error.WriteLine("SECRET_SCAN_GATE: hook error (failing open): $($_.Exception.Message)")
    exit 0
}
