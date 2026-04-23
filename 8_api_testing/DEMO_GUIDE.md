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
```bash
locust
```
1. Mở http://localhost:8089
2. Users: 50, Spawn rate: 5, Host: http://localhost:8000
3. Start Swarming → Xem biểu đồ Response Time & Error Rate

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
