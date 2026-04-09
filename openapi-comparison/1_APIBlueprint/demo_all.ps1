# Kịch bản Demo Toàn diện API Blueprint
# Chay file: .\demo_all.ps1

Write-Host "========== API BLUEPRINT FULL DEMO ==========" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path generated | Out-Null

# 1. Sinh HTML Docs bằng Aglio
Write-Host "`n[1] Generating HTML Docs voi Aglio..." -ForegroundColor Yellow
npx aglio -i library-api.apib -o generated/docs_demo.html
Write-Host "-> Da sinh tai lieu o generated/docs_demo.html" -ForegroundColor Gray

# 2. Khoi dong Mock Server bằng Drakov
Write-Host "`n[2] Starting Mock Server (Drakov) tren port 3500..." -ForegroundColor Yellow
$drakovProcess = Start-Process -FilePath "npx.cmd" -ArgumentList "drakov -f library-api.apib -p 3500" -PassThru -NoNewWindow
Start-Sleep -Seconds 5 # Cho server len

# 3. Chay Mock Test bằng Dredd
Write-Host "`n[3] Running Mock Tests (Dredd) chong lai Mock Server vua dung..." -ForegroundColor Yellow
npx dredd library-api.apib http://localhost:3500

# 4. Tat Mock Server sau khi Test xong
Write-Host "`n[4] Shutting down Mock Server..." -ForegroundColor Yellow
if ($drakovProcess -and -not $drakovProcess.HasExited) {
    Stop-Process -Id $drakovProcess.Id -Force
}

Write-Host "`n========== DEMO HOAN TAT ==========" -ForegroundColor Green
