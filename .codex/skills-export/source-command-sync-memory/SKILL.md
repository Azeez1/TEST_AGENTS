---
name: "source-command-sync-memory"
description: "Copy local Codex memory stores to OneDrive so the other desktop can see them"
---

# source-command-sync-memory

Use this skill when the user asks to run the migrated source command `sync-memory`.

## Command Template

Sync local Codex memory to OneDrive backup so the other desktop sees the latest state.
Current Codex memory is SQLite-backed in `~/.codex`, while the old
`~/.Codex/projects/.../memory/` path may not exist.

Run this PowerShell command:

```powershell
$dst = "C:\Users\sabaa\OneDrive\Desktop\MEMORY\Codex-memory"
$allowedRoot = (Resolve-Path -LiteralPath "C:\Users\sabaa\OneDrive\Desktop\MEMORY").Path
if (-not (Test-Path -LiteralPath $dst)) { New-Item -ItemType Directory -Path $dst | Out-Null }
$resolvedDst = (Resolve-Path -LiteralPath $dst).Path
if (-not $resolvedDst.StartsWith($allowedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to sync outside MEMORY folder: $resolvedDst"
}

$memoriesDst = Join-Path $resolvedDst "memories"
if (-not (Test-Path -LiteralPath $memoriesDst)) { New-Item -ItemType Directory -Path $memoriesDst | Out-Null }
robocopy "C:\Users\sabaa\.codex\memories" $memoriesDst /MIR /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -gt 7) { throw "robocopy failed with exit code $LASTEXITCODE" }

Copy-Item -LiteralPath "C:\Users\sabaa\.codex\memories_1.sqlite" -Destination (Join-Path $resolvedDst "memories_1.sqlite") -Force
$sqliteDst = Join-Path $resolvedDst "sqlite"
if (-not (Test-Path -LiteralPath $sqliteDst)) { New-Item -ItemType Directory -Path $sqliteDst | Out-Null }
Copy-Item -LiteralPath "C:\Users\sabaa\.codex\sqlite\memories_1.sqlite" -Destination (Join-Path $sqliteDst "memories_1.sqlite") -Force

$files = Get-ChildItem -LiteralPath $resolvedDst -Recurse -File -ErrorAction SilentlyContinue
$count = @($files).Count
$size = ($files | Measure-Object -Property Length -Sum).Sum
if ($null -eq $size) { $size = 0 }
$sizeLabel = if ($size -ge 1GB) { "{0:N2} GB" -f ($size / 1GB) } elseif ($size -ge 1MB) { "{0:N2} MB" -f ($size / 1MB) } elseif ($size -ge 1KB) { "{0:N2} KB" -f ($size / 1KB) } else { "$size B" }
"Synced $count files | $sizeLabel | $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
```

Report back the file count, size, and timestamp from the output.
