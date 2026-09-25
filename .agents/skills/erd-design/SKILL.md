---
name: erd-design
description: Build workshop ER diagrams with explicit keys, cardinalities and constraints consistent with the database design.
---

# ERD Design Skill

## Inputs
docs/requirements.md, docs/database-design.md, database/schema.sql và các quyết định về vật tư/công đoạn.

## Process
1. Liệt kê đúng 11 bảng URD, PK/FK, trường bắt buộc và đơn vị tính; ghi rõ điểm thiếu khóa trước khi đề xuất sửa.
2. Mô hình hóa sản phẩm, định mức theo sản phẩm, nguyên liệu, đơn, kế hoạch, công đoạn, phân công, tiến độ, sử dụng nguyên liệu và lỗi theo URD.
3. Thể hiện quan hệ 1--N hoặc N--N qua bảng nối; ghi tùy chọn/bắt buộc phù hợp luồng nghiệp vụ.
4. Kiểm tra đường truy vết đơn/công đoạn/tiến độ/lỗi và đơn/công đoạn/sử dụng nguyên liệu; nêu rõ lỗ hổng liên kết MaDon trong TienDoCongDoan và PhanCong.
5. Vẽ ERD nguồn, gọi diagram-design để render và xem ảnh.
6. So sánh ERD với schema thực tế; báo bảng/cột/khóa hoặc cardinality không khớp.

## Rules
- Không dùng một trường văn bản để lưu danh sách vật tư hoặc danh sách nhân viên thay bảng quan hệ.
- URD chưa quy định phiên bản định mức; chỉ đề xuất bổ sung sau khi nhóm xác nhận nhu cầu lưu lịch sử.
- Các quy tắc liên bảng và đồng thời phải kiểm tra trong service/transaction; CHECK đơn lẻ không thay thế toàn bộ nghiệp vụ.

## Outputs
- docs/diagrams/erd.puml và ảnh tương ứng
- docs/data-dictionary.md
- docs/diagram-review.md với sai lệch ERD ↔ schema

## Verification
Không có FK mồ côi; tên bảng/cột nhất quán; cardinality rõ; các ràng buộc nghiệp vụ có nơi thực thi.
