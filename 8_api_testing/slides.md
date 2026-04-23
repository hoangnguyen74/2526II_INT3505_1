# Buổi 8: API Testing và Quality Assurance

> **Thời lượng:** 30 phút · **Đối tượng:** SV năm 3 (đã biết REST, đã dùng Postman cơ bản)
> **Mục tiêu:** Hiểu phân loại test, viết test tự động trong Postman, chạy Newman & Load Test

---

## Slide 1: Mở đầu – Tại sao phải Test API?

### Nội dung

**Tình huống thực tế:**
- Dev viết xong API, test bằng tay trên Postman → "Chạy được rồi!" → Deploy lên server
- 2 tuần sau, sửa 1 bug nhỏ → API cũ bị hỏng mà không ai biết (**regression bug**)
- Khách hàng phát hiện trước team dev → Mất uy tín

**API Testing giải quyết gì?**
- Phát hiện lỗi **tự động**, không cần click tay lại từng endpoint
- Đảm bảo mỗi lần sửa code, **toàn bộ API cũ vẫn hoạt động đúng**
- Đo được API **nhanh hay chậm**, chịu được bao nhiêu người dùng

> **🎯 Nguyên tắc Shift-Left:** Tìm bug càng sớm (ở tầng API) → sửa càng rẻ. Đừng chờ tester/khách hàng phát hiện.

### Speaker Notes
```
Mở đầu bằng câu hỏi: "Ai trong lớp đã từng sửa 1 hàm xong mà API khác bị lỗi theo?"
Giải thích ngắn: regression bug là lỗi phát sinh khi sửa code chỗ khác.
Nhấn mạnh: Test thủ công (bấm Send trong Postman) không scale khi có 50-100 API.
```

---

## Slide 2: Các loại Test – Tháp Testing (Testing Pyramid)

### Nội dung

```
        ╱ ╲           E2E / UI Test
       ╱   ╲          (Selenium, Cypress)
      ╱     ╲         → Chậm, đắt, dễ vỡ
     ╱───────╲
    ╱         ╲        Integration Test
   ╱           ╲       (Postman, Newman, httpx)
  ╱             ╲      → Kiểm tra liên kết giữa các thành phần
 ╱───────────────╲
╱                 ╲    Unit Test
╱                   ╲   (pytest, unittest)
─────────────────────   → Nhanh nhất, nhiều nhất, rẻ nhất
```

| Loại test | Kiểm tra cái gì? | Công cụ | Tốc độ |
|-----------|-------------------|---------|--------|
| **Unit Test** | 1 hàm / 1 module riêng lẻ | pytest | ⚡ Cực nhanh (ms) |
| **Integration Test** | API endpoint qua HTTP thật | Postman, Newman | 🏃 Nhanh (s) |
| **Performance Test** | Chịu tải, thời gian phản hồi | Locust, k6, JMeter | 🐢 Chậm (phút) |

### Speaker Notes
```
Giải thích tháp: càng lên cao → càng chậm, tốn kém, nhưng bao phủ nhiều hơn.
Quy tắc: 70% Unit → 20% Integration → 10% E2E.
Hôm nay tập trung vào 2 tầng dưới: Unit Test (pytest) và Integration Test (Postman/Newman).
Performance Test sẽ demo bằng Locust ở cuối buổi.
```

---

## Slide 3: Unit Test với pytest – Kiểm tra từng khối nhỏ nhất

### Nội dung

**Unit Test là gì?**
- Test **một hàm duy nhất**, không cần chạy server, không cần database
- FastAPI hỗ trợ `TestClient` cho phép gọi API mà không cần khởi động uvicorn

**Ví dụ: Test endpoint GET /products**

```python
# test_unit.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)   # Không cần bật server!

def test_get_all_products():
    response = client.get("/products")
    assert response.status_code == 200         # Phải trả về 200
    assert isinstance(response.json(), list)   # Body phải là mảng
    assert len(response.json()) >= 1           # Phải có ít nhất 1 item

def test_product_not_found():
    response = client.get("/products/9999")
    assert response.status_code == 404         # ID không tồn tại → 404
```

**Chạy:**
```bash
py -m pytest test_unit.py -v
```

**Kết quả mong đợi:**
```
test_unit.py::test_get_all_products      PASSED
test_unit.py::test_create_product        PASSED
test_unit.py::test_get_single_product    PASSED
test_unit.py::test_update_product        PASSED
test_unit.py::test_product_not_found     PASSED

=============== 5 passed in 0.34s ===============
```

### Speaker Notes
```
Demo trực tiếp: Mở terminal, chạy pytest, cho lớp xem 5 dòng PASSED xanh lá.
Nhấn mạnh: Chưa cần bật server uvicorn! TestClient chạy "nội bộ" trong bộ nhớ.
Giải thích assert: Nếu điều kiện sai → test FAILED → dev biết ngay hàm nào hỏng.
Trả lời câu hỏi có thể gặp: "Khác gì chạy trên Postman?" → Unit test không qua mạng, 
nhanh hơn 100x, chạy tự động trong CI/CD.
```

---

## Slide 4: Integration Test với Postman – Viết Test Script

### Nội dung

**Integration Test khác Unit Test thế nào?**
- Gọi API **qua HTTP thật** (localhost:8000), server phải đang chạy
- Kiểm tra: routing, middleware, validation, serialization **làm việc cùng nhau**

**Bí mật ít người biết:** Postman không chỉ để bấm Send!

Tab **"Scripts > Post-response"** (hoặc tab Tests ở bản cũ) cho phép viết JavaScript để tự kiểm tra kết quả:

```javascript
// Kiểm tra mã trạng thái
pm.test("Status code là 200", function () {
    pm.response.to.have.status(200);
});

// Kiểm tra thời gian phản hồi
pm.test("Phản hồi dưới 500ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(500);
});

// Kiểm tra nội dung body
pm.test("Body trả về là mảng", function () {
    const data = pm.response.json();
    pm.expect(data).to.be.an('array');
    pm.expect(data.length).to.be.greaterThan(0);
});

// Kiểm tra cấu trúc dữ liệu
pm.test("Sản phẩm có đủ trường bắt buộc", function () {
    const first = pm.response.json()[0];
    pm.expect(first).to.have.property('id');
    pm.expect(first).to.have.property('name');
    pm.expect(first).to.have.property('price');
});
```

### Speaker Notes
```
[DEMO TRÊN POSTMAN]
1. Mở Postman → Import file postman_collection.json (có sẵn trong thư mục)
2. Mở request "1. GET /products" → Click tab "Scripts > Post-response"
3. Chỉ cho lớp thấy 4 đoạn pm.test() đang nằm sẵn
4. Bấm Send → Xem tab "Test Results" hiện 4/4 PASS màu xanh
5. Hỏi lớp: "Nếu server trả về 500 thì sao?" → Sửa URL sai thử → Thấy FAIL đỏ

Giải thích pm object:
- pm.response = object chứa status code, body, headers, time
- pm.test() = khai báo 1 test case
- pm.expect() = so sánh giá trị (giống assert trong Python)
```

---

## Slide 5: Postman nâng cao – Collection Variables & Chuỗi Request

### Nội dung

**Vấn đề:** Test POST tạo sản phẩm → Server sinh ra ID mới → Làm sao GET/PUT/DELETE đúng ID đó?

**Giải pháp:** Dùng **Collection Variables** để truyền dữ liệu giữa các request

```javascript
// Trong Tests của POST /products:
const data = pm.response.json();
pm.collectionVariables.set("created_id", data.id);  // Lưu ID vừa tạo
```

```javascript
// Trong URL của GET /products/:id:
{{base_url}}/products/{{created_id}}    // Tự động điền ID
```

**Luồng chạy khi Run Collection:**

```
POST /products          → Tạo sản phẩm, lưu ID=4
  ↓ (created_id = 4)
GET /products/4         → Kiểm tra tồn tại
  ↓
PUT /products/4         → Cập nhật giá
  ↓
DELETE /products/4      → Xoá
  ↓
GET /products/4         → Kiểm tra 404 (đã xoá thật)
```

### Speaker Notes
```
[DEMO TRÊN POSTMAN]
1. Mở Collection, click vào tab "Variables" → Chỉ cho lớp thấy biến base_url và created_id
2. Giải thích: {{created_id}} là placeholder, Postman tự thay bằng giá trị thực
3. Click nút "Run" (biểu tượng ▶ trên Collection) → "Run Collection"
4. Nhấn "Run Buổi 8 - Product API Test Suite"
5. Chờ 2-3 giây → Kết quả hiện lên: 5 requests, ~12 test cases, tất cả PASS ✅
6. Nhấn mạnh: "Mình vừa test 5 API trong 2 giây, không cần click tay từng cái"
```

---

## Slide 6: Newman – Đưa Postman Test vào Terminal & CI/CD

### Nội dung

**Newman là gì?**
- Phiên bản **dòng lệnh (CLI)** của Postman Collection Runner
- Cùng file `.json`, cùng test script – nhưng **chạy trong Terminal**, không cần mở app Postman
- Ứng dụng quan trọng: Tích hợp vào **CI/CD pipeline** (GitHub Actions, GitLab CI)

**Cài đặt & Chạy:**
```bash
# Cài Newman (1 lần)
npm install -g newman

# Chạy toàn bộ test suite
newman run postman_collection.json
```

**Kết quả hiển thị trên Terminal:**

```
→ 1. GET /products - Lấy danh sách
  GET http://localhost:8000/products [200 OK, 523B, 45ms]
  ✓ Status code = 200
  ✓ Response time < 500ms
  ✓ Body trả về là mảng
  ✓ Mỗi sản phẩm có id, name, price

→ 2. POST /products - Tạo mới
  POST http://localhost:8000/products [201 Created, 312B, 12ms]
  ✓ Status code = 201 Created
  ✓ Trả về đúng tên sản phẩm
  ✓ Server tự sinh ID

   ...

┌─────────────────────────┬──────────┬──────────┐
│                         │ executed │   failed │
├─────────────────────────┼──────────┼──────────┤
│           iterations    │        1 │        0 │
│           requests      │        5 │        0 │
│         test-scripts    │        5 │        0 │
│           assertions    │       12 │        0 │
├─────────────────────────┼──────────┼──────────┤
│   total run duration    │    382ms │          │
└─────────────────────────┴──────────┴──────────┘
```

**Tích hợp CI/CD (ví dụ GitHub Actions):**
```yaml
# .github/workflows/api-test.yml
jobs:
  test:
    steps:
      - run: npm install -g newman
      - run: newman run postman_collection.json
      # Nếu bất kỳ test nào FAIL → pipeline dừng → không cho deploy
```

### Speaker Notes
```
[DEMO TRÊN TERMINAL]
1. Mở terminal thứ 2 (server FastAPI vẫn đang chạy ở terminal 1)
2. cd vào thư mục 8_api_testing
3. Chạy: newman run postman_collection.json
4. Cho lớp xem bảng tổng kết: 5 requests, 12 assertions, 0 failed
5. Giải thích: Đây chính là thứ chạy tự động mỗi khi push code lên Git
6. Hỏi lớp: "Nếu dev sửa code làm hỏng API DELETE, ai phát hiện?" → Newman phát hiện
   trong pipeline → Chặn deploy → Dev biết ngay và sửa trước khi lên production
```

---

## Slide 7: Performance Testing – Đo sức chịu đựng của API

### Nội dung

**Câu hỏi:** API chạy đúng với 1 người, nhưng nếu 1000 người gọi cùng lúc thì sao?

**3 chỉ số quan trọng cần đo:**

| Chỉ số | Ý nghĩa | Ngưỡng chấp nhận |
|--------|---------|-------------------|
| **Response Time** | Thời gian từ lúc gửi request → nhận response | < 200ms (tốt), < 1s (chấp nhận), > 3s (tệ) |
| **Throughput (RPS)** | Số request server xử lý được trong 1 giây | Càng cao càng tốt |
| **Error Rate** | Tỉ lệ request bị lỗi (4xx, 5xx) | < 1% (tốt), > 5% (nghiêm trọng) |

**Các mức kiểm tra hiệu năng:**

- **Load Test:** Đẩy N user vào hệ thống → Xem có chịu nổi không (VD: 100 user đồng thời)
- **Stress Test:** Tăng user liên tục cho đến khi server sập → Tìm giới hạn chịu đựng
- **Spike Test:** Đột ngột tung 1000 user trong 1 giây → Mô phỏng flash sale, sự kiện

### Speaker Notes
```
Giải thích bằng ví dụ đời thường:
- Response Time = Bạn gọi món, bao lâu bồi bàn mang ra?
- Throughput = Nhà hàng phục vụ được bao nhiêu bàn/giờ?
- Error Rate = Bao nhiêu bàn bị quên món hoặc mang sai?

Liên hệ thực tế: Shopee flash sale 12/12, nếu không load test trước → sập server → 
mất hàng triệu đơn. Đó là lý do cần Performance Testing.
```

---

## Slide 8: Demo Locust – Load Testing bằng Python

### Nội dung

**Locust là gì?**
- Công cụ load testing mã nguồn mở, viết kịch bản bằng **Python**
- Có giao diện web trực quan, biểu đồ **thời gian thực**

**Cách viết kịch bản test:**
```python
# locustfile.py
from locust import HttpUser, task, between

class ProductAPIUser(HttpUser):
    wait_time = between(0.5, 1.5)  # Nghỉ 0.5-1.5s giữa mỗi request

    @task(5)                         # Trọng số 5 → chạy nhiều nhất
    def browse_products(self):
        self.client.get("/products")

    @task(3)
    def view_detail(self):
        self.client.get("/products/1")

    @task(1)                         # Trọng số 1 → chạy ít nhất
    def create_product(self):
        self.client.post("/products", json={
            "name": "Test Product",
            "price": 100000
        })
```

**Giải thích:**
- Mỗi `@task(n)` = 1 hành vi của user. Số `n` = trọng số (tỷ lệ thực hiện)
- `wait_time = between(0.5, 1.5)` mô phỏng user thật: không ai click liên tục không nghỉ
- Khi chạy 50 user → Locust tạo 50 "con" đồng thời, mỗi con lặp lại các task

**Chạy:**
```bash
locust                            # Mở web UI tại http://localhost:8089
locust --headless -u 50 -r 5     # Chạy không UI: 50 user, tăng 5 user/s
```

### Speaker Notes
```
[DEMO TRỰC TIẾP]
1. Đảm bảo server FastAPI đang chạy ở terminal 1
2. Terminal 2: chạy "locust"
3. Mở trình duyệt: http://localhost:8089
4. Điền: Number of users = 50, Spawn rate = 5, Host = http://localhost:8000
5. Nhấn "Start Swarming"
6. Chỉ cho lớp xem:
   - Tab "Charts": Biểu đồ Response Time đang chạy real-time
   - Đường Response Time sẽ nhảy vọt khi user tăng
   - Cột Error Rate nhảy đỏ vì endpoint /products/heavy/report cố tình trả 500
7. Giải thích: "Endpoint heavy/report mình cố tình code cho nó lag 2 giây và 
   30% trả lỗi 500 để biểu đồ cho thấy rõ ràng API nào có vấn đề"
8. Dừng test → Xem tab Statistics: Bảng tổng kết Response Time trung bình, 
   percentile 95%, Error Rate cho từng endpoint
```

---

## Slide 9: So sánh tổng hợp công cụ

### Nội dung

| Tiêu chí | pytest | Postman | Newman | Locust |
|----------|--------|---------|--------|--------|
| **Loại test** | Unit | Integration | Integration | Performance |
| **Cần server chạy?** | ❌ Không | ✅ Có | ✅ Có | ✅ Có |
| **Giao diện** | Terminal | GUI đẹp | Terminal | Web UI |
| **Ngôn ngữ script** | Python | JavaScript | JavaScript | Python |
| **CI/CD** | ✅ | ❌ | ✅ | ✅ |
| **Khi nào dùng?** | Dev code xong, test nhanh | Thiết kế & debug API | Automation pipeline | Trước khi go-live |

**Quy trình lý tưởng trong dự án thực tế:**

```
Dev viết code → pytest (Unit) → Push Git →
  ↓ (CI tự chạy)
Newman (Integration) → PASS → Deploy staging →
  ↓
Locust (Performance) → PASS → Deploy production ✅
```

### Speaker Notes
```
Tổng kết lại: Mỗi công cụ có vai trò riêng, không thay thế nhau.
- pytest chạy không cần server → phù hợp kiểm tra logic nhanh
- Postman/Newman chạy qua HTTP thật → bắt lỗi routing, middleware, validation
- Locust bắt lỗi chỉ xuất hiện khi có nhiều user đồng thời → memory leak, deadlock, timeout

Nhấn mạnh: Trong dự án nhóm cuối kỳ, ít nhất nên có Unit Test + Newman trong pipeline.
```

---

## Slide 10: Tổng kết & Câu hỏi

### Nội dung

**Kiến thức đã học:**
- ✅ Phân biệt 3 loại test: Unit → Integration → Performance
- ✅ Viết test script trong Postman với `pm.test()` và `pm.expect()`
- ✅ Chuỗi request với Collection Variables
- ✅ Chạy test tự động bằng Newman trên Terminal / CI/CD
- ✅ Đo hiệu năng API bằng Locust (Response Time, Error Rate, Throughput)

**Bài tập gợi ý:**
1. Thêm test case kiểm tra "tạo sản phẩm với giá âm → phải trả 422"
2. Thêm 1 test case trong Newman kiểm tra response header `Content-Type: application/json`
3. Chạy Locust với 200 user, quan sát server FastAPI bắt đầu chậm ở mức nào

### Speaker Notes
```
Slide cuối: Hỏi lớp có thắc mắc gì không.
Nếu không ai hỏi, tự đặt câu: "Theo các bạn, nếu chỉ được chọn 1 loại test duy nhất 
cho dự án, nên chọn loại nào?" → Đáp án gợi ý: Integration Test (Newman) vì nó cân bằng 
giữa tốc độ và độ bao phủ.
```

---

## Phụ lục: Câu hỏi thường gặp khi demo

**Q1: Unit Test với Integration Test khác nhau chỗ nào? Cả hai đều gọi API mà?**
> Unit Test dùng TestClient chạy **trong bộ nhớ**, không qua mạng. Integration Test gọi **qua HTTP thật** (localhost:8000). Unit Test nhanh gấp 100 lần nhưng không bắt được lỗi mạng, CORS, middleware.

**Q2: Sao không dùng Postman luôn cho tất cả, cần chi Newman?**
> Postman là GUI, cần người ngồi bấm hoặc mở app. Newman chạy bằng dòng lệnh → tích hợp được vào CI/CD (GitHub Actions). Mỗi lần push code, Newman tự chạy không cần con người.

**Q3: Locust viết bằng Python, vậy có thể test API viết bằng Java/Go không?**
> Được! Locust chỉ gửi HTTP request đến URL. Nó không quan tâm backend viết bằng gì. Bạn có thể dùng Locust test bất kỳ API nào có URL.

**Q4: Error Rate 30% trong demo có phải lỗi thật không?**
> Không. Trong file `main.py`, endpoint `/products/heavy/report` được **cố tình** code `random.random() < 0.3` để 30% request trả 500. Mục đích là để biểu đồ Locust cho thấy rõ Error Rate nhảy đỏ. Trong thực tế, Error Rate > 1% là đã nghiêm trọng.

**Q5: `pm.collectionVariables.set()` khác `pm.environment.set()` thế nào?**
> `collectionVariables` gắn với Collection (file JSON), di chuyển được. `environment` gắn với môi trường (dev/staging/prod), thường chứa URL và API key. Trong demo mình dùng collectionVariables cho đơn giản.
