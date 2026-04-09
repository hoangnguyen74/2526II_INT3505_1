# Tổng quan về Authentication và Authorization API

Trong việc xây dựng API an toàn, **xác thực (Authentication)** và **phân quyền (Authorization)** là hai lớp cửa bảo vệ tối quan trọng. Dưới đây là kiến thức nền tảng trong buổi 6.

## 1. So sánh JWT vs OAuth 2.0

Rất nhiều người bị nhầm lẫn giữa JWT và OAuth 2.0. Thực chất chúng đóng 2 vai trò khác nhau và thường được **sử dụng cùng nhau**.

| Tiêu chí | JWT (JSON Web Token) | OAuth 2.0 |
|----------|----------------------|------------|
| **Bản chất** | Một ĐỊNH DẠNG (format) để đóng gói và vận chuyển dữ liệu an toàn. | Một GIAO THỨC (protocol) / luồng (flow) uỷ quyền truy cập. |
| **Mục đích chính** | Stateless Authentication (Xác thực 1 bên, bỏ qua database). | Delegated Authorization (Cho bên thứ 3 truy cập mà không lộ password). |
| **Ví dụ thực tế** | Chiếc "Thẻ ra vào" của Công ty đúc sẵn Tên & Chức vụ trên thẻ. | Hành động "Đăng nhập bằng Google/Facebook" trên một website khác. |
| **Khả năng uỷ quyền** | Không. Chỉ chứng minh "Tôi là ai". | Rất mạnh. Cho phép App Mới lấy danh bạ từ máy chủ Google mà App đó không bao giờ biết pass của bạn. |

=> **Mối quan hệ:** OAuth 2.0 là quy trình. JWT là kết quả. Sau khi luồng OAuth 2.0 diễn ra thành công, máy chủ cấp phép thường "nhả" ra một chiếc vé (Access Token). Chiếc vé đó 99% được định dạng bằng JWT.

## 2. Giải mã thuật ngữ (Keywords)

### A. Bearer Token
**Khái niệm:** Bearer có nghĩa là "Người mang / Người cầm". Bearer Token là một mã thông báo mở: **Bất cứ ai cầm được nó đều nghiễm nhiên có quyền như người sở hữu**.
**Đặc tính:** Nó giống như tiền mặt (tiền giấy). Ai nhặt được đồng 500k thì người đó ném đi mua đồ được ngay, cửa hàng không cần biết họ là chủ thực tế hay ăn cắp.
=> Đòi hỏi cực kỳ gắt gao rằng Bearer Token luôn phải truyền qua kết nối mã hóa `HTTPS` và cất giấu kỹ ở Client. Thiết kế chuẩn của tiêu đề (Header): 
`Authorization: Bearer <token_string>`

### B. Refresh Token
**Khái niệm:** Vì Bearer Token rất nguy hiểm nếu bị mất, người ta sẽ ép Access Token này có vòng đời cực ngắn (Vd: 30 phút). Để tránh User phải gõ Password lại liên tục, server sẽ cấp thêm 1 đồng xu tên là **Refresh Token** (Có hạn sống cực dài từ 1 tuần - 1 tháng).
**Luồng chạy:**
1. Khi Access Token hết hạn `(401 Unauthorized)`.
2. Trình duyệt ngầm đưa Refresh Token lên gửi cho `/api/refresh`.
3. Server quét Database xem Refresh Token này còn hợp lệ không (có bị ai thu hồi hay Report chặn không). Bất kỳ dấu hiệu khả nghi nào, Refresh Token sẽ bị đốt bỏ. Nếu an toàn, Server xuất xưởng 1 cặp Access Token mới.

### C. Roles (Vai trò)
**Khái niệm:** Phân cấp quyền dựa trên thân phận User trong nội bộ một hệ thống khép kín.
Ví dụ: `admin`, `editor`, `customer`, `guest`. Thường một User thuộc về 1 hoặc 2 role nào đó và có toàn quyền kiểm soát trong ranh giới Role đó.

### D. Scopes (Phạm vi)
**Khái niệm:** Một phần của OAuth 2.0. Phân quyền rất mịn màng theo một "giới hạn cho phép" cực kỳ cụ thể, khi cấp quyền cho CÔNG CỤ THỨ 3 truy cập tài khoản gốc.
Ví dụ: 
- `email:read` (App chỉ được quyền xem hòm thư).
- `drive:write` (App được quyền tải ảnh lên Drive).
- Tránh việc bạn uỷ quyền App xem báo mà nó lại bay vào hòm thư nhắn tin phá phách.
