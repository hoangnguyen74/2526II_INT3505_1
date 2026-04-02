# Script sinh code tu API Blueprint spec
# Chay: .\generate.ps1

Write-Host "=== API Blueprint Code Generation ===" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path generated | Out-Null

# 1. Generate HTML docs
Write-Host "`n[1] Generating HTML documentation (with Aglio)..." -ForegroundColor Yellow
npx aglio -i library-api.apib -o generated/docs.html

# 2. Convert to OpenAPI de gen code
Write-Host "`n[2] Converting API Blueprint to OpenAPI..." -ForegroundColor Yellow
npx apib2swagger -i library-api.apib -o library-api.yaml

# 3. Generate Python client
Write-Host "`n[3] Generating Python client..." -ForegroundColor Yellow
npx @openapitools/openapi-generator-cli generate `
  -i library-api.yaml `
  -g python `
  -o generated/python-client `
  --additional-properties=packageName=library_client

# 4. Generate Python FastAPI Server
Write-Host "`n[4] Generating Python FastAPI server..." -ForegroundColor Yellow
npx @openapitools/openapi-generator-cli generate `
  -i library-api.yaml `
  -g python-fastapi `
  -o generated/python-fastapi `
  --additional-properties=packageName=library_server

Write-Host "`n=== Done! Check generated/ folder ===" -ForegroundColor Green
