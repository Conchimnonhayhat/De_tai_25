# Báo Cáo Kiểm Toán Bảo Mật (Security Review Report)

Dự án: Hệ thống Quản lý Xưởng Sản xuất Nhỏ (Đề tài 25 theo URD)  
Ngày kiểm toán: 2026-09-23  
Công cụ thực hiện: `security-review` skill

---

## 1. Kết Quả Kiểm Toán Chi Tiết Theo Tiêu Chuẩn OWASP Top 10

### 1. SQL Injection (A03:2021 - Injection)
- **Trạng thái**: **SECURE (An toàn)**
- **Kiểm tra**: Rà soát 100% các hàm trong `database/db.py`, `models/`, và `services/`.
- **Bằng chứng**: Không tồn tại bất kỳ câu lệnh SQL nào ghép chuỗi (string concatenation hoặc f-strings). Tất cả đều sử dụng cú pháp tham số hóa `%s` (cho MySQL) hoặc `?` (cho SQLite) thông qua con trỏ DB API:
  ```python
  cursor.execute(adapted_query, args)
  ```

---

### 2. Cross-Site Scripting - XSS (A03:2021 - Injection)
- **Trạng thái**: **SECURE (An toàn)**
- **Kiểm tra**: Các trường nhập tự do từ người dùng như `MoTaLoi` (Mô tả lỗi sản xuất) hoặc `GhiChu` (Ghi chú đơn hàng).
- **Bằng chứng**:
  - Tại tầng backend: `ProductionService.record_defect` sử dụng `html.escape(defect_desc.strip())` trước khi ghi vào CSDL.
  - Tại tầng frontend: Jinja2 template engine tự động bật chế độ Auto-Escaping cho toàn bộ biến HTML.

---

### 3. Broken Access Control & RBAC (A01:2021 - Broken Access Control)
- **Trạng thái**: **SECURE (An toàn)**
- **Kiểm tra**: Khả năng leo thang đặc quyền từ Nhân viên lên Quản lý hoặc Quản trị viên.
- **Bằng chứng**:
  - Mọi route nhạy cảm (`/admin/users`, `/products` [POST], `/orders` [POST]) đều được bảo vệ bằng `@role_required` tại server.
  - Đã có unit test `test_worker_cannot_access_admin_route` chứng minh khi `NhanVien` gọi endpoint quản trị sẽ bị trả về `403 Forbidden`.

---

### 4. Cryptographic Failures & Password Storage (A02:2021 - Cryptographic Failures)
- **Trạng thái**: **SECURE (An toàn)**
- **Kiểm tra**: Lưu trữ mật khẩu người dùng trong bảng `TaiKhoan`.
- **Bằng chứng**: Mật khẩu được băm an toàn thông qua hàm `generate_password_hash` của Werkzeug/Python (chuẩn `scrypt` hoặc `pbkdf2:sha256:600000`). Tuyệt đối không lưu mật khẩu dạng bản rõ (plain-text).

---

### 5. Quản Lý Secrets & Biến Môi Trường (Security Misconfiguration)
- **Trạng thái**: **SECURE (An toàn)**
- **Kiểm tra**: Tệp `.env` và API keys.
- **Bằng chứng**: Tệp `.env` được khai báo rõ trong `.gitignore`. Không có bất kỳ API key nào của Gemini hoặc chuỗi kết nối MySQL có mật khẩu bị đẩy lên Git repository.

---

### 6. Ranh Giới An Toàn Dữ Liệu AI (AI Data Boundary & Prompt Injection)
- **Trạng thái**: **SECURE (An toàn)**
- **Kiểm tra**: Tích hợp dịch vụ Gemini API.
- **Bằng chứng**:
  - Gemini Service chỉ nhận **Snapshot dữ liệu sản xuất đã được lọc quyền** từ backend, không được cấp quyền kết nối hay thao tác CSDL.
  - Các chỉ thị trong prompt quy định nghiêm ngặt: AI không được tự ý sửa số liệu và không biến văn bản mô tả lỗi thành lệnh thực thi hệ thống.
