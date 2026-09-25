# Danh Sách Ca Sử Dụng (Use Cases - UC001 đến UC013)

Bảng ánh xạ chuẩn hóa theo tài liệu URD `Detai25.1.docx`.

---

| Mã UC | Tên Ca Sử Dụng | Tác Nhân Chính | Truy Vết FR | Mô Tả Tóm Tắt |
|---|---|---|---|---|
| **UC001** | Đăng nhập / Đăng xuất hệ thống | Tất cả tác nhân | FR-01 | Xác thực danh tính người dùng và cấp phiên làm việc. |
| **UC002** | Quản lý tài khoản & phân quyền | Quản trị viên (Admin) | FR-02 | Tạo tài khoản, kích hoạt/vô hiệu hóa, gán 1 trong 3 vai trò: Quản lý xưởng, Tổ trưởng, Nhân viên. |
| **UC003** | Quản lý danh mục sản phẩm | Quản lý xưởng | FR-03 | Xem, tạo mới, chỉnh sửa thông tin sản phẩm và trạng thái sản xuất. |
| **UC004** | Quản lý định mức nguyên liệu (BOM) | Quản lý xưởng | FR-04 | Thiết lập danh mục nguyên liệu và số lượng định mức trên 1 đơn vị sản phẩm. |
| **UC005** | Quản lý đơn & kế hoạch sản xuất | Quản lý xưởng | FR-05, FR-06 | Tiếp nhận đơn, đặt hạn giao, lập kế hoạch ngày bắt đầu/kết thúc gắn với đơn. |
| **UC006** | Quản lý công đoạn & phân công | Quản lý xưởng, Tổ trưởng | FR-07, FR-08 | Định nghĩa các bước công đoạn và phân bổ nhân sự thực hiện theo ca. |
| **UC007** | Cập nhật tiến độ công đoạn | Tổ trưởng, Nhân viên | FR-09 | Nhập sản lượng hoàn thành của công đoạn và chuyển trạng thái (Đang làm, Hoàn thành). |
| **UC008** | Ghi nhận lỗi & sản phẩm hỏng | Tổ trưởng, Nhân viên | FR-10 | Báo cáo chi tiết lỗi phát sinh kèm số lượng sản phẩm hỏng theo từng công đoạn/đơn. |
| **UC009** | Ghi nhận sử dụng nguyên liệu | Tổ trưởng, Nhân viên | FR-11 | Ghi nhận lượng nguyên liệu xuất dùng thực tế cho đơn hàng. |
| **UC010** | Xem báo cáo & thống kê xưởng | Quản lý xưởng, Tổ trưởng | FR-12, FR-13, FR-14 | Xem biểu đồ tiến độ, năng suất và tỷ lệ lỗi sản xuất. |
| **UC011** | Yêu cầu AI tóm tắt tiến độ đơn | Quản lý xưởng, Tổ trưởng, Hệ thống AI | FR-15 | Gửi yêu cầu tóm tắt đơn; AI phân tích snapshot và diễn giải tình hình tiến độ. |
| **UC012** | Yêu cầu AI phân tích mô tả lỗi | Quản lý xưởng, Tổ trưởng, Hệ thống AI | FR-16 | AI gom nhóm các lỗi tương đồng, tổng hợp tần suất và đề xuất giả thuyết nguyên nhân. |
| **UC013** | Yêu cầu AI gợi ý ưu tiên đơn | Quản lý xưởng, Hệ thống AI | FR-17 | AI phân tích hạn giao, tiến độ và tồn kho nguyên liệu để xếp hạng thứ tự ưu tiên đề xuất. |
