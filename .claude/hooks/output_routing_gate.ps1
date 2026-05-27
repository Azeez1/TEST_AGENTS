# Output Routing Gate (Lesson 2 + Lesson 5)
#
# PreToolUse hook that inspects Write/Edit file paths against routing convention.
# Phase C-1 deployment: WARN-only. Violations are logged to LOGS/routing-violations.log
# but do not block. Flip $ENFORCE_MODE to $true after observation period (~7 days clean)
# to convert WARNs into BLOCKs.
#
# Scope: MARKETING_TEAM and PROPOSAL_TEAM only this pass. Other teams allowed silently.
#
# Wired in .claude/settings.local.json under hooks.PreToolUse.

$ErrorActionPreference = "Stop"

# --- TOGGLE: flip to $true to enforce ---------------------------------
$ENFORCE_MODE = $false

# --- Paths ------------------------------------------------------------
$VIOLATIONS_LOG = Join-Path $PSScriptRoot "..\..\LOGS\routing-violations.log"
$REPO_ROOT      = "C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS"

# --- File-extension sets ----------------------------------------------
# Content files that should NEVER live bare at outputs/ or docs/ root
$CONTENT_EXTS = @(".md", ".pdf", ".docx", ".jpg", ".jpeg", ".png", ".json", ".txt", ".csv", ".html", ".xlsx", ".pptx")

# Files allowed at repo root (whitelist)
$ROOT_ALLOWED = @(
    "CLAUDE.md", "README.md", "AGENTS.md",
    "MULTI_AGENT_GUIDE.md", "CLAUDE_REFERENCE.md", "MCP_SETUP.md",
    "TOOL_REGISTRY.md", "LLAR_CONFIG.json",
    "MEMORY_ROUTING.md",
    ".gitignore", ".gitattributes",
    "package.json", "pnpm-lock.yaml", "package-lock.json",
    "MEMORY.md", "skills-lock.json"
)

# MARKETING_TEAM/docs allowed subfolders (per docs_folder_structure.json)
$MKT_DOCS_SUBS = @("getting-started", "guides", "architecture", "reference")

# --- Classify a normalized relative path ------------------------------
function Get-Verdict($rel) {
    $parts = $rel -split '/'
    $top = $parts[0]
    $ext = [System.IO.Path]::GetExtension($rel).ToLower()

    # CASE 1: file at repo root (no slash in path)
    if ($parts.Length -eq 1) {
        if ($ROOT_ALLOWED -contains $rel) { return @{ v = "ALLOW"; r = "" } }
        # Hidden files (.something) at root are usually config - allow
        if ($rel.StartsWith(".")) { return @{ v = "ALLOW"; r = "" } }
        return @{ v = "WARN"; r = "Repo-root writes are forbidden per CLAUDE.md. Use {TEAM}/outputs/{subfolder}/" }
    }

    # CASE 2: docs/ - ADR + general docs enforcement
    if ($top -eq "docs") {
        $section = if ($parts.Length -ge 2) { $parts[1] } else { "" }
        $third   = if ($parts.Length -ge 3) { $parts[2] } else { "" }

        # docs/file.md at bare root - must be in a subfolder
        if ($parts.Length -eq 2 -and $CONTENT_EXTS -contains $ext) {
            return @{ v = "WARN"; r = "docs/ requires a subfolder. ADRs go in docs/adr/. General docs need a topic subfolder." }
        }

        # docs/adr/...
        if ($section -eq "adr") {
            # docs/adr/file at adr root - must be ADR-NNNN-kebab.md or README.md
            if ($parts.Length -eq 3 -and $ext -eq ".md") {
                if ($third -eq "README.md") {
                    return @{ v = "ALLOW"; r = "" }
                }
                if ($third -notmatch '^ADR-\d{4}-[a-z0-9\-]+\.md$') {
                    return @{ v = "WARN"; r = "ADR files must match pattern: ADR-NNNN-kebab-case.md (got: $third)" }
                }
            }
            # docs/adr/<deeper>/... - allow (supporting assets like images)
            return @{ v = "ALLOW"; r = "" }
        }

        # Other docs/ subfolders - allow for now (more conventions may come later)
        return @{ v = "ALLOW"; r = "" }
    }

    # CASE 3: not in MARKETING_TEAM, PROPOSAL_TEAM, or VOICE_TEAM - out of scope
    if ($top -ne "MARKETING_TEAM" -and $top -ne "PROPOSAL_TEAM" -and $top -ne "VOICE_TEAM") {
        return @{ v = "ALLOW"; r = "" }
    }

    # CASE 3: MARKETING_TEAM, PROPOSAL_TEAM, and VOICE_TEAM enforcement
    $section = $parts[1]

    # 3a - bare file in TEAM/ root (e.g. MARKETING_TEAM/blog.md, VOICE_TEAM/something.json)
    # README.md and DEMO_RUNBOOK.md are explicitly allowed at the team root.
    $TEAM_ROOT_ALLOWED = @("README.md", "DEMO_RUNBOOK.md", "AGENTS.md")
    if ($parts.Length -eq 2 -and $CONTENT_EXTS -contains $ext) {
        if ($TEAM_ROOT_ALLOWED -contains $parts[1]) {
            return @{ v = "ALLOW"; r = "" }
        }
        return @{ v = "WARN"; r = "$top requires output to be inside outputs/<subfolder>/, not bare at team root" }
    }

    # 3b - TEAM/outputs/...
    if ($section -eq "outputs") {
        # outputs/file.md (bare content file at outputs root) - WARN
        if ($parts.Length -eq 3 -and $CONTENT_EXTS -contains $ext) {
            return @{ v = "WARN"; r = "$top/outputs/ requires a subfolder. Got bare file: $rel" }
        }
        # outputs/<subfolder>/... - ALLOW (any subfolder, including _dumps/ for VOICE_TEAM debug artifacts)
        return @{ v = "ALLOW"; r = "" }
    }

    # 3c - MARKETING_TEAM/docs/ (strict canonical subfolders per docs_folder_structure.json)
    if ($top -eq "MARKETING_TEAM" -and $section -eq "docs") {
        if ($parts.Length -eq 3 -and $CONTENT_EXTS -contains $ext) {
            return @{ v = "WARN"; r = "MARKETING_TEAM/docs/ requires subfolder: getting-started, guides, architecture, or reference" }
        }
        if ($parts.Length -ge 3) {
            $third = $parts[2]
            if ($MKT_DOCS_SUBS -notcontains $third) {
                return @{ v = "WARN"; r = "MARKETING_TEAM/docs/$third is not a canonical subfolder (use getting-started/guides/architecture/reference)" }
            }
        }
        return @{ v = "ALLOW"; r = "" }
    }

    # 3d - any other section (memory, logs, examples, templates, tools, ...) - ALLOW
    return @{ v = "ALLOW"; r = "" }
}

# --- Main -------------------------------------------------------------
try {
    $stdin = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($stdin)) { exit 0 }

    $payload = $stdin | ConvertFrom-Json

    # Only inspect file-writing tools
    $relevantTools = @("Write", "Edit", "MultiEdit", "NotebookEdit")
    if ($relevantTools -notcontains $payload.tool_name) { exit 0 }

    # Extract path
    $path = $payload.tool_input.file_path
    if ([string]::IsNullOrWhiteSpace($path)) {
        $path = $payload.tool_input.notebook_path
    }
    if ([string]::IsNullOrWhiteSpace($path)) { exit 0 }

    # Normalize: forward slashes, strip repo-root prefix
    $normalized = $path -replace '\\', '/'
    $rootNormalized = $REPO_ROOT -replace '\\', '/'
    $relPath = $normalized
    if ($normalized -like "$rootNormalized/*") {
        $relPath = $normalized.Substring($rootNormalized.Length + 1)
    } elseif ($normalized -eq $rootNormalized) {
        exit 0
    } elseif (-not [System.IO.Path]::IsPathRooted($path)) {
        # Already a relative path; strip leading ./
        $relPath = $relPath -replace '^\./',''
    } else {
        # Absolute path outside the repo - allow (could be user's home, temp, etc.)
        exit 0
    }

    $result = Get-Verdict $relPath

    if ($result.v -eq "ALLOW") { exit 0 }

    # WARN or BLOCK path - log + stderr
    $ts = (Get-Date).ToString("o")
    $logDir = Split-Path $VIOLATIONS_LOG -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    $logEntry = "[$ts] [$($result.v)] $($payload.tool_name) -> $relPath | $($result.r)"
    Add-Content -Path $VIOLATIONS_LOG -Value $logEntry

    [Console]::Error.WriteLine("ROUTING_GATE: [$($result.v)] $relPath")
    [Console]::Error.WriteLine("  $($result.r)")

    if ($ENFORCE_MODE) {
        [Console]::Error.WriteLine("ROUTING_GATE: ENFORCE_MODE is ON - blocking this write.")
        exit 2
    }

    # WARN-only mode: log + warn but allow
    [Console]::Error.WriteLine("  (WARN-only mode - write allowed. Flip `$ENFORCE_MODE to `$true to block.)")
    exit 0
}
catch {
    # Hook errors must NEVER block the user's tool call - fail open.
    [Console]::Error.WriteLine("ROUTING_GATE: hook script error: $($_.Exception.Message)")
    exit 0
}
