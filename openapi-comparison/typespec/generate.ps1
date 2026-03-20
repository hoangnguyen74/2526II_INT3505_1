# Script compile TypeSpec va sinh code
# Chay: .\generate.ps1

Write-Host "=== TypeSpec Code Generation ===" -ForegroundColor Cyan

# 1. Install dependencies
Write-Host "`n[1] Installing TypeSpec dependencies..." -ForegroundColor Yellow
npm init -y 2>$null
npm install @typespec/compiler @typespec/http @typespec/rest @typespec/openapi3

# 2. Compile TypeSpec -> OpenAPI
Write-Host "`n[2] Compiling TypeSpec to OpenAPI..." -ForegroundColor Yellow
npx tsp compile main.tsp

# 3. Generate HTML docs from OpenAPI output
Write-Host "`n[3] Generating HTML documentation..." -ForegroundColor Yellow
npx @redocly/cli build-docs generated/openapi.yaml -o generated/docs.html

Write-Host "`n=== Done! Check generated/ folder ===" -ForegroundColor Green
Write-Host "  - generated/openapi.yaml  (OpenAPI output)" -ForegroundColor Gray
Write-Host "  - generated/docs.html     (HTML docs)" -ForegroundColor Gray
