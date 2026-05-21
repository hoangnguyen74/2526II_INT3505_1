# Buổi 11-12: API Design Patterns — Demo Guide

## Cài đặt

```powershell
cd 11_api_design_patterns
pip install -r requirements.txt
```

---

## Khởi động

Mở **2 terminal**:

```powershell
# Terminal 1 — Main API server
py -m uvicorn main:app --reload --port 8000

# Terminal 2 — Webhook Receiver
py -m uvicorn webhook_receiver:app --port 8001
```

- Swagger UI main: http://localhost:8000/docs
- Swagger UI receiver: http://localhost:8001/docs
- Events nhận được: http://localhost:8001/events

---

## Demo Pattern 1 — CRUD

```powershell
# List products (có pagination + HATEOAS links)
Invoke-RestMethod http://localhost:8000/api/v1/products

# Create product
Invoke-RestMethod -Method POST http://localhost:8000/api/v1/products `
  -ContentType "application/json" `
  -Body '{"name":"Sony WH-1000XM5","price":7990000,"category":"audio","stock":25}'

# Get single product — xem _links trong response
Invoke-RestMethod http://localhost:8000/api/v1/products/prod_001

# Update
Invoke-RestMethod -Method PUT http://localhost:8000/api/v1/products/prod_001 `
  -ContentType "application/json" `
  -Body '{"name":"iPhone 16 Pro","price":27990000,"category":"electronics","stock":45}'

# Delete
Invoke-RestMethod -Method DELETE http://localhost:8000/api/v1/products/prod_003
```

---

## Demo Pattern 2 — Query Pattern

```powershell
# Filter theo category
Invoke-RestMethod "http://localhost:8000/api/v1/products?category=electronics"

# Filter khoảng giá + sort
Invoke-RestMethod "http://localhost:8000/api/v1/products?min_price=5000000&max_price=30000000&sort=price:asc"

# Full-text search
Invoke-RestMethod "http://localhost:8000/api/v1/products?q=macbook"

# Sparse Fieldsets — chỉ lấy id, status, total
Invoke-RestMethod "http://localhost:8000/api/v1/orders?fields=id,status,total"

# Pagination
Invoke-RestMethod "http://localhost:8000/api/v1/products?page=1&limit=5"
```

---

## Demo Pattern 3 — HATEOAS + State Machine

### Bước 1: Tạo order

```powershell
$order = Invoke-RestMethod -Method POST http://localhost:8000/api/v1/orders `
  -ContentType "application/json" `
  -Body '{
    "customer_email": "alice@example.com",
    "items": [
      {"product_id": "prod_001", "quantity": 1},
      {"product_id": "prod_003", "quantity": 2}
    ]
  }'

# Xem _links — có confirm và cancel, không có ship hay deliver
$order._links
```

**Quan sát** `_links` trong response → có `confirm` và `cancel`, không có `ship` hay `deliver`.

### Bước 2: Chuyển trạng thái

```powershell
$oid = $order.id
Invoke-RestMethod -Method PATCH "http://localhost:8000/api/v1/orders/$oid/status" `
  -ContentType "application/json" `
  -Body '{"status":"confirmed"}'
```

**Quan sát** `_links` → giờ có `ship` và `cancel`, không còn `confirm`.

### Bước 3: Thử transition không hợp lệ → 409

```powershell
try {
    Invoke-RestMethod -Method PATCH "http://localhost:8000/api/v1/orders/$oid/status" `
      -ContentType "application/json" `
      -Body '{"status":"delivered"}'
} catch { $_.ErrorDetails.Message }
# → 409 INVALID_TRANSITION
```

### Bước 4: Đi hết vòng đời order

```powershell
# Chuyển sang shipped
Invoke-RestMethod -Method PATCH "http://localhost:8000/api/v1/orders/$oid/status" `
  -ContentType "application/json" `
  -Body '{"status":"shipped"}'

# Chuyển sang delivered — _links sẽ rỗng (terminal state)
Invoke-RestMethod -Method PATCH "http://localhost:8000/api/v1/orders/$oid/status" `
  -ContentType "application/json" `
  -Body '{"status":"delivered"}'
```

---

## Demo Pattern 4 — Event-driven

```powershell
# Xem tất cả events đã publish
Invoke-RestMethod http://localhost:8000/api/v1/events

# Filter theo loại event
Invoke-RestMethod "http://localhost:8000/api/v1/events?event_type=order.confirmed"
```

**Giải thích**: Mỗi action (create/update product, create/update order) đều publish một domain event.
Các subscribers có thể react độc lập: gửi email, cập nhật inventory, trigger webhook...

---

## Demo Pattern 5 — Webhook

### Bước 1: Đăng ký webhook

```powershell
$wh = Invoke-RestMethod -Method POST http://localhost:8000/api/v1/webhooks `
  -ContentType "application/json" `
  -Body '{
    "url": "http://localhost:8001/webhook",
    "events": ["order.created", "order.confirmed", "order.shipped", "order.delivered"],
    "secret": "demo-secret-123"
  }'

$wid = $wh.id
Write-Host "Webhook ID: $wid"
```

### Bước 2: Gửi test event

```powershell
Invoke-RestMethod -Method POST "http://localhost:8000/api/v1/webhooks/$wid/test"
```

**Kiểm tra** Terminal 2 — webhook receiver in log nhận được.

### Bước 3: Tạo order → trigger webhook tự động

```powershell
Invoke-RestMethod -Method POST http://localhost:8000/api/v1/orders `
  -ContentType "application/json" `
  -Body '{
    "customer_email": "bob@example.com",
    "items": [{"product_id": "prod_002", "quantity": 1}]
  }'
```

**Quan sát** Terminal 2 in `[WEBHOOK] order.created`.

### Bước 4: Xem delivery log

```powershell
Invoke-RestMethod "http://localhost:8000/api/v1/webhooks/$wid/deliveries"
```

### Bước 5: Retry demo (tắt receiver rồi trigger event)

```powershell
# Dừng Terminal 2 (Ctrl+C), sau đó tạo order mới
Invoke-RestMethod -Method POST http://localhost:8000/api/v1/orders `
  -ContentType "application/json" `
  -Body '{"customer_email":"retry@example.com","items":[{"product_id":"prod_001","quantity":1}]}'

# Webhook sẽ retry 3 lần, mỗi lần cách nhau 2s, 4s
# Khởi động lại receiver → xem delivery log có status "failed"
Invoke-RestMethod "http://localhost:8000/api/v1/webhooks/$wid/deliveries"
```

---

## Bonus — So sánh REST / gRPC / GraphQL

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/patterns/analysis
```

---

## Verify chữ ký HMAC (giống Stripe SDK)

```python
import hmac, hashlib, json

secret = "demo-secret-123"
payload = '{"type": "order.created", "data": {...}}'
signature = "sha256=" + hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

# Verify
received_sig = "sha256=..."  # từ header X-Webhook-Signature
assert hmac.compare_digest(signature, received_sig), "Invalid signature!"
```
