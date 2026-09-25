# Kiểm tra hệ thống và dữ liệu demo — 25/09/2026

## Báo cáo cuối ngày demo

- Mã báo cáo: `BC8EB4C0948AEF64D7`.
- Đơn sản xuất: `#26`; người nộp: tài khoản tổ trưởng `3`.
- Kết quả demo: 8 sản phẩm đạt, 1 sản phẩm hỏng.
- Trạng thái: **Chờ xem** để quản lý xưởng có thể thử nút **Xác nhận**.
- Ghi chú trong báo cáo nêu rõ đây là dữ liệu demo.
- Ảnh giao diện: [demo_daily_report.png](demo_daily_report.png).

## Kiểm tra tài khoản và quyền

Đăng nhập thành công bằng cả 9 tài khoản đang hoạt động: 1 admin, 1 quản lý xưởng, 2 tổ trưởng và 5 nhân viên. Kiểm tra 9 trang chính cho mỗi tài khoản (81 lượt) và trang AI cho cả 9 tài khoản (9 lượt): tất cả trả về đúng quyền truy cập.

Các thao tác nộp và lọc báo cáo, phạm vi xem báo cáo của tổ trưởng, đăng xuất, tạo/sửa/xóa sản phẩm, đơn hàng, kho, phân công, tiến độ, lỗi sản xuất, quản lý tài khoản và thống kê được kiểm tra qua giao diện hoặc bộ kiểm thử tự động. Bộ kiểm thử dùng CSDL riêng; kết quả cuối cùng: **87/87 bài đạt**.

## Kiểm tra Gemini với API thật

- Quản lý xưởng: tóm tắt tiến độ, phân tích lỗi, gợi ý ưu tiên đơn đều trả về `status=ok` và `provider=gemini`.
- Tổ trưởng: tóm tắt tiến độ trả về `status=ok` và `provider=gemini`; chức năng ưu tiên đơn bị chặn đúng quyền.
- Nhân viên không thể dùng API AI.
- Ba chế độ đều được chạy trên giao diện trình duyệt và hiện **ĐÃ XÁC MINH**. Ảnh minh họa: [demo_ai_assistant.png](demo_ai_assistant.png).

API Key không được ghi vào tài liệu hoặc ảnh. Tệp `.env` được Git bỏ qua.
