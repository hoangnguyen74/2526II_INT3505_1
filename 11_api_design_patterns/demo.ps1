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

Pause


# -------------------------------------------------------
Title "DEMO 1 - CRUD Pattern + HATEOAS Links"

Step "List products (co _links pagination)"
$list = Invoke-RestMethod "$BASE/api/v1/products"
Write-Host "  Total: $($list.total) products"
Write-Host "  _links keys: $($list._links.PSObject.Properties.Name -join ', ')"

Step "Tao product moi"
$newP = Invoke-RestMethod -Method POST "$BASE/api/v1/products" `
  -ContentType "application/json" `
  -Body '{"name":"Sony WH-1000XM5","price":7990000,"category":"audio","stock":25}'
Write-Host "  Tao thanh cong: $($newP.id) - $($newP.name)"
Write-Host "  _links actions: $($newP._links.PSObject.Properties.Name -join ', ')"

Step "Get 1 product -- xem day du _links"
$p = Invoke-RestMethod "$BASE/api/v1/products/prod_001"
Show "_links" $p._links

Step "Update product"
$upd = Invoke-RestMethod -Method PUT "$BASE/api/v1/products/prod_001" `
  -ContentType "application/json" `
  -Body '{"name":"iPhone 16 Pro - Updated","price":28990000,"category":"electronics","stock":40}'
Write-Host "  Updated: $($upd.name) -- $($upd.price) VND"

Write-Host ""
Write-Host "  [OK] CRUD co day du _links (self, update, delete, collection)" -ForegroundColor Green

Pause


# -------------------------------------------------------
Title "DEMO 2 - Query Pattern (Filter, Sort, Sparse Fieldsets)"

Step "Filter theo category"
$res = Invoke-RestMethod "$BASE/api/v1/products?category=electronics"
Write-Host "  Tim duoc $($res.total) products trong electronics"

Step "Filter khoang gia + sort tang dan"
$res = Invoke-RestMethod "$BASE/api/v1/products?min_price=5000000&max_price=30000000&sort=price:asc"
Write-Host "  Ket qua (gia tu thap den cao):"
$res.items | ForEach-Object { Write-Host "    $($_.name) -- $($_.price) VND" }

Step "Full-text search"
$res = Invoke-RestMethod "$BASE/api/v1/products?q=macbook"
Write-Host "  Tim 'macbook': $($res.total) ket qua"

Step "Sparse Fieldsets -- chi lay id, status, total"
$res = Invoke-RestMethod "$BASE/api/v1/orders?fields=id,status,total"
Write-Host "  Chi co 3 fields (khong co created_at, customer_email...):"
$res.items | Select-Object -First 2 | ForEach-Object { Write-Host "    $_" }

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
Write-Host "  --> Co 'confirm' va 'cancel', KHONG co 'ship' hay 'deliver'" -ForegroundColor Yellow

Step "Buoc 2: Xac nhan order (pending -> confirmed)"
$confirmed = Invoke-RestMethod -Method PATCH "$BASE/api/v1/orders/$oid/status" `
  -ContentType "application/json" -Body '{"status":"confirmed"}'
Write-Host "  Status moi: $($confirmed.status)"
Write-Host "  _links moi: $($confirmed._links.PSObject.Properties.Name -join ', ')"
Write-Host "  --> Gio co 'ship', KHONG con 'confirm' nua" -ForegroundColor Yellow

Step "Buoc 3: Thu chay transition khong hop le (confirmed -> delivered) -- phai 409"
try {
    Invoke-RestMethod -Method PATCH "$BASE/api/v1/orders/$oid/status" `
      -ContentType "application/json" -Body '{"status":"delivered"}'
    Write-Host "  UNEXPECTED: khong co loi!" -ForegroundColor Red
} catch {
    Write-Host "  [OK] Loi mong doi: $($_.ErrorDetails.Message)" -ForegroundColor Green
}

Step "Buoc 4: Di het vong doi -- shipped -> delivered"
Invoke-RestMethod -Method PATCH "$BASE/api/v1/orders/$oid/status" `
  -ContentType "application/json" -Body '{"status":"shipped"}' | Out-Null
$done = Invoke-RestMethod -Method PATCH "$BASE/api/v1/orders/$oid/status" `
  -ContentType "application/json" -Body '{"status":"delivered"}'
Write-Host "  Final status: $($done.status)"
Write-Host "  _links: $(@($done._links.PSObject.Properties.Name).Count) actions (terminal state = rong)" -ForegroundColor Yellow

Write-Host ""
Write-Host "  [OK] State machine chi cho phep transition hop le, links thay doi theo trang thai" -ForegroundColor Green

Pause


# -------------------------------------------------------
Title "DEMO 4 - Event-driven (EventBus)"

Step "Xem tat ca events da publish (tu cac action truoc)"
$events = Invoke-RestMethod "$BASE/api/v1/events"
Write-Host "  Tong so events: $($events.total)"
$events.events | Select-Object -First 5 | ForEach-Object {
    Write-Host "    [$($_.event_type)] $($_.aggregate_id) luc $($_.timestamp)"
}

Step "Filter chi lay order events"
$orderEvents = Invoke-RestMethod "$BASE/api/v1/events?event_type=order.confirmed"
Write-Host "  order.confirmed events: $($orderEvents.total)"

Write-Host ""
Write-Host "  [OK] Moi action tao 1 domain event -- subscriber doc lap co the react" -ForegroundColor Green

Pause


# -------------------------------------------------------
Title "DEMO 5 - Webhook (Stripe-style, HMAC-SHA256)"

Step "Buoc 1: Dang ky webhook vao receiver (terminal 2)"
$wh = Invoke-RestMethod -Method POST "$BASE/api/v1/webhooks" `
  -ContentType "application/json" `
  -Body '{"url":"http://localhost:8001/webhook","events":["order.created","order.confirmed","order.shipped"],"secret":"demo-secret-123"}'
$wid = $wh.id
Write-Host "  Webhook ID: $wid"
Write-Host "  Listen events: $($wh.events -join ', ')"

Step "Buoc 2: Gui test event -- xem terminal 2 nhan duoc"
Invoke-RestMethod -Method POST "$BASE/api/v1/webhooks/$wid/test" | Out-Null
Write-Host "  Test event da gui --> xem terminal 2 (webhook receiver)" -ForegroundColor Yellow
Start-Sleep -Seconds 1

Step "Buoc 3: Tao order moi -- webhook tu dong trigger"
$newOrder = Invoke-RestMethod -Method POST "$BASE/api/v1/orders" `
  -ContentType "application/json" `
  -Body '{"customer_email":"bob@example.com","items":[{"product_id":"prod_002","quantity":1}]}'
Write-Host "  Order moi: $($newOrder.id)"
Write-Host "  --> Terminal 2 se in [WEBHOOK] order.created" -ForegroundColor Yellow
Start-Sleep -Seconds 1

Step "Buoc 4: Xem delivery log (co HMAC signature)"
$deliveries = Invoke-RestMethod "$BASE/api/v1/webhooks/$wid/deliveries"
Write-Host "  Tong deliveries: $($deliveries.Count)"
$deliveries | Select-Object -First 2 | ForEach-Object {
    Write-Host "    event=$($_.event_type) | status=$($_.status) | attempt=$($_.attempt)"
}

Write-Host ""
Write-Host "  [OK] HMAC-SHA256 signing giong Stripe -- receiver verify chu ky truoc khi xu ly" -ForegroundColor Green

Step "Xem events nhan duoc tai receiver"
try {
    $received = Invoke-RestMethod "http://localhost:8001/events"
    Write-Host "  Receiver da nhan $($received.total) events"
} catch {
    Write-Host "  [!] Receiver chua chay o terminal 2" -ForegroundColor Yellow
}

Pause


# -------------------------------------------------------
Title "BONUS - REST vs gRPC vs GraphQL Analysis"

Step "Phan tich khi nao dung cong nghe nao"
$analysis = Invoke-RestMethod "$BASE/api/v1/patterns/analysis"
Write-Host "  Stripe patterns: $($analysis.stripe_patterns.PSObject.Properties.Name -join ', ')"
Write-Host "  GitHub patterns: $($analysis.github_patterns.PSObject.Properties.Name -join ', ')"
Write-Host ""
Write-Host "  REST dung khi: $($analysis.when_to_use.REST -join '; ')"
Write-Host "  gRPC dung khi: $($analysis.when_to_use.gRPC -join '; ')"
Write-Host "  GraphQL dung khi: $($analysis.when_to_use.GraphQL -join '; ')"


# -------------------------------------------------------
Title "XONG! Tom tat da demo"

Write-Host ""
Write-Host "  1. CRUD    --> products CRUD + _links (self, update, delete)" -ForegroundColor White
Write-Host "  2. QUERY   --> filter, sort, sparse fieldsets, full-text search" -ForegroundColor White
Write-Host "  3. HATEOAS --> state machine, link thay doi theo trang thai, 409 cho invalid transition" -ForegroundColor White
Write-Host "  4. EVENTS  --> domain events tu dong publish sau moi action" -ForegroundColor White
Write-Host "  5. WEBHOOK --> HMAC sign, delivery log, retry, giong Stripe" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
