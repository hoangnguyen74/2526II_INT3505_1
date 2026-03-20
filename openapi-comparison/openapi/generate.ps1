# Script sinh code tu OpenAPI spec
# Chay: .\generate.ps1

Write-Host "=== OpenAPI Code Generation ===" -ForegroundColor Cyan

# 1. Validate spec
Write-Host "`n[1] Validating spec..." -ForegroundColor Yellow
npx @apidevtools/swagger-cli validate library-api.yaml

# 2. Generate Python client
Write-Host "`n[2] Generating Python client..." -ForegroundColor Yellow
npx @openapitools/openapi-generator-cli generate `
  -i library-api.yaml `
  -g python `
  -o generated/python-client `
  --additional-properties=packageName=library_client

# 3. Generate HTML docs
Write-Host "`n[3] Generating HTML documentation..." -ForegroundColor Yellow
npx @redocly/cli build-docs library-api.yaml -o generated/docs.html

Write-Host "`n=== Done! Check generated/ folder ===" -ForegroundColor Green
