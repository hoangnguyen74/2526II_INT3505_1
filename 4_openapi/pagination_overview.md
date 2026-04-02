# Tổng quan về Pagination (Phân trang)

Trong thiết kế RESTful API, khi tập dữ liệu lớn, ta không thể trả về toàn bộ dữ liệu trong một request. Pagination (Phân trang) là kỹ thuật chia nhỏ dữ liệu thành các trang để tăng hiệu năng và trải nghiệm người dùng.

Dưới đây là so sánh 3 phương pháp phổ biến:

## 1. Offset / Limit Pagination
**Cấu trúc URL:** `/books?offset=0&limit=10` (Lấy từ vị trí 0, độ dài 10)

- **Ưu điểm:**
  - Rất dễ hiểu và dễ code (SQL: `OFFSET x LIMIT y`).
  - Hỗ trợ tốt cho các trường hợp không cần thứ tự tuyệt đối.
- **Nhược điểm:**
  - **Chậm với dữ liệu lớn:** Khi offset quá lớn (vd: offset=1,000,000), cơ sở dữ liệu vẫn phải quét qua 1 triệu dòng đầu tiên trước khi lấy ra dòng cần thiết, gây chậm truy vấn.
  - **Lệch dữ liệu (Data drift):** Nếu có dữ liệu mới được chèn vào hoặc bị xoá đi trong khoảng thời gian người dùng đang chuyển trang, kết quả ở trang tiếp theo có thể bị lặp lại hoặc bù sót dữ liệu.

## 2. Page-based Pagination
**Cấu trúc URL:** `/books?page=1&size=10`

- **Đặc điểm:** 
  - Bản chất tương tự Offset / Limit (ở phần logic tính toán trong code: `offset = (page - 1) * size`).
  - Thường trả về thêm metadata: `total_pages`, `total_items`, `current_page`.
- **Ưu điểm:**
  - Thân thiện với UI/UX cho End-User (ví dụ như ở dưới các trang thông thường hiển thị danh sách trang [1] [2] [3] ... [Trang cuối]).
  - Rất trực quan để người dùng có thể "nhảy" thẳng đến một trang cụ thể.
- **Nhược điểm:**
  - Vẫn mang yếu điểm về "hiệu suất OFFSET chậm" và "lệch dữ liệu" tương tự Offset / Limit Pagination.
  
## 3. Cursor-based Pagination
**Cấu trúc URL:** `/reviews?cursor=1699111032&limit=10` (Sử dụng một con trỏ - thường là ID hoặc Timestamp)

- **Cơ chế hoạt động:** Thay vì báo Database "Bỏ qua X bản ghi", nó báo "Tìm các bản ghi có ID hoặc Timestamp NHỎ HƠN (hoặc LỚN HƠN) giá trị trỏ (cursor) này, với số lượng tối đa là Limit". (SQL: `WHERE id > cursor LIMIT y`).
- **Ưu điểm:**
  - **Hiệu năng cực nhanh:** Không bị "offset fatigue". Query tận dụng hoàn toàn sức mạnh của Index trong Database. Kể cả ở hàng thứ tỉ, query vẫn cực kỳ nhanh.
  - **Tránh lệch dữ liệu:** Vì cursor dựa trên vị trí tuyệt đối của bản ghi cuối trước đó, nên việc người khác thêm hay xóa dữ liệu mới không làm mảng dữ liệu bị lặp khi chuyển trang. Phù hợp tuyệt vời cho Feed như Facebook, Twitter, Tiktok (Endless scroll).
- **Nhược điểm:**
  - Bắt buộc phải sắp xếp dựa trên một/nhiều cột sequential/unique (ví dụ ID tự tăng hoặc Timestamp).
  - Không thể "nhảy" trang (Không thể từ trang 1 nhảy sang trang 50 một cách tự nhiên nếu chưa có cursor của cuối trang 49).

## Kết luận
- **Trang Admin UI, Website Danh bạ:** Thường ưu tiên **Page-based**.
- **Social Feed, Chat logs, Mobile Endless Scroll:** Bắt buộc dùng **Cursor-based**.
- **Offset/limit:** Dùng cho resource phụ, logic API thuần túy khi không cần Metadata trang phức tạp.
