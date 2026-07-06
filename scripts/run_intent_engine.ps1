# run_intent_engine.ps1 - Windows Task Scheduler runner for the Dux Intent Signal Engine.
#
# WEEKLY-ROBUST DESIGN: the monolithic all-avenues scan can die hard (OOM / one
# collector taking the whole shared process down). This runner instead runs EACH
# of the 6 avenues as its OWN python process, so a single avenue crashing can
# never stop the others, then a final --export-only process assembles the
# combined customers/acquisitions lists + Google Sheet tabs + PIPELINE tab.
#
# Invokes ONLY python (run_intent_scan.py). It NEVER calls claude.exe, so a
# scheduled run can never bill the Anthropic API. ASCII-only, PowerShell 5.1 safe.
# Logs to LOGS\scheduled\intent-engine-<date>.log.
param(
    [int]$SinceDays = 7,
    [string]$Metros = "houston,atlanta"
)

$repo = "C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS"
Set-Location $repo

$logDir = Join-Path $repo "LOGS\scheduled"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ("intent-engine-{0}.log" -f (Get-Date -Format 'yyyy-MM-dd'))

function Write-Log($msg) {
    Add-Content -Path $log -Value ("[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg)
}

# Kill switch (same pattern as run_scheduled_claude.ps1): add 'intent-engine' to
# this list to make the scheduled task a no-op without unregistering it.
$disabledTasks = @()
if ($disabledTasks -contains 'intent-engine') {
    Write-Log "SKIPPED intent-engine - task disabled by operator"
    exit 0
}

$python = "C:\Python314\python.exe"
if (-not (Test-Path $python)) { $python = "python" }
$script = Join-Path $repo "SALES_TEAM\tools\intent_engine\run_intent_scan.py"
$dataHome = Join-Path $env:USERPROFILE ".dux_intent"

# --------------------------------------------------------------------------- #
# ONE-TIME PREP: kill any STRAY intent-scan python (leftover / concurrent runs
# hold the SQLite lock) and clear the WAL/SHM sidecar files. Only intent-scan
# processes are targeted by command line - unrelated python (e.g. a local
# webhook) is left untouched. Concurrent scans = lock errors, so this must run
# before the loop and the loop itself is strictly sequential (one at a time).
# --------------------------------------------------------------------------- #
Write-Log "=== START intent engine (per-avenue) since-days=$SinceDays metros=$Metros ==="

$killed = 0
try {
    $procs = Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='pythonw.exe'" -ErrorAction Stop |
        Where-Object { $_.CommandLine -and $_.CommandLine -like '*run_intent_scan.py*' }
    foreach ($p in $procs) {
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
        $killed++
    }
} catch {
    Write-Log ("WARNING: could not enumerate python processes ({0})" -f $_.Exception.Message)
}
if ($killed -gt 0) {
    Write-Log "killed $killed stray intent-scan python process(es)"
    Start-Sleep -Seconds 2
}

foreach ($sidecar in @("intent.db-wal", "intent.db-shm")) {
    $f = Join-Path $dataHome $sidecar
    if (Test-Path $f) {
        try {
            Remove-Item $f -Force -ErrorAction Stop
            Write-Log "cleared $sidecar"
        } catch {
            Write-Log ("WARNING: could not remove {0} ({1})" -f $sidecar, $_.Exception.Message)
        }
    }
}

# --------------------------------------------------------------------------- #
# PER-AVENUE COLLECTION: each avenue is its own process. One crashing avenue is
# logged and the loop CONTINUES to the next. --no-sheet keeps every collection
# run cheap; the sheet is written once at the end by the export step.
# --------------------------------------------------------------------------- #
$avenues = @("trucking", "manufacturing", "mechanical", "property_mgmt", "dead_listings", "pe_distress")
$results = @()

foreach ($avenue in $avenues) {
    Write-Log "--- avenue '$avenue' START ---"
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $argList = @($script, "--avenues", $avenue, "--metros", $Metros, "--since-days", "$SinceDays", "--no-sheet", "--scheduled")
    & $python @argList *>> $log
    $code = $LASTEXITCODE
    $sw.Stop()
    $secs = [math]::Round($sw.Elapsed.TotalSeconds, 1)
    $results += [pscustomobject]@{ Avenue = $avenue; Exit = $code; Seconds = $secs }
    if ($code -eq 0) {
        Write-Log "--- avenue '$avenue' DONE exit=0 ($secs s) ---"
    } else {
        Write-Log "--- avenue '$avenue' FAILED exit=$code ($secs s) - continuing to next avenue ---"
    }
}

# --------------------------------------------------------------------------- #
# FINAL ASSEMBLY: one --export-only process re-scores the persisted DB across
# ALL avenues and writes the combined customers/acquisitions CSVs + the Google
# Sheet tabs (CUSTOMERS/ACQUISITIONS/per-avenue/SUMMARY) + the PIPELINE tab.
# Degrades to CSV-only if the spreadsheet id / creds are absent.
# --------------------------------------------------------------------------- #
Write-Log "--- export-only assembly START ---"
$sw = [System.Diagnostics.Stopwatch]::StartNew()
& $python @($script, "--export-only", "--scheduled") *>> $log
$exportCode = $LASTEXITCODE
$sw.Stop()
$exportSecs = [math]::Round($sw.Elapsed.TotalSeconds, 1)
if ($exportCode -eq 0) {
    Write-Log "--- export-only assembly DONE exit=0 ($exportSecs s) ---"
} else {
    Write-Log "--- export-only assembly FAILED exit=$exportCode ($exportSecs s) ---"
}

# --------------------------------------------------------------------------- #
# ONE-LINE SUMMARY per avenue + final export status.
# --------------------------------------------------------------------------- #
Write-Log "=== SUMMARY ==="
foreach ($r in $results) {
    $status = if ($r.Exit -eq 0) { "OK" } else { "FAIL(exit=$($r.Exit))" }
    Write-Log ("  {0,-14} {1,-14} {2,6} s" -f $r.Avenue, $status, $r.Seconds)
}
$exportStatus = if ($exportCode -eq 0) { "OK" } else { "FAIL(exit=$exportCode)" }
Write-Log ("  {0,-14} {1,-14} {2,6} s" -f "export-only", $exportStatus, $exportSecs)

$failCount = ($results | Where-Object { $_.Exit -ne 0 }).Count
Write-Log ("=== END intent engine ({0}/{1} avenues ok, export {2}) ===" -f ($avenues.Count - $failCount), $avenues.Count, $exportStatus)

# Exit 0 as long as the export assembly succeeded; a single avenue failure does
# NOT fail the scheduled task (the whole point of per-avenue isolation).
if ($exportCode -eq 0) { exit 0 } else { exit 1 }
