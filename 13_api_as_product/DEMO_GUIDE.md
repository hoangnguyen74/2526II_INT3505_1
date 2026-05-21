# Buổi 13: API as a Product — Demo Guide

## Khởi động

```powershell
cd 13_api_as_product
pip install -r requirements.txt
py -m uvicorn main:app --reload
```

- Swagger UI: http://localhost:8000/docs
- Developer Portal: mở `portal.html` trực tiếp trong trình duyệt

---

## Phần 1 — Developer Experience

### 1.1 Xem bảng giá

```powershell
Invoke-RestMethod http://localhost:8000/plans
```

**Hỏi lớp**: Tại sao Free plan lại cần? (Acquisition funnel)

---

### 1.2 Sandbox — không cần key

```powershell
# Ai cũng gọi được, không tốn quota
Invoke-RestMethod http://localhost:8000/sandbox/products
```

**Quan sát**: data có `[DEMO]` prefix, có hướng dẫn đăng ký key.

---

### 1.3 Đăng ký API key (Free)

```powershell
$reg = Invoke-RestMethod -Method POST http://localhost:8000/developers/register `
  -ContentType "application/json" `
  -Body '{"name":"Demo User","email":"demo@test.com","plan":"free"}'

$key = $reg.api_key
Write-Host "API Key: $key"
```

**Quan sát**: Key được cấp ngay, không cần phê duyệt → **Time-to-first-call < 1 phút**.

---

### 1.4 Gọi API với key — xem response headers

```powershell
$resp = Invoke-WebRequest -Uri http://localhost:8000/api/v1/products `
  -Headers @{"X-API-Key"=$key}

# Xem headers quota
$resp.Headers["X-Plan"]
$resp.Headers["X-Quota-Limit"]
$resp.Headers["X-Quota-Remaining"]
$resp.Headers["X-Response-Time"]
```

**Quan sát** response headers:
```
X-Plan: free
X-Quota-Limit: 100
X-Quota-Remaining: 99
X-Response-Time: 12.3ms
```

---

## Phần 2 — Quota & Monetization

### 2.1 Gọi API không có key → 422/401

```powershell
# Gọi không có key --> 422
try { Invoke-RestMethod http://localhost:8000/api/v1/products } catch { $_.ErrorDetails.Message }

# Key sai --> 401
try {
    Invoke-RestMethod http://localhost:8000/api/v1/products `
      -Headers @{"X-API-Key"="sk_invalid"}
} catch { $_.ErrorDetails.Message }
```

---

### 2.2 Feature gating — Search chỉ cho Pro+

```powershell
# Dùng key của Free user --> 403 FEATURE_LOCKED
try {
    Invoke-RestMethod "http://localhost:8000/api/v1/search?q=iphone" `
      -Headers @{"X-API-Key"=$key}
} catch { $_.ErrorDetails.Message }
```

**Thảo luận**: Feature gating vs. Quota limit — dùng khi nào?

---

### 2.3 Nâng cấp plan

```powershell
Invoke-RestMethod -Method POST http://localhost:8000/developers/upgrade `
  -ContentType "application/json" `
  -Body '{"email":"demo@test.com","new_plan":"pro"}'

# Sau khi nâng cấp — Search thành công
Invoke-RestMethod "http://localhost:8000/api/v1/search?q=iphone" `
  -Headers @{"X-API-Key"=$key}
```

---

### 2.4 Xem usage của developer

```powershell
Invoke-RestMethod http://localhost:8000/developers/demo@test.com/usage
```

**Quan sát**: `today.used`, `today.remaining`, `daily_history`.

---

## Phần 3 — KPI Analytics (Admin)

```powershell
# Dashboard KPI: MRR, error rate, top endpoints
Invoke-RestMethod http://localhost:8000/admin/analytics `
  -Headers @{"X-Admin-Key"="admin-secret-key"}

# Danh sách developers + revenue breakdown
Invoke-RestMethod http://localhost:8000/admin/developers `
  -Headers @{"X-Admin-Key"="admin-secret-key"}
```

**KPIs có trong response**:
- `registered_developers`: Tổng số đăng ký
- `active_developers_today`: Active trong ngày
- `total_api_calls`: Tổng lượt gọi
- `error_rate_percent`: Tỉ lệ lỗi
- `calls_by_plan`: Phân bố theo plan
- `top_endpoints`: Endpoints phổ biến nhất
- `monthly_recurring_revenue_usd`: Doanh thu MRR

---

## Phần 4 — Developer Portal (portal.html)

1. Mở `portal.html` trong trình duyệt (double-click file)
2. **Live Stats** tự cập nhật mỗi 5 giây từ `/admin/analytics`
3. **Register** form → nhận API key hiển thị ngay
4. **My Usage** → nhập email → xem quota bar đổi màu (xanh/vàng/đỏ)
5. **Quick Start** tabs → copy code mẫu cURL/Python/JavaScript

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
