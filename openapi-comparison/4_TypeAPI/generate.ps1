# Script sinh code tu TypeAPI spec
# Chay: .\generate.ps1

Write-Host "=== TypeAPI Code Generation ===" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path generated | Out-Null
New-Item -ItemType Directory -Force -Path generated/python-client | Out-Null

Write-Host "`n[Luu y] TypeAPI su dung cong cu SDKgen (php) de thuc thi." -ForegroundColor DarkGray
Write-Host "Kiem tra xem may co PHP hay khong...`n"

try {
    $php_version = php -v 2>&1
    Write-Host "[1] PHP da duoc cai dat. Tien hanh tai sdkgen.phar..." -ForegroundColor Green
    if (-Not (Test-Path "sdkgen.phar")) {
        Invoke-WebRequest -Uri "https://github.com/apioo/sdkgen-cli/releases/latest/download/sdkgen.phar" -OutFile "sdkgen.phar"
    }

    Write-Host "`n[2] Generating Python Client..." -ForegroundColor Yellow
    php sdkgen.phar generate -i library-api.json -d python -o generated/python-client
    
} catch {
    Write-Host "ERROR: Khong tim thay PHP tren may tinh cua ban!" -ForegroundColor Red
    Write-Host "=> TypeAPI yeu cau PHP de chay SDKgen. Do do qua trinh auto-build bi bo qua." -ForegroundColor Yellow
    
    # Tao mock file de folder ko bi rong
    Set-Content -Path "generated/python-client/MOCK_WARNING.md" -Value "May tinh cua ban hien chua cai dat PHP. De xem file code client thuc te duoc sinh ra tu sdkgen cua TypeAPI, hay cai dat PHP roi chay lai nhe."
    Write-Host "Da tao file canh bao MOCK_WARNING_PHP vao folder generated/" -ForegroundColor Gray
}

Write-Host "`nTypeAPI the manh nhat la gen Type-Safe Client. De tao FastAPI Server stub, ta thuong phai convert nguoc JSON qua OpenAPI truoc. (SDKgen ho tro xuat OpenAPI)." -ForegroundColor Magenta

Write-Host "`n=== Done! ===" -ForegroundColor Green
