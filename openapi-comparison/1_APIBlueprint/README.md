# API Blueprint — Library Management API

## Giới thiệu

**API Blueprint** sử dụng cú pháp Markdown để mô tả API. Dễ đọc nhất trong các formats — giống viết tài liệu thông thường.

## Cấu trúc file

```
api-blueprint/
├── library-api.apib    ← File spec chính (Markdown-based)
├── README.md           ← File này
└── generate.ps1        ← Script sinh docs/mock
```

## Đặc điểm cú pháp

```markdown
# Tên endpoint [/path]
### Mô tả hành động [GET]
+ Parameters       ← Khai báo param
+ Request           ← Request body
+ Response 200     ← Response
```

> 💡 Cú pháp rất tự nhiên, gần như viết tài liệu Markdown bình thường.

## Cài đặt & Chạy

### 1. Render HTML docs bằng Aglio (deprecated nhưng vẫn dùng được)

```bash
npm install -g aglio
aglio -i library-api.apib -o docs.html
# Mở docs.html trong trình duyệt
```

### 2. Render bằng Snowboard (thay thế Aglio, mới hơn)

```bash
npm install -g snowboard
snowboard html -o docs.html library-api.apib
```

### 3. Mock server bằng Drakov

```bash
npm install -g drakov
drakov -f library-api.apib --port 4000
# → http://localhost:4000 — mock server từ spec
```

### 4. Xem trên Apiary (Online)

```
# Paste nội dung .apib vào:
https://app.apiary.io/
```

## Sinh code/test

### Tạo mock server

```bash
drakov -f library-api.apib --port 4000

# Test
curl http://localhost:4000/books
# → Trả về example data từ file .apib
```

### API Blueprint → OpenAPI (chuyển đổi)

```bash
# Cài apib2swagger
npm install -g apib2swagger

# Chuyển từ API Blueprint → OpenAPI
apib2swagger -i library-api.apib -o openapi-output.yaml
# → Giờ dùng được tools OpenAPI (Swagger UI, codegen...)
```

> ⚠️ **Lưu ý:** Ecosystem API Blueprint nhỏ hơn OpenAPI. Cách phổ biến là chuyển sang OpenAPI rồi dùng tools OpenAPI.
