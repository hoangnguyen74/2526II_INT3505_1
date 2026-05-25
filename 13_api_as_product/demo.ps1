# demo.ps1 - Demo buoi 13: API as a Product (20 phut)
# Yeu cau: py -m uvicorn main:app --reload (dang chay o terminal khac)
# Chay: PowerShell -ExecutionPolicy Bypass -File demo.ps1

$BASE  = "http://localhost:8000"
$ADMIN = "admin-secret-key"
$EMAIL = "demo@test.com"

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
Title "DEMO A - Developer Journey"

Step "1. Sandbox -- khong can key, ai cung goi duoc"
$sandbox = Invoke-RestMethod "$BASE/sandbox/products"
Write-Host "  sandbox = $($sandbox.sandbox)"
$sandbox.data | ForEach-Object {
    Write-Host "    $($_.name) -- $($_.price) VND"
}
Write-Host "  CTA: $($sandbox.get_real_data)" -ForegroundColor Yellow

Step "2. Xem bang gia (3 tiers)"
$plans = Invoke-RestMethod "$BASE/plans"
$plans.plans.PSObject.Properties | ForEach-Object {
    $p = $_.Value
    $quota = if ($p.daily_quota) { "$($p.daily_quota) req/ngay" } else { "Unlimited" }
    Write-Host "  $($_.Name.ToUpper()): `$$($p.price_usd)/thang | $quota | $($p.features -join ', ')"
}

Step "3. Dang ky developer -- nhan key NGAY (time-to-first-call < 1 phut)"
try {
    $reg = Invoke-RestMethod -Method POST "$BASE/developers/register" `
      -ContentType "application/json" `
      -Body "{`"name`":`"Demo User`",`"email`":`"$EMAIL`",`"plan`":`"free`"}"
    $script:key = $reg.api_key
    Write-Host "  $($reg.message)" -ForegroundColor Green
} catch {
    # Email da ton tai -- lay key tu /admin/developers
    Write-Host "  [!] $EMAIL da ton tai, lay key tu admin..." -ForegroundColor Yellow
    $devs = Invoke-RestMethod "$BASE/admin/developers" -Headers @{"X-Admin-Key" = $ADMIN}
    $found = $devs.developers | Where-Object { $_.email -eq $EMAIL }
    if ($found) {
        $usage = Invoke-RestMethod "$BASE/developers/$EMAIL/usage"
        $script:key = $usage.api_key
    } else {
        $script:key = ($devs.developers | Select-Object -First 1).email
        $usage = Invoke-RestMethod "$BASE/developers/$($script:key)/usage"
        $script:key = $usage.api_key
    }
}
Write-Host "  API Key: $($script:key)" -ForegroundColor Green

Step "4. Goi API voi key -- xem quota headers"
$resp = Invoke-WebRequest -Uri "$BASE/api/v1/products" `
  -Headers @{"X-API-Key" = $script:key} -UseBasicParsing
Write-Host "  HTTP $($resp.StatusCode)"
Write-Host "  X-Plan            : $($resp.Headers['X-Plan'])"
Write-Host "  X-Quota-Limit     : $($resp.Headers['X-Quota-Limit'])"
Write-Host "  X-Quota-Remaining : $($resp.Headers['X-Quota-Remaining'])"
Write-Host "  X-Response-Time   : $($resp.Headers['X-Response-Time'])"

Step "5. Feature Gating: Search bi chan cho Free (403)"
try {
    Invoke-RestMethod "$BASE/api/v1/search?q=iphone" `
      -Headers @{"X-API-Key" = $script:key} | Out-Null
    Write-Host "  UNEXPECTED: khong bi chan!" -ForegroundColor Red
} catch {
    Write-Host "  --> 403 FEATURE_LOCKED (dung!)" -ForegroundColor Green
    Write-Host "  $($_.ErrorDetails.Message)" -ForegroundColor DarkGray
}

Step "6. Upgrade len Pro --> Search thanh cong"
Invoke-RestMethod -Method POST "$BASE/developers/upgrade" `
  -ContentType "application/json" `
  -Body "{`"email`":`"$EMAIL`",`"new_plan`":`"pro`"}" | Out-Null
Write-Host "  Da nang cap len Pro ($29/thang, 10000 req/ngay)"

$search = Invoke-RestMethod "$BASE/api/v1/search?q=iphone" `
  -Headers @{"X-API-Key" = $script:key}
Write-Host "  Search 'iphone': $($search.count) ket qua" -ForegroundColor Green
$search.data | ForEach-Object { Write-Host "    $($_.name) -- $($_.price) VND" }

Step "7. Xem usage"
$usage = Invoke-RestMethod "$BASE/developers/$EMAIL/usage"
Write-Host "  Hom nay: $($usage.today.used)/$($usage.today.quota) ($($usage.today.remaining) con lai)"

Write-Host ""
Write-Host "  [OK] Developer tu sandbox -> dang ky -> goi API -> upgrade trong vai phut" -ForegroundColor Green

Pause


# -------------------------------------------------------
Title "DEMO B - Admin KPI Dashboard"

Step "Tao them traffic de co du lieu"
$devs = Invoke-RestMethod "$BASE/admin/developers" -Headers @{"X-Admin-Key" = $ADMIN}
foreach ($dev in $devs.developers) {
    $devUsage = Invoke-RestMethod "$BASE/developers/$($dev.email)/usage"
    $k = $devUsage.api_key
    for ($i = 1; $i -le 3; $i++) {
        try { Invoke-RestMethod "$BASE/api/v1/products" -Headers @{"X-API-Key" = $k} | Out-Null } catch { }
    }
}
Write-Host "  Da tao traffic tu $($devs.total) accounts"

Step "KPI Dashboard (/admin/analytics)"
$kpi = Invoke-RestMethod "$BASE/admin/analytics" -Headers @{"X-Admin-Key" = $ADMIN}
Write-Host ""
Write-Host "  === KPI DASHBOARD ===" -ForegroundColor Yellow
Write-Host "  Registered developers : $($kpi.registered_developers)"
Write-Host "  Active today          : $($kpi.active_developers_today)"
Write-Host "  Total API calls       : $($kpi.total_api_calls)"
Write-Host "  Error rate            : $($kpi.error_rate_percent)%"
Write-Host "  MRR (doanh thu)       : `$$($kpi.monthly_recurring_revenue_usd)/thang"

Write-Host ""
Write-Host "  Calls by plan:"
$kpi.calls_by_plan.PSObject.Properties | ForEach-Object {
    Write-Host "    $($_.Name): $($_.Value) calls"
}

Write-Host ""
Write-Host "  Top endpoints:"
$kpi.top_endpoints | Select-Object -First 3 | ForEach-Object {
    Write-Host "    $($_.endpoint): $($_.calls) calls"
}

Step "Revenue breakdown (/admin/developers)"
$devs = Invoke-RestMethod "$BASE/admin/developers" -Headers @{"X-Admin-Key" = $ADMIN}
Write-Host "  Total MRR: `$$($devs.total_mrr)/thang" -ForegroundColor Yellow
$devs.developers | ForEach-Object {
    Write-Host "    $($_.email) | $($_.plan) | calls=$($_.total_calls) | `$$($_.monthly_rev_usd)/mo"
}

Write-Host ""
Write-Host "  [OK] Admin thay duoc MRR, error rate, top endpoints, revenue per dev" -ForegroundColor Green

Pause


# -------------------------------------------------------
Title "DEMO C - Developer Portal (portal.html)"

Write-Host ""
Write-Host "  Mo portal.html trong trinh duyet:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. LIVE STATS (goc tren) -- tu cap nhat moi 5 giay"
Write-Host "     Registered, Active, Total Calls, Error Rate, Uptime"
Write-Host ""
Write-Host "  2. PRICING -- 3 cards: Free / Pro (Popular) / Enterprise"
Write-Host "     So sanh tinh nang va gia"
Write-Host ""
Write-Host "  3. GET API KEY -- nhap ten + email + plan"
Write-Host "     Bam Register --> key hien ngay, copy duoc"
Write-Host ""
Write-Host "  4. MY USAGE -- nhap email"
Write-Host "     Thanh quota doi mau: xanh (<50%%) | vang (50-80%%) | do (>80%%)"
Write-Host ""
Write-Host "  5. QUICK START -- tabs curl / Python / JavaScript"
Write-Host "     Copy code mau chay ngay"
Write-Host ""
Write-Host "  [Luu y] App phai dang chay tai localhost:8000" -ForegroundColor Yellow

Pause


# -------------------------------------------------------
Title "TOM TAT"

Write-Host ""
Write-Host "  API as Product = DX + Monetization + Analytics" -ForegroundColor Yellow
Write-Host ""
Write-Host "  DX            : Sandbox, instant key, docs, quota headers" -ForegroundColor White
Write-Host "  Monetization  : Freemium (Free/Pro/Enterprise), Feature Gating" -ForegroundColor White
Write-Host "  Analytics     : MRR, error rate, conversion, active devs" -ForegroundColor White
Write-Host ""
Write-Host "  Quy tac vang: Toi uu cho developer truoc -- doanh thu theo sau." -ForegroundColor Green
Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
