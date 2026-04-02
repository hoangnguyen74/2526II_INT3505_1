# Script sinh code tu TypeSpec spec
# Chay: .\generate.ps1

Write-Host "=== TypeSpec Code Generation ===" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path generated | Out-Null

# 1. Compile sang OpenAPI
Write-Host "`n[1] Compiling TypeSpec to OpenAPI..." -ForegroundColor Yellow
npx @typespec/compiler compile main.tsp
# Kết quả mặc định sinh ra tại tsp-output/@typespec/openapi3/openapi.yaml

$OPENAPI_FILE = "tsp-output/@typespec/openapi3/openapi.yaml"

# 2. Generate Python client
Write-Host "`n[2] Generating Python client..." -ForegroundColor Yellow
npx @openapitools/openapi-generator-cli generate `
  -i $OPENAPI_FILE `
  -g python `
  -o generated/python-client `
  --additional-properties=packageName=library_client

# 3. Generate Python FastAPI Server
Write-Host "`n[3] Generating Python FastAPI server..." -ForegroundColor Yellow
npx @openapitools/openapi-generator-cli generate `
  -i $OPENAPI_FILE `
  -g python-fastapi `
  -o generated/python-fastapi `
  --additional-properties=packageName=library_server

Write-Host "`n=== Done! Check generated/ folder ===" -ForegroundColor Green
