# Script sinh docs tu RAML
# Chay: .\generate.ps1

Write-Host "=== RAML Code Generation ===" -ForegroundColor Cyan

# 1. Render HTML docs
Write-Host "`n[1] Rendering HTML documentation..." -ForegroundColor Yellow
npx raml2html library-api.raml > generated/docs.html

# 2. Convert to OpenAPI
Write-Host "`n[2] Converting to OpenAPI format..." -ForegroundColor Yellow
npx oas-raml-converter --from RAML --to OAS30 library-api.raml > generated/openapi-output.yaml

Write-Host "`n=== Done! Check generated/ folder ===" -ForegroundColor Green
