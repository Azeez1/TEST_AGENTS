# Launch TradingView Desktop with Chrome DevTools Protocol enabled for the tradingview-mcp server.
# The repo's bundled launch_tv_debug.bat does not work for MSIX installs on Windows because its
# `dir /s` against WindowsApps fails on UWP ACLs. This launches the .exe directly.
#
# Usage: pwsh HEDGE_FUND/tools/launch_tv_debug.ps1 [port]

param(
    [int]$Port = 9222
)

$installLocation = (Get-AppxPackage -Name TradingView.Desktop -ErrorAction SilentlyContinue).InstallLocation
if (-not $installLocation) {
    Write-Host "TradingView MSIX package not found. Install TradingView Desktop from the Microsoft Store." -ForegroundColor Red
    exit 1
}
$tvExe = Join-Path $installLocation "TradingView.exe"

if (-not (Test-Path $tvExe)) {
    Write-Host "TradingView.exe not found at $tvExe (MSIX package present but exe missing)." -ForegroundColor Red
    exit 1
}

Write-Host "Stopping any running TradingView instances..." -ForegroundColor Cyan
Stop-Process -Name "TradingView" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "Launching TV with --remote-debugging-port=$Port..." -ForegroundColor Cyan
Start-Process -FilePath $tvExe -ArgumentList "--remote-debugging-port=$Port"

Write-Host "Waiting for CDP endpoint (up to 40s)..." -ForegroundColor Cyan
$ready = $false
for ($i = 0; $i -lt 40; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:$Port/json/version" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        $ready = $true
        Write-Host "CDP READY on port $Port (took ~${i}s)" -ForegroundColor Green
        Write-Host $resp.Content
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $ready) {
    Write-Host "CDP did not come up within 40 seconds. Check that TV is fully loaded and not blocked on a modal/login." -ForegroundColor Red
    exit 1
}
