# Hướng dẫn Demo Buổi 10: Security & Monitoring

## Chuẩn bị

```bash
cd 10_security_monitoring
pip install -r requirements.txt
```

## Bật server

```bash
py -m uvicorn main:app --reload
```
→ Swagger UI: http://localhost:8000/docs
→ Metrics: http://localhost:8000/metrics

---

## Kịch bản Demo (theo thứ tự slide)

### Demo 1: Structured Logging
1. Gọi vài API trên Swagger UI (GET /api/products, POST /api/products)
2. Xem terminal → Mỗi request sinh 2 dòng JSON log
3. Gọi `GET /api/logs/recent` → Xem log dưới dạng JSON đẹp

### Demo 2: Prometheus Metrics
1. Gọi thêm vài API khác nhau
2. Mở trình duyệt: **http://localhost:8000/metrics**
3. Chỉ cho lớp: format text Prometheus, mỗi dòng là 1 metric
4. So sánh request count và duration giữa các endpoint

### Demo 3: Rate Limiting (ĐẶC SẮC!)
Mở terminal mới, chạy:
```powershell
for ($i=1; $i -le 15; $i++) {
  try {
    $r = Invoke-WebRequest http://localhost:8000/api/limited -UseBasicParsing
    Write-Host "Request $i : Status $($r.StatusCode) | Remaining: $($r.Headers['X-RateLimit-Remaining'])"
  } catch {
    Write-Host "Request $i : Status 429 - BI CHAN!" -ForegroundColor Red
  }
}
```
→ Request 1-10: Status 200, Remaining đếm ngược
→ Request 11+: Status **429 Too Many Requests** (đỏ lè!)

### Demo 4: Circuit Breaker
1. Gọi `GET /api/external/payment-gateway` nhiều lần liên tiếp
2. Mỗi lần: 60% OK (200), 40% lỗi (502)
3. Sau 3 lần lỗi → Circuit OPEN → Gọi tiếp nhận 503 ngay lập tức
4. Gọi `GET /api/external/circuit-status` → Xem state
5. Đợi 15 giây hoặc gọi `POST /api/external/circuit-reset` → Circuit reset

### Demo 5: Security Headers + WAF
1. Gọi bất kỳ API → Tab Headers → Chỉ 4 security headers
2. POST /api/products với body:
```json
{
  "name": "<script>alert('hack')</script>",
  "price": 1000
}
```
→ Bị chặn, trả **400**
3. Gọi `GET /api/logs/recent` → Thấy log cảnh báo XSS

### Demo 6: Audit Log
1. POST /api/products → Tạo sản phẩm
2. DELETE /api/products/{id} → Xóa sản phẩm
3. GET /api/logs/audit → Xem audit log ghi rõ: AI làm GÌ, lúc NÀO, từ IP NÀO

---

## Cấu trúc thư mục

```
10_security_monitoring/
├── main.py              # FastAPI server (logging, metrics, rate limit, circuit breaker)
├── slides.md            # Nội dung slide
├── requirements.txt     # Dependencies
├── DEMO_GUIDE.md        # File này
└── logs/                # (Tự tạo khi chạy)
    ├── api.log          # Application log
    └── audit.log        # Audit log
```
