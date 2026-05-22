# demo.ps1 - Kich ban demo buoi 13: API as a Product
# Yeu cau: app dang chay
#   py -m uvicorn main:app --reload
# Chay: PowerShell -ExecutionPolicy Bypass -File demo.ps1

$BASE = "http://localhost:8000"
$ADMIN = "admin-secret-key"

function Title($text) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Magenta
    Write-Host "  $text" -ForegroundColor Magenta
    Write-Host "============================================================" -ForegroundColor Magenta
}

function Step($text) {
    Write-Host ""
    Write-Host "-- $text" -ForegroundColor Cyan
}

function Pause {
    Write-Host ""
    Write-Host "[Nhan Enter de tiep tuc...]" -ForegroundColor Yellow
    Read-Host | Out-Null
}

# -------------------------------------------------------
Title "DEMO BUOI 13 - API as a Product"
Write-Host ""
Write-Host "  Swagger UI     : $BASE/docs"
Write-Host "  Developer Portal: mo portal.html trong trinh duyet"

Pause


# -------------------------------------------------------
Title "DEMO 1 - Developer Experience (DX)"

Step "Buoc 1: Sandbox -- khong can key, ai cung goi duoc"
$sandbox = Invoke-RestMethod "$BASE/sandbox/products"
Write-Host "  Sandbox products (co [DEMO] prefix):"
$sandbox.products | Select-Object -First 3 | ForEach-Object {
    Write-Host "    $($_.name) -- $($_.price) VND"
}
Write-Host "  Register hint: $($sandbox.register_hint)" -ForegroundColor Yellow

Step "Buoc 2: Xem bang gia"
$plans = Invoke-RestMethod "$BASE/plans"
$plans.PSObject.Properties | ForEach-Object {
    $p = $_.Value
    Write-Host "  $($_.Name.ToUpper()): $($p.price_usd)/thang | $($p.daily_limit) req/ngay | features: $($p.features -join ', ')"
}

Step "Buoc 3: Dang ky -- nhan API key ngay (time-to-first-call < 1 phut)"
try {
    $reg = Invoke-RestMethod -Method POST "$BASE/developers/register" `
      -ContentType "application/json" `
      -Body '{"name":"Demo User","email":"demo@test.com","plan":"free"}'
    $script:key = $reg.api_key
} catch {
    # Da ton tai, lay key tu alice
    $script:key = "sk_free_alice123"
    Write-Host "  [!] demo@test.com da ton tai, dung key mac dinh" -ForegroundColor Yellow
}
Write-Host "  API Key: $($script:key)" -ForegroundColor Green
Write-Host "  Plan: free | Quota: 100 req/ngay"

Step "Buoc 4: Goi API voi key -- xem response headers quota"
$resp = Invoke-WebRequest -Uri "$BASE/api/v1/products" `
  -Headers @{"X-API-Key" = $script:key} -UseBasicParsing
Write-Host "  HTTP $($resp.StatusCode)"
Write-Host "  X-Plan            : $($resp.Headers['X-Plan'])"
Write-Host "  X-Quota-Limit     : $($resp.Headers['X-Quota-Limit'])"
Write-Host "  X-Quota-Remaining : $($resp.Headers['X-Quota-Remaining'])"
Write-Host "  X-Response-Time   : $($resp.Headers['X-Response-Time'])"

Write-Host ""
Write-Host "  [OK] Developer tu dang ky, lay key, goi API trong < 1 phut" -ForegroundColor Green

Pause


# -------------------------------------------------------
Title "DEMO 2 - Quota Enforcement & Auth"

Step "Goi khong co API key --> 422 Unprocessable"
try {
    Invoke-RestMethod "$BASE/api/v1/products" | Out-Null
} catch {
    Write-Host "  [OK] $($_.ErrorDetails.Message)" -ForegroundColor Green
}

Step "Key sai --> 401 Unauthorized"
try {
    Invoke-RestMethod "$BASE/api/v1/products" `
      -Headers @{"X-API-Key" = "sk_invalid_key"} | Out-Null
} catch {
    Write-Host "  [OK] $($_.ErrorDetails.Message)" -ForegroundColor Green
}

Step "Feature gating: Search chi cho Pro+ (dung Free key --> 403)"
try {
    Invoke-RestMethod "$BASE/api/v1/search?q=iphone" `
      -Headers @{"X-API-Key" = $script:key} | Out-Null
    Write-Host "  UNEXPECTED: khong co loi!" -ForegroundColor Red
} catch {
    Write-Host "  [OK] Free plan bi chan: $($_.ErrorDetails.Message)" -ForegroundColor Green
}

Step "Nang cap len Pro -- mo khoa Search"
Invoke-RestMethod -Method POST "$BASE/developers/upgrade" `
  -ContentType "application/json" `
  -Body "{`"email`":`"demo@test.com`",`"new_plan`":`"pro`"}" | Out-Null
Write-Host "  Da nang cap len Pro (10000 req/ngay, $29/thang)"

$search = Invoke-RestMethod "$BASE/api/v1/search?q=iphone" `
  -Headers @{"X-API-Key" = $script:key}
Write-Host "  Search thanh cong: $($search.results.Count) ket qua cho 'iphone'"

Step "Xem usage cua developer"
$usage = Invoke-RestMethod "$BASE/developers/demo@test.com/usage"
Write-Host "  Hom nay dung: $($usage.today.used)/$($usage.today.limit) ($($usage.today.remaining) con lai)"

Write-Host ""
Write-Host "  [OK] Freemium model: free thi han che, tra tien thi mo tinh nang" -ForegroundColor Green

Pause


# -------------------------------------------------------
Title "DEMO 3 - KPI Analytics (Admin Dashboard)"

Step "Goi tat ca 3 endpoints voi 3 accounts de co du lieu"
$accounts = @(
    @{email="alice@example.com"; key="sk_free_alice123"},
    @{email="bob@example.com";   key="sk_pro_bob456"}
)
foreach ($acc in $accounts) {
    for ($i = 1; $i -le 5; $i++) {
        try {
            Invoke-RestMethod "$BASE/api/v1/products" `
              -Headers @{"X-API-Key" = $acc.key} | Out-Null
        } catch { }
    }
}
Write-Host "  Da tao du lieu tu nhieu accounts"

Step "Admin: KPI Dashboard"
$analytics = Invoke-RestMethod "$BASE/admin/analytics" `
  -Headers @{"X-Admin-Key" = $ADMIN}

Write-Host ""
Write-Host "  === KPI DASHBOARD ===" -ForegroundColor Yellow
Write-Host "  Registered developers  : $($analytics.registered_developers)"
Write-Host "  Active today           : $($analytics.active_developers_today)"
Write-Host "  Total API calls        : $($analytics.total_api_calls)"
Write-Host "  Error rate             : $($analytics.error_rate_percent)%"
Write-Host "  MRR (Monthly Revenue)  : `$$($analytics.monthly_recurring_revenue_usd)"
Write-Host ""
Write-Host "  Calls by plan:"
$analytics.calls_by_plan.PSObject.Properties | ForEach-Object {
    Write-Host "    $($_.Name): $($_.Value) calls"
}
Write-Host ""
Write-Host "  Top endpoints:"
$analytics.top_endpoints | Select-Object -First 3 | ForEach-Object {
    Write-Host "    $($_.endpoint): $($_.calls) calls"
}

Step "Admin: Danh sach developers + revenue"
$devs = Invoke-RestMethod "$BASE/admin/developers" `
  -Headers @{"X-Admin-Key" = $ADMIN}
Write-Host "  Total: $($devs.total) developers"
$devs.developers | ForEach-Object {
    Write-Host "    $($_.email) | $($_.plan) | calls_today=$($_.calls_today) | revenue=`$$($_.monthly_revenue_usd)/mo"
}

Write-Host ""
Write-Host "  [OK] Co the theo doi MRR, error rate, top endpoints, revenue per developer" -ForegroundColor Green

Pause


# -------------------------------------------------------
Title "DEMO 4 - Developer Portal (portal.html)"

Write-Host ""
Write-Host "  Huong dan demo portal.html:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Mo file portal.html trong trinh duyet (double-click)"
Write-Host "     --> Thay Live Stats tu cap nhat moi 5 giay"
Write-Host ""
Write-Host "  2. Pricing section:"
Write-Host "     --> Free / Pro / Enterprise voi tinh nang va gia"
Write-Host ""
Write-Host "  3. Register form:"
Write-Host "     --> Nhap ten, email, chon plan Free"
Write-Host "     --> Bam Register --> API key hien thi ngay"
Write-Host ""
Write-Host "  4. My Usage:"
Write-Host "     --> Nhap email vua dang ky"
Write-Host "     --> Thanh quota doi mau: xanh (<50%), vang (50-80%), do (>80%)"
Write-Host ""
Write-Host "  5. Quick Start tabs:"
Write-Host "     --> Copy code mau curl / Python / JavaScript"
Write-Host ""
Write-Host "  [Luu y]: App phai dang chay tai localhost:8000 portal moi lay duoc du lieu" -ForegroundColor Yellow

Pause


# -------------------------------------------------------
Title "DEMO 5 - Business Model Canvas"

Write-Host ""
Write-Host "  Mo file: 13_api_as_product\business_model_canvas.md"
Write-Host ""
Write-Host "  Diem chinh can giai thich cho lop:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  [Customer Segments]"
Write-Host "    Free: nha phat trien ca nhan, sinh vien, startup"
Write-Host "    Pro : cong ty vua (main revenue source)"
Write-Host "    Enterprise: tap doan lon (high value, custom contract)"
Write-Host ""
Write-Host "  [Revenue Streams]"
Write-Host "    Freemium: 2-5% convert Free->Pro = profitable"
Write-Host "    Pay-per-call: scale theo usage"
Write-Host ""
Write-Host "  [KPIs quan trong]"
Write-Host "    MRR   = Monthly Recurring Revenue"
Write-Host "    Churn = % cancel plan / thang"
Write-Host "    ARPU  = Average Revenue Per User"
Write-Host "    Conversion rate = % Free->Pro"
Write-Host ""
Write-Host "  [Thao luan nhom]: Ap dung BMC cho API nhom dang lam" -ForegroundColor Cyan


# -------------------------------------------------------
Title "XONG! Tom tat da demo"

Write-Host ""
Write-Host "  1. DEVELOPER EXPERIENCE --> Sandbox, dang ky, key trong < 1 phut" -ForegroundColor White
Write-Host "  2. QUOTA ENFORCEMENT    --> 422 khong co key, 401 key sai, headers X-Quota-*" -ForegroundColor White
Write-Host "  3. FEATURE GATING       --> Search chi cho Pro+, 403 cho Free" -ForegroundColor White
Write-Host "  4. KPI ANALYTICS        --> MRR, error rate, top endpoints (admin)" -ForegroundColor White
Write-Host "  5. DEVELOPER PORTAL     --> portal.html: pricing, register, usage bar" -ForegroundColor White
Write-Host "  6. BUSINESS MODEL       --> Freemium, conversion funnel, BMC" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
