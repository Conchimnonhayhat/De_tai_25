# Vấn Đề Và Thách Thức Khi Tích Hợp AI Sản Xuất (AI Requirements Issues)

---

## 1. Rủi Ro Ảo Giác (Hallucination Risks)
- **Vấn đề**: LLM thường có xu hướng suy diễn hoặc bịa ra nguyên nhân hư hỏng của máy móc (ví dụ: tự khẳng định "Máy CNC số 2 bị mòn dao") mặc dù CSDL chỉ ghi nhận mô tả hiện tượng "bề mặt trầy xước".
- **Giải pháp**: Xây dựng quy tắc Prompting nghiêm ngặt (Grounding Rules) và gắn nhãn rõ ràng: mọi phân tích nguyên nhân chỉ là `Giả thuyết sơ bộ cần kỹ thuật viên xác minh tại hiện trường`.

## 2. Nguy Cơ Rò Rỉ Dữ Liệu (Data Privacy)
- **Vấn đề**: Gửi thông tin cá nhân của công nhân (Họ tên, lương, email) sang dịch vụ AI đám mây bên ngoài.
- **Giải pháp**: Tầng Context Builder chỉ lọc lấy dữ liệu kỹ thuật (Mã đơn, Sản lượng, Tên công đoạn, Mô tả lỗi), loại bỏ hoàn toàn thông tin nhạy cảm của người dùng.

## 3. Quản Trị Quyền Quyết Định Nghiệp Vụ (Human-in-the-loop)
- **Vấn đề**: AI đề xuất thay đổi thứ tự ưu tiên sản xuất có thể dẫn đến việc xáo trộn kế hoạch sản xuất nếu tự động cập nhật CSDL.
- **Giải pháp**: Nghiêm cấm AI gọi bất kỳ endpoint cập nhật nào. Giao diện Web hiển thị bản đề xuất kèm nút "Xác nhận & Áp dụng" dành riêng cho Quản lý xưởng.
