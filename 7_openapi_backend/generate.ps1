# Chay script: .\generate.ps1
Write-Host "=== OpenAPI Backend Generation ===" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path backend-server | Out-Null

Write-Host "`n[1] Su dung openapi-generator tao source-code ung dung NodeJS..." -ForegroundColor Yellow
# Su dung nodejs-express-server template de gen ra cau truc model-controller route
npx -y @openapitools/openapi-generator-cli generate `
  -i product_api.yaml `
  -g nodejs-express-server `
  -o backend-server

Write-Host "`n=== Da generate boiler-plate thanh cong! Kiem tra folder backend-server ===" -ForegroundColor Green
