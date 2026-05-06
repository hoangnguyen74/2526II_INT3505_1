# Hướng dẫn Demo Buổi 9: API Versioning

## Chuẩn bị (làm trước khi lên lớp)

```bash
cd 9_api_versioning
pip install -r requirements.txt
```

## Trình tự Demo trên lớp

### Bước 1: Bật server FastAPI
```bash
py -m uvicorn main:app --reload
```
→ Swagger UI: http://localhost:8000/docs (đây là công cụ demo chính!)

---

### Bước 2: Demo chiến lược URL Path (v1 vs v2)

**2a. Tạo thanh toán v1 (có lỗi bảo mật):**
```bash
POST /api/v1/payments
Body:
{
  "amount": "50000",
  "card_number": "4111111111111111",
  "description": "Thanh toan don hang"
}
```
→ Chỉ cho lớp: Response trả lại toàn bộ `card_number` (lỗi bảo mật!)
→ Click tab **Headers** trong Response: thấy `Deprecation: true`, `Sunset: 2026-09-01`

**2b. Tạo thanh toán v2 (đã fix):**
```bash
POST /api/v2/payments
Body:
{
  "amount": 5000000,
  "currency": "VND",
  "card_last4": "1111",
  "description": "Thanh toan",
  "idempotency_key": "order-123"
}
```
→ Chỉ cho lớp: card đã mask `****-****-****-1111`, response bọc trong `{data, meta}`

**2c. Demo chống gửi trùng (idempotency):**
→ Gửi lại request v2 với cùng `idempotency_key: "order-123"`
→ Server trả `"duplicate": true` – không tạo bản ghi mới!

---

### Bước 3: Demo chiến lược Header Versioning

```bash
# Không gửi header → mặc định v1 (mảng phẳng)
GET /api/products

# Gửi header X-API-Version: 2 → v2 (bọc data + meta)
GET /api/products
Headers: X-API-Version: 2
```
→ So sánh 2 response: cùng URL, khác header, khác kết quả

---

### Bước 4: Demo chiến lược Query Param

```bash
# Mặc định v1
GET /api/orders

# Thêm ?version=2
GET /api/orders?version=2
```
→ v2 có thêm `total_formatted: "150,000 VND"`

---

### Bước 5: Xem Migration Guide

```bash
GET /api/migration-guide
```
→ Server trả JSON hướng dẫn chi tiết 4 breaking changes + timeline 4 giai đoạn

---

## Cấu trúc thư mục

```
9_api_versioning/
├── main.py                  # FastAPI server (3 chiến lược versioning)
├── slides.md                # Nội dung slide
├── requirements.txt         # Dependencies Python
└── DEMO_GUIDE.md            # File này
```

## Lưu ý khi demo
- Dùng **Swagger UI** (http://localhost:8000/docs) để demo cho nhanh và trực quan
- Các endpoint đã được nhóm theo tags: "Strategy 1", "Strategy 2", "Strategy 3", "Lifecycle"
- Khi demo v1, nhớ **click vào tab Headers** của Response để chỉ deprecation headers
