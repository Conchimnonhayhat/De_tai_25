-- =============================================================================
-- DU LIEU KHOI TAO HE THONG (SEED DATA)
-- =============================================================================

-- 1. TaiKhoan (Mat khau mac dinh: 123456)
INSERT INTO TaiKhoan (MaTaiKhoan, HoTen, Email, MatKhau, VaiTro, TrangThai) VALUES
(1, 'Quản Trị Viên', 'admin@workshop.edu.vn', 'scrypt:32768:8:1$nT5Z9706KaxPpWOE$109e03896417bf3f7f77badaea13ab51dd534206c997a1771341a293f2961c67a735b1f8c3b5ace9e48def2b167b0eb642b76df8b1eced0a49bbe9a8a1142a12', 'Admin', 'Active'),
(2, 'Nguyễn Văn Quản Lý', 'manager@workshop.edu.vn', 'scrypt:32768:8:1$nT5Z9706KaxPpWOE$109e03896417bf3f7f77badaea13ab51dd534206c997a1771341a293f2961c67a735b1f8c3b5ace9e48def2b167b0eb642b76df8b1eced0a49bbe9a8a1142a12', 'QuanLyXuong', 'Active'),
(3, 'Trần Văn Tổ Trưởng', 'leader@workshop.edu.vn', 'scrypt:32768:8:1$nT5Z9706KaxPpWOE$109e03896417bf3f7f77badaea13ab51dd534206c997a1771341a293f2961c67a735b1f8c3b5ace9e48def2b167b0eb642b76df8b1eced0a49bbe9a8a1142a12', 'ToTruong', 'Active'),
(4, 'Lê Văn Công Nhân', 'worker@workshop.edu.vn', 'scrypt:32768:8:1$nT5Z9706KaxPpWOE$109e03896417bf3f7f77badaea13ab51dd534206c997a1771341a293f2961c67a735b1f8c3b5ace9e48def2b167b0eb642b76df8b1eced0a49bbe9a8a1142a12', 'NhanVien', 'Active'),
('TTDEMO02', 'To truong Demo 2', 'demo.leader2@workshop.edu.vn', 'scrypt:32768:8:1$nT5Z9706KaxPpWOE$109e03896417bf3f7f77badaea13ab51dd534206c997a1771341a293f2961c67a735b1f8c3b5ace9e48def2b167b0eb642b76df8b1eced0a49bbe9a8a1142a12', 'ToTruong', 'Active'),
('NVDEMO11', 'Nhan vien Demo 1A', 'demo.worker1a@workshop.edu.vn', 'scrypt:32768:8:1$nT5Z9706KaxPpWOE$109e03896417bf3f7f77badaea13ab51dd534206c997a1771341a293f2961c67a735b1f8c3b5ace9e48def2b167b0eb642b76df8b1eced0a49bbe9a8a1142a12', 'NhanVien', 'Active'),
('NVDEMO12', 'Nhan vien Demo 1B', 'demo.worker1b@workshop.edu.vn', 'scrypt:32768:8:1$nT5Z9706KaxPpWOE$109e03896417bf3f7f77badaea13ab51dd534206c997a1771341a293f2961c67a735b1f8c3b5ace9e48def2b167b0eb642b76df8b1eced0a49bbe9a8a1142a12', 'NhanVien', 'Active'),
('NVDEMO21', 'Nhan vien Demo 2A', 'demo.worker2a@workshop.edu.vn', 'scrypt:32768:8:1$nT5Z9706KaxPpWOE$109e03896417bf3f7f77badaea13ab51dd534206c997a1771341a293f2961c67a735b1f8c3b5ace9e48def2b167b0eb642b76df8b1eced0a49bbe9a8a1142a12', 'NhanVien', 'Active'),
('NVDEMO22', 'Nhan vien Demo 2B', 'demo.worker2b@workshop.edu.vn', 'scrypt:32768:8:1$nT5Z9706KaxPpWOE$109e03896417bf3f7f77badaea13ab51dd534206c997a1771341a293f2961c67a735b1f8c3b5ace9e48def2b167b0eb642b76df8b1eced0a49bbe9a8a1142a12', 'NhanVien', 'Active');

INSERT INTO ThanhVienTo (MaToTruong, MaNhanVien) VALUES (3, 4);
INSERT INTO ThanhVienTo (MaToTruong, MaNhanVien) VALUES
(3, 'NVDEMO11'), (3, 'NVDEMO12'),
('TTDEMO02', 'NVDEMO21'), ('TTDEMO02', 'NVDEMO22');

-- 2. SanPham
INSERT INTO SanPham (MaSanPham, TenSanPham, DonViTinh, MoTa, TrangThai) VALUES
('SP01', 'Bàn cắt cơ khí CNC mini', 'Cái', 'Bàn cắt kim loại gia công cơ khí kích thước 1200x800mm', 'Active'),
('SP02', 'Khung thép chịu lực 500kg', 'Khung', 'Khung thép chữ I sơn tĩnh điện chịu tải trọng công nghiệp', 'Active');

-- 3. NguyenLieu
INSERT INTO NguyenLieu (MaNguyenLieu, TenNguyenLieu, DonViTinh, SoLuongTon, TrangThai) VALUES
('NL01', 'Thép tấm chịu lực 5mm', 'kg', 2500.00, 'Active'),
('NL02', 'Bu lông ốc vít M8 inox', 'cái', 5000.00, 'Active'),
('NL03', 'Sơn tĩnh điện chống rỉ', 'lít', 120.00, 'Active'),
('NL04', 'Que hàn kết cấu chịu nhiệt', 'que', 800.00, 'Active');

-- 4. DinhMucNguyenLieu (BOM cho 1 đơn vị SP)
INSERT INTO DinhMucNguyenLieu (MaSanPham, MaNguyenLieu, SoLuongDinhMuc, DonViTinh, GhiChu) VALUES
('SP01', 'NL01', 15.000, 'kg', '15kg thép tấm / 1 bàn cắt'),
('SP01', 'NL02', 20.000, 'cái', '20 bu lông M8 / 1 bàn cắt'),
('SP01', 'NL03', 0.500, 'lít', '0.5 lít sơn / 1 bàn cắt'),
('SP02', 'NL01', 40.000, 'kg', '40kg thép / 1 khung'),
('SP02', 'NL04', 15.000, 'que', '15 que hàn / 1 khung');

-- 5. DonSanXuat
INSERT INTO DonSanXuat (MaDon, MaSanPham, SoLuongYeuCau, HanGiao, TrangThai, GhiChu) VALUES
(25, 'SP01', 100, '2026-09-30', 'Đang thực hiện', 'Đơn hàng trọng điểm Quý 3/2026 - Công ty Cơ khí Á Châu'),
(26, 'SP02', 50, '2026-09-25', 'Mới tạo', 'Đơn hàng cần ưu tiên theo tiến độ giao hàng'),
(27, 'SP01', 20, '2026-10-15', 'Mới tạo', 'Đơn dự phòng kho');

-- 6. CongDoan (cho SP01)
INSERT INTO CongDoan (MaCongDoan, MaSanPham, TenCongDoan, ThuTu, MoTa, TrangThai) VALUES
(101, 'SP01', 'Cắt phôi thép CNC', 1, 'Cắt thép tấm theo kích thước thiết kế CAD', 'Active'),
(102, 'SP01', 'Gia công hàn định hình', 2, 'Hàn các khớp nối khung bàn cơ khí', 'Active'),
(103, 'SP01', 'Mài & Xử lý bề mặt', 3, 'Làm sạch xỉ hàn, mài phẳng ba via', 'Active'),
(104, 'SP01', 'Sơn tĩnh điện & Hoàn thiện', 4, 'Sơn phủ và kiểm tra lắp ráp cuối cùng', 'Active');

-- 7. KeHoachSanXuat
INSERT INTO KeHoachSanXuat (MaKeHoach, MaDon, NgayBatDau, NgayKetThuc) VALUES
(1, 25, '2026-09-15', '2026-09-29'),
(2, 26, '2026-09-20', '2026-09-24');

-- 8. PhanCong
INSERT INTO PhanCong (MaPhanCong, MaCongDoan, MaTaiKhoan, MaDon, NgayPhanCong) VALUES
(1, 101, 3, 25, '2026-09-15'),
(2, 102, 4, 25, '2026-09-16'),
(3, 103, 4, 25, '2026-09-18'),
(4, 104, 3, 25, '2026-09-20');

-- 9. TienDoCongDoan (Đơn 25: 60/100 sản phẩm đã hoàn thành ở công đoạn 104)
INSERT INTO TienDoCongDoan (MaTienDo, MaCongDoan, MaDon, SoLuongHoanThanh, TrangThai) VALUES
(1, 101, 25, 80, 'Đang thực hiện'),
(2, 102, 25, 75, 'Đang thực hiện'),
(3, 103, 25, 70, 'Đang thực hiện'),
(4, 104, 25, 60, 'Đang thực hiện');

-- 10. SuDungNguyenLieu (Thực tế đã dùng cho Đơn 25)
INSERT INTO SuDungNguyenLieu (MaSuDung, MaDon, MaCongDoan, MaNguyenLieu, SoLuongSuDung) VALUES
(1, 25, 101, 'NL01', 950.00),
(2, 25, 102, 'NL02', 1300.00),
(3, 25, 104, 'NL03', 32.00);

-- 11. LoiSanXuat (Ghi nhận lỗi phát sinh ở Đơn 25)
INSERT INTO LoiSanXuat (MaLoi, MaDon, MaCongDoan, MoTaLoi, SoLuongHong) VALUES
(1, 25, 101, 'Vết xước kim loại trên bề mặt phôi cắt', 2),
(2, 25, 103, 'Bề mặt trầy xước nhẹ do rung lắc đồ gá', 3);
