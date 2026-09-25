# Nhật Ký Quyết Định Kiến Trúc (Architectural Decision Records - ADR)

---

## ADR-01: Lựa Chọn Phong Cách Kiến Trúc Phân Tầng (Layered Architecture)
- **Bối cảnh**: Hệ thống quản lý xưởng sản xuất nhỏ có các nghiệp vụ từ kho, đơn hàng, công đoạn đến tích hợp AI. Cần cấu trúc rõ ràng, dễ bảo trì, dễ kiểm thử và độc lập giữa các tầng.
- **Quyết định**: Áp dụng Kiến trúc Phân tầng: Presentation (HTML/JS) -> Controller (Flask Routes) -> Business Service -> Data Access Layer (DAO) -> Database.
- **Hệ quả**: Logic nghiệp vụ được cô lập trong tầng Service; việc thay đổi cơ sở dữ liệu hay giao diện không làm ảnh hưởng đến các quy tắc kiểm tra tiến độ, định mức vật tư.

---

## ADR-02: Cơ Chế Xác Thực & Phân Quyền (Authentication & RBAC)
- **Bối cảnh**: Hệ thống có 4 vai trò người dùng (Admin, Quản lý xưởng, Tổ trưởng, Nhân viên) với quyền hạn thao tác khác biệt trên cùng dữ liệu đơn và công đoạn.
- **Quyết định**: Sử dụng Cookie-based Session có cờ `HttpOnly` và `SameSite=Lax`. Mật khẩu được băm bằng thuật toán an toàn `pbkdf2:sha256` của Werkzeug/Python. Sử dụng Decorator `@role_required(['Admin', 'QuanLyXuong'])` để bảo vệ từng route backend.
- **Hệ quả**: Ngăn chặn hoàn toàn việc bypass quyền hạn tại client; kiểm tra quyền luôn được thực thi ở máy chủ.

---

## ADR-03: Chiến Lược Truy Cập CSDL & Tính Linh Hoạt Môi Trường
- **Bối cảnh**: Đề bài chỉ định MySQL, nhưng môi trường thực hành hoặc máy chấm của giáo viên có thể chưa cài sẵn MySQL server đang chạy hoặc có tài khoản khác nhau.
- **Quyết định cập nhật 2026-09-25**: Chọn CSDL qua `USE_MYSQL`. Khi chọn MySQL mà kết nối thất bại, ứng dụng báo lỗi và dừng; chỉ dùng SQLite khi cấu hình `USE_MYSQL=false`.
- **Hệ quả**: Không có nguy cơ ghi dữ liệu sang SQLite âm thầm khi người vận hành tưởng đang dùng MySQL. Bộ kiểm thử dùng SQLite riêng.

---

## ADR-04: Tích Hợp AI An Toàn & Ngăn Ngừa Ảo Giác (Safe AI Integration & Anti-Hallucination)
- **Bối cảnh**: AI (Gemini) có khả năng sinh ra các con số ảo (hallucination), tự bịa đặt số lượng tồn hoặc tự ý thay đổi dữ liệu sản xuất.
- **Quyết định**:
  1. Không cho phép LLM truy vấn CSDL hay gọi function sửa dữ liệu.
  2. Dữ liệu đầu vào cho AI là một **Snapshot có cấu trúc** do backend truy xuất độc lập bằng SQL tham số hóa.
  3. Xây dựng `ResponseValidator`: Kiểm tra đối chiếu số liệu định lượng trong câu trả lời của AI với snapshot từ CSDL; nếu sai lệch hoặc thiếu dữ liệu thì đánh dấu `needs_review` hoặc `missing_data`.
  4. Mọi gợi ý của AI chỉ là bản nháp; Quản lý xưởng là người duyệt hành động cuối cùng.
- **Hệ quả**: Đảm bảo tính an toàn dữ liệu, tuân thủ NFR-06 và BR-08, BR-09.

---

## ADR-05: Quản Lý Giao Dịch Khi Cập Nhật Tiến Độ & Vật Tư
- **Bối cảnh**: Việc cập nhật tiến độ công đoạn hoặc ghi nhận sử dụng nguyên liệu đòi hỏi tính nhất quán giữa kiểm tra số lượng hợp lệ và cập nhật dữ liệu.
- **Quyết định**: Sử dụng Database Transactions với cơ chế Commit/Rollback. Nếu kiểm tra thứ tự công đoạn thất bại hoặc số lượng hoàn thành công đoạn sau vượt công đoạn trước, transaction sẽ được rollback ngay lập tức.
- **Hệ quả**: Tránh hiện tượng dữ liệu rác (dirty read/inconsistent state) trong CSDL xưởng sản xuất.
