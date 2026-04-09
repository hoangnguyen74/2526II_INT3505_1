# Script sinh code tu RAML spec
# Chay: .\generate.ps1

Write-Host "=== RAML Code Generation ===" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path generated | Out-Null

# 1. Convert to OpenAPI de gen code
Write-Host "`n[1] Converting RAML to OpenAPI..." -ForegroundColor Yellow
# Su dung npx -y ket hop cong cu chinh chu cua Mulesoft de tranh loi treo
npx -y oas-raml-converter --from RAML --to OAS20 ./library-api.raml ./library-api.yaml

# 2. Generate Python client
Write-Host "`n[2] Generating Python client..." -ForegroundColor Yellow
npx -y @openapitools/openapi-generator-cli generate `
  -i library-api.yaml `
  -g python `
  -o generated/python-client `
  --additional-properties=packageName=library_client

# 3. Generate Python FastAPI Server
Write-Host "`n[3] Generating Python FastAPI server..." -ForegroundColor Yellow
npx -y @openapitools/openapi-generator-cli generate `
  -i library-api.yaml `
  -g python-fastapi `
  -o generated/python-fastapi `
  --additional-properties=packageName=library_server

Write-Host "`n=== Done! Check generated/ folder ===" -ForegroundColor Green
