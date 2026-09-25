# Tiêu Chí Nghiệm Thu Trợ Lý AI (AI Acceptance Criteria)

---

### AC-AI-001: Nghiệm thu chức năng Tóm tắt tiến độ đơn (US-AI-001)
- **Given**: Đơn 25 có `SoLuongYeuCau=100`, công đoạn 104 có `SoLuongHoanThanh=60`, hạn giao `2026-09-30`.
- **When**: Người dùng chọn "Tóm tắt tiến độ" cho Đơn 25.
- **Then**: 
  - Hệ thống trích xuất snapshot: `SoLuongYeuCau: 100`, `SoLuongHoanThanh: 60`, `progress_percent: 60.0%`.
  - Phản hồi JSON có `status: "ok"`, `task_type: "progress_summary"`.
  - Thuộc tính `facts` phản ánh đúng các số liệu trên.
  - Thuộc tính `source_ids` chứa danh sách mã bản ghi nguồn: `["DonSanXuat:25", "TienDoCongDoan:4"]`.
  - Nội dung tóm tắt nêu rõ đạt 60% và không tự bịa thêm nguyên nhân trễ nếu hạn giao chưa quá.

### AC-AI-002: Nghiệm thu chức năng Phân tích mô tả lỗi (US-AI-002)
- **Given**: Đơn 25 ghi nhận 2 lỗi: "Vết xước kim loại trên bề mặt phôi cắt" và "Bề mặt trầy xước nhẹ do rung lắc đồ gá".
- **When**: Người dùng yêu cầu phân tích lỗi Đơn 25.
- **Then**:
  - AI gom 2 lỗi vào nhóm "Lỗi bề mặt / trầy xước" (tổng cộng 5 sản phẩm hỏng).
  - Thuộc tính `source_ids` chứa `["LoiSanXuat:1", "LoiSanXuat:2"]`.
  - Đề xuất giả thuyết kỹ thuật kèm nhãn `Giả thuyết cần xác minh`, không khẳng định kết luận khi chưa có kiểm định cơ khí.

### AC-AI-003: Nghiệm thu chức năng Gợi ý ưu tiên đơn (US-AI-003)
- **Given**: Đơn 26 có hạn giao 2026-09-25 (gần hơn Đơn 25 hạn 2026-09-30). Đơn 25 đủ vật tư, Đơn 26 có cảnh báo thiếu vật tư.
- **When**: Quản lý xưởng bấm "Gợi ý ưu tiên đơn sản xuất".
- **Then**:
  - AI xếp hạng Đơn 26 và Đơn 25 kèm lý do rõ ràng.
  - Cảnh báo rõ tình trạng vật tư của từng đơn trong `material_constraint`.
  - AI không tự động cập nhật kế hoạch; Quản lý xưởng mở đơn và tự sửa kế hoạch sau khi đối chiếu dữ liệu.

### AC-AI-004: Nghiệm thu khả năng chịu lỗi & Dữ liệu mâu thuẫn
- **Given**: CSDL không có đơn hàng nào hoặc Gemini API gặp lỗi timeout/network.
- **When**: Người dùng gửi yêu cầu phân tích AI.
- **Then**: 
  - Hệ thống trả về trạng thái `no_data` hoặc `provider_error` với thông báo thân thiện.
  - Các chức năng quản lý xưởng lõi vẫn hoạt động bình thường, không bị gián đoạn.
