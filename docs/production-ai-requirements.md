# Yêu Cầu Trợ Lý AI Trong Xưởng Sản Xuất (Production AI Requirements)

Dự án: Hệ thống Quản lý Xưởng Sản xuất Nhỏ (Đề tài 25 theo URD)  
Nguồn tham chiếu: `de_tai_25_theo_URD.md` Phần XXIII, `docs/requirements.md` (FR-15, FR-16, FR-17)

---

## 1. Mục Đích & Bối Cảnh Nghiệp Vụ
Hệ thống cần cung cấp trợ lý AI phục vụ Quản lý xưởng và Tổ trưởng sản xuất trong phạm vi dữ liệu được phân quyền truy cập. Trợ lý AI thực hiện 3 tác vụ phân tích cốt lõi:
1. **Tóm tắt tiến độ đơn sản xuất (FR-15)**: Diễn giải dữ liệu số lượng hoàn thành của các công đoạn, đối chiếu hạn giao và cảnh báo nguy cơ chậm tiến độ.
2. **Phân tích mô tả lỗi sản xuất (FR-16)**: Nhóm các bản ghi mô tả lỗi phân tán trong tuần/tháng thành các cụm lỗi kỹ thuật tương đồng và đưa ra các giả thuyết nguyên nhân cần kiểm tra.
3. **Gợi ý thứ tự ưu tiên đơn sản xuất (FR-17)**: Phân tích đồng thời hạn giao, tiến độ hiện tại và mức độ sẵn sàng của nguyên vật liệu trong kho để đề xuất thứ tự ưu tiên xử lý. Quản lý xưởng là người quyết định cuối cùng.

---

## 2. Nguyên Tắc An Toàn & Chống Ảo Giác (Anti-Hallucination Policy)
- **Không tự bịa dữ liệu**: Trợ lý AI tuyệt đối không được tự suy đoán hoặc sáng tạo ra mã đơn, số lượng sản phẩm, hạn giao, hoặc lượng tồn kho không có trong CSDL.
- **Xử lý dữ liệu thiếu hoặc mâu thuẫn**: Nếu CSDL không có dữ liệu hoặc dữ liệu tiến độ mâu thuẫn, AI phải trả trạng thái rõ ràng `missing_data` hoặc `data_issues`, yêu cầu con người kiểm tra thực tế thay vì tự điền số liệu.
- **Phân biệt dữ kiện và giả thuyết**: Số liệu định lượng (sản lượng, tỷ lệ %) phải lấy chính xác từ facts do backend tính toán; giả thuyết nguyên nhân lỗi của AI phải được gắn nhãn rõ là `Giả thuyết cần xác minh`.
- **Ranh giới thẩm quyền (Human Authority - BR-08, BR-09)**: AI không có quyền ghi CSDL, không tự ý dời lịch sản xuất hay tự ý phát sinh lệnh mua vật tư. Mọi đề xuất của AI chỉ là bản nháp chờ con người duyệt.
- **Bảo mật**: API key của Gemini không được xuất hiện trong mã nguồn client (JavaScript) và không log ra console.
