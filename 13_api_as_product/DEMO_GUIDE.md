# Buổi 13: API as a Product — Demo Guide

## Khởi động

```bash
cd 13_api_as_product
pip install -r requirements.txt
py -m uvicorn main:app --reload
```

- Swagger UI: http://localhost:8000/docs
- Developer Portal: mở `portal.html` trực tiếp trong trình duyệt

---

## Phần 1 — Developer Experience

### 1.1 Xem bảng giá

```bash
curl http://localhost:8000/plans | python -m json.tool
```

**Hỏi lớp**: Tại sao Free plan lại cần? (Acquisition funnel)

---

### 1.2 Đăng ký API key (Free)

```bash
curl -X POST http://localhost:8000/developers/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Demo User","email":"demo@test.com","plan":"free"}'
```

**Quan sát**: Key được cấp ngay, không cần phê duyệt → **Time-to-first-call < 1 phút**.

Lưu lại `api_key` từ response (dạng `sk_xxxxxxxx`).

---

### 1.3 Gọi API với key

```bash
# Thay YOUR_KEY bằng key vừa nhận
curl -H "X-API-Key: YOUR_KEY" http://localhost:8000/api/v1/products
```

**Quan sát** response headers:
```
X-Plan: free
X-Quota-Limit: 100
X-Quota-Remaining: 99
X-Response-Time: 12.3ms
```

---

### 1.4 Sandbox — không cần key

```bash
# Ai cũng gọi được, không tốn quota
curl http://localhost:8000/sandbox/products
```

**Quan sát**: data có `[DEMO]` prefix, có hướng dẫn đăng ký key.

---

## Phần 2 — Quota & Monetization

### 2.1 Gọi API không có key → 422/401

```bash
curl http://localhost:8000/api/v1/products
# → 422: X-API-Key header bắt buộc

curl -H "X-API-Key: sk_invalid" http://localhost:8000/api/v1/products
# → 401: Invalid API key
```

---

### 2.2 Feature gating — Search chỉ cho Pro+

```bash
# Dùng key của Free user
curl -H "X-API-Key: YOUR_FREE_KEY" \
  "http://localhost:8000/api/v1/search?q=iphone"
# → 403: FEATURE_LOCKED với hướng dẫn upgrade
```

**Thảo luận**: Feature gating vs. Quota limit — dùng khi nào?

---

### 2.3 Nâng cấp plan

```bash
curl -X POST http://localhost:8000/developers/upgrade \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@test.com","new_plan":"pro"}'
```

Sau đó gọi lại search → thành công.

---

### 2.4 Xem usage của developer

```bash
curl http://localhost:8000/developers/demo@test.com/usage
```

**Quan sát**: `today.used`, `today.remaining`, `daily_history`.

---

## Phần 3 — KPI Analytics (Admin)

```bash
# Admin key: admin-secret-key
curl -H "X-Admin-Key: admin-secret-key" \
  http://localhost:8000/admin/analytics | python -m json.tool
```

**KPIs có trong response**:
- `registered_developers`: Tổng số đăng ký
- `active_developers_today`: Active trong ngày
- `total_api_calls`: Tổng lượt gọi
- `error_rate_percent`: Tỉ lệ lỗi
- `calls_by_plan`: Phân bố theo plan
- `top_endpoints`: Endpoints phổ biến nhất
- `monthly_recurring_revenue_usd`: Doanh thu MRR

```bash
# Danh sách developers + revenue breakdown
curl -H "X-Admin-Key: admin-secret-key" \
  http://localhost:8000/admin/developers | python -m json.tool
```

---

## Phần 4 — Developer Portal (portal.html)

1. Mở `portal.html` trong trình duyệt
2. Demo live stats tự cập nhật mỗi 5 giây
3. Điền form đăng ký → nhận key hiển thị ngay
4. Tab Quick Start → copy code mẫu
5. My Usage → nhập email → xem usage bar + quota

---

## Phần 5 — Business Model Canvas

Mở `business_model_canvas.md` và đi qua:
1. **Customer Segments**: Free (acquisition) → Pro (main rev) → Enterprise (high value)
2. **Revenue Streams**: Freemium vs Pay-per-call
3. **KPIs**: Conversion rate, Churn, MRR, ARPU
4. **Launch Strategy**: Private Beta → Public Beta → GA

**Thực hành nhóm**: Áp dụng BMC cho API nhóm đang làm.

---

## Tóm tắt

| Khái niệm | Demo |
|-----------|------|
| Developer Experience | Đăng ký → key < 1 phút, sandbox không cần key |
| Freemium | Free 100 calls/ngày, nâng lên Pro/Enterprise |
| Feature Gating | Search API chỉ cho Pro+ |
| Quota Enforcement | Header X-Quota-Remaining, 429 khi hết |
| KPI Analytics | Admin dashboard: MRR, error rate, top endpoints |
| Developer Portal | portal.html: pricing, register, usage dashboard |
