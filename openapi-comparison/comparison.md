# So sánh các chuẩn tài liệu hóa API

## Tổng quan 4 formats

| Tiêu chí | OpenAPI (Swagger) | API Blueprint | RAML | TypeSpec |
|----------|------------------|---------------|------|----------|
| **Format** | YAML / JSON | Markdown | YAML | TypeScript-like DSL |
| **Phiên bản mới nhất** | 3.1.0 | 1A9 | 1.0 | 0.x (evolving) |
| **Tổ chức phát triển** | OpenAPI Initiative (Linux Foundation) | Apiary (Oracle) | MuleSoft (Salesforce) | Microsoft |
| **Năm ra đời** | 2011 (Swagger) | 2013 | 2013 | 2021 |
| **Approach** | YAML/JSON schema | Markdown viết tay | YAML + types | Code-first, compile ra OpenAPI |
| **Learning curve** | ⭐⭐ Trung bình | ⭐ Dễ nhất | ⭐⭐ Trung bình | ⭐⭐⭐ Khó nhất |
| **Ecosystem** | ⭐⭐⭐ Rất lớn | ⭐ Nhỏ | ⭐⭐ Trung bình | ⭐⭐ Đang phát triển |
| **Code generation** | ✅ Rất tốt (openapi-generator) | ⚠️ Hạn chế | ✅ Tốt (raml-generator) | ✅ Compile ra OpenAPI → dùng tools OpenAPI |
| **Mock server** | ✅ Prism, Stoplight | ✅ Drakov | ✅ Osprey | ⚠️ Qua OpenAPI output |
| **Render docs** | Swagger UI, ReDoc | Aglio, Snowboard | raml2html, API Console | Qua OpenAPI → Swagger UI |

## Chi tiết từng format

### 1. OpenAPI (Swagger)

**Ưu điểm:**
- Chuẩn phổ biến nhất — industry standard
- Ecosystem khổng lồ: Swagger UI, ReDoc, openapi-generator, Prism...
- Được hỗ trợ bởi hầu hết frameworks (FastAPI, Spring, NestJS...)
- JSON Schema compatible (v3.1)

**Nhược điểm:**
- File YAML có thể rất dài, verbose
- Khó đọc khi API phức tạp (hàng nghìn dòng)

**Phù hợp:** Mọi dự án, đặc biệt khi cần ecosystem tools phong phú.

---

### 2. API Blueprint

**Ưu điểm:**
- Cú pháp Markdown — rất dễ đọc, dễ viết
- Tự nhiên như viết tài liệu thông thường
- Dễ học nhất trong 4 formats

**Nhược điểm:**
- Ecosystem nhỏ, ít tools hỗ trợ
- Không còn được phát triển mạnh (Apiary bị Oracle mua)
- Code generation hạn chế

**Phù hợp:** Dự án nhỏ, prototype, hoặc khi team thích viết Markdown.

---

### 3. RAML (RESTful API Modeling Language)

**Ưu điểm:**
- YAML-based, dễ đọc hơn OpenAPI
- Hỗ trợ type inheritance, traits, resource types → tái sử dụng tốt
- MuleSoft Anypoint Platform tích hợp sẵn

**Nhược điểm:**
- Ecosystem nhỏ hơn OpenAPI
- Ít được sử dụng ngoài MuleSoft ecosystem
- Một số tools đã deprecated

**Phù hợp:** Dự án dùng MuleSoft, hoặc khi cần type system mạnh trong spec.

---

### 4. TypeSpec (Microsoft)

**Ưu điểm:**
- Cú pháp giống TypeScript — quen thuộc với web devs
- Compile ra OpenAPI → dùng được toàn bộ ecosystem OpenAPI
- Type system mạnh, hỗ trợ decorator, namespace
- DRY — code ngắn gọn, ít lặp

**Nhược điểm:**
- Rất mới, đang phát triển (breaking changes)
- Community nhỏ, ít tài liệu
- Cần bước compile thêm

**Phù hợp:** Dự án Microsoft/Azure, team thích TypeScript, API lớn cần type safety.

---

## Tổng kết: Chọn format nào?

```
Dự án mới, cần ecosystem → OpenAPI ✅
Prototype nhanh, thích Markdown → API Blueprint
Dùng MuleSoft → RAML
API lớn, team biết TypeScript → TypeSpec
```

> 💡 **Thực tế:** ~80% dự án chọn OpenAPI vì ecosystem quá mạnh. TypeSpec đang rất tiềm năng vì compile ra OpenAPI.
