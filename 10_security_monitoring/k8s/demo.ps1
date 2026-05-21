# demo.ps1 - Kich ban demo buoi 10: Kubernetes Observability
# Yeu cau: 4 terminal port-forward dang chay
#   App      : kubectl port-forward svc/payment-api 8000:8000 -n monitoring
#   Grafana  : kubectl port-forward svc/kube-prom-grafana 3000:80 -n monitoring
#   Jaeger   : kubectl port-forward svc/jaeger-query 16686:16686 -n monitoring
#   Prometheus: kubectl port-forward svc/kube-prom-kube-prometheus-prometheus 9090:9090 -n monitoring
# Chay: PowerShell -ExecutionPolicy Bypass -File k8s\demo.ps1

$BASE = "http://localhost:8000"

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

function CallApi($uri, $label) {
    try {
        $r = Invoke-WebRequest -Uri $uri -UseBasicParsing -ErrorAction SilentlyContinue
        $status = $r.StatusCode
    } catch {
        $status = $_.Exception.Response.StatusCode.value__
        if (-not $status) { $status = "ERR" }
    }

    $color = "Gray"
    if ($status -eq 200 -or $status -eq 201) { $color = "Green" }
    elseif ($status -eq 429)                 { $color = "Yellow" }
    elseif ($status -eq 503 -or $status -eq 500) { $color = "Red" }

    Write-Host "  $label" -NoNewline
    Write-Host " --> HTTP $status" -ForegroundColor $color
    return $status
}

# -------------------------------------------------------
Title "DEMO BUOI 10 - Kubernetes Observability"
Write-Host ""
Write-Host "  App       : $BASE/docs"
Write-Host "  Grafana   : http://localhost:3000  (admin / admin123)"
Write-Host "  Jaeger    : http://localhost:16686"
Write-Host "  Prometheus: http://localhost:9090"

Pause


# -------------------------------------------------------
Title "DEMO 1 - Tao traffic co ban (Logs + Metrics)"

Step "Goi 20 requests --> /api/products"
Write-Host "  Tip: Mo Grafana --> Explore --> Loki --> {app=`"payment-api`"}" -ForegroundColor DarkGray

for ($i = 1; $i -le 20; $i++) {
    CallApi "$BASE/api/products" "Request $i"
    Start-Sleep -Milliseconds 200
}

Write-Host ""
Write-Host "  [OK] Logs xuat hien trong Grafana: Explore --> Loki --> {app=`"payment-api`"}" -ForegroundColor Green
Write-Host "  [OK] Metrics: Explore --> Prometheus --> http_requests_total" -ForegroundColor Green

Pause


# -------------------------------------------------------
Title "DEMO 2 - Rate Limiting (HTTP 429)"

Step "Goi 15 requests nhanh --> /api/limited"
Write-Host "  Gioi han: 10 req/phut -- tu lan thu 11 se bi chan" -ForegroundColor DarkGray
Write-Host ""

for ($i = 1; $i -le 15; $i++) {
    $status = CallApi "$BASE/api/limited" "Lan $i   "
    if ($status -eq 429) {
        Write-Host "         ^ BI CHAN! Rate limit kich hoat" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "  [OK] Grafana --> Prometheus --> rate_limit_hits_total" -ForegroundColor Green
Write-Host "  [OK] Grafana --> Loki --> {app=`"payment-api`"} loc level=warning" -ForegroundColor Green

Pause


# -------------------------------------------------------
Title "DEMO 3 - Circuit Breaker (HTTP 503)"

Step "Goi 10 requests --> /api/external/payment-gateway"
Write-Host "  Sau 3 lan fail: circuit OPEN --> tra 503 ngay lap tuc" -ForegroundColor DarkGray
Write-Host ""

for ($i = 1; $i -le 10; $i++) {
    try {
        $r      = Invoke-WebRequest -Uri "$BASE/api/external/payment-gateway" -UseBasicParsing -ErrorAction SilentlyContinue
        $status = $r.StatusCode
        $body   = $r.Content | ConvertFrom-Json -ErrorAction SilentlyContinue
        $state  = if ($body.circuit_state) { $body.circuit_state } else { "?" }
    } catch {
        $status = $_.Exception.Response.StatusCode.value__
        if (-not $status) { $status = "ERR" }
        $state  = "?"
    }

    $sColor = if ($status -eq 200) { "Green" } elseif ($status -eq 503) { "Red" } else { "Yellow" }
    $cColor = if ($state -eq "closed") { "Green" } elseif ($state -eq "open") { "Red" } else { "Yellow" }

    Write-Host "  Lan $i --> " -NoNewline
    Write-Host "HTTP $status" -ForegroundColor $sColor -NoNewline
    Write-Host " | Circuit: " -NoNewline
    Write-Host $state -ForegroundColor $cColor

    if ($state -eq "open" -and $i -le 5) {
        Write-Host "         ^ CIRCUIT NGAT! Khong thu goi nua, tra 503 ngay" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 300
}

Step "Kiem tra circuit status hien tai"
try {
    $r = Invoke-WebRequest -Uri "$BASE/api/external/circuit-status" -UseBasicParsing -ErrorAction Stop
    Write-Host "  $($r.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "  Loi: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "  [OK] Grafana --> Prometheus --> circuit_breaker_state" -ForegroundColor Green

Pause


# -------------------------------------------------------
Title "DEMO 4 - Distributed Tracing (Jaeger)"

Step "Goi 5 requests de tao traces"
for ($i = 1; $i -le 5; $i++) {
    CallApi "$BASE/api/products" "Trace $i"
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "  [OK] Mo http://localhost:16686" -ForegroundColor Green
Write-Host "  [OK] Service: payment-api --> Find Traces" -ForegroundColor Green
Write-Host "  [OK] Click vao 1 trace --> xem cac span (buoc xu ly)" -ForegroundColor Green

Pause


# -------------------------------------------------------
Title "DEMO 5 - Tat ca endpoints cua App"

Step "Goi tat ca cac endpoint chinh"
$endpoints = @(
    @{ path = "/health";                     label = "Health check       " }
    @{ path = "/api/products";               label = "Danh sach products " }
    @{ path = "/api/orders?status=pending";  label = "Orders (filter)    " }
    @{ path = "/api/orders?fields=id,total"; label = "Orders (sparse)    " }
    @{ path = "/api/limited";                label = "Rate limited       " }
    @{ path = "/metrics";                    label = "Prometheus metrics " }
)

foreach ($ep in $endpoints) {
    CallApi "$BASE$($ep.path)" $ep.label
    Start-Sleep -Milliseconds 150
}

Write-Host ""
Write-Host "  [OK] Swagger UI day du: http://localhost:8000/docs" -ForegroundColor Green


# -------------------------------------------------------
Title "XONG! Tom tat da demo"

Write-Host ""
Write-Host "  1. LOGS          --> Grafana / Loki / {app=`"payment-api`"}" -ForegroundColor White
Write-Host "  2. METRICS       --> Grafana / Prometheus / http_requests_total" -ForegroundColor White
Write-Host "  3. RATE LIMIT    --> HTTP 429 sau 10 req/phut" -ForegroundColor White
Write-Host "  4. CIRCUIT BREAK --> HTTP 503 sau 3 fail lien tiep" -ForegroundColor White
Write-Host "  5. TRACES        --> Jaeger / payment-api / Find Traces" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
