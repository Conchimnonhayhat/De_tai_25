# Báo Cáo Đánh Giá Mã Nguồn (Code Review Report)

Dự án: Hệ thống Quản lý Xưởng Sản xuất Nhỏ (Đề tài 25 theo URD)  
Ngày thực hiện review: 2026-09-23  
Công cụ hỗ trợ: `code-review` skill

---

## 1. Tổng Quan Kết Quả Đánh Giá
Đánh giá toàn diện mã nguồn triển khai tại `database/`, `models/`, `services/`, `routes/`, `templates/`, `static/`, và `app.py`.

---

## 2. Danh Mục Các Phát Hiện (Findings by Severity)

### CRITICAL (Nghiêm trọng - 0 phát hiện)
*Không phát hiện lỗ hổng nghiêm trọng. Không có plain-text password, không có SQL Injection qua string formatting.*

---

### HIGH (Cao - Đã xử lý & ghi nhận)
- **H-01 (Đã khắc phục)**: Lỗi logic kiểm tra quyền trong decorator `@role_required`:
  - *Hiện tượng ban đầu*: Biểu thức `current_role not in allowed_roles and 'Admin' not in allowed_roles` khiến kiểm tra bị bỏ qua khi `'Admin'` nằm trong `allowed_roles`.
  - *Biện pháp xử lý*: Đã chuẩn hóa thành `if current_role not in allowed_roles: abort(403)`. Ca kiểm thử `test_worker_cannot_access_admin_route` đã xác minh sửa lỗi thành công.
- **H-02 (Tuân thủ thiết kế)**: Đảm bảo tính nguyên tử khi xuất kho và ghi tiến độ:
  - *Xác nhận*: `ProductionService.update_progress` và `record_material_usage` đều được bao bọc trong `with transaction():` đảm bảo rollback ngay lập tức nếu kiểm tra thứ tự hoặc tồn kho thất bại.

---

### MEDIUM (Trung bình - 1 khuyến nghị)
- **M-01**: Cân nhắc bổ sung phân trang (Pagination) cho danh sách lịch sử lỗi (`LoiSanXuat`) và lịch sử xuất vật tư (`SuDungNguyenLieu`) khi xưởng vận hành lâu dài và số lượng bản ghi vượt quá 10.000 (theo NFR-10).

---

### LOW (Thấp - 2 khuyến nghị)
- **L-01**: Một số thông báo flash message nên đồng bộ chuẩn hóa tiếng Việt có dấu. (Đã hoàn thiện đồng bộ).
- **L-02**: Thêm docstrings giải thích chi tiết các tham số của `StatisticsService.get_defect_rate_statistics`.

---

## 3. Kết Luận Chất Lượng Mã Nguồn
Mã nguồn tuân thủ tốt nguyên tắc phân tầng (Layered Architecture), tuân thủ 100% quy tắc nghiệp vụ BR-01 đến BR-06, và được bảo vệ bởi bộ test tự động đầy đủ.
