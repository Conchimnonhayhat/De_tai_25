---
name: uml-diagrams
description: Model workshop actors, production workflows, interactions and domain classes using reviewed UML diagrams.
---

# UML Diagrams Skill

## Inputs
Yêu cầu FR-01 đến FR-17, UC001--UC013, BR-01 đến BR-09 và kiến trúc đã duyệt; URD Detai25.1.docx là nguồn nghiệp vụ.

## Process
1. Use Case: vẽ Admin, Quản lý xưởng, Tổ trưởng, Nhân viên và hệ thống AI bên ngoài; gắn UC001--UC013 đúng quyền URD.
2. Activity: khai báo sản phẩm/định mức → đơn/kế hoạch → công đoạn/phân công → tiến độ/vật tư/lỗi → thống kê hoặc AI hỗ trợ quyết định.
3. Activity thể hiện trạng thái công đoạn Chưa thực hiện → Đang thực hiện → Hoàn thành; nhánh dữ liệu thiếu/mâu thuẫn phải được cảnh báo.
4. Sequence: UI → API → Service → Repository → MySQL; kiểm quyền và ràng buộc số lượng, nêu giao dịch/rollback nếu thao tác cần tính nguyên tử.
5. Class: dùng đúng 11 thực thể URD: TaiKhoan, SanPham, NguyenLieu, DinhMucNguyenLieu, DonSanXuat, CongDoan, KeHoachSanXuat, PhanCong, TienDoCongDoan, SuDungNguyenLieu, LoiSanXuat.
6. Dùng diagram-design để render, xem ảnh, sửa bố cục và kiểm tra truy vết.

## Rules
- Không cho Nhân viên sửa định mức hoặc tự duyệt kế hoạch.
- Không cho AI trực tiếp cập nhật tồn, tiến độ hoặc thứ tự kế hoạch.
- include/extend chỉ dùng khi đúng ngữ nghĩa UML; không dùng chỉ để nối cho đủ chức năng.
- Đường lỗi và điều kiện chuyển trạng thái phải khớp mô tả ca sử dụng.

## Outputs
- docs/diagrams/use-case.puml
- docs/diagrams/production-activity.puml
- docs/diagrams/progress-sequence.puml
- docs/diagrams/domain-class.puml
- Ảnh render tương ứng và bảng FR/UC → phần tử sơ đồ.

## Verification
Đối chiếu quyền, luồng chính/ngoại lệ, trạng thái và tên API; người phụ trách duyệt trước lập trình.
