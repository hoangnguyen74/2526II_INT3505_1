# So sánh các chuẩn tài liệu hóa API

## 1. Tổng quan 5 formats

| Tiêu chí | OpenAPI | API Blueprint | RAML | TypeSpec | TypeAPI |
|----------|---------|---------------|------|----------|---------|
| **Format dữ liệu** | YAML / JSON | Markdown | YAML | TypeScript DSL | JSON |
| **Đơn vị phát triển**| Linux Foundation | Apiary (Oracle) | MuleSoft (Salesforce) | Microsoft | Fusio (TypeSchema) |
| **Cách tiếp cận** | Schema-First / Docs | Docs-driven bằng văn bản | API Modeling phân tầng | Code-first (compile to OpenAPI) | JSON Type-safe API Builder |
| **Learning Curve** | ⭐⭐ Trung bình | ⭐ Dễ nhất | ⭐⭐ Trung bình | ⭐⭐⭐ Khó | ⭐⭐ Trung bình |
| **Ecosystem** | Rất Lớn (Industry Standard) | Nhỏ | Trung bình | Vừa / Đang phát triển | Cơ bản / Mới mẻ |
| **Code Generation** | ✅ Cực Tốt (Server/Tests/Client)| ⚠️ Hạn chế (thường sinh HTML)| ✅ Tốt (raml2html, osprey)| ✅ Compile ra OpenAPI rồi dùng tool OpenAPI | ✅ Tốt (TypeAPI generator) |

## 2. Chi tiết từng format

### 2.1. OpenAPI (Swagger)
- **Ưu điểm:** Là "Vua" của chuẩn API. Ecosystem khổng lồ, tooling cực kỳ đa dạng. Hỗ trợ JSON Schema mạnh mẽ và có tích hợp với gần như mọi web framework.
- **Nhược điểm:** File YAML phình to rất nhanh với hệ thống lớn, khiến việc đọc tay trở nên khó khăn.
- **Trường hợp sử dụng:** Rất an toàn để ứng dụng vào hầu hết các dự án thương mại vừa và lớn. Dễ dàng sinh code backend (FastAPI), frontend Client, kiểm thử (Tests), Mock mượt mà qua công cụ `openapi-generator`.

### 2.2. API Blueprint
- **Ưu điểm:** Định dạng Markdown khiến nó trở nên rất thân thiện với non-coder (như BA, Designer). Việc viết API như thể đang viết một bài blog.
- **Nhược điểm:** Cú pháp tuy dễ nhưng dễ bị vỡ format nếu không viết cẩn thận. Ít tool tự động hoá sinh server code, ecosystem bị bỏ ngỏ.
- **Trường hợp sử dụng:** Prototype nhanh, dự án làm API nội bộ cần tài liệu tường minh.

### 2.3. RAML (RESTful API Modeling Language)
- **Ưu điểm:** Khả năng tái sử dụng xuất sắc qua việc kế thừa resource types và traits (DRY model). Phù hợp tuyệt vời với hệ sinh thái Enterprise của MuleSoft.
- **Nhược điểm:** Lượng tooling bên ngoài hệ sinh thái MuleSoft ngày càng hạn chế. Nhìn chung độ phổ biến kém xa OpenAPI.
- **Trường hợp sử dụng:** Dự án Salesforce, API lớn có nhiều logic chung cần tách và kế thừa.

### 2.4. TypeSpec (Microsoft)
- **Ưu điểm:** Cú pháp vay mượn từ TypeScript thân quen thuộc với đại đa số lập trình viên hiện tại. Tránh được sự lộn xộn của YAML. Cung cấp quy trình biên dịch (`tsp compile`) xuất trực tiếp ra OpenAPI chuẩn 3.0. Nhờ đó, bạn tiếp cận được ecosystem khổng lồ của OpenAPI.
- **Nhược điểm:** Là chuẩn còn khá mới mẻ nên cộng đồng nhỏ. Buộc phải thêm giai đoạn compile (biên dịch) khi tích hợp CI/CD.
- **Trường hợp sử dụng:** Các Node/TS web developer muốn Code-first cho kiến trúc API lớn, yêu cầu gắt gao về Type Safety.

### 2.5. TypeAPI
- **Ưu điểm:** Mô tả API qua JSON sử dụng chuẩn `TypeSchema`. Nó đặc biệt giúp xây dựng Type-safe REST APIs và tạo ra các SDK Client một cách minh bạch, an toàn hơn JSON Schema thuần của OpenAPI vì bỏ qua các yếu tố lỏng lẻo. 
- **Nhược điểm:** Mới mẻ, khá ngách, phần lớn tài liệu phát triển quanh cộng đồng Fusio/PHP.
- **Trường hợp sử dụng:** Cung cấp giải pháp định nghĩa tĩnh qua metadata JSON, phù hợp cho người không thích phức tạp như GraphQL nhưng vẫn cần phân phối Type-Safe Client hiệu quả.

## 3. Tổng kết
- Cần một chuẩn an toàn, mọi nền tảng đều hỗ trợ, gen code thoải mái: **Chắc chắn là OpenAPI**.
- Team developer chuộng JavaScript/TypeScript, muốn tách rời file mô tả dễ quản lý như code: **TypeSpec**.
- Muốn tài liệu đọc nhẹ nhàng như văn bản truyền thống: **API Blueprint**.
