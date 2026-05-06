# Hướng dẫn Demo Buổi 8

## Chuẩn bị (làm trước khi lên lớp)

```bash
cd 8_api_testing
pip install -r requirements.txt
npm install -g newman
```

## Trình tự Demo trên lớp

### Bước 1: Bật server FastAPI
```bash
py -m uvicorn main:app --reload
```
→ Server chạy tại http://localhost:8000
→ Swagger UI tại http://localhost:8000/docs

### Bước 2: Chạy Unit Test (pytest)
Mở terminal thứ 2:
```bash
py -m pytest test_unit.py -v
```
→ Kết quả: 5 passed (xanh lá)

### Bước 3: Import & Chạy Postman Collection
1. Mở Postman → Import → Chọn file `postman_collection.json`
2. Mở 1 request → Chỉ tab Tests cho lớp xem code JavaScript
3. Bấm "Run Collection" → Xem 12 test cases PASS

### Bước 4: Chạy Newman (CLI)
```bash
newman run postman_collection.json
```
→ Kết quả: Bảng tổng kết 5 requests, 12 assertions, 0 failed

### Bước 5: Load Test với Locust

> **Lưu ý:** Trên Windows nếu gõ `locust` bị lỗi "not recognized", hãy dùng lệnh:
```bash
py -m locust
```
Locust sẽ in ra dòng: `Starting web interface at http://localhost:8089`

#### Bước 5.1: Mở giao diện Locust
- Mở trình duyệt, truy cập: **http://localhost:8089**
- Bạn sẽ thấy 1 form với 3 ô cần điền

#### Bước 5.2: Cấu hình thông số
| Ô nhập | Giá trị | Ý nghĩa |
|--------|---------|---------|
| **Number of users** | `50` | Giả lập 50 người dùng đồng thời |
| **Ramp up (users/s)** | `5` | Cứ mỗi giây thêm 5 user mới vào hệ thống |
| **Host** | `http://localhost:8000` | Địa chỉ API FastAPI đang chạy |

#### Bước 5.3: Nhấn "Start" và quan sát
Sau khi nhấn **Start**, giao diện sẽ chuyển sang 3 tab quan trọng:

1. **Tab "Statistics"** — Bảng số liệu:
   - Cột **Avg (ms)**: Thời gian phản hồi trung bình. API `/products` sẽ rất nhanh (~5ms)
   - Cột **Fail**: Số request thất bại. Endpoint `/products/heavy/report` sẽ có lỗi vì ta đã **cố tình** code cho nó 30% trả lỗi 500
   - Chỉ vào 2 dòng này so sánh cho lớp thấy sự khác biệt

2. **Tab "Charts"** — Biểu đồ thời gian thực:
   - **Biểu đồ trên**: Response Time (ms) — đường xanh vọt lên khi nhiều user
   - **Biểu đồ giữa**: Requests per second (RPS/Throughput)
   - **Biểu đồ dưới**: Failures — sẽ có vệt đỏ nhấp nháy liên tục vì endpoint heavy

3. **Tab "Failures"** — Chi tiết lỗi:
   - Hiện rõ endpoint nào gây lỗi, lỗi gì (500 Internal Server Error)

#### Bước 5.4: Dừng test
- Nhấn nút **"Stop"** ở góc trên phải
- Locust sẽ giữ nguyên kết quả và biểu đồ để bạn trình bày tiếp

#### Điểm nhấn khi nói trước lớp
> Chỉ tay vào biểu đồ Failures và nói:
> *"Endpoint `/products/heavy/report` mình đã cố tình code cho nó chạy chậm 2 giây và 30% trả lỗi 500. Trong thực tế, nếu Error Rate vượt 1% thì đội DevOps phải vào cuộc ngay. Locust giúp ta phát hiện điểm yếu này TRƯỚC khi khách hàng thật vào dùng."*

## Cấu trúc thư mục

```
8_api_testing/
├── main.py                  # FastAPI server (5 CRUD endpoints)
├── test_unit.py             # Unit test với pytest
├── postman_collection.json  # Postman Collection (import vào Postman)
├── locustfile.py            # Kịch bản Load Test
├── requirements.txt         # Dependencies Python
├── slides.md                # Nội dung slide (paste vào Gemini AI)
└── DEMO_GUIDE.md            # File này
```
