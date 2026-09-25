# Báo Cáo Đánh Giá Năng Lực AI Trong SDLC (AI Evaluation Report)

Dự án: Hệ thống Quản lý Xưởng Sản xuất Nhỏ (Đề tài 25 theo URD)  
Đối tượng đánh giá: Codex / AI Agent trong chu trình AI-Augmented SDLC

---

## 1. Đánh Giá Theo Từng Hoạt Động SDLC

| Giai Đoạn SDLC | Mức Độ Hỗ Trợ Của AI | Điểm Mạnh Của AI | Hạn Chế / Điểm Cần Con Người Can Thiệp |
|---|---|---|---|
| **1. Requirements** | 8.5 / 10 | Phân rã nhanh từ ngôn ngữ tự nhiên thành 17 FRs, 11 NFRs, 9 BRs và User Stories có cấu trúc. | AI dễ bị "bịa thêm" chức năng ngoài phạm vi (như tự động đặt hàng vật tư). Con người phải chặn mở rộng phạm vi và phát hiện lỗ hổng thiếu `MaDon`. |
| **2. Architecture** | 9.0 / 10 | Đề xuất kiến trúc phân tầng chuẩn xác, tách biệt Service và DAO, tạo sơ đồ PlantUML trực quan. | Cần con người rà soát ma trận truy vết và thiết lập ranh giới cô lập Gemini Adapter không cho truy cập CSDL. |
| **3. Database** | 9.5 / 10 | Mô hình hóa 11 bảng chuẩn hóa 3NF, thiết lập đầy đủ khóa chính, khóa ngoại, ràng buộc CHECK và indexes. | Con người phải quyết định vị trí bổ sung `MaDon` vào `TienDoCongDoan` và `PhanCong`. |
| **4. Implementation** | 9.0 / 10 | Viết code Flask, Model, Service sạch, tuân thủ nguyên tắc SQL tham số hóa và Transaction context manager. | AI có thể viết sai biểu thức logic boolean phức tạp (như lỗi logic RBAC ban đầu); con người phải chạy test để phát hiện. |
| **5. Testing** | 9.5 / 10 | Tạo bộ test toàn diện 30 ca kiểm thử bao phủ các ca biên (số âm, vượt sản lượng, chia cho 0). | AI có thể tạo test giả lập nếu không bị ép buộc chạy lệnh terminal thực tế và trích xuất terminal log thật. |
| **6. Code & Security** | 9.0 / 10 | Rà soát rất tốt các lỗi XSS, SQLi, kiểm tra băm mật khẩu và cờ cookie an toàn. | Cần con người xác minh ngữ cảnh nghiệp vụ để phân biệt rủi ro thực sự với cảnh báo tĩnh (false positive). |
| **7. Production AI** | 9.0 / 10 | Thiết kế xuất sắc pipeline 7 bước có Validator đối chiếu số liệu định lượng, ngăn ngừa ảo giác. | Con người phải giữ quyền quyết định cuối cùng tại giao diện web (Human-in-the-loop). |

---

## 2. Các Bài Học Kinh Nghiệm Cốt Lõi Về AI Agent
1. **Agent tốt phải biết dừng lại**: AI không được tự động suy đoán khi gặp các điểm thiếu sót nghiệp vụ trong URD (như quan hệ tiến độ hay nhiều kế hoạch cho một đơn). Agent xuất sắc phải biết dừng lại và ghi nhận issue để con người quyết định.
2. **Kỹ năng (Skill) là kim chỉ nam**: Nếu chỉ prompt thông thường, AI sẽ sinh code lộn xộn. Khi có Skill (`SKILL.md`) quy định rõ Input, Process, Rules, Outputs và Verification, AI tuân thủ quy trình phần mềm một cách chuyên nghiệp và có kỷ luật.
3. **Không tin tưởng tuyệt đối vào kết quả sinh ra**: Luôn áp dụng nguyên tắc **Human Gate**: Yêu cầu $\to$ AI Agent $\to$ Human Verification $\to$ APPROVED $\to$ Giai đoạn tiếp theo.
