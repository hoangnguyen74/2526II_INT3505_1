# Security Audit Report

## 1. Mục tiêu Kiểm toán (Audit Constraints)
- Đánh giá khả năng bị lộ lọt khoá Token (Token Leakage).
- Đánh giá khả năng kiểm soát vòng đời của Token chống bị phát lại (Replay Attack).

## 2. Các rủi ro phát hiện trong mã nguồn (Vulnerabilities)

### A. Rủi ro rò rỉ Token (Token Leakage) ở Endpoint `/api/vulnerable/profile`
**Mức độ (Severity):** CRITICAL (Nghiêm trọng).
- Đoạn mã sử dụng `const token = req.query.token` thay vì đọc từ Headers.
- **Tại sao nó nguy hiểm?** Việc phơi bày một Token ra thẳng địa chỉ URL (VD: `http://localhost/api?token=eyJ...`) sẽ khiến Token này lập tức bị:
  1. Ghi cứng vào lịch sử duyệt web (Browser History). Người thân lén mở máy là lấy được nick.
  2. Nằm phơi bày trong các công cụ Logging của các đường truyền trung gian (ISP, Vercel logs, Cloudflare).
  3. Bị tuồn lén qua mã tĩnh `Referer` Header khi người dùng click vào link thứ 3.

### B. Rủi ro Tấn công Lặp Lại (Replay Attack)
**Mức độ (Severity):** CRITICAL (Nghiêm trọng).
- Đoạn mã đã giải mã Token bằng hàm Verify nhưng nhắm mắt làm ngơ qua việc hết hạn (sử dụng params `{ ignoreExpiration: true }`). Đôi khi lập trình viên tắt Cờ này để "tạm thời Fix lỗi" cho App chạy lúc Deploy gấp nhưng quên gỡ ra.
- **Tại sao nó nguy hiểm?** Đây là mảnh đất hoàn hảo cho Replay Attack. Kẻ gian dù chỉ lấy trộm được lượng Token sống 5s (ví dụ lấy cáp mạng ở quán Cà phê WiFi), hắn ta có thể chép lại chữ ký này và phát đi rập khuôn các request hệt như vậy (Replayed Request) tới server vô thời hạn để đánh cắp hồ sơ, chuyển tiền mà Server cứ ngỡ là "khách quen thăng hạng".

## 3. Kiến nghị Giải pháp Đặc trị (Mitigation / Best Practices)

Bản code tại cổng bảo mật (`/secure/profile`) đã khép chặt 2 điểm yếu trên:
1. **Khóa tử URL truyền Token:** Thay vào đó, lập trình viên sử dụng khối kiểm tra bắt buộc thông qua Header `Authorization: Bearer <chiếc_token_được_giấu_kín>`. Payload này được mã hoá cùng TLS (HTTPS) ở đường truyền Tầng Socket, nên hoàn toàn vô hình với bất kỳ tay chơi trung gian nào. 
2. **Luật Expiration khắt khe (30s):** Hàm `jwt.verify(token, JWT_SECRET, ...)` được giữ nguyên lý tính mặc định, rà rất chặt tham số Ngày phát hành (iat) và Cột mốc hết hạn (exp). Bất kỳ một tay Hacker nào mò mẫm đưa Token trễ qua dù 1 mili-giây, Verify sẽ khạc ra lỗi 403 Forbidden chặn cửa tức khắc. Replay Attack phá sản!
