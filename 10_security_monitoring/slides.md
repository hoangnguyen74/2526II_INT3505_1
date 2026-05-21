# Buổi 10: Service Operation – Security & Monitoring

> **Thời lượng:** 30 phút · **Đối tượng:** SV năm 3 (đã làm buổi 7–9)
> **Mục tiêu:** Hiểu observability (log, metrics, tracing), rate limiting, circuit breaker, security headers

---

## Slide 1: Mở đầu – API chạy được ≠ API sẵn sàng cho Production

### Nội dung

**Dev thường nghĩ:** "API chạy đúng trên máy mình là xong!"

**Thực tế production:**
- API bị gọi 10,000 req/s → Server sập vì không có **rate limiting**
- Dịch vụ thanh toán bên ngoài lỗi → Cả hệ thống treo theo vì không có **circuit breaker**
- Bị hack 3 ngày trước nhưng không ai biết → Vì không có **logging & monitoring**
- Hacker chèn `<script>` vào tên sản phẩm → Vì không có **input sanitization**

**3 trụ cột của Production-Ready API:**

| Trụ cột | Giải quyết vấn đề gì? |
|---------|----------------------|
| **Observability** | Biết chuyện gì đang xảy ra (logs, metrics, tracing) |
| **Resilience** | Chịu được lỗi mà không sập (rate limit, circuit breaker) |
| **Security** | Chống tấn công, bảo vệ dữ liệu (WAF, headers, audit log) |

### Speaker Notes
```
Mở đầu: "Các buổi trước mình xây API, test API, version API. 
Hôm nay là câu hỏi cuối cùng: Làm sao để API SỐNG SÓT trên production?"
Hỏi lớp: "Ai đã từng deploy xong rồi không biết API có đang chạy không?"
```

---

## Slide 2: Structured Logging – Không chỉ là print()

### Nội dung

**Vấn đề với `print()`:**
```python
print("User 123 vua tao don hang")      # ❌ Không có timestamp
print("Lỗi rồi!")                        # ❌ Không biết lỗi ở đâu
print(f"Request mat {duration}ms")       # ❌ Không search/filter được
```

**Structured Log (JSON format) – chuẩn production:**
```json
{
  "timestamp": "2026-05-15T07:30:00Z",
  "level": "INFO",
  "message": "POST /api/products",
  "service": "payment-api",
  "method": "POST",
  "path": "/api/products",
  "client_ip": "192.168.1.100",
  "duration_ms": 45.2,
  "status_code": 201
}
```

**Tại sao JSON?**
- Máy đọc được → Dễ import vào ELK Stack, Grafana, Datadog
- Có timestamp, level → Filter theo thời gian, mức độ nghiêm trọng
- Có context (IP, path, duration) → Debug nhanh gấp 10 lần

### Speaker Notes
```
[DEMO]
1. Bật server: py -m uvicorn main:app --reload
2. Gọi vài API trên Swagger UI
3. Chỉ cho lớp xem terminal: mỗi request sinh ra 2 dòng JSON log (request + response)
4. Gọi GET /api/logs/recent → Server trả lại 20 dòng log gần nhất dưới dạng JSON
5. Nhấn mạnh: "Trong production, log này được gửi tới ELK Stack hoặc Grafana Loki 
   để search và alert tự động."
```

---

## Slide 3: Metrics & Prometheus – Đo lường sức khỏe API

### Nội dung

**Metrics là gì?** Các con số thống kê về hoạt động của API theo thời gian.

**4 metrics quan trọng nhất (RED + Uptime):**

| Metric | Ý nghĩa | Ví dụ |
|--------|---------|-------|
| **Request Rate** | Bao nhiêu request/giây? | `http_requests_total{path="/api/products"} 1523` |
| **Error Rate** | Bao nhiêu % bị lỗi? | `http_errors_total{path="/api/products"} 12` |
| **Duration** | Trung bình mất bao lâu? | `http_request_duration_ms{path="..."} 42.50` |
| **Uptime** | Server đã chạy bao lâu? | `uptime_seconds 86400` |

**Prometheus format:**
```
# HELP http_requests_total So luong request
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/api/products"} 1523
http_requests_total{method="POST",path="/api/products"} 47

# HELP http_request_duration_ms Thoi gian xu ly TB
# TYPE http_request_duration_ms gauge
http_request_duration_ms{method="GET",path="/api/products"} 12.50
```

### Speaker Notes
```
[DEMO]
1. Gọi vài API khác nhau để tạo dữ liệu
2. Mở trình duyệt: http://localhost:8000/metrics
3. Chỉ cho lớp: format text Prometheus – mỗi dòng là 1 metric
4. Giải thích: Prometheus server sẽ gọi /metrics mỗi 15 giây để thu thập
5. "Grafana kết nối Prometheus → Vẽ dashboard biểu đồ đẹp tự động"
```

---

## Slide 4: Rate Limiting – Chống quá tải

### Nội dung

**Vấn đề:** Không giới hạn → 1 client gọi 10,000 req/s → Server chết → Tất cả user khác mất dịch vụ

**Rate Limiting là gì?** Giới hạn số request mỗi client được gọi trong 1 khoảng thời gian.

**Thuật toán Sliding Window:**
```
Cửa sổ 60 giây, tối đa 10 request:

Timeline: ──────────────────────────────→
Request:   ① ② ③ ④ ⑤ ⑥ ⑦ ⑧ ⑨ ⑩ ⑪ ← BỊ CHẶN!
                                         HTTP 429: Too Many Requests
```

**Response khi bị chặn:**
```json
HTTP 429 Too Many Requests
Headers:
  X-RateLimit-Limit: 10
  X-RateLimit-Remaining: 0
  Retry-After: 60

{
  "error": "TOO_MANY_REQUESTS",
  "message": "Vuot qua 10 request/60s. Vui long doi."
}
```

### Speaker Notes
```
[DEMO – Phần hay nhất!]
1. Mở terminal mới, chạy vòng lặp:
   for ($i=1; $i -le 15; $i++) { 
     $r = Invoke-WebRequest http://localhost:8000/api/limited -UseBasicParsing
     Write-Host "$i. Status: $($r.StatusCode) | Remaining: $($r.Headers['X-RateLimit-Remaining'])"
   }
2. Lớp sẽ thấy: Request 1-10 trả 200, request 11+ trả 429
3. Chỉ header X-RateLimit-Remaining đếm ngược: 9, 8, 7... 0
4. "Trong thực tế: API key khác nhau có limit khác nhau. Free=100/h, Pro=10000/h"
```

---

## Slide 5: Circuit Breaker – Ngắt mạch khi dịch vụ lỗi

### Nội dung

**Vấn đề:** Gọi dịch vụ bên ngoài (payment gateway, email service) → Service đó sập → Request của mình bị treo 30s → Toàn bộ hệ thống bị nghẽn

**Circuit Breaker hoạt động như cầu dao điện:**

```
   CLOSED (Bình thường)          OPEN (Chặn hết)          HALF_OPEN (Thử lại)
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│  Cho request đi  │ ───→  │  Chặn mọi request│ ───→  │  Cho 1 request   │
│  qua bình thường │  3    │  Trả 503 ngay    │  15s  │  thử lại         │
│                  │ lỗi   │  (không chờ)     │  chờ  │  OK → CLOSED     │
│  Đếm lỗi: 0/3   │       │                  │       │  Fail → OPEN     │
└──────────────────┘       └──────────────────┘       └──────────────────┘
```

**Lợi ích:**
- Không chờ timeout 30s → Trả lỗi ngay (fail fast)
- Server không bị nghẽn request đang treo
- Tự phục hồi khi service bên ngoài hoạt động lại

### Speaker Notes
```
[DEMO]
1. Gọi GET /api/external/payment-gateway nhiều lần
2. Khi gặp 3 lần lỗi liên tiếp → Circuit chuyển OPEN
3. Gọi tiếp → Nhận 503 ngay lập tức (không chờ)
4. Gọi GET /api/external/circuit-status → Xem state hiện tại
5. Đợi 15 giây → Circuit chuyển HALF_OPEN → Gọi lại → Nếu OK → CLOSED
6. Hoặc dùng POST /api/external/circuit-reset để reset nhanh khi demo
7. Ví dụ: "Netflix dùng Hystrix circuit breaker. Khi 1 microservice chết, 
   các service khác vẫn sống nhờ circuit breaker ngắt kịp thời."
```

---

## Slide 6: Security Headers – Lớp phòng thủ miễn phí

### Nội dung

**Mỗi response API nên có các header bảo mật:**

| Header | Chống tấn công gì? | Giá trị |
|--------|-------------------|---------|
| `X-Content-Type-Options` | MIME sniffing | `nosniff` |
| `X-Frame-Options` | Clickjacking (nhúng web vào iframe) | `DENY` |
| `X-XSS-Protection` | Cross-Site Scripting | `1; mode=block` |
| `Strict-Transport-Security` | Downgrade HTTPS → HTTP | `max-age=31536000` |

**Input Sanitization (WAF đơn giản):**
```python
# Chặn XSS trong input
if "<script>" in body.name.lower():
    raise HTTPException(400, "Phat hien ma doc")
```

### Speaker Notes
```
[DEMO]
1. Gọi bất kỳ API nào → Tab Headers trong Response → Chỉ 4 security headers
2. Thử tạo sản phẩm: POST /api/products với name = "<script>alert('hack')</script>"
   → Bị chặn, trả 400
3. Xem log: GET /api/logs/recent → Thấy dòng log cảnh báo "XSS attempt detected"
4. "Trong production thật, dùng WAF như Cloudflare, AWS WAF để chặn hàng trăm loại tấn công"
```

---

## Slide 7: Audit Log – Ai làm gì, lúc nào?

### Nội dung

**Audit Log ≠ Application Log**

| | Application Log | Audit Log |
|---|---|----|
| **Mục đích** | Debug lỗi | Truy vết hành động |
| **Ghi gì?** | Request/response, errors | AI tạo/sửa/xóa cái gì |
| **Ai đọc?** | Developer | Security team, auditor |
| **Ví dụ** | `POST /products 201 45ms` | `User admin XÓA product #5 lúc 10:30` |

**Mẫu audit log:**
```json
{
  "timestamp": "2026-05-15T10:30:00Z",
  "level": "INFO",
  "message": "PRODUCT_DELETED",
  "action": "DELETE",
  "resource": "product",
  "resource_id": 5,
  "data": {"id": 5, "name": "iPhone 16", "price": 28990000},
  "client_ip": "192.168.1.100"
}
```

### Speaker Notes
```
[DEMO]
1. Tạo 1 sản phẩm: POST /api/products
2. Xóa nó: DELETE /api/products/{id}
3. Xem audit log: GET /api/logs/audit
4. Chỉ cho lớp: Audit log ghi rõ AI xóa CÁI GÌ, lúc nào, từ IP nào
5. "Nếu nhân viên xóa dữ liệu rồi chối, audit log là bằng chứng không thể chối cãi."
```

---

## Slide 8: Tổng quan kiến trúc Observability

### Nội dung

```
                    ┌──────────────────────────┐
                    │     Grafana Dashboard    │
                    │  (Biểu đồ, Alert, Panel) │
                    └──────────┬───────────────┘
                               │ query
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
      ┌──────────────┐ ┌────────────┐ ┌──────────────┐
      │  Prometheus  │ │   Loki     │ │   Jaeger     │
      │  (Metrics)   │ │  (Logs)    │ │  (Tracing)   │
      └──────┬───────┘ └─────┬──────┘ └──────┬───────┘
             │ pull /metrics  │ push logs      │ traces
             ▼                ▼                ▼
      ┌─────────────────────────────────────────────┐
      │              FastAPI Application             │
      │  /metrics    JSON logs     trace_id headers  │
      └─────────────────────────────────────────────┘
```

| Thành phần | Vai trò | Tool phổ biến |
|-----------|---------|---------------|
| **Metrics** | Đếm, đo (request rate, latency) | Prometheus + Grafana |
| **Logs** | Chi tiết từng event | ELK Stack / Grafana Loki |
| **Tracing** | Theo dõi 1 request qua nhiều service | Jaeger / Zipkin |

### Speaker Notes
```
"3 trụ cột này gọi là Observability. Hôm nay mình demo Metrics + Logs.
Tracing thường dùng khi có microservices (1 request đi qua 5 service khác nhau)."
Chỉ sơ đồ: Application push data lên → Tools thu thập → Grafana hiển thị.
```

---

## Slide 9: Tổng kết

### Nội dung

**Checklist Production-Ready API:**

| # | Hạng mục | Công cụ demo | Trạng thái |
|---|---------|-------------|------------|
| 1 | Structured Logging (JSON) | Python logging + JSONFormatter | ✅ |
| 2 | Prometheus Metrics | GET /metrics | ✅ |
| 3 | Rate Limiting (10 req/min) | Sliding Window + 429 | ✅ |
| 4 | Circuit Breaker | 3 states: CLOSED/OPEN/HALF_OPEN | ✅ |
| 5 | Security Headers | X-Content-Type-Options, HSTS... | ✅ |
| 6 | Input Sanitization (WAF) | Chặn `<script>` | ✅ |
| 7 | Audit Log | Ghi CREATE/DELETE riêng file | ✅ |
| 8 | Health Check | GET /health | ✅ |

> "API chạy được chỉ là bước 1. API sống sót trên production mới là đẳng cấp."

### Speaker Notes
```
Tổng kết: Đi qua checklist, mỗi mục nhắc lại 1 câu ngắn.
Hỏi lớp: "Nếu chỉ được chọn 2 thứ triển khai đầu tiên, chọn gì?"
Gợi ý: Logging + Rate Limiting – vì logging để biết chuyện gì xảy ra, 
rate limiting để không bị sập.
```

---

## Phụ lục: Câu hỏi thường gặp

**Q1: Rate limiting theo IP hay theo API key?**
> Theo IP cho anonymous request. Theo API key cho authenticated request (mỗi khách hàng có limit khác nhau). Trong demo mình dùng IP cho đơn giản.

**Q2: Circuit Breaker khác retry thế nào?**
> Retry = cứ thử lại, có thể làm service quá tải hơn. Circuit Breaker = NGỪNG gọi luôn khi phát hiện lỗi liên tiếp, cho service thời gian phục hồi. Thường dùng kết hợp: Retry 3 lần → vẫn fail → Circuit OPEN.

**Q3: Tại sao ghi log ra file thay vì database?**
> File nhanh hơn 100x, không bị phụ thuộc DB. Log được ghi ra file (hoặc stdout) → Tool như Fluentd/Logstash thu thập → Đẩy vào Elasticsearch để search. Không nên ghi log trực tiếp vào DB.

**Q4: `X-RateLimit-Remaining` có bắt buộc không?**
> Không bắt buộc theo RFC, nhưng là best practice. Giúp client biết còn bao nhiêu request → tự điều chỉnh tốc độ (throttling). GitHub, Twitter đều trả header này.

**Q5: WAF là gì? Có khác input validation không?**
> WAF (Web Application Firewall) là lớp bảo vệ ở tầng mạng, chặn request trước khi đến server. Input validation là code trong app. Demo mình chặn `<script>` ở tầng app. WAF thật (Cloudflare, AWS WAF) chặn ở tầng proxy, mạnh hơn nhiều.
