# demo.ps1 - Kich ban demo buoi 11-12: API Design Patterns
# Yeu cau: 2 terminal dang chay
#   Terminal 1: py -m uvicorn main:app --reload --port 8000
#   Terminal 2: py -m uvicorn webhook_receiver:app --port 8001
# Chay: PowerShell -ExecutionPolicy Bypass -File demo.ps1

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

function Show($label, $obj) {
    Write-Host "  [$label]" -ForegroundColor Yellow
    $obj | ConvertTo-Json -Depth 3 | Write-Host
}

function Pause {
    Write-Host ""
    Write-Host "[Nhan Enter de tiep tuc...]" -ForegroundColor Yellow
    Read-Host | Out-Null
}

# -------------------------------------------------------
Title "DEMO BUOI 11-12 - API Design Patterns"
Write-Host ""
Write-Host "  Swagger UI  : $BASE/docs"
Write-Host "  Webhook recv: http://localhost:8001/docs"
Write-Host "  Events nhan : http://localhost:8001/events"

# === DANG KY WEBHOOK TRUOC ===
# Dang ky webhook ngay tu dau voi ["*"] de nhan TAT CA events
# Nhu vay moi action o cac demo sau deu duoc gui den receiver
Step "Dang ky webhook truoc (nhan tat ca events qua cac demo)"
try {
    $wh = Invoke-RestMethod -Method POST "$BASE/api/v1/webhooks" `
      -ContentType "application/json" `
      -Body '{"url":"http://localhost:8001/webhook","events":["*"],"secret":"demo-secret-123"}'
    $script:wid = $wh.id
    Write-Host "  Webhook ID: $($script:wid) | events: [*] (tat ca)" -ForegroundColor Green
    Write-Host "  --> Moi event tu gio deu gui den http://localhost:8001/webhook" -ForegroundColor Green
    Write-Host "  --> Xem terminal 2 de thay webhook duoc nhan real-time" -ForegroundColor Yellow
} catch {
    Write-Host "  [!] Khong dang ky duoc webhook (terminal 2 co dang chay?)" -ForegroundColor Yellow
    $script:wid = $null
}

Pause


# -------------------------------------------------------
Title "DEMO 1 - CRUD Pattern + HATEOAS Links"

Step "List products (co _links pagination)"
$list = Invoke-RestMethod "$BASE/api/v1/products"
Write-Host "  Total: $($list.meta.total) products"
Write-Host "  _links keys: $($list._links.PSObject.Properties.Name -join ', ')"

Step "Tao product moi"
$newP = Invoke-RestMethod -Method POST "$BASE/api/v1/products" `
  -ContentType "application/json" `
  -Body '{"name":"Sony WH-1000XM5","price":7990000,"category":"audio","stock":25}'
Write-Host "  Tao thanh cong: $($newP.id) - $($newP.name)"
Write-Host "  _links actions: $($newP._links.PSObject.Properties.Name -join ', ')"
Write-Host "  --> Terminal 2: [WEBHOOK] product.created" -ForegroundColor Yellow

Step "Get 1 product -- xem day du _links"
$p = Invoke-RestMethod "$BASE/api/v1/products/prod_001"
Show "_links" $p._links

Step "Update product"
$upd = Invoke-RestMethod -Method PUT "$BASE/api/v1/products/prod_001" `
  -ContentType "application/json" `
  -Body '{"name":"iPhone 16 Pro - Updated","price":28990000,"category":"electronics","stock":40}'
Write-Host "  Updated: $($upd.name) -- $($upd.price) VND"
Write-Host "  --> Terminal 2: [WEBHOOK] product.updated" -ForegroundColor Yellow

Write-Host ""
Write-Host "  [OK] CRUD co day du _links (self, update, delete, collection)" -ForegroundColor Green

Pause


# -------------------------------------------------------
Title "DEMO 2 - Query Pattern (Filter, Sort, Sparse Fieldsets)"

Step "Filter theo category"
$res = Invoke-RestMethod "$BASE/api/v1/products?category=electronics"
Write-Host "  Tim duoc $($res.meta.total) products trong electronics"

Step "Filter khoang gia + sort tang dan"
$res = Invoke-RestMethod "$BASE/api/v1/products?min_price=5000000&max_price=30000000&sort=price:asc"
Write-Host "  Ket qua (gia tu thap den cao):"
$res.data | ForEach-Object { Write-Host "    $($_.name) -- $($_.price) VND" }

Step "Full-text search"
$res = Invoke-RestMethod "$BASE/api/v1/products?q=macbook"
Write-Host "  Tim 'macbook': $($res.meta.total) ket qua"

Step "Sparse Fieldsets -- chi lay id, status, total"
$res = Invoke-RestMethod "$BASE/api/v1/orders?fields=id,status,total"
Write-Host "  Chi co 3 fields (khong co created_at, customer_email...):"
Write-Host "  (Chua co order nao? Se tao o Demo 3)" -ForegroundColor DarkGray

Write-Host ""
Write-Host "  [OK] Client tu chon fields can thiet, giam payload size" -ForegroundColor Green

Pause


# -------------------------------------------------------
Title "DEMO 3 - HATEOAS + State Machine"

Step "Buoc 1: Tao order -- xem _links"
$order = Invoke-RestMethod -Method POST "$BASE/api/v1/orders" `
  -ContentType "application/json" `
  -Body '{"customer_email":"alice@example.com","items":[{"product_id":"prod_001","quantity":1},{"product_id":"prod_003","quantity":2}]}'

$oid = $order.id
Write-Host "  Order: $oid | Status: $($order.status)"
Write-Host "  _links co the thuc hien: $($order._links.PSObject.Properties.Name -join ', ')"
Write-Host "  --> Co 'confirmed' va 'cancelled', KHONG co 'shipped' hay 'delivered'" -ForegroundColor Yellow
Write-Host "  --> Terminal 2: [WEBHOOK] order.created" -ForegroundColor Yellow

Step "Buoc 2: Xac nhan order (pending -> confirmed)"
$confirmed = Invoke-RestMethod -Method PATCH "$BASE/api/v1/orders/$oid/status" `
  -ContentType "application/json" -Body '{"status":"confirmed"}'
Write-Host "  Status moi: $($confirmed.status)"
Write-Host "  _links moi: $($confirmed._links.PSObject.Properties.Name -join ', ')"
Write-Host "  --> Gio co 'shipped', KHONG con 'confirmed' nua" -ForegroundColor Yellow
Write-Host "  --> Terminal 2: [WEBHOOK] order.confirmed" -ForegroundColor Yellow

Step "Buoc 3: Thu chay transition khong hop le (confirmed -> delivered)"
try {
    Invoke-RestMethod -Method PATCH "$BASE/api/v1/orders/$oid/status" `
      -ContentType "application/json" -Body '{"status":"delivered"}'
    Write-Host "  UNEXPECTED: khong co loi!" -ForegroundColor Red
} catch {
    Write-Host "  --> HTTP 409 INVALID_TRANSITION (dung!)" -ForegroundColor Green
    Write-Host "  $($_.ErrorDetails.Message)" -ForegroundColor DarkGray
}

Step "Buoc 4: Di het vong doi -- shipped -> delivered"
$shipped = Invoke-RestMethod -Method PATCH "$BASE/api/v1/orders/$oid/status" `
  -ContentType "application/json" -Body '{"status":"shipped"}'
Write-Host "  Status: $($shipped.status) --> Terminal 2: [WEBHOOK] order.shipped" -ForegroundColor Yellow

$done = Invoke-RestMethod -Method PATCH "$BASE/api/v1/orders/$oid/status" `
  -ContentType "application/json" -Body '{"status":"delivered"}'
Write-Host "  Status: $($done.status) (terminal state)"
Write-Host "  _links: $(@($done._links.PSObject.Properties).Count) actions con lai (terminal = rong)" -ForegroundColor Yellow
Write-Host "  --> Terminal 2: [WEBHOOK] order.delivered" -ForegroundColor Yellow

Write-Host ""
Write-Host "  [OK] State machine chi cho phep transition hop le, links thay doi theo trang thai" -ForegroundColor Green

Pause


# -------------------------------------------------------
Title "DEMO 4 - Event-driven (EventBus)"

Step "Xem tat ca events da publish (tu cac action truoc)"
$events = Invoke-RestMethod "$BASE/api/v1/events"
Write-Host "  Tong so events: $($events.total)"
Write-Host "  Cac loai events:" -ForegroundColor Yellow
$events.available_types | ForEach-Object { Write-Host "    - $_" }
Write-Host ""
Write-Host "  5 events gan nhat:"
$events.events | Select-Object -Last 5 | ForEach-Object {
    Write-Host "    [$($_.type)] $($_.timestamp)"
}

Step "Filter chi lay order.confirmed events"
$orderEvents = Invoke-RestMethod "$BASE/api/v1/events?event_type=order.confirmed"
Write-Host "  order.confirmed events: $($orderEvents.total)"

Write-Host ""
Write-Host "  [OK] Moi action tao 1 domain event -- subscriber doc lap co the react" -ForegroundColor Green

Pause


# -------------------------------------------------------
Title "DEMO 5 - Webhook (Stripe-style, HMAC-SHA256)"

Step "Webhook da duoc dang ky tu dau voi events: [*]"
Write-Host "  Webhook ID: $($script:wid)"
Write-Host "  Moi event tu Demo 1-4 deu da duoc gui den receiver" -ForegroundColor Green

Step "Xem delivery log -- tat ca cac lan gui"
if ($script:wid) {
    Start-Sleep -Seconds 2
    $dlv = Invoke-RestMethod "$BASE/api/v1/webhooks/$($script:wid)/deliveries"
    Write-Host "  Tong so deliveries: $($dlv.total)" -ForegroundColor Yellow
    Write-Host ""
    $dlv.data | ForEach-Object {
        $statusColor = if ($_.status -eq "delivered") { "Green" } else { "Red" }
        Write-Host "    $($_.event_type)" -NoNewline
        Write-Host " --> $($_.status)" -ForegroundColor $statusColor
    }
}

Step "Xem events tai receiver (http://localhost:8001/events)"
try {
    $received = Invoke-RestMethod "http://localhost:8001/events"
    Write-Host "  Receiver da nhan: $($received.total) events" -ForegroundColor Green
    Write-Host ""
    $received.events | ForEach-Object {
        Write-Host "    $($_.event_type) | sig_valid=$($_.signature_valid) | $($_.received_at)"
    }
} catch {
    Write-Host "  [!] Khong ket noi duoc receiver (terminal 2 co dang chay?)" -ForegroundColor Yellow
}

Step "Gui test event rieng (giong nut 'Send test webhook' cua Stripe)"
if ($script:wid) {
    $testResult = Invoke-RestMethod -Method POST "$BASE/api/v1/webhooks/$($script:wid)/test"
    Write-Host "  Test event: $($testResult.delivery.status)" -ForegroundColor Green
    Write-Host "  --> Terminal 2 in [WEBHOOK] webhook.test" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  [OK] HMAC-SHA256 signing giong Stripe -- receiver verify chu ky truoc khi xu ly" -ForegroundColor Green
Write-Host "  [OK] Delivery log ghi lai tung lan gui, retry status, signature" -ForegroundColor Green

Pause


# -------------------------------------------------------
Title "BONUS - REST vs gRPC vs GraphQL Analysis"

Step "Phan tich khi nao dung cong nghe nao"
$analysis = Invoke-RestMethod "$BASE/api/v1/patterns/analysis"
Write-Host "  Stripe patterns: $($analysis.stripe_patterns.PSObject.Properties.Name -join ', ')"
Write-Host "  GitHub patterns: $($analysis.github_patterns.PSObject.Properties.Name -join ', ')"
Write-Host ""
$analysis.when_to_use.PSObject.Properties | ForEach-Object {
    Write-Host "  $($_.Name) dung khi:" -ForegroundColor Yellow
    $_.Value | ForEach-Object { Write-Host "    - $_" }
}


# -------------------------------------------------------
Title "XONG! Tom tat da demo"

Write-Host ""
Write-Host "  1. CRUD    --> products CRUD + _links (self, update, delete)" -ForegroundColor White
Write-Host "  2. QUERY   --> filter, sort, sparse fieldsets, full-text search" -ForegroundColor White
Write-Host "  3. HATEOAS --> state machine, link thay doi theo trang thai, 409 cho invalid transition" -ForegroundColor White
Write-Host "  4. EVENTS  --> domain events tu dong publish sau moi action" -ForegroundColor White
Write-Host "  5. WEBHOOK --> HMAC sign, delivery log cho TAT CA events tu Demo 1-4" -ForegroundColor White
Write-Host ""
Write-Host "  Kiem tra: http://localhost:8001/events --> thay tat ca events" -ForegroundColor Green
Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
