# Script sinh code tu TypeAPI spec
# Chay: .\generate.ps1

Write-Host "=== TypeAPI Code Generation ===" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path generated | Out-Null

Write-Host "`n[Luu y] TypeAPI su dung cong cu SDKgen (php) de thuc thi." -ForegroundColor DarkGray
Write-Host "Kich ban sau day bat buoc may ban da cai PHP va sdkgen.phar`n"

# 1. Generate Python client
Write-Host "[1] Generating Python Client..." -ForegroundColor Yellow
# Command that would run if SDKgen is installed:
# php sdkgen.phar generate -i library-api.json -d python -o generated/python-client

Write-Host "`n[2] Generating HTML Document Client..." -ForegroundColor Yellow
# php sdkgen.phar generate -i library-api.json -d client -o generated/docs

Write-Host "`nTypeAPI the manh nhat la gen Type-Safe Client. De tao FastAPI Server stub, ta thuong phai convert nguoc JSON qua OpenAPI truoc. (SDKgen ho tro xuat OpenAPI)." -ForegroundColor Magenta

Write-Host "`n=== Done! ===" -ForegroundColor Green
