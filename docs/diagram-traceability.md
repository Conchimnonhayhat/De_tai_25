# Bảng Truy Vết Sơ Đồ (Diagram Traceability Matrix)

Ma trận truy vết giữa Yêu cầu chức năng (FR), Ca sử dụng (UC) và các phần tử sơ đồ UML.

---

| Yêu Cầu Chức Năng (FR) | Ca Sử Dụng (UC) | Tác Nhân Thao Tác | Phần Tử Trên Sơ Đồ Use Case | Sơ Đồ Liên Quan Khác |
|---|---|---|---|---|
| **FR-01** | UC001 | Tất cả tác nhân | `UC001: Đăng nhập / Đăng xuất` | Sequence: Login & Auth Check |
| **FR-02** | UC002 | Quản trị viên (Admin) | `UC002: Quản lý tài khoản & Phân quyền` | Class: `TaiKhoan` |
| **FR-03** | UC003 | Quản lý xưởng | `UC003: Quản lý sản phẩm` | Class & ERD: `SanPham` |
| **FR-04** | UC004 | Quản lý xưởng | `UC004: Quản lý định mức BOM` | Class & ERD: `DinhMucNguyenLieu` |
| **FR-05** | UC005 | Quản lý xưởng | `UC005: Quản lý đơn sản xuất & Kế hoạch` | Activity: Order lifecycle; ERD: `DonSanXuat` |
| **FR-06** | UC005 | Quản lý xưởng | `UC005: Quản lý đơn sản xuất & Kế hoạch` | ERD: `KeHoachSanXuat` |
| **FR-07** | UC006 | Quản lý xưởng, Tổ trưởng | `UC006: Quản lý công đoạn & Phân công` | Activity: Operation flow; ERD: `CongDoan` |
| **FR-08** | UC006 | Quản lý xưởng, Tổ trưởng | `UC006: Quản lý công đoạn & Phân công` | ERD: `PhanCong` |
| **FR-09** | UC007 | Tổ trưởng, Nhân viên | `UC007: Cập nhật tiến độ công đoạn` | Sequence: Progress Update; ERD: `TienDoCongDoan` |
| **FR-10** | UC008 | Tổ trưởng, Nhân viên | `UC008: Ghi nhận lỗi & Sản phẩm hỏng` | ERD: `LoiSanXuat` |
| **FR-11** | UC009 | Tổ trưởng, Nhân viên | `UC009: Ghi nhận sử dụng nguyên vật liệu` | ERD: `SuDungNguyenLieu` |
| **FR-12** | UC010 | Quản lý xưởng, Tổ trưởng | `UC010: Thống kê tiến độ, Năng suất, Lỗi` | Dashboard Activity Flow |
| **FR-13** | UC010 | Quản lý xưởng, Tổ trưởng | `UC010: Thống kê tiến độ, Năng suất, Lỗi` | Dashboard Activity Flow |
| **FR-14** | UC010 | Quản lý xưởng, Tổ trưởng | `UC010: Thống kê tiến độ, Năng suất, Lỗi` | Dashboard Activity Flow |
| **FR-15** | UC011 | Quản lý, Tổ trưởng, AI | `UC011: AI tóm tắt tiến độ đơn` | AI Data Flow, Sequence AI |
| **FR-16** | UC012 | Quản lý, Tổ trưởng, AI | `UC012: AI phân tích lỗi` | AI Data Flow, Sequence AI |
| **FR-17** | UC013 | Quản lý, AI | `UC013: AI gợi ý thứ tự ưu tiên` | AI Data Flow, Sequence AI |
