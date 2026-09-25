# Báo Cáo Kiểm Tra & Đánh Giá Sơ Đồ (Diagram Review Report)

Dự án: Hệ thống Quản lý Xưởng Sản xuất Nhỏ (Đề tài 25 theo URD)  
Ngày kiểm tra: 2026-09-23

> Lưu ý 2026-09-25: Đây là biên bản kiểm tra lịch sử. Sơ đồ ERD hiện đã bổ sung ba bảng theo `docs/urd-change-decisions.md`; chưa chạy lại bước render và rà bố cục cho bản ERD mới.

---

## 1. Danh Sách Sơ Đồ Đã Tạo & Trạng Thái

| Tên Sơ Đồ | File Nguồn PlantUML | Loại Sơ Đồ | Kiểm Tra Cú Pháp | Kiểm Tra Bố Cục & Nhãn | Đối Chiếu Nghiệp Vụ URD |
|---|---|---|---|---|---|
| **Use Case Diagram** | `docs/diagrams/use-case.puml` | Use Case | PASS | Rõ 4 tác nhân + External AI, không đè chữ | Đúng 13 ca sử dụng UC001--UC013 |
| **System Architecture** | `docs/diagrams/architecture.puml` | Component | PASS | Phân 6 tầng rõ ràng, ranh giới AI độc lập | Khớp kiến trúc phân tầng trong ADR-01 |
| **Production Activity** | `docs/diagrams/production-activity.puml`| Activity | PASS | Nhánh rẽ điều kiện rõ ràng, có nhánh lỗi | Khớp chu trình BR-01, BR-02, BR-06 |
| **Progress Sequence** | `docs/diagrams/progress-sequence.puml` | Sequence | PASS | Có Transaction BEGIN/COMMIT/ROLLBACK | Khớp quy trình cập nhật tiến độ |
| **Domain Class Diagram**| `docs/diagrams/domain-class.puml` | Class | PASS | Đầy đủ 11 thực thể domain URD + các quan hệ | Khớp 11 bảng CSDL URD |

---

## 2. Chi Tiết Kiểm Tra Chất Lượng (Quality Checklist)
- [x] **Cú pháp PlantUML**: Tất cả file `.puml` đều tuân thủ cú pháp chuẩn PlantUML, có thể render trực tiếp bằng công cụ PlantUML Java JAR hoặc PlantUML Server.
- [x] **Độ rõ ràng của nhãn (Labels)**: Tên các vai trò, thực thể, phương thức và thông điệp sử dụng tiếng Việt có dấu rõ ràng hoặc tên kỹ thuật chuẩn xác, không bị viết tắt tối nghĩa.
- [x] **Tránh chồng chéo (No overlap)**: Sử dụng các chỉ dẫn layout (skinparam, partition, alt/else) để đường nối (connector) không đi xuyên qua node hoặc tiêu đề.
- [x] **Tính trung thực với URD**: 
  - Không tự bịa thêm quyền sửa định mức cho nhân viên.
  - Không cho phép hệ thống AI có quyền thực thi lệnh cập nhật trực tiếp vào cơ sở dữ liệu.
  - Ghi nhận rõ điểm đề xuất `MaDon` trong `TienDoCongDoan` và `PhanCong` như một nhãn `[DeXuat]` để người duyệt dễ dàng theo dõi.
