---
name: diagram-design
description: Create traceable software diagrams from approved project artifacts and refine their layout for a readable report.
---

# Diagram Design Skill

## Objective
Tạo sơ đồ đúng nghiệp vụ, có file nguồn chỉnh sửa được, có ảnh render và kiểm tra trực quan.

## Inputs
Đọc requirements, user stories, acceptance criteria, architecture, database design và quyết định Human Gate liên quan.

## Supported diagrams
Use Case, Activity, Sequence, Class, ERD, System Architecture và AI Data Flow.

## Process
1. Xác định loại sơ đồ và câu hỏi nghiệp vụ cần thể hiện.
2. Lập danh sách phần tử/quan hệ và mã FR, UC hoặc thực thể làm nguồn.
3. Tạo file PlantUML trong docs/diagrams/; tên vai trò, bảng, module phải thống nhất.
4. Render thành PNG/SVG bằng công cụ sẵn có; không báo đã render khi chỉ mới có source.
5. Mở ảnh ở kích thước dự kiến đưa vào báo cáo. Sửa nhãn, khoảng cách và hướng cạnh; render lại khi còn lỗi.
6. Đối chiếu ảnh và source với yêu cầu đã duyệt; ghi sai lệch vào docs/diagram-review.md.

## Rules
- Không tự thêm tác nhân, quyền, bảng hoặc luồng chưa có nguồn hoặc chưa được duyệt.
- Nhãn đọc được; node và chữ không chồng nhau; connector không đi xuyên node hoặc chữ.
- Hạn chế đường cắt nhau; tách sơ đồ lớn theo nghiệp vụ thay vì thu nhỏ chữ quá mức.
- Giữ source, ảnh, prompt và commit cùng phiên bản; ảnh đẹp chưa đủ để chứng minh đúng nghiệp vụ.

## Outputs
- docs/diagrams/*.puml
- docs/diagrams/*.png hoặc *.svg nếu render thành công
- docs/diagram-traceability.md
- docs/diagram-review.md

## Verification
Kiểm tra cú pháp, nguồn truy vết, tính đầy đủ, quyền, chiều quan hệ và bố cục trước Human Gate.
