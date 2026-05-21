# Buổi 11-12: API Design Patterns

---

## Agenda

1. Các patterns cốt lõi: CRUD · Query · HATEOAS · Event-driven · Webhook
2. REST vs gRPC vs GraphQL — khi nào dùng cái nào?
3. Live demo: Order Management System
4. Phân tích Stripe & GitHub APIs

---

## 1. CRUD Pattern

**Nguyên tắc**: Mỗi resource ánh xạ trực tiếp tới 4 thao tác:

| Operation | HTTP Method | Endpoint              |
|-----------|-------------|-----------------------|
| Create    | POST        | `/api/v1/products`    |
| Read      | GET         | `/api/v1/products/{id}` |
| Update    | PUT / PATCH | `/api/v1/products/{id}` |
| Delete    | DELETE      | `/api/v1/products/{id}` |

**Quan trọng**: `PUT` thay toàn bộ resource, `PATCH` chỉ thay một phần.

---

## 2. Query Pattern

Cho phép client kiểm soát **lượng và thứ tự** dữ liệu nhận về:

```
GET /api/v1/orders
  ?status=confirmed          # Filtering
  &min_total=500000          # Range filter
  &sort=created_at:desc      # Sorting
  &fields=id,status,total    # Sparse Fieldsets
  &page=2&limit=10           # Pagination
```

### Sparse Fieldsets
- Client chỉ yêu cầu fields cần thiết → giảm bandwidth
- Stripe: `?expand[]=customer` để lấy thêm nested data
- GraphQL làm điều này tự nhiên hơn REST

---

## 3. HATEOAS — Hypermedia As The Engine Of Application State

**Vấn đề** với REST thông thường: Client phải hardcode URLs và biết trước valid transitions.

**HATEOAS giải quyết**: Response chứa `_links` chỉ expose những action *hợp lệ* tại thời điểm đó.

### Ví dụ: Order state machine

```json
// Order ở trạng thái "confirmed"
{
  "id": "ord_abc123",
  "status": "confirmed",
  "_links": {
    "self":    "/api/v1/orders/ord_abc123",
    "ship":    {"href": "/api/v1/orders/ord_abc123/status", "method": "PATCH"},
    "cancel":  {"href": "/api/v1/orders/ord_abc123/status", "method": "PATCH"}
    // "confirm" KHÔNG có vì đã confirmed rồi
    // "deliver" KHÔNG có vì chưa shipped
  }
}
```

**Lợi ích**: 
- Client resilient với thay đổi URL
- Tự document trạng thái hệ thống
- Ngăn client gọi transition không hợp lệ

**Thực tế**: GitHub trả về `*_url` fields, Stripe trả về `object` + related IDs.

---

## 4. Event-driven Pattern

```
[Action] ──► [Event Published] ──► [Event Bus] ──► [Subscribers]
                                                    ├── Webhook delivery
                                                    ├── Email notification
                                                    ├── Audit log
                                                    └── Analytics
```

### Domain Events trong demo

| Trigger         | Event Type          |
|-----------------|---------------------|
| Tạo sản phẩm    | `product.created`   |
| Tạo đơn hàng    | `order.created`     |
| Xác nhận đơn    | `order.confirmed`   |
| Giao vận        | `order.shipped`     |
| Hoàn thành      | `order.delivered`   |
| Hủy đơn         | `order.cancelled`   |

**Lợi ích**:
- Loose coupling: producer không biết consumer
- Dễ thêm subscriber mới mà không sửa producer
- Tự nhiên cho async operations

---

## 5. Webhook Pattern

### Webhook vs Polling

| | Polling | Webhook |
|---|---------|---------|
| Cơ chế | Client hỏi định kỳ | Server chủ động gửi |
| Latency | Cao (phụ thuộc interval) | Thấp (gần real-time) |
| Tài nguyên | Lãng phí nếu không có data | Hiệu quả |
| Phức tạp | Đơn giản | Cần endpoint công khai |

### Luồng Webhook (Stripe-style)

```
1. Client đăng ký: POST /webhooks + URL + events + secret
2. Sự kiện xảy ra → Server tạo event object
3. Server tính HMAC-SHA256(secret, payload)
4. Server POST → client URL + X-Webhook-Signature header
5. Client verify chữ ký trước khi xử lý
6. Client trả 200 → Server đánh dấu "delivered"
7. Client trả !2xx → Server retry (max 3 lần, exponential backoff)
```

### Verify chữ ký

```python
import hmac, hashlib

def verify(secret: str, payload: bytes, signature: str) -> bool:
    expected = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

**Tại sao cần verify?**
- Ngăn giả mạo: bất kỳ ai có URL đều có thể POST vào endpoint
- HMAC đảm bảo payload chỉ đến từ server nắm giữ secret

---

## REST vs gRPC vs GraphQL

### Khi nào dùng REST?
- Public API cần dễ document và debug
- CRUD resource đơn giản
- Cần HTTP cache, CDN
- Team chưa quen với schema-first tools

### Khi nào dùng gRPC?
- Internal microservices (latency thấp, throughput cao)
- Bidirectional streaming (live feed, chat)
- Strongly-typed contracts quan trọng
- Polyglot environment (Go + Java + Python cùng giao tiếp)

### Khi nào dùng GraphQL?
- Client linh hoạt chọn fields (mobile vs web cần data khác nhau)
- Aggregate data từ nhiều sources trong 1 request
- Real-time với Subscription
- Rapid iteration — frontend thay schema không cần đợi backend

### Thực tế tại Stripe & GitHub

| | Stripe | GitHub |
|---|--------|--------|
| Public API | REST | REST |
| Internal ops | REST + gRPC | REST |
| Complex queries | — | GraphQL v4 |
| Streaming | Webhooks | Webhooks + SSE |

---

## Phân tích Stripe API — Best Practices

1. **Idempotency Keys**: `Idempotency-Key: <uuid>` cho POST → safe retry
2. **API Versioning**: Header `Stripe-Version: 2024-06-20` — không dùng URL path
3. **Cursor Pagination**: `?starting_after=ch_xxx` thay vì `?page=2` → stable khi data thay đổi
4. **Expand**: `?expand[]=customer` — selective eager loading thay vì N+1 requests
5. **Webhook Timestamp**: `Stripe-Signature: t=<unix_ts>,v1=<hmac>` → ngăn replay attack

---

## Phân tích GitHub API — Best Practices

1. **Link Header Pagination**: `Link: <url>; rel="next", <url>; rel="last"` — không trong body
2. **HATEOAS via URL fields**: `comments_url`, `commits_url`, `labels_url` trong mọi resource
3. **Delivery ID**: `X-GitHub-Delivery: <uuid>` → idempotent event processing
4. **Dual API**: REST cho CRUD đơn giản, GraphQL cho queries phức tạp
5. **Rate Limit Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

---

## Tổng kết

```
Pattern       │ Giải quyết vấn đề gì?
──────────────┼────────────────────────────────────────────
CRUD          │ Standard resource operations
Query         │ Client kiểm soát data shape & volume
HATEOAS       │ Discoverable API, state-driven navigation
Event-driven  │ Loose coupling, async side effects
Webhook       │ Real-time push thay vì polling
```

**Nguyên tắc kết hợp**: 
- CRUD là nền tảng → thêm Query để filter/sort
- HATEOAS để expose state machine
- Events để trigger side effects
- Webhooks để notify external systems
