# TypeAPI

TypeAPI là chuẩn thiết kế API bằng định dạng JSON thuần (dựa trên TypeSchema). Định dạng này loại bỏ các yếu tố dườm rà của OpenAPI, giúp thiết kế API nhanh gọn và đặc biệt tối ưu cho việc sinh Client SDKs (Type-Safe).

## 1. Cài đặt SDKGen (Công cụ chính của TypeAPI)
TypeAPI sử dụng [SDKGen](https://sdkgen.app/) để sinh code.

- **Yêu cầu:** Máy bạn cần cài đặt **PHP**.
- Thay vì `openapi-generator`, TypeAPI sử dụng `sdkgen`:
```bash
# Tải về bộ sdkgen
wget https://github.com/apioo/sdkgen-cli/releases/latest/download/sdkgen.phar
```

## 2. Cách sinh code
Chạy file `generate.ps1` hoặc gõ thủ công:

```bash
# Sinh code Python Client Test
php sdkgen.phar generate -i library-api.json -d python -o generated/python-client

# Sinh TypeAPI Document HTML
php sdkgen.phar generate -i library-api.json -d client -o generated/docs
```

*(Lưu ý: TypeAPI phù hợp mạnh nhất để sinh Code SDK và build trên Fusio App. Để sinh Python FastAPI server, quy trình phổ biến thường là viết Converter ra OpenAPI rồi dùng openapi-generator.)*
