# RAML — Library Management API

## Giới thiệu

**RAML** (RESTful API Modeling Language) là ngôn ngữ mô tả API dựa trên YAML, phát triển bởi MuleSoft. Đặc điểm nổi bật: **traits** (tái sử dụng behavior) và **type inheritance**.

## Cấu trúc file

```
raml/
├── library-api.raml    ← File spec chính
├── README.md           ← File này
└── generate.ps1        ← Script sinh docs
```

## Đặc điểm riêng của RAML

```yaml
# Traits — tái sử dụng xử lý lỗi
traits:
  hasNotFound:
    responses:
      404:
        body: ...

# Áp dụng trait
/books/{id}:
  get:
    is: [hasNotFound]    # ← Dùng trait, ko cần viết lại 404
```

> 💡 RAML có `traits` (tái sử dụng behavior) và `resourceTypes` (khuôn mẫu endpoint) — OpenAPI không có tính năng tương đương trực tiếp.

## Cài đặt & Chạy

### 1. Render HTML docs

```bash
# Cài raml2html
npm install -g raml2html

# Render
raml2html library-api.raml > docs.html
# Mở docs.html trong trình duyệt
```

### 2. Validate

```bash
npm install -g raml-cop
raml-cop library-api.raml
```

### 3. Mock server

```bash
npm install -g osprey-mock-service
osprey-mock-service -f library-api.raml --port 4001
# → http://localhost:4001
```

## Sinh code/test

### RAML → OpenAPI (chuyển đổi)

```bash
# Cài oas-raml-converter
npm install -g oas-raml-converter

# Chuyển RAML → OpenAPI 3.0
oas-raml-converter --from RAML --to OAS30 library-api.raml > openapi-output.yaml
# → Giờ dùng được openapi-generator
```

### Sinh code từ RAML

```bash
# Cài raml-client-generator
npm install -g raml-client-generator

# Sinh JavaScript client
raml-client-generator library-api.raml -o generated/js-client -l javascript
```

### Render docs đẹp hơn với API Console

```bash
# MuleSoft API Console (Web Component)
npm install api-console
```

> ⚠️ **Lưu ý:** Nhiều RAML tools đã cũ/deprecated. Thực tế thường convert sang OpenAPI rồi dùng tools OpenAPI.
