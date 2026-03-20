# OpenAPI — Library Management API

## Giới thiệu

**OpenAPI** (trước gọi là Swagger) là chuẩn tài liệu hóa API phổ biến nhất. File spec viết bằng YAML hoặc JSON.

## Cấu trúc file

```
openapi/
├── library-api.yaml    ← File spec chính
├── README.md           ← File này
└── generate.ps1        ← Script sinh code
```

## Cài đặt & Chạy

### 1. Xem tài liệu bằng Swagger Editor (Online)

```bash
# Mở trình duyệt → paste nội dung YAML
https://editor.swagger.io/
```

### 2. Swagger UI local (Docker)

```bash
docker run -p 8080:8080 -e SWAGGER_JSON=/spec/library-api.yaml \
  -v $(pwd):/spec swaggerapi/swagger-ui
# Mở http://localhost:8080
```

### 3. Swagger UI bằng FastAPI (không cần Docker)

```bash
pip install fastapi uvicorn
# FastAPI tự sinh Swagger UI từ code tại /docs
```

### 4. Validate spec

```bash
# Cài swagger-cli
npm install -g @apidevtools/swagger-cli

# Validate
swagger-cli validate library-api.yaml
```

## Sinh code tự động

### Sinh Python client

```bash
# Cài openapi-generator
npm install -g @openapitools/openapi-generator-cli

# Sinh Python client SDK
openapi-generator-cli generate \
  -i library-api.yaml \
  -g python \
  -o generated/python-client

# Sinh Python server (FastAPI)
openapi-generator-cli generate \
  -i library-api.yaml \
  -g python-fastapi \
  -o generated/python-server
```

### Sinh test cases (Postman collection)

```bash
# Import vào Postman
# Postman → Import → File → Chọn library-api.yaml
# → Tự tạo collection + request body + test sẵn
```

### Mock server (không cần code backend)

```bash
# Cài Prism
npm install -g @stoplight/prism-cli

# Chạy mock server
prism mock library-api.yaml
# → http://localhost:4010 — server giả trả data mẫu
```
