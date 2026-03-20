# Script sinh docs/mock tu API Blueprint
# Chay: .\generate.ps1

Write-Host "=== API Blueprint Code Generation ===" -ForegroundColor Cyan

# 1. Render HTML docs
Write-Host "`n[1] Rendering HTML documentation..." -ForegroundColor Yellow
npx snowboard html -o generated/docs.html library-api.apib

# 2. Convert to OpenAPI
Write-Host "`n[2] Converting to OpenAPI format..." -ForegroundColor Yellow
npx apib2swagger -i library-api.apib -o generated/openapi-output.yaml

# 3. Start mock server (foreground)
Write-Host "`n[3] Starting mock server on port 4000..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
npx drakov -f library-api.apib --port 4000
