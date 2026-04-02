# Mục đích và Yêu cầu

Trong bối cảnh phát triển API, việc sử dụng các chuẩn mô tả tài liệu (API Specification Formats) là cực kỳ quan trọng để đảm bảo tính nhất quán, dễ dàng áp dụng thiết kế theo hướng Design-First và có khả năng sinh mã (Code generation).

## Yêu cầu
1. Đánh giá và so sánh chuyên sâu 5 chuẩn tài liệu hóa API: **OpenAPI**, **API Blueprint**, **RAML**, **TypeSpec**, và **TypeAPI**.
2. Với mỗi chuẩn format, xây dựng một bản demo nhỏ dựa trên bài toán **Quản lý Thư viện (Library Management)** với yêu cầu mô phỏng đúng cấu trúc.
3. Hướng dẫn sử dụng kịch bản sinh code/test từ mỗi định dạng tài liệu cụ thể đó (như tạo Server FastAPI, kiểm thử Mock test hay HTML Docs).

## Phương pháp So sánh
Các tài liệu sẽ được so sánh trên các khía cạnh:
- **Cú pháp và Định dạng (Syntax):** Mức độ dễ đọc, dễ tiếp cận (YAML, JSON, Markdown, hay DSL).
- **Hệ sinh thái (Ecosystem):** Tools có sẵn, khả năng tương thích và thư viện cộng đồng.
- **Khả năng Sinh Code (Code Generation) & Mocking:** Khả năng tự động hóa để sinh ra các bộ khung Code Server (Server Stub), hay Test Client (Mock Test).
- **Learning Curve:** Khó khăn hay thuận lợi vào thời điểm bắt đầu.

Chi tiết đối trọng và bảng so sánh trực quan được biểu diễn trong tài liệu `SLIDE_CONTENT.md`.
