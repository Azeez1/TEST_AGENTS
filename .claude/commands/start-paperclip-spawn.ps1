$env:Path = "C:\Users\sabaa\.local\node22;" + $env:Path
Set-Location "C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS"
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host " Paperclip Server (Node 22 portable)" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "Node version:" (node --version)
Write-Host "Working directory: $(Get-Location)"
Write-Host "Starting server... (postgres init takes ~60s)"
Write-Host ""
pnpm --prefix INFRASTRUCTURE/paperclip --filter @paperclipai/server exec tsx src/index.ts
