-- =============================================================================
-- HE THONG QUAN LY XUONG SAN XUAT NHO (AI-AUGMENTED WORKSHOP MANAGEMENT)
-- Co so du lieu 11 bang theo chuan URD Detai25.1.docx
-- Bang BaoCaoNgay bo sung theo quy trinh bao cao cuoi ngay duoc nhom thong nhat
-- Tuong thich: MySQL 8.0+ / SQLite 3
-- =============================================================================

-- 1. Bảng TaiKhoan (Xác thực và phân quyền 4 vai trò)
CREATE TABLE IF NOT EXISTS TaiKhoan (
    MaTaiKhoan VARCHAR(32) PRIMARY KEY,
    HoTen VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    MatKhau VARCHAR(255) NOT NULL,
    VaiTro VARCHAR(50) NOT NULL, -- chuoi rong khi cho duyet; sau do Admin cap vai tro
    TrangThai VARCHAR(20) DEFAULT 'Active' -- 'Pending', 'Active', 'Suspended', 'Frozen'; 'Deleted' noi bo
);

-- 2. Bảng SanPham (Danh mục sản phẩm xưởng sản xuất)
CREATE TABLE IF NOT EXISTS SanPham (
    MaSanPham VARCHAR(32) PRIMARY KEY,
    TenSanPham VARCHAR(150) NOT NULL,
    DonViTinh VARCHAR(20) NOT NULL,
    MoTa TEXT,
    TrangThai VARCHAR(20) DEFAULT 'Active',
    NgayTao DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. Bảng NguyenLieu (Kho nguyên vật liệu tồn kho)
CREATE TABLE IF NOT EXISTS NguyenLieu (
    MaNguyenLieu VARCHAR(32) PRIMARY KEY,
    TenNguyenLieu VARCHAR(150) NOT NULL,
    DonViTinh VARCHAR(20) NOT NULL,
    SoLuongTon DECIMAL(12,2) DEFAULT 0.00,
    TrangThai VARCHAR(20) DEFAULT 'Active',
    NgayCapNhat DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. Bảng DinhMucNguyenLieu (BOM cho 1 đơn vị sản phẩm - BR-04)
CREATE TABLE IF NOT EXISTS DinhMucNguyenLieu (
    MaSanPham VARCHAR(32) NOT NULL,
    MaNguyenLieu VARCHAR(32) NOT NULL,
    SoLuongDinhMuc DECIMAL(18,4) NOT NULL,
    DonViTinh VARCHAR(20) NOT NULL,
    GhiChu VARCHAR(255),
    NgayCapNhat DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (MaSanPham, MaNguyenLieu),
    FOREIGN KEY (MaSanPham) REFERENCES SanPham(MaSanPham) ON DELETE CASCADE,
    FOREIGN KEY (MaNguyenLieu) REFERENCES NguyenLieu(MaNguyenLieu) ON DELETE RESTRICT
);

-- 5. Bảng DonSanXuat (Đơn hàng sản xuất)
CREATE TABLE IF NOT EXISTS DonSanXuat (
    MaDon VARCHAR(32) PRIMARY KEY,
    MaSanPham VARCHAR(32) NOT NULL,
    SoLuongYeuCau INT NOT NULL,
    HanGiao DATE NOT NULL,
    TrangThai VARCHAR(30) DEFAULT 'Mới tạo', -- 'Mới tạo', 'Đang thực hiện', 'Hoàn thành', 'Hủy'
    NgayTao DATETIME DEFAULT CURRENT_TIMESTAMP,
    GhiChu TEXT,
    FOREIGN KEY (MaSanPham) REFERENCES SanPham(MaSanPham)
);

-- 6. Bảng CongDoan (Quy trình công đoạn thuộc sản phẩm)
CREATE TABLE IF NOT EXISTS CongDoan (
    MaCongDoan VARCHAR(32) PRIMARY KEY,
    MaSanPham VARCHAR(32) NOT NULL,
    TenCongDoan VARCHAR(100) NOT NULL,
    ThuTu INT NOT NULL,
    MoTa TEXT,
    TrangThai VARCHAR(20) DEFAULT 'Active',
    NgayCapNhat DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (MaSanPham) REFERENCES SanPham(MaSanPham) ON DELETE CASCADE
);

-- 7. Bảng KeHoachSanXuat (Kế hoạch thời gian gắn với đơn)
CREATE TABLE IF NOT EXISTS KeHoachSanXuat (
    MaKeHoach VARCHAR(32) PRIMARY KEY,
    MaDon VARCHAR(32) NOT NULL,
    NgayBatDau DATE NOT NULL,
    NgayKetThuc DATE NOT NULL,
    FOREIGN KEY (MaDon) REFERENCES DonSanXuat(MaDon) ON DELETE CASCADE
);

-- 8. Bảng PhanCong (Phân công nhân sự cho công đoạn, kèm MaDon đề xuất giải quyết Issue #01)
CREATE TABLE IF NOT EXISTS PhanCong (
    MaPhanCong VARCHAR(32) PRIMARY KEY,
    MaCongDoan VARCHAR(32) NOT NULL,
    MaTaiKhoan VARCHAR(32) NOT NULL,
    MaDon VARCHAR(32),
    NgayPhanCong DATE NOT NULL,
    FOREIGN KEY (MaCongDoan) REFERENCES CongDoan(MaCongDoan),
    FOREIGN KEY (MaTaiKhoan) REFERENCES TaiKhoan(MaTaiKhoan),
    FOREIGN KEY (MaDon) REFERENCES DonSanXuat(MaDon)
);

-- 9. Bảng TienDoCongDoan (Tiến độ sản lượng hoàn thành theo công đoạn và đơn)
CREATE TABLE IF NOT EXISTS TienDoCongDoan (
    MaTienDo VARCHAR(32) PRIMARY KEY,
    MaCongDoan VARCHAR(32) NOT NULL,
    MaDon VARCHAR(32),
    SoLuongHoanThanh INT DEFAULT 0,
    TrangThai VARCHAR(30) DEFAULT 'Chưa thực hiện', -- 'Chưa thực hiện', 'Đang thực hiện', 'Hoàn thành'
    NgayCapNhat DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (MaCongDoan) REFERENCES CongDoan(MaCongDoan),
    FOREIGN KEY (MaDon) REFERENCES DonSanXuat(MaDon)
);

-- 10. Bảng SuDungNguyenLieu (Theo dõi tiêu hao vật tư thực tế)
CREATE TABLE IF NOT EXISTS SuDungNguyenLieu (
    MaSuDung VARCHAR(32) PRIMARY KEY,
    MaDon VARCHAR(32) NOT NULL,
    MaCongDoan VARCHAR(32) NOT NULL,
    MaNguyenLieu VARCHAR(32) NOT NULL,
    SoLuongSuDung DECIMAL(12,2) NOT NULL,
    NgayGhiNhan DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (MaDon) REFERENCES DonSanXuat(MaDon),
    FOREIGN KEY (MaCongDoan) REFERENCES CongDoan(MaCongDoan),
    FOREIGN KEY (MaNguyenLieu) REFERENCES NguyenLieu(MaNguyenLieu)
);

-- 11. Bảng LoiSanXuat (Ghi nhận lỗi và sản phẩm hỏng)
CREATE TABLE IF NOT EXISTS LoiSanXuat (
    MaLoi VARCHAR(32) PRIMARY KEY,
    MaDon VARCHAR(32) NOT NULL,
    MaCongDoan VARCHAR(32) NOT NULL,
    MoTaLoi TEXT NOT NULL,
    SoLuongHong INT DEFAULT 1,
    NgayGhiNhan DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (MaDon) REFERENCES DonSanXuat(MaDon),
    FOREIGN KEY (MaCongDoan) REFERENCES CongDoan(MaCongDoan)
);

-- Chỉ mục tối ưu hóa hiệu năng truy vấn
CREATE INDEX IF NOT EXISTS idx_don_trangthai ON DonSanXuat(TrangThai);
CREATE INDEX IF NOT EXISTS idx_don_hangiao ON DonSanXuat(HanGiao);
CREATE INDEX IF NOT EXISTS idx_tiendo_don_cd ON TienDoCongDoan(MaDon, MaCongDoan);
CREATE INDEX IF NOT EXISTS idx_sudung_don ON SuDungNguyenLieu(MaDon);

CREATE TABLE IF NOT EXISTS BaoCaoNgay (
    MaBaoCao VARCHAR(32) PRIMARY KEY,
    MaDon VARCHAR(32) NOT NULL,
    MaTaiKhoan VARCHAR(32) NOT NULL,
    NgayBaoCao DATE NOT NULL,
    SoLuongHoanThanh INT NOT NULL DEFAULT 0,
    SoLuongHong INT NOT NULL DEFAULT 0,
    GhiChu TEXT,
    TrangThai VARCHAR(20) NOT NULL DEFAULT 'Pending',
    NgayTao DATETIME DEFAULT CURRENT_TIMESTAMP,
    NgayDuyet DATETIME,
    MaNguoiDuyet VARCHAR(32),
    UNIQUE (MaDon, MaTaiKhoan, NgayBaoCao),
    FOREIGN KEY (MaDon) REFERENCES DonSanXuat(MaDon),
    FOREIGN KEY (MaTaiKhoan) REFERENCES TaiKhoan(MaTaiKhoan),
    FOREIGN KEY (MaNguoiDuyet) REFERENCES TaiKhoan(MaTaiKhoan)
);
CREATE INDEX IF NOT EXISTS idx_loi_don ON LoiSanXuat(MaDon);

-- Báo vật tư đã dùng; chỉ phiếu được quản lý duyệt mới tạo xuất kho thực tế.
CREATE TABLE IF NOT EXISTS BaoVatTu (
    MaBaoVatTu VARCHAR(32) PRIMARY KEY,
    MaDon VARCHAR(32) NOT NULL,
    MaCongDoan VARCHAR(32) NOT NULL,
    MaNguyenLieu VARCHAR(32) NOT NULL,
    MaTaiKhoan VARCHAR(32) NOT NULL,
    SoLuongBaoCao DECIMAL(18,4) NOT NULL,
    TrangThai VARCHAR(20) NOT NULL DEFAULT 'Pending',
    NgayBaoCao DATETIME DEFAULT CURRENT_TIMESTAMP,
    NgayDuyet DATETIME,
    MaNguoiDuyet VARCHAR(32),
    MaSuDung VARCHAR(32),
    FOREIGN KEY (MaDon) REFERENCES DonSanXuat(MaDon),
    FOREIGN KEY (MaCongDoan) REFERENCES CongDoan(MaCongDoan),
    FOREIGN KEY (MaNguyenLieu) REFERENCES NguyenLieu(MaNguyenLieu),
    FOREIGN KEY (MaTaiKhoan) REFERENCES TaiKhoan(MaTaiKhoan),
    FOREIGN KEY (MaNguoiDuyet) REFERENCES TaiKhoan(MaTaiKhoan),
    FOREIGN KEY (MaSuDung) REFERENCES SuDungNguyenLieu(MaSuDung)
);
CREATE INDEX IF NOT EXISTS idx_baovattu_don ON BaoVatTu(MaDon, TrangThai);

-- Phạm vi nhân sự của tổ trưởng; Quản lý xưởng quyết định thành viên tổ.
CREATE TABLE IF NOT EXISTS ThanhVienTo (
    MaToTruong VARCHAR(32) NOT NULL,
    MaNhanVien VARCHAR(32) NOT NULL,
    PRIMARY KEY (MaToTruong, MaNhanVien),
    FOREIGN KEY (MaToTruong) REFERENCES TaiKhoan(MaTaiKhoan),
    FOREIGN KEY (MaNhanVien) REFERENCES TaiKhoan(MaTaiKhoan)
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_thanhvien_one_team ON ThanhVienTo(MaNhanVien);
