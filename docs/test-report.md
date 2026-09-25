# Báo cáo kiểm thử hiện tại

Ngày thực hiện: 2026-09-25. Môi trường: Windows, Python trong `venv`, SQLite độc lập cho từng ca kiểm thử.

```text
python -m pytest tests -q
.................................................................        [100%]
65 passed in 6.97s
```

Các trường hợp quan trọng đã được kiểm tra: đăng ký mã `DTC12345` và chờ Admin duyệt; Admin không vào trang sản xuất/kho; tài khoản đã xóa không được kích hoạt lại; tạo, sửa và xóa sản phẩm/BOM; khai báo công đoạn, đơn và kế hoạch; phân công đúng tổ và đúng đơn; cập nhật tiến độ tuần tự; báo vật tư không trừ kho trước khi Quản lý xưởng duyệt và không trừ lặp; kiểm tra CSRF; thống kê và ba tác vụ trợ lý AI; phản hồi AI bịa mã/số liệu bị đánh dấu cần kiểm tra.

Kiểm tra đọc trên CSDL SQLite đang dùng sau khi chuyển mã: 8 tài khoản vẫn tồn tại; các trang Quản lý xưởng `/dashboard`, `/products`, `/orders`, `/production`, `/inventory`, `/teams`, `/daily-reports`, `/statistics`, `/ai/assistant` trả HTTP 200. Bảng thành viên tổ trên dữ liệu đang dùng hiện trống; Quản lý xưởng cần thêm thành viên qua trang **Thành Viên Tổ** trước khi Tổ trưởng giao việc cho nhân viên mới.

Giới hạn kiểm thử: dịch vụ MySQL80 đang chạy nhưng dự án chưa có cấu hình kết nối hoặc CSDL thử nghiệm, nên đường kết nối và migration MySQL cũ chưa được chạy tích hợp. Bộ kiểm thử 65 ca không chứng minh ứng dụng đáp ứng toàn bộ URD; các thay đổi so với URD được ghi tại `docs/urd-change-decisions.md`.
