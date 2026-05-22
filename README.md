# INT3505 — Service-Oriented Architecture

Khóa học 13 buổi tại UET Vietnam, xây dựng API từ cơ bản đến production.

## Cấu trúc

| Buổi | Thư mục | Chủ đề |
|------|---------|--------|
| 4 | `4_openapi/` | API Specification & OpenAPI |
| 8 | `8_api_testing/` | API Testing |
| 9 | `9_api_versioning/` | API Versioning |
| 10 | `10_security_monitoring/` | Security, Monitoring & Kubernetes |
| 11-12 | `11_api_design_patterns/` | API Design Patterns |
| 13 | `13_api_as_product/` | API as a Product |

---

## Buổi 10 — Security & Monitoring trên Kubernetes

### Khởi động cluster

```powershell
cd 10_security_monitoring
PowerShell -ExecutionPolicy Bypass -File k8s\start-cluster.ps1
```

### Port-forward (mở 4 terminal riêng)

```powershell
# Terminal 1 — App
kubectl port-forward svc/payment-api 8000:8000 -n monitoring

# Terminal 2 — Grafana  (admin / admin123)
kubectl port-forward svc/kube-prom-grafana 3000:80 -n monitoring

# Terminal 3 — Jaeger
kubectl port-forward svc/jaeger-query 16686:16686 -n monitoring

# Terminal 4 — Prometheus
kubectl port-forward svc/kube-prom-kube-prometheus-prometheus 9090:9090 -n monitoring
```

### Chạy kịch bản demo tự động

```powershell
PowerShell -ExecutionPolicy Bypass -File k8s\demo.ps1
```

### Demo thủ công

```powershell
# Tạo traffic
for ($i=1; $i -le 20; $i++) {
    Invoke-RestMethod http://localhost:8000/api/products
}

# Rate limiting — lần 11+ trả HTTP 429
for ($i=1; $i -le 15; $i++) {
    try { $r = Invoke-RestMethod http://localhost:8000/api/limited; $s=200 }
    catch { $s=$_.Exception.Response.StatusCode.value__ }
    Write-Host "Lan $i --> $s"
}

# Circuit breaker — sau 3 fail trả HTTP 503
for ($i=1; $i -le 10; $i++) {
    try { $r = Invoke-RestMethod http://localhost:8000/api/external/payment-gateway; $s=200; $c=$r.circuit_state }
    catch { $s=$_.Exception.Response.StatusCode.value__; $c="?" }
    Write-Host "Lan $i --> $s | circuit=$c"
}
```

### Xem trong Grafana (localhost:3000)

| Muốn xem | Nơi | Query |
|----------|-----|-------|
| Logs real-time | Explore → Loki | `{app="payment-api"}` |
| Tổng requests | Explore → Prometheus | `http_requests_total` |
| Rate limit hits | Explore → Prometheus | `rate_limit_hits_total` |
| Traces | Jaeger UI localhost:16686 | Service: payment-api |

---

## Buổi 11-12 — API Design Patterns

### Khởi động

```powershell
cd 11_api_design_patterns
pip install -r requirements.txt

# Terminal 1 — Main API
py -m uvicorn main:app --reload --port 8000

# Terminal 2 — Webhook Receiver
py -m uvicorn webhook_receiver:app --port 8001
```

Swagger: http://localhost:8000/docs | Webhook events: http://localhost:8001/events

### Chạy kịch bản demo tự động

```powershell
PowerShell -ExecutionPolicy Bypass -File demo.ps1
```

### Demo CRUD Pattern

```powershell
# List products
Invoke-RestMethod http://localhost:8000/api/v1/products

# Create product
Invoke-RestMethod -Method POST http://localhost:8000/api/v1/products `
  -ContentType "application/json" `
  -Body '{"name":"Sony WH-1000XM5","price":7990000,"category":"audio","stock":25}'

# Get single — xem _links trong response
Invoke-RestMethod http://localhost:8000/api/v1/products/prod_001
```

### Demo Query Pattern (Sparse Fieldsets, Filter, Sort)

```powershell
# Filter + sort
Invoke-RestMethod "http://localhost:8000/api/v1/products?category=electronics&sort=price:asc"

# Sparse fieldsets — chi tra ve cac fields can thiet
Invoke-RestMethod "http://localhost:8000/api/v1/orders?fields=id,status,total"

# Full-text search
Invoke-RestMethod "http://localhost:8000/api/v1/products?q=macbook"
```

### Demo HATEOAS + State Machine

```powershell
# Buoc 1: Tao order
$order = Invoke-RestMethod -Method POST http://localhost:8000/api/v1/orders `
  -ContentType "application/json" `
  -Body '{"customer_email":"alice@example.com","items":[{"product_id":"prod_001","quantity":1}]}'

# Xem _links — chi co confirmed va cancelled, KHONG co shipped
$order._links

# Buoc 2: Chuyen trang thai
$oid = $order.id
Invoke-RestMethod -Method PATCH "http://localhost:8000/api/v1/orders/$oid/status" `
  -ContentType "application/json" `
  -Body '{"status":"confirmed"}'

# Buoc 3: Thu transition khong hop le --> 409
try {
    Invoke-RestMethod -Method PATCH "http://localhost:8000/api/v1/orders/$oid/status" `
      -ContentType "application/json" `
      -Body '{"status":"delivered"}'
} catch { $_.ErrorDetails.Message }

# Buoc 4: Di den cuoi vong doi
Invoke-RestMethod -Method PATCH "http://localhost:8000/api/v1/orders/$oid/status" `
  -ContentType "application/json" -Body '{"status":"shipped"}'
Invoke-RestMethod -Method PATCH "http://localhost:8000/api/v1/orders/$oid/status" `
  -ContentType "application/json" -Body '{"status":"delivered"}'
```

### Demo Webhook (Stripe-style)

```powershell
# Buoc 1: Dang ky webhook
$wh = Invoke-RestMethod -Method POST http://localhost:8000/api/v1/webhooks `
  -ContentType "application/json" `
  -Body '{"url":"http://localhost:8001/webhook","events":["order.created","order.confirmed"],"secret":"demo-secret-123"}'
$wid = $wh.id

# Buoc 2: Gui test event
Invoke-RestMethod -Method POST "http://localhost:8000/api/v1/webhooks/$wid/test"

# Buoc 3: Tao order --> webhook tu dong duoc gui
Invoke-RestMethod -Method POST http://localhost:8000/api/v1/orders `
  -ContentType "application/json" `
  -Body '{"customer_email":"bob@example.com","items":[{"product_id":"prod_002","quantity":1}]}'

# Buoc 4: Xem delivery log
Invoke-RestMethod "http://localhost:8000/api/v1/webhooks/$wid/deliveries"

# Xem lich su events
Invoke-RestMethod http://localhost:8000/api/v1/events
```

---

## Buổi 13 — API as a Product

### Khởi động

```powershell
cd 13_api_as_product
pip install -r requirements.txt
py -m uvicorn main:app --reload
```

- Swagger: http://localhost:8000/docs  
- Developer Portal: mở `portal.html` trực tiếp trong trình duyệt

### Chạy kịch bản demo tự động

```powershell
PowerShell -ExecutionPolicy Bypass -File demo.ps1
```

### Demo Developer Experience

```powershell
# Sandbox — khong can key, ai cung dung duoc
Invoke-RestMethod http://localhost:8000/sandbox/products

# Xem bang gia
Invoke-RestMethod http://localhost:8000/plans

# Dang ky developer account --> nhan API key ngay
$reg = Invoke-RestMethod -Method POST http://localhost:8000/developers/register `
  -ContentType "application/json" `
  -Body '{"name":"Demo User","email":"demo@test.com","plan":"free"}'
$key = $reg.api_key
Write-Host "API Key: $key"

# Goi API voi key -- xem headers X-Quota-Limit, X-Quota-Remaining
$resp = Invoke-WebRequest -Uri http://localhost:8000/api/v1/products `
  -Headers @{"X-API-Key"=$key}
$resp.Headers | Select-String "Quota|Plan|Response-Time"
```

### Demo Quota & Feature Gating

```powershell
# Goi khong co key --> 422
try { Invoke-RestMethod http://localhost:8000/api/v1/products } catch { $_.ErrorDetails.Message }

# Key sai --> 401
try {
    Invoke-RestMethod http://localhost:8000/api/v1/products `
      -Headers @{"X-API-Key"="sk_invalid"}
} catch { $_.ErrorDetails.Message }

# Feature gating: Search chi cho Pro+ (dung free key --> 403)
try {
    Invoke-RestMethod "http://localhost:8000/api/v1/search?q=iphone" `
      -Headers @{"X-API-Key"=$key}
} catch { $_.ErrorDetails.Message }

# Nang cap len Pro
Invoke-RestMethod -Method POST http://localhost:8000/developers/upgrade `
  -ContentType "application/json" `
  -Body '{"email":"demo@test.com","new_plan":"pro"}'

# Sau khi nang cap -- Search thanh cong
Invoke-RestMethod "http://localhost:8000/api/v1/search?q=iphone" `
  -Headers @{"X-API-Key"=$key}

# Xem usage cua developer
Invoke-RestMethod http://localhost:8000/developers/demo@test.com/usage
```

### Demo KPI Analytics (Admin)

```powershell
# Dashboard KPI: MRR, error rate, top endpoints
Invoke-RestMethod http://localhost:8000/admin/analytics `
  -Headers @{"X-Admin-Key"="admin-secret-key"}

# Danh sach developers + revenue
Invoke-RestMethod http://localhost:8000/admin/developers `
  -Headers @{"X-Admin-Key"="admin-secret-key"}
```

### Developer Portal (portal.html)

1. Mở `portal.html` trong trình duyệt (double-click file)
2. **Live Stats** tự cập nhật mỗi 5 giây từ `/admin/analytics`
3. **Register** form → nhận API key hiển thị ngay
4. **My Usage** → nhập email → xem quota bar đổi màu (xanh/vàng/đỏ)
5. **Quick Start** tabs → copy code mẫu cURL/Python/JavaScript

---

## Links nhanh

| Buổi | Swagger | Notes |
|------|---------|-------|
| 10 | http://localhost:8000/docs | Cần port-forward trước |
| 11-12 | http://localhost:8000/docs | Cần chạy cả terminal 2 (webhook receiver) |
| 13 | http://localhost:8000/docs | Mở thêm portal.html |
