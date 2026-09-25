# Yêu Cầu Chức Năng Phân Rã Cho Trợ Lý AI (AI Functional Requirements)

Mã kỹ thuật phục vụ kiểm thử và truy vết về FR-15, FR-16, FR-17 của URD.

---

| Mã FR-AI | Tên Yêu Cầu Kỹ Thuật | Truy Vết FR URD | Mô Tả Thực Hiện |
|---|---|---|---|
| **FR-AI-001** | Yêu cầu tóm tắt tiến độ đơn | FR-15 | Người có quyền gửi yêu cầu kèm mã đơn; hệ thống phân tích snapshot tiến độ và trả về bản tóm tắt có cấu trúc. |
| **FR-AI-002** | Yêu cầu gom nhóm & phân tích lỗi | FR-16 | Người có quyền gửi yêu cầu kèm khoảng thời gian/mã đơn; AI phân nhóm các chuỗi mô tả lỗi và đưa giả thuyết. |
| **FR-AI-003** | Gợi ý thứ tự ưu tiên đơn sản xuất | FR-17 | Quản lý xưởng yêu cầu đề xuất tối đa N đơn ưu tiên theo hạn giao, tiến độ và mức sẵn sàng của nguyên vật liệu. |
| **FR-AI-004** | Trích xuất snapshot CSDL có kiểm soát | NFR-03, NFR-06 | Hệ thống chỉ trích xuất dữ liệu thuộc phạm vi quyền của user hiện tại, gắn kèm mã nguồn (`source_ids`). |
| **FR-AI-005** | Xây dựng ngữ cảnh & Prompt tối thiểu | NFR-04, NFR-06 | Lọc bỏ thông tin thừa/nhạy cảm, đóng gói facts và quy tắc kiểm soát vào prompt gửi sang Gemini qua backend. |
| **FR-AI-006** | Kiểm chứng kết quả phản hồi (Validator) | NFR-06 | Backend kiểm tra cấu trúc JSON, đối chiếu các số liệu trong facts với CSDL trước khi trả về client. |
| **FR-AI-007** | Xử lý lỗi nhà cung cấp & Dữ liệu rỗng | NFR-02, NFR-06 | Khi Gemini timeout, lỗi mạng, hoặc CSDL rỗng, hệ thống hiển thị thông báo thân thiện; không làm crash app. |
