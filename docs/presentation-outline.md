# Dàn Ý Thuyết Trình Báo Cáo Dự Án (Presentation Outline)

Đề tài 25: Hệ Thống Quản Lý Xưởng Sản Xuất Nhỏ Có Tích Hợp AI Bằng AI-Augmented SDLC

---

## Slide 1: Trang Bìa
- **Tiêu đề**: Xây dựng Hệ thống Quản lý Xưởng Sản xuất Nhỏ có Tích hợp AI bằng AI-Augmented SDLC.
- **Người thực hiện**: Sinh viên thực hiện đề tài.
- **Cốt lõi**: Đánh giá năng lực sử dụng AI như một Agent có kiểm soát quy trình, thay vì chỉ là công cụ sinh code.

---

## Slide 2: Đặt Vấn Đề & Mục Tiêu Dự Án
- **Bài toán thực tế**: Xưởng sản xuất cơ khí nhỏ gặp khó khăn trong việc theo dõi tiến độ công đoạn, định mức tiêu hao nguyên liệu, phân tích nguyên nhân lỗi và sắp xếp thứ tự đơn hàng.
- **Mục tiêu**:
  - Xây dựng hệ thống quản lý 4 vai trò (Admin, Quản lý, Tổ trưởng, Nhân viên) theo đúng URD.
  - Tích hợp 3 tính năng AI: Tóm tắt tiến độ (FR-15), Phân tích lỗi (FR-16), Gợi ý ưu tiên đơn (FR-17).
  - Triển khai toàn bộ quy trình phát triển theo mô hình AI-Augmented SDLC.

---

## Slide 3: Mô Hình AI-Augmented SDLC Với Codex
- **4 Thành phần cốt lõi**:
  - `Codex`: AI Agent điều phối và thực thi tác vụ.
  - `Skill`: 15 Skills quy định chuẩn mực thủ tục (độc lập tại `.agents/skills/`).
  - `Tool`: Bộ công cụ máy trạm (Terminal, Pytest, Git, File system).
  - `MCP`: Cơ chế kết nối hệ thống bên ngoài (Issue tracking, CSDL).
- **Human Gates**: 3 điểm kiểm soát độc lập của con người ngăn ngừa ảo giác và sai lệch nghiệp vụ.

---

## Slide 4: Phân Tích Yêu Cầu & Human Gate 1
- **Phạm vi**: 17 FRs, 11 NFRs, 9 BRs, 13 Use Cases.
- **Phát hiện quan trọng của Human Gate 1**:
  - Bảng `TienDoCongDoan` và `PhanCong` trong URD thiếu `MaDon`.
  - Con người can thiệp phê chuẩn bổ sung `MaDon` để hệ thống hỗ trợ đa đơn hàng mà không bị xung đột tiến độ.

---

## Slide 5: Kiến Trúc Phân Tầng & Thiết Kế CSDL
- **Kiến trúc**: Presentation -> Controller -> Business Service -> Data Access Layer -> MySQL / SQLite.
- **CSDL**: 11 bảng cốt lõi của URD và 3 bảng bổ sung cho báo cáo cuối ngày, báo vật tư và thành viên tổ. Mã nghiệp vụ dùng chuỗi chữ-số.
- **Ranh giới an toàn**: Google Gemini được cô lập phía sau tầng Service Adapter; AI không thể truy cập hay ghi dữ liệu trực tiếp vào CSDL.

---

## Slide 6: Cơ Chế Trợ Lý AI & Pipeline 7 Bước
- Quy trình: `Request Analyzer` -> `Data Retriever` -> `Context Builder` -> `Prompt Builder` -> `Gemini Provider` -> `Response Validator` -> `Human Review`.
- **Cơ chế chống ảo giác**:
  - Đối chiếu số liệu trong phản hồi với CSDL gốc.
  - Gắn nhãn phân định `Dữ kiện xác minh` vs `Giả thuyết cần kiểm tra`.
  - Quản lý xưởng tự xem và sửa kế hoạch sau khi đối chiếu đề xuất; AI không ghi CSDL.

---

## Slide 7: Kết Quả Kiểm Thử & Kiểm Toán Chất Lượng
- **Kiểm thử tự động**: 65/65 ca đạt `PASS` trên `pytest` ở lần chạy 2026-09-25; MySQL chưa được kiểm thử tích hợp.
- **Code Review**: Không có lỗi CRITICAL, đã khắc phục logic RBAC.
- **Bảo mật đã kiểm tra**: Phân quyền theo vai trò, mã CSRF cho biểu mẫu, truy vấn tham số hóa ở các luồng chính và băm mật khẩu.

---

## Slide 8: Demo Sản Phẩm Trực Tiếp
- Kịch bản 1: Đăng nhập Quản lý xưởng -> Xem Dashboard & Kiểm tra tính khả thi vật tư của Đơn 25, Đơn 26.
- Kịch bản 2: Cập nhật sản lượng công đoạn -> Kiểm chứng thứ tự công đoạn không bị vượt.
- Kịch bản 3: Chạy Trợ lý AI tóm tắt tiến độ Đơn 25 và gợi ý ưu tiên; mở đơn để tự điều chỉnh kế hoạch nếu cần.

---

## Slide 9: Bài Học & Kết Luận
- **Skills** giúp thống nhất cách làm; **Human Gates** dùng để đối chiếu kết quả AI với URD và dữ liệu thực tế.
- Quản lý phiên bản Skill cùng với mã nguồn bằng Git là chìa khóa để duy trì chất lượng dự án phần mềm lâu dài.
