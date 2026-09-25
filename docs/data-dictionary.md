# Từ Điển Dữ Liệu (Data Dictionary)

Chi tiết 11 bảng cốt lõi của URD và 3 bảng bổ sung cho quy trình nhóm đã thống nhất.

---

### 1. Bảng `TaiKhoan`
| Tên Cột | Kiểu Dữ Liệu | Khóa | Bắt buộc | Mô Tả |
|---|---|---|---|---|
| `MaTaiKhoan` | VARCHAR(32) | PK | YES | Mã tài khoản chữ-số, ví dụ DTC12345 |
| `HoTen` | VARCHAR(100) | | YES | Họ và tên người dùng |
| `Email` | VARCHAR(100) | UNIQUE | YES | Địa chỉ email đăng nhập |
| `MatKhau` | VARCHAR(255) | | YES | Mật khẩu đã được băm an toàn |
| `VaiTro` | VARCHAR(50) | | YES | Để trống khi chờ duyệt; sau duyệt: 'Admin', 'QuanLyXuong', 'ToTruong', 'NhanVien' |
| `TrangThai` | VARCHAR(20) | | NO | 'Pending', 'Active', 'Suspended', 'Frozen', 'Deleted' |

### 2. Bảng `SanPham`
| Tên Cột | Kiểu Dữ Liệu | Khóa | Bắt buộc | Mô Tả |
|---|---|---|---|---|
| `MaSanPham` | VARCHAR(32) | PK | YES | Mã sản phẩm (ví dụ: SP01) |
| `TenSanPham` | VARCHAR(150) | | YES | Tên đầy đủ của sản phẩm |
| `DonViTinh` | VARCHAR(20) | | YES | Đơn vị tính (Cái, Bộ, Khung, ...) |
| `MoTa` | TEXT | | NO | Mô tả quy cách kỹ thuật |
| `TrangThai` | VARCHAR(20) | | NO | 'Active', 'Discontinued' |
| `NgayTao` | DATETIME | | NO | Thời điểm tạo bản ghi |

### 3. Bảng `NguyenLieu`
| Tên Cột | Kiểu Dữ Liệu | Khóa | Bắt buộc | Mô Tả |
|---|---|---|---|---|
| `MaNguyenLieu` | VARCHAR(32) | PK | YES | Mã nguyên liệu (ví dụ: NL01) |
| `TenNguyenLieu`| VARCHAR(150) | | YES | Tên nguyên vật liệu |
| `DonViTinh` | VARCHAR(20) | | YES | Đơn vị tính (kg, mét, lít, cái, que, ...) |
| `SoLuongTon` | DECIMAL(12,2)| | YES | Số lượng tồn kho thực tế (>= 0) |
| `TrangThai` | VARCHAR(20) | | NO | 'Active', 'Out_of_stock' |
| `NgayCapNhat` | DATETIME | | NO | Thời điểm cập nhật số lượng tồn |

### 4. Bảng `DinhMucNguyenLieu` (BOM)
| Tên Cột | Kiểu Dữ Liệu | Khóa | Bắt buộc | Mô Tả |
|---|---|---|---|---|
| `MaSanPham` | VARCHAR(32) | PK, FK | YES | Khóa ngoại tham chiếu SanPham |
| `MaNguyenLieu`| VARCHAR(32) | PK, FK | YES | Khóa ngoại tham chiếu NguyenLieu |
| `SoLuongDinhMuc`| DECIMAL(18,4)| | YES | Lượng vật tư cần cho 1 SP (> 0) |
| `DonViTinh` | VARCHAR(20) | | YES | Đơn vị tính vật tư |
| `GhiChu` | VARCHAR(255) | | NO | Ghi chú quy cách |
| `NgayCapNhat` | DATETIME | | NO | Thời điểm cập nhật định mức |

### 5. Bảng `DonSanXuat`
| Tên Cột | Kiểu Dữ Liệu | Khóa | Bắt buộc | Mô Tả |
|---|---|---|---|---|
| `MaDon` | VARCHAR(32) | PK | YES | Mã đơn sản xuất chữ-số |
| `MaSanPham` | VARCHAR(32) | FK | YES | Mã sản phẩm cần sản xuất |
| `SoLuongYeuCau`| INT | | YES | Số lượng sản phẩm cần giao (> 0) |
| `HanGiao` | DATE | | YES | Ngày hạn chót bàn giao sản phẩm |
| `TrangThai` | VARCHAR(30) | | NO | 'Mới tạo', 'Đang thực hiện', 'Hoàn thành', 'Hủy' |
| `NgayTao` | DATETIME | | NO | Thời điểm tạo đơn |
| `GhiChu` | TEXT | | NO | Yêu cầu kỹ thuật từ khách hàng |

### 6. Bảng `CongDoan`
| Tên Cột | Kiểu Dữ Liệu | Khóa | Bắt buộc | Mô Tả |
|---|---|---|---|---|
| `MaCongDoan` | VARCHAR(32) | PK | YES | Mã công đoạn chữ-số |
| `MaSanPham` | VARCHAR(32) | FK | YES | Sản phẩm sở hữu quy trình công đoạn |
| `TenCongDoan` | VARCHAR(100) | | YES | Tên bước công đoạn (Cắt, Hàn, Mài, ...) |
| `ThuTu` | INT | | YES | Thứ tự tuần tự thực hiện (1, 2, 3...) |
| `MoTa` | TEXT | | NO | Hướng dẫn thao tác kỹ thuật |
| `TrangThai` | VARCHAR(20) | | NO | 'Active', 'Inactive' |
| `NgayCapNhat` | DATETIME | | NO | Thời điểm cập nhật |

### 7. Bảng `KeHoachSanXuat`
| Tên Cột | Kiểu Dữ Liệu | Khóa | Bắt buộc | Mô Tả |
|---|---|---|---|---|
| `MaKeHoach` | VARCHAR(32) | PK | YES | Mã kế hoạch chữ-số |
| `MaDon` | VARCHAR(32) | FK | YES | Khóa ngoại tham chiếu DonSanXuat |
| `NgayBatDau` | DATE | | YES | Ngày bắt đầu triển khai sản xuất |
| `NgayKetThuc` | DATE | | YES | Ngày dự kiến hoàn thành kế hoạch |

### 8. Bảng `PhanCong`
| Tên Cột | Kiểu Dữ Liệu | Khóa | Bắt buộc | Mô Tả |
|---|---|---|---|---|
| `MaPhanCong` | VARCHAR(32) | PK | YES | Mã phân công chữ-số |
| `MaCongDoan` | VARCHAR(32) | FK | YES | Khóa ngoại tham chiếu CongDoan |
| `MaTaiKhoan` | VARCHAR(32) | FK | YES | Khóa ngoại tham chiếu TaiKhoan (Nhân viên) |
| `MaDon` | VARCHAR(32) | FK | NO | Khóa ngoại tham chiếu DonSanXuat (Đề xuất) |
| `NgayPhanCong`| DATE | | YES | Ngày giao nhiệm vụ ca làm |

### 9. Bảng `TienDoCongDoan`
| Tên Cột | Kiểu Dữ Liệu | Khóa | Bắt buộc | Mô Tả |
|---|---|---|---|---|
| `MaTienDo` | VARCHAR(32) | PK | YES | Mã tiến độ chữ-số |
| `MaCongDoan` | VARCHAR(32) | FK | YES | Khóa ngoại tham chiếu CongDoan |
| `MaDon` | VARCHAR(32) | FK | NO | Khóa ngoại tham chiếu DonSanXuat (Đề xuất) |
| `SoLuongHoanThanh`| INT | | YES | Số lượng sản phẩm đạt tại công đoạn (>= 0) |
| `TrangThai` | VARCHAR(30) | | NO | 'Chưa thực hiện', 'Đang thực hiện', 'Hoàn thành' |
| `NgayCapNhat` | DATETIME | | NO | Thời điểm ghi nhận sản lượng |

### 10. Bảng `SuDungNguyenLieu`
| Tên Cột | Kiểu Dữ Liệu | Khóa | Bắt buộc | Mô Tả |
|---|---|---|---|---|
| `MaSuDung` | VARCHAR(32) | PK | YES | Mã ghi nhận tiêu hao chữ-số |
| `MaDon` | VARCHAR(32) | FK | YES | Đơn hàng sử dụng vật tư |
| `MaCongDoan` | VARCHAR(32) | FK | YES | Công đoạn sử dụng vật tư |
| `MaNguyenLieu`| VARCHAR(32) | FK | YES | Loại nguyên liệu sử dụng |
| `SoLuongSuDung`| DECIMAL(12,2)| | YES | Khối lượng/số lượng thực tế đã xuất (> 0) |
| `NgayGhiNhan` | DATETIME | | NO | Thời điểm xuất dùng |

### 11. Bảng `LoiSanXuat`
| Tên Cột | Kiểu Dữ Liệu | Khóa | Bắt buộc | Mô Tả |
|---|---|---|---|---|
| `MaLoi` | VARCHAR(32) | PK | YES | Mã lỗi chữ-số |
| `MaDon` | VARCHAR(32) | FK | YES | Đơn hàng phát sinh lỗi |
| `MaCongDoan` | VARCHAR(32) | FK | YES | Công đoạn phát sinh lỗi |
| `MoTaLoi` | TEXT | | YES | Mô tả chi tiết hiện tượng lỗi |
| `SoLuongHong` | INT | | YES | Số lượng sản phẩm bị hỏng/phế phẩm (>= 0) |
| `NgayGhiNhan` | DATETIME | | NO | Thời điểm phát hiện lỗi |

### 12. Bảng `BaoCaoNgay` (bổ sung)
| Tên Cột | Kiểu Dữ Liệu | Khóa | Bắt buộc | Mô Tả |
|---|---|---|---|---|
| `MaBaoCao` | VARCHAR(32) | PK | YES | Mã báo cáo chữ-số |
| `MaDon` | VARCHAR(32) | FK | YES | Đơn được báo cáo |
| `MaTaiKhoan` | VARCHAR(32) | FK | YES | Tổ trưởng lập báo cáo |
| `NgayBaoCao` | DATE | UNIQUE tổ hợp | YES | Mỗi tổ trưởng lập một báo cáo cho mỗi đơn trong ngày |
| `SoLuongHoanThanh` | INT | | YES | Sản lượng trong báo cáo |
| `SoLuongHong` | INT | | YES | Số lượng hỏng trong báo cáo |
| `GhiChu` | TEXT | | NO | Diễn giải |
| `TrangThai` | VARCHAR(20) | | YES | Pending hoặc Approved |
| `NgayTao` | DATETIME | | NO | Thời điểm lập |
| `NgayDuyet` | DATETIME | | NO | Thời điểm duyệt |
| `MaNguoiDuyet` | VARCHAR(32) | FK | NO | Quản lý xưởng duyệt |

### 13. Bảng `BaoVatTu` (bổ sung)
| Tên Cột | Kiểu Dữ Liệu | Khóa | Bắt buộc | Mô Tả |
|---|---|---|---|---|
| `MaBaoVatTu` | VARCHAR(32) | PK | YES | Mã phiếu báo vật tư chữ-số |
| `MaDon` | VARCHAR(32) | FK | YES | Đơn liên quan |
| `MaCongDoan` | VARCHAR(32) | FK | YES | Công đoạn dùng vật tư |
| `MaNguyenLieu` | VARCHAR(32) | FK | YES | Vật tư thuộc BOM của sản phẩm |
| `MaTaiKhoan` | VARCHAR(32) | FK | YES | Người báo cáo |
| `SoLuongBaoCao` | DECIMAL(18,4) | | YES | Lượng sử dụng được báo cáo |
| `TrangThai` | VARCHAR(20) | | YES | Pending hoặc Approved |
| `NgayBaoCao` | DATETIME | | NO | Thời điểm gửi báo cáo |
| `NgayDuyet` | DATETIME | | NO | Thời điểm duyệt |
| `MaNguoiDuyet` | VARCHAR(32) | FK | NO | Quản lý xưởng duyệt |
| `MaSuDung` | VARCHAR(32) | FK | NO | Bản ghi xuất dùng được tạo khi duyệt |

### 14. Bảng `ThanhVienTo` (bổ sung)
| Tên Cột | Kiểu Dữ Liệu | Khóa | Bắt buộc | Mô Tả |
|---|---|---|---|---|
| `MaToTruong` | VARCHAR(32) | PK, FK | YES | Tổ trưởng phụ trách |
| `MaNhanVien` | VARCHAR(32) | PK, FK, UNIQUE | YES | Nhân viên chỉ thuộc một tổ tại một thời điểm |
