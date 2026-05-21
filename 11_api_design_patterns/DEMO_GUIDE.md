# Buổi 11-12: API Design Patterns — Demo Guide

## Cài đặt

```bash
cd 11_api_design_patterns
pip install -r requirements.txt
```

---

## Khởi động

Mở **2 terminal**:

```bash
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

```bash
# List products (có pagination + HATEOAS links)
curl http://localhost:8000/api/v1/products

# Create product
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Sony WH-1000XM5","price":7990000,"category":"audio","stock":25}'

# Get single product — xem _links
curl http://localhost:8000/api/v1/products/prod_001

# Update
curl -X PUT http://localhost:8000/api/v1/products/prod_001 \
  -H "Content-Type: application/json" \
  -d '{"name":"iPhone 16 Pro","price":27990000,"category":"electronics","stock":45}'

# Delete
curl -X DELETE http://localhost:8000/api/v1/products/prod_003
```

---

## Demo Pattern 2 — Query Pattern

```bash
# Filter theo category
curl "http://localhost:8000/api/v1/products?category=electronics"

# Filter khoảng giá + sort
curl "http://localhost:8000/api/v1/products?min_price=5000000&max_price=30000000&sort=price:asc"

# Full-text search
curl "http://localhost:8000/api/v1/products?q=macbook"

# Sparse Fieldsets — chỉ lấy id, status, total
curl "http://localhost:8000/api/v1/orders?fields=id,status,total"
```

---

## Demo Pattern 3 — HATEOAS + State Machine

### Bước 1: Tạo order

```bash
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "alice@example.com",
    "items": [
      {"product_id": "prod_001", "quantity": 1},
      {"product_id": "prod_003", "quantity": 2}
    ]
  }'
```

**Quan sát** `_links` trong response → có `confirm` và `cancel`, không có `ship` hay `deliver`.

### Bước 2: Chuyển trạng thái

```bash
# Thay ORDER_ID bằng id thực từ bước trên
curl -X PATCH http://localhost:8000/api/v1/orders/ORDER_ID/status \
  -H "Content-Type: application/json" \
  -d '{"status":"confirmed"}'
```

**Quan sát** `_links` → giờ có `ship` và `cancel`, không còn `confirm`.

### Bước 3: Thử transition không hợp lệ → 409

```bash
curl -X PATCH http://localhost:8000/api/v1/orders/ORDER_ID/status \
  -H "Content-Type: application/json" \
  -d '{"status":"delivered"}'
# → 409 INVALID_TRANSITION
```

---

## Demo Pattern 4 — Event-driven

```bash
# Xem tất cả events đã publish
curl http://localhost:8000/api/v1/events

# Filter theo loại
curl "http://localhost:8000/api/v1/events?event_type=order.confirmed"
```

**Giải thích**: Mỗi action (create/update product, create/update order) đều publish một domain event.
Các subscribers có thể react độc lập: gửi email, cập nhật inventory, trigger webhook...

---

## Demo Pattern 5 — Webhook

### Bước 1: Đăng ký webhook

```bash
curl -X POST http://localhost:8000/api/v1/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://localhost:8001/webhook",
    "events": ["order.created", "order.confirmed", "order.shipped", "order.delivered"],
    "secret": "demo-secret-123"
  }'
```

Lưu lại `webhook_id` từ response.

### Bước 2: Gửi test event

```bash
curl -X POST http://localhost:8000/api/v1/webhooks/WEBHOOK_ID/test
```

**Kiểm tra** Terminal 2 — webhook receiver in log nhận được.

### Bước 3: Tạo order → trigger webhook tự động

```bash
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "bob@example.com",
    "items": [{"product_id": "prod_002", "quantity": 1}]
  }'
```

**Quan sát** Terminal 2 in `[WEBHOOK] order.created`.

### Bước 4: Xem delivery log

```bash
curl http://localhost:8000/api/v1/webhooks/WEBHOOK_ID/deliveries
```

### Bước 5: Test retry (tắt receiver rồi trigger event)

```bash
# Dừng Terminal 2 (Ctrl+C)
# Tạo thêm order → webhook sẽ retry 3 lần, mỗi lần cách nhau 2s, 4s
# Khởi động lại receiver → xem delivery log có status "failed"
```

---

## Bonus — So sánh REST / gRPC / GraphQL

```bash
curl http://localhost:8000/api/v1/patterns/analysis | python -m json.tool
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
