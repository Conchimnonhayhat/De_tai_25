# Tiêu Chí Chấp Nhận (Acceptance Criteria - AC)

Định dạng chuẩn: Given - When - Then theo từng User Story trọng yếu.

---

### AC-01: Đăng nhập hệ thống (US-01 / FR-01)
- **Scenario 1**: Đăng nhập thành công với thông tin hợp lệ
  - **Given**: Người dùng đã được Admin kích hoạt tài khoản với vai trò `QuanLyXuong`.
  - **When**: Người dùng nhập đúng Email và Mật khẩu rồi nhấn Đăng nhập.
  - **Then**: Hệ thống thiết lập phiên làm việc, chuyển hướng đến trang Dashboard Quản lý và hiển thị đúng tên vai trò.
- **Scenario 2**: Đăng nhập thất bại với sai mật khẩu
  - **When**: Người dùng nhập sai mật khẩu.
  - **Then**: Hệ thống từ chối xác thực, hiển thị thông báo "Email hoặc mật khẩu không chính xác" và không tiết lộ sự tồn tại của email.

### AC-02: Phân quyền vai trò (US-02 / FR-02)
- **Given**: Tài khoản có vai trò `NhanVien`.
- **When**: Cố tình truy cập vào URL quản trị `/admin/users` hoặc API `/api/users`.
- **Then**: Hệ thống trả về mã lỗi 403 Forbidden và ghi nhận nhật ký vi phạm quyền truy cập.

### AC-03: Thiết lập định mức nguyên liệu (US-04 / FR-04)
- **Given**: Đã có sản phẩm SP01 và nguyên liệu NL01 trong hệ thống.
- **When**: Quản lý nhập định mức SoLuongDinhMuc = 2.5 (kg) cho 1 đơn vị SP01.
- **Then**: Hệ thống lưu thành công bản ghi vào bảng `DinhMucNguyenLieu`.
- **When**: Quản lý nhập SoLuongDinhMuc <= 0.
- **Then**: Hệ thống chặn lại và báo lỗi "Định mức nguyên liệu phải lớn hơn 0".

### AC-04: Cập nhật tiến độ công đoạn (US-08 / FR-09)
- **Given**: Đơn sản xuất có SoLuongYeuCau = 100 sản phẩm. Công đoạn 1 đang có SoLuongHoanThanh = 40.
- **When**: Nhân viên cập nhật thêm 30 sản phẩm hoàn thành tại Công đoạn 1.
- **Then**: Hệ thống cập nhật tổng SoLuongHoanThanh = 70, trạng thái chuyển thành `Đang thực hiện`.
- **When**: Nhân viên cố tình cập nhật số lượng hoàn thành công đoạn 2 là 80 (vượt quá 70 của công đoạn 1).
- **Then**: Hệ thống từ chối cập nhật và báo lỗi vi phạm thứ tự công đoạn: "Sản lượng công đoạn sau không được vượt công đoạn trước liền kề".

### AC-05: Ghi nhận lỗi và sản phẩm hỏng (US-09 / FR-10)
- **Given**: Đơn 25 đang tiến hành công đoạn 2.
- **When**: Tổ trưởng ghi nhận lỗi "Gãy chốt nối", SoLuongHong = 5.
- **Then**: Bản ghi được lưu vào bảng `LoiSanXuat`, liên kết chính xác với Mã đơn và Mã công đoạn.

### AC-06: Thống kê tỷ lệ lỗi (US-13 / FR-14)
- **Given**: Tổng sản lượng ghi nhận = 500, tổng số lượng hỏng = 25.
- **When**: Quản lý mở trang thống kê chất lượng.
- **Then**: Hệ thống tính toán và hiển thị Tỷ lệ lỗi = (25 / 500) * 100% = 5.0%.
- **Given**: Hệ thống mới tạo chưa có sản lượng ghi nhận (mẫu số = 0).
- **Then**: Hiển thị nhãn `Chưa có dữ liệu`, không bị lỗi chia cho 0 (ZeroDivisionError).

### AC-07: AI tóm tắt tiến độ đơn sản xuất (US-14 / FR-15 / AC-AI-001)
- **Given**: Đơn 25 yêu cầu 100 sản phẩm, công đoạn cuối ghi nhận hoàn thành 60 sản phẩm, hạn giao 2026-09-30.
- **When**: Quản lý gửi yêu cầu "Tóm tắt tiến độ Đơn 25".
- **Then**: Hệ thống trích xuất snapshot chuẩn xác: `SoLuongYeuCau=100`, `SoLuongHoanThanh=60`, `progress_percent=60%`.
- **And**: AI phản hồi tóm tắt tiến độ đạt 60%, dẫn đúng mã bản ghi nguồn (`DonSanXuat:25`, `TienDoCongDoan:...`). AI không tự suy đoán thông tin ngoài snapshot.

### AC-08: AI phân tích mô tả lỗi (US-15 / FR-16 / AC-AI-002)
- **Given**: Trong tuần có 2 bản ghi lỗi: "Bề mặt trầy xước nhẹ" và "Vết xước kim loại trên vỏ".
- **When**: Tổ trưởng yêu cầu AI phân tích lỗi.
- **Then**: AI nhóm 2 lỗi trên vào nhóm "Lỗi bề mặt / trầy xước", dẫn nguồn 2 mã lỗi và đưa ra giả thuyết nguyên nhân (ví dụ: cần kiểm tra đồ gá, dao cắt) với nhãn rõ ràng là "Giả thuyết cần kiểm tra thực tế", không khẳng định chắc chắn khi chưa có bằng chứng kỹ thuật.

### AC-09: AI gợi ý ưu tiên đơn (US-16 / FR-17 / AC-AI-003)
- **Given**: Đơn A cần 20 kg nhôm, tồn kho còn 15 kg (thiếu 5 kg), hạn giao còn 2 ngày. Đơn B đủ vật tư, hạn giao còn 1 ngày.
- **When**: Quản lý xưởng bấm "Gợi ý ưu tiên đơn sản xuất".
- **Then**: AI gợi ý ưu tiên Đơn B do sắp đến hạn và sẵn sàng vật tư; cảnh báo Đơn A đang thiếu 5 kg nguyên liệu để sản xuất.
- **And**: AI chỉ đề xuất kèm lý do, Quản lý xưởng bấm nút duyệt trên giao diện nếu đồng ý áp dụng.
