# Buổi 9: API Versioning và Lifecycle Management

> **Thời lượng:** 30 phút · **Đối tượng:** SV năm 3 (đã biết REST, đã làm buổi 7–8)
> **Mục tiêu:** Hiểu 3 chiến lược versioning, xử lý breaking changes, viết deprecation notice

---

## Slide 1: Mở đầu – Tại sao API cần Versioning?

### Nội dung

**Tình huống thực tế:**
- Bạn phát hành API thanh toán, 50 ứng dụng đang sử dụng
- Khách hàng yêu cầu thêm trường `currency` (loại tiền), đổi `amount` từ string → integer
- Nếu sửa trực tiếp → **50 app cùng lúc bị hỏng** (Breaking Change)

**Versioning giải quyết gì?**
- Cho phép **v1 cũ vẫn chạy** trong khi v2 mới triển khai song song
- Developers có thời gian chuyển đổi (migration) thay vì bị ép buộc
- Đảm bảo **backward compatibility** – nguyên tắc vàng của API public

> **Quy tắc:** Không bao giờ phá vỡ API đang có người dùng. Hãy tạo phiên bản mới.

### Speaker Notes
```
Mở đầu: "Ai đã từng cập nhật app trên điện thoại xong bị lỗi vì server đổi API?"
Giải thích: Breaking Change = thay đổi khiến code cũ không hoạt động được nữa.
Ví dụ đời thường: Ổ cắm điện 2 chân → 3 chân. Nếu bỏ ổ 2 chân ngay → 
cả nhà mất điện. Phải lắp song song 2 loại ổ, rồi từ từ chuyển.
```

---

## Slide 2: 3 Chiến lược Versioning

### Nội dung

| Chiến lược | Ví dụ | Ưu điểm | Nhược điểm |
|------------|-------|---------|------------|
| **1. URL Path** | `/api/v1/payments` → `/api/v2/payments` | Rõ ràng nhất, dễ hiểu, dễ cache | URL dài, phải maintain nhiều route |
| **2. Header** | `X-API-Version: 2` | URL sạch, không thay đổi endpoint | Khó test bằng trình duyệt, dev dễ quên |
| **3. Query Param** | `/api/orders?version=2` | Dễ test, dễ chuyển đổi | Không RESTful chuẩn, dễ bị cache sai |

**Thực tế doanh nghiệp:**
- **URL Path** là phổ biến nhất: Stripe (`/v1/charges`), GitHub (`/v3/repos`)
- **Header**: Accept header (`application/vnd.github.v3+json`)
- **Query**: Google Maps API (`&v=3.54`)

### Speaker Notes
```
Hỏi lớp: "Theo các bạn, cách nào phổ biến nhất?" → URL Path.
Giải thích: URL Path thắng vì khi dev nhìn URL là biết ngay đang gọi version nào.
Header versioning thường dùng cho API nội bộ (internal), không public.
Demo: Mở Swagger UI, chỉ cho thấy 3 nhóm endpoint tương ứng 3 chiến lược.
```

---

## Slide 3: Demo chiến lược 1 – URL Path Versioning

### Nội dung

**Cùng 1 tài nguyên "Payment", 2 URL khác nhau:**

```
POST /api/v1/payments    →    POST /api/v2/payments
```

**v1 (thiết kế cũ – có lỗi):**
```json
{
  "amount": "50000",              // ⚠ String → dễ sai khi so sánh
  "card_number": "4111111111111111",  // ⚠ Lộ toàn bộ số thẻ!
  "description": "Thanh toan"
}
```

**v2 (thiết kế mới – đã sửa):**
```json
{
  "amount": 5000000,              // ✅ Integer, tính bằng xu
  "currency": "VND",              // ✅ Mới: loại tiền tệ
  "card_last4": "1111",           // ✅ Chỉ 4 số cuối
  "description": "Thanh toan",
  "idempotency_key": "order-123"  // ✅ Mới: chống gửi trùng
}
```

### Speaker Notes
```
[DEMO TRÊN POSTMAN hoặc Swagger UI http://localhost:8000/docs]
1. Gọi POST /api/v1/payments → Chỉ cho lớp thấy response trả card_number đầy đủ (lỗi bảo mật!)
2. Gọi POST /api/v2/payments → Response bọc trong {data: ..., meta: ...}, card đã mask ****-1111
3. Chỉ vào Response Headers của v1 → Thấy header "Deprecation: true" và "Sunset: 2026-09-01"
4. Hỏi lớp: "Nếu bạn là dev mobile, bạn sẽ phản ứng thế nào khi thấy header Sunset?"
```

---

## Slide 4: Demo chiến lược 2 – Header Versioning

### Nội dung

**Cùng 1 URL, kết quả khác nhau tuỳ header:**

```bash
# Gọi v1 (mặc định, hoặc gửi X-API-Version: 1)
GET /api/products
→ Trả về mảng phẳng: [{id: 1, name: "iPhone"}, ...]

# Gọi v2 (gửi header X-API-Version: 2)
GET /api/products
Headers: X-API-Version: 2
→ Trả về wrapper: {data: [...], meta: {total: 2}}
```

**Code FastAPI:**
```python
@app.get("/api/products")
def get_products(
    x_api_version: str = Header(default="1", alias="X-API-Version")
):
    if x_api_version == "2":
        return {"data": products, "meta": {"total": len(products)}}
    else:
        return products   # v1: mảng phẳng
```

### Speaker Notes
```
[DEMO]
1. Trên Postman: GET /api/products không gửi header → Nhận mảng phẳng (v1)
2. Thêm header X-API-Version: 2 → Nhận wrapper {data, meta} (v2)
3. Nhấn mạnh: URL hoàn toàn giống nhau, chỉ khác header
4. Nhược điểm: Nếu quên gửi header → mặc định v1, dev không biết có v2 tồn tại
```

---

## Slide 5: Demo chiến lược 3 – Query Param Versioning

### Nội dung

```bash
# v1 mặc định
GET /api/orders
→ [{id: "ORD-001", total: 150000, items: 3}]

# v2 qua query param
GET /api/orders?version=2
→ {data: [{..., total_formatted: "150,000 VND"}], meta: {...}}
```

**So sánh 3 chiến lược – Khi nào dùng cái nào?**

| Tình huống | Nên dùng |
|------------|----------|
| API public cho bên thứ 3 (Stripe, Shopee) | **URL Path** – rõ ràng nhất |
| API nội bộ giữa microservices | **Header** – URL sạch |
| Thử nghiệm nhanh, A/B testing | **Query Param** – dễ switch |
| Không chắc chọn gì | **URL Path** – an toàn nhất |

### Speaker Notes
```
[DEMO]
1. GET /api/orders → v1
2. GET /api/orders?version=2 → v2, có thêm total_formatted
3. Tổng kết: Chỉ ra bảng so sánh, nhấn mạnh URL Path là lựa chọn an toàn nhất
4. Hỏi lớp: "API trường mình /api/students nên dùng chiến lược nào?" → URL Path
```

---

## Slide 6: Breaking Changes – Thay đổi gì thì bị "phá"?

### Nội dung

**Breaking Changes (Phá vỡ – PHẢI tạo version mới):**
- ❌ Xoá hoặc đổi tên field (`card_number` → `card_last4`)
- ❌ Đổi kiểu dữ liệu (`amount: string` → `amount: integer`)
- ❌ Thêm field **bắt buộc** mới (`currency` required)
- ❌ Đổi cấu trúc response (`{id, name}` → `{data: {id, name}}`)
- ❌ Đổi HTTP method hoặc status code

**Non-Breaking Changes (An toàn – KHÔNG cần version mới):**
- ✅ Thêm field **tuỳ chọn** mới (VD: thêm `note` optional)
- ✅ Thêm endpoint mới
- ✅ Thêm giá trị enum mới
- ✅ Tăng giới hạn (max length 50 → 100)
- ✅ Sửa lỗi trả về sai

### Speaker Notes
```
Đây là slide LÝ THUYẾT quan trọng nhất. Nhấn mạnh:
"Quy tắc đơn giản: Nếu code cũ của client GỌI Y NGUYÊN mà vẫn hoạt động → Non-breaking. 
Nếu client phải SỬA CODE → Breaking."
Liên hệ case study: v1 → v2 có 4 breaking changes: đổi kiểu amount, đổi tên card field, 
thêm currency bắt buộc, thay đổi response format.
```

---

## Slide 7: Deprecation – Quy trình "khai tử" API cũ

### Nội dung

**4 giai đoạn Sunset một API version:**

```
Giai đoạn 1          Giai đoạn 2          Giai đoạn 3          Giai đoạn 4
  Ra mắt v2      →     Cảnh báo       →     Hạn chế        →     Tắt v1
  v1 vẫn chạy        Header Deprecation    Rate limit v1       Trả 410 Gone
  (song song)         + Email thông báo     10 req/phút         "API đã ngừng"
  
  01/05/2026          01/07/2026           01/08/2026          01/09/2026
```

**HTTP Headers chuẩn cho Deprecation:**
```http
Deprecation: true
Sunset: 2026-09-01T00:00:00Z
Link: </api/v2/payments>; rel="successor-version"
```

### Speaker Notes
```
[DEMO]
1. Gọi POST /api/v1/payments trên Postman
2. Click tab "Headers" trong Response → Chỉ cho lớp thấy 3 header: Deprecation, Sunset, Link
3. Giải thích: Đây là chuẩn RFC 8594 (Sunset Header) – không phải tự chế.
4. "Khi dev thấy header này → biết deadline để migration, không bị bất ngờ."
```

---

## Slide 8: Case Study – Migration Plan (v1 → v2 Payment API)

### Nội dung

**Bảng đối chiếu thay đổi:**

| Hạng mục | v1 (cũ) | v2 (mới) | Hành động migration |
|----------|---------|----------|---------------------|
| `amount` | `"50000"` (string) | `5000000` (integer, xu) | Chuyển string → int, ×100 |
| `card_number` | `"4111...1111"` (full) | `"1111"` (4 số cuối) | Cắt chuỗi, lấy 4 ký tự cuối |
| `currency` | Không có | `"VND"` (bắt buộc) | Thêm field vào request body |
| Response | `{id, amount, ...}` | `{data: {...}, meta: {...}}` | Đọc `response.data` thay vì `response` |

**Code migration phía client (trước / sau):**
```python
# ❌ Code cũ (gọi v1)
resp = requests.post("/api/v1/payments", json={
    "amount": "50000",
    "card_number": "4111111111111111"
})
payment = resp.json()    # Trả trực tiếp object

# ✅ Code mới (gọi v2)
resp = requests.post("/api/v2/payments", json={
    "amount": 5000000,          # Integer, đơn vị xu
    "currency": "VND",          # Thêm trường mới
    "card_last4": "1111"        # Chỉ 4 số cuối
})
payment = resp.json()["data"]   # Đọc từ wrapper .data
```

### Speaker Notes
```
Slide này cực quan trọng cho case study.
[DEMO]
1. Mở Swagger UI: GET /api/migration-guide → Server trả về JSON hướng dẫn chi tiết
2. Chỉ cho lớp thấy: Trong thực tế, trang migration guide này sẽ nằm trên docs website
3. "Một API provider tốt luôn cung cấp migration guide kèm code sample cho developer."
```

---

## Slide 9: Viết Deprecation Notice cho Developers

### Nội dung

**Mẫu thông báo deprecation chuyên nghiệp:**

```markdown
📢 THÔNG BÁO: API Payment v1 sẽ ngừng hoạt động

Kính gửi các Developer,

Payment API v1 (/api/v1/payments) sẽ chính thức ngừng hoạt động 
vào ngày 01/09/2026.

📅 Timeline:
  • 01/07/2026: Header Deprecation được gắn vào mọi response v1
  • 01/08/2026: Rate limit v1 giảm xuống 10 requests/phút
  • 01/09/2026: v1 trả về HTTP 410 Gone

🔄 Hành động cần thực hiện:
  1. Đổi base URL: /api/v1/ → /api/v2/
  2. Cập nhật field amount: string → integer (đơn vị xu)
  3. Thay card_number bằng card_last4
  4. Thêm trường currency (mặc định "VND")
  5. Đọc response từ .data thay vì trực tiếp

📖 Tài liệu: GET /api/migration-guide
📧 Hỗ trợ: api-support@company.com
```

### Speaker Notes
```
Cho lớp xem mẫu notice này và hỏi: "Thông báo này thiếu gì không?"
Đáp án gợi ý: Code sample (đã có ở slide trước), SDK version mới, changelog link.
Nhấn mạnh: Deprecation notice tốt = developer không bao giờ bị bất ngờ.
```

---

## Slide 10: Tổng kết

### Nội dung

**Kiến thức đã học:**
- ✅ 3 chiến lược versioning: URL Path (phổ biến nhất), Header, Query Param
- ✅ Phân biệt Breaking vs Non-Breaking Changes
- ✅ Quy trình Deprecation 4 giai đoạn (ra mắt → cảnh báo → hạn chế → tắt)
- ✅ HTTP headers chuẩn: `Deprecation`, `Sunset`, `Link`
- ✅ Viết Migration Plan và Deprecation Notice chuyên nghiệp

**Bài học quan trọng nhất:**
> "Versioning không chỉ là kỹ thuật, mà là **cam kết** với developer rằng bạn sẽ không phá vỡ ứng dụng của họ."

### Speaker Notes
```
Tổng kết ngắn gọn, hỏi lớp có câu hỏi không.
Nếu không ai hỏi: "Nếu bạn là Stripe, bạn sẽ chọn chiến lược versioning nào?" 
→ URL Path, vì API public cần rõ ràng tối đa.
```

---

## Phụ lục: Câu hỏi thường gặp

**Q1: Có cần version ngay từ đầu không? Hay chờ khi cần mới tạo?**
> Nên version ngay từ đầu (`/api/v1/...`). Chi phí thêm `/v1/` vào URL là 0, nhưng nếu không có sẵn, khi cần thêm v2 sẽ rất khó xử lý URL cũ không có version.

**Q2: Nên maintain bao nhiêu version cùng lúc?**
> Tối đa 2–3 version. Giữ quá nhiều → tốn tài nguyên bảo trì. Quy tắc: version cũ nhất không quá 12 tháng sau khi version mới ra.

**Q3: `idempotency_key` trong v2 là gì?**
> Là khoá chống gửi trùng. Khi mạng lag, client gửi 2 lần cùng 1 request → server nhận ra key trùng → chỉ xử lý 1 lần. Rất quan trọng cho API thanh toán (tránh trừ tiền 2 lần).

**Q4: Tại sao v2 dùng đơn vị "xu" (cent) cho amount thay vì đồng?**
> Tránh lỗi số thập phân (floating point). `0.1 + 0.2 = 0.30000000000000004` trong hầu hết ngôn ngữ. Stripe, PayPal đều dùng cent/xu để tránh lỗi này.

**Q5: Header `Sunset` là chuẩn gì?**
> RFC 8594, được IETF phê duyệt. Cho biết chính xác ngày API sẽ ngừng hoạt động. Client có thể đọc header này tự động để gửi alert cho team dev.
