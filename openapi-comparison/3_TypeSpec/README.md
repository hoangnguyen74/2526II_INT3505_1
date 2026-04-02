# TypeSpec — Library Management API

## Giới thiệu

**TypeSpec** (Microsoft) là ngôn ngữ mô tả API với cú pháp giống TypeScript. Đặc điểm: **viết code ngắn gọn, compile ra OpenAPI** → dùng được toàn bộ ecosystem OpenAPI.

## Cấu trúc file

```
typespec/
├── main.tsp            ← File spec chính (TypeScript-like)
├── tspconfig.yaml      ← Config output
├── README.md           ← File này
└── generate.ps1        ← Script compile
```

## Đặc điểm cú pháp

```typespec
// Model giống TypeScript interface
model Book {
  id: int32;
  title: string;
  author: string;
  genre?: string;        // Optional với ?
  available?: boolean = true;  // Default value
}

// Operation giống function
@get op list(@query genre?: string): Book[];
@post op create(@body book: BookCreate): { @statusCode: 201; @body: Book; };
```

> 💡 So với OpenAPI YAML (~150 dòng), TypeSpec chỉ cần ~90 dòng cho cùng API!

## Cài đặt & Chạy

### 1. Cài TypeSpec compiler

```bash
npm install -g @typespec/compiler
```

### 2. Cài dependencies cho project

```bash
cd typespec/
npm init -y
npm install @typespec/http @typespec/rest @typespec/openapi3
```

### 3. Compile ra OpenAPI

```bash
tsp compile main.tsp
# → Output: generated/openapi.yaml
```

### 4. Xem kết quả bằng Swagger UI

```bash
# Dùng OpenAPI output với Swagger UI
npx @redocly/cli preview-docs generated/openapi.yaml
# Mở http://localhost:8080
```

## Sinh code/test

### Workflow: TypeSpec → OpenAPI → Code

```
main.tsp
  ↓ tsp compile
openapi.yaml
  ↓ openapi-generator
Python client / Server / Tests
```

### Compile + Generate code

```bash
# 1. Compile TypeSpec → OpenAPI
tsp compile main.tsp

# 2. Sinh Python client từ OpenAPI output
npx @openapitools/openapi-generator-cli generate \
  -i generated/openapi.yaml \
  -g python \
  -o generated/python-client

# 3. Render docs
npx @redocly/cli build-docs generated/openapi.yaml -o generated/docs.html
```

## So sánh độ dài code

| Format | Số dòng (cùng API) |
|--------|-------------------|
| OpenAPI YAML | ~150 dòng |
| RAML | ~160 dòng |
| API Blueprint | ~170 dòng |
| **TypeSpec** | **~90 dòng** ✅ |

> 💡 TypeSpec ngắn nhất vì: type inference, decorator syntax, không cần lặp schema.
