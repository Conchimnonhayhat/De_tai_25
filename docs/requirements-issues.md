# Báo Cáo Các Vấn Đề Và Điểm Chưa Rõ Trong Yêu Cầu (Requirements Issues)

Hệ thống Quản lý Xưởng Sản xuất Nhỏ (Đề tài 25 theo URD)  
Ngày ghi nhận: 2026-09-23

---

## 1. Danh sách Vấn đề Kỹ thuật Cốt lõi (Core Issues)

### Issue #01 (CRITICAL): Thiếu khóa liên kết `MaDon` trong `TienDoCongDoan` và `PhanCong`
- **Mô tả hiện trạng theo URD gốc**:
  - Bảng `CongDoan` thuộc về `SanPham` (`MaSanPham` là FK).
  - Bảng `TienDoCongDoan` chỉ có `MaCongDoan` (FK), không có `MaDon`.
  - Bảng `PhanCong` chỉ có `MaCongDoan` (FK) và `MaTaiKhoan` (FK), không có `MaDon`.
- **Hệ quả nghiệp vụ**:
  - Khi xưởng nhận 2 đơn sản xuất khác nhau (ví dụ Đơn 25 và Đơn 26) cùng sản xuất một Sản phẩm A: Cả 2 đơn đều dùng chung các công đoạn của Sản phẩm A.
  - Do đó, nếu bảng tiến độ chỉ gắn với `MaCongDoan`, hệ thống **không thể xác định** số lượng hoàn thành đang thuộc về Đơn 25 hay Đơn 26! Tương tự, không biết nhân viên được phân công làm cho đơn hàng nào.
- **Đề xuất giải pháp kỹ thuật**:
  - Bổ sung trường `MaDon` (INT, FK trỏ tới `DonSanXuat.MaDon`) vào cả 2 bảng `TienDoCongDoan` và `PhanCong`.
  - Giữ lại thiết kế gốc URD làm cơ sở đối chiếu, và tạo bản mở rộng có bổ sung `MaDon` để hệ thống vận hành thực tế không bị xung đột dữ liệu.

---

### Issue #02 (HIGH): Quan hệ 1 đơn có nhiều kế hoạch sản xuất (`KeHoachSanXuat`)
- **Mô tả hiện trạng theo URD**:
  - URD định nghĩa quan hệ 1 Đơn sản xuất (`DonSanXuat`) có thể liên kết 1-N với `KeHoachSanXuat`.
  - Tuy nhiên, URD không quy định kế hoạch nào đang có hiệu lực thi hành khi một đơn có nhiều kế hoạch điều chỉnh (phiên bản kế hoạch, ngày bắt đầu/kết thúc thay đổi).
- **Đề xuất giải pháp kỹ thuật**:
  - Mặc định chọn kế hoạch có ngày kết thúc xa nhất hoặc kế hoạch được tạo sau cùng (`ORDER BY MaKeHoach DESC LIMIT 1`) làm kế hoạch hiệu lực hiện tại, trừ khi người dùng chỉ định rõ.

---

### Issue #03 (MEDIUM): Công thức tính Năng suất (FR-13)
- **Mô tả hiện trạng theo URD**:
  - FR-13 yêu cầu "Thống kê năng suất", nhưng trong cấu trúc 11 bảng của URD không có bảng chấm công, giờ bắt đầu/kết thúc thực tế của từng nhân viên (`GioCong`).
- **Đề xuất giải pháp kỹ thuật**:
  - Tính toán năng suất dựa trên: **Tổng sản lượng hoàn thành** theo từng công đoạn / nhân viên trong phạm vi thời gian được chọn, tránh tự ý suy diễn công thức "sản phẩm / giờ" chưa có dữ liệu hỗ trợ.

---

### Issue #04 (MEDIUM): Ranh giới phân quyền chi tiết giữa Tổ trưởng và Nhân viên
- **Mô tả hiện trạng theo URD**:
  - URD phân định: Tổ trưởng phân công, theo dõi tiến độ, ghi lỗi, ghi vật tư; Nhân viên cập nhật tiến độ, lỗi, vật tư theo quyền.
- **Đề xuất giải pháp kỹ thuật**:
  - Nhân viên chỉ được xem và cập nhật công đoạn mà chính mình được phân công (`PhanCong.MaTaiKhoan = current_user.id`).
  - Tổ trưởng có quyền xem và cập nhật mọi công đoạn trong xưởng hoặc thuộc tổ quản lý.

---

## 2. Kiểm soát Mở rộng Phạm vi (Scope Creep Prevention)
- Codex tuyệt đối không tự ý thêm các chức năng:
  1. Tự động gửi email/thông báo đặt hàng vật tư tới nhà cung cấp bên ngoài.
  2. Tự động thay đổi lịch sản xuất trong CSDL khi AI phân tích.
  3. Bổ sung các bảng kế toán, thanh toán, quản lý khách hàng ngoài phạm vi 11 bảng URD.
