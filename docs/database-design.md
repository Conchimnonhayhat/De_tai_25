# Thiết Kế Cơ Sở Dữ Liệu Chi Tiết (Database Design Document)

Hệ thống Quản lý Xưởng Sản xuất Nhỏ (Đề tài 25 theo URD)  
Hệ quản trị CSDL mục tiêu: MySQL 8.0+; SQLite 3 dùng cho chạy cục bộ và kiểm thử tự động.

---

## 1. Chuẩn Hóa Dữ Liệu (Normalization)

Cơ sở dữ liệu được thiết kế đạt **Chuẩn hóa bậc 3 (3NF)**:
- **1NF**: Mọi thuộc tính đều mang giá trị nguyên tử (atomic), không chứa danh sách lặp (ví dụ: nguyên vật liệu trong đơn hàng được tách thành bảng quan hệ `DinhMucNguyenLieu` và `SuDungNguyenLieu` chứ không lưu dạng chuỗi văn bản phân tách bằng dấu phẩy).
- **2NF**: Đạt 1NF và mọi thuộc tính không khóa đều phụ thuộc hàm đầy đủ vào khóa chính (đặc biệt trong các bảng có khóa phức hợp như `DinhMucNguyenLieu(MaSanPham, MaNguyenLieu)`).
- **3NF**: Đạt 2NF và không có thuộc tính không khóa nào phụ thuộc bắc cầu (transitive dependency) vào khóa chính.

---

## 2. Mười một bảng URD và chiến lược khóa (PK / FK)

Theo quyết định cập nhật của nhóm, tất cả trường mã nghiệp vụ `Ma...` và khóa ngoại tương ứng dùng `VARCHAR(32)`; mã có thể gồm chữ và số như `DTC12345`, giữ nguyên số 0 đầu. Đây là khác biệt có chủ ý so với các khóa `int` trong từ điển URD gốc. Các trường số lượng và thứ tự vẫn là kiểu số. `SoLuongDinhMuc` dùng `DECIMAL(18,4)`.

1. **`TaiKhoan`**: Quản lý thông tin đăng nhập và phân quyền. `MaTaiKhoan` (PK). Mật khẩu được băm an toàn 255 ký tự.
2. **`SanPham`**: Danh mục sản phẩm sản xuất. `MaSanPham` (PK dạng mã định danh chuỗi, ví dụ `SP01`).
3. **`NguyenLieu`**: Danh mục nguyên vật liệu tồn kho. `MaNguyenLieu` (PK).
4. **`DinhMucNguyenLieu`**: Định mức vật tư (BOM) cho 1 đơn vị sản phẩm (BR-04). Khóa chính kết hợp `(MaSanPham, MaNguyenLieu)`.
5. **`DonSanXuat`**: Đơn đặt hàng sản xuất từ khách hàng. `MaDon` (PK mã chuỗi). FK `MaSanPham` trỏ tới `SanPham`.
6. **`CongDoan`**: Quy trình công đoạn thuộc sản phẩm. `MaCongDoan` (PK). FK `MaSanPham` trỏ tới `SanPham`.
7. **`KeHoachSanXuat`**: Kế hoạch thực hiện theo thời gian. `MaKeHoach` (PK). FK `MaDon` trỏ tới `DonSanXuat`.
8. **`PhanCong`**: Phân công nhân sự cho công đoạn. `MaPhanCong` (PK). FK `MaCongDoan`, FK `MaTaiKhoan`, và FK `MaDon` (đề xuất bổ sung để phân biệt theo đơn).
9. **`TienDoCongDoan`**: Ghi nhận số lượng hoàn thành và trạng thái. `MaTienDo` (PK). FK `MaCongDoan` và FK `MaDon` (đề xuất bổ sung giải quyết Issue #01).
10. **`SuDungNguyenLieu`**: Theo dõi vật tư xuất dùng thực tế. `MaSuDung` (PK). FK `MaDon`, FK `MaCongDoan`, FK `MaNguyenLieu`.
11. **`LoiSanXuat`**: Ghi nhận lỗi phát sinh và sản phẩm hỏng. `MaLoi` (PK). FK `MaDon`, FK `MaCongDoan`.

Ba bảng bổ sung theo quyết định của nhóm: `BaoCaoNgay` cho kết quả cuối ngày của Tổ trưởng; `BaoVatTu` cho phiếu báo vật tư chờ Quản lý xưởng duyệt và liên kết duy nhất tới bản ghi xuất dùng; `ThanhVienTo` giới hạn nhân viên mà Tổ trưởng được phân công. Chúng không nằm trong 11 bảng URD gốc và phải được ghi rõ trong ma trận truy vết.

---

## 3. Ràng Buộc Nghiệp Vụ Trong CSDL (Constraints)
- `SoLuongYeuCau > 0`, `SoLuongDinhMuc > 0`, `SoLuongSuDung > 0`.
- `SoLuongTon >= 0`, `SoLuongHoanThanh >= 0`, `SoLuongHong >= 0`.
- Ràng buộc tham chiếu toàn vẹn: Khi xóa sản phẩm sẽ xóa cascade các công đoạn và định mức; không được xóa nguyên liệu nếu đã có trong định mức BOM (`ON DELETE RESTRICT`).
- Ràng buộc liên bảng phức tạp (ví dụ: sản lượng công đoạn sau không được vượt công đoạn trước, trừ kho vật tư khi xuất dùng) được đảm bảo trong Database Transactions tại tầng Business Service.

---

## 4. Tối Ưu Hóa Truy Vấn & Chỉ Mục (Indexes)
- Đánh index trên `TrangThai` và `HanGiao` của `DonSanXuat` để phục vụ nhanh truy vấn tóm tắt tiến độ và gợi ý ưu tiên của AI (FR-15, FR-17).
- Đánh composite index trên `TienDoCongDoan(MaDon, MaCongDoan)` để truy xuất tức thời tiến độ đơn hàng.
- Đánh index trên `SuDungNguyenLieu(MaDon)` và `LoiSanXuat(MaDon)`.
