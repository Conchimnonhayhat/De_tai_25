# Các API đang triển khai

Các mã nghiệp vụ (`order_id`, `operation_id`, `defect_id`...) là chuỗi, ví dụ `DSX12345`. Các API dùng phiên đăng nhập. Với mọi yêu cầu `POST` ngoài môi trường kiểm thử, gửi mã CSRF từ trang trong header `X-CSRF-Token` hoặc trường form `csrf_token`. Lỗi thiếu mã trả HTTP 400.

| Phương thức và đường dẫn | Quyền | Dữ liệu chính | Kết quả |
|---|---|---|---|
| `POST /api/progress/update` | Tổ trưởng, Nhân viên được giao | `order_id`, `operation_id`, `additional_qty` | JSON gồm trạng thái và tiến độ mới |
| `POST /api/defects/record` | Tổ trưởng, Nhân viên được giao | `order_id`, `operation_id`, `defect_desc`, `defect_qty` | JSON gồm mã lỗi mới |
| `GET /api/statistics/summary?order_id=...` | Quản lý xưởng | Mã đơn tùy chọn | JSON tiến độ và tỷ lệ lỗi |
| `POST /api/ai/progress-summary` | Quản lý xưởng, Tổ trưởng trong phạm vi | `order_id` tùy chọn | Tóm tắt, facts và nguồn dữ liệu |
| `POST /api/ai/defect-analysis` | Quản lý xưởng, Tổ trưởng trong phạm vi | `order_id` tùy chọn | Nhóm lỗi, giả thuyết và nguồn |
| `POST /api/ai/order-priority` | Quản lý xưởng | `max_suggestions` từ 1 đến 5 | Danh sách gợi ý ưu tiên |

Ví dụ yêu cầu cập nhật tiến độ:

```json
{"order_id":"DSX12345","operation_id":"CD12345","additional_qty":5}
```

Những đường dẫn thao tác qua biểu mẫu web: `POST /register` tạo tài khoản chờ duyệt; `POST /admin/users/<id>/approve` để Admin cấp vai trò; `POST /products`, `POST /products/<id>/edit`, `POST /products/<id>/delete`; `POST /orders`, `POST /orders/<id>/plans`, `POST /plans/<id>/edit`; `POST /production/assign`, `POST /production/unassign/<id>`; `POST /production` với action tiến độ/lỗi/báo vật tư; `POST /material-reports/<id>/approve` để Quản lý xưởng trừ kho sau duyệt; `POST /daily-reports` và `POST /daily-reports/<id>/review`; `POST /teams` và `POST /teams/<leader_id>/<worker_id>/remove`.

Kết quả AI có thể mang `status: ok`, `no_data` hoặc `needs_review`. Ở trạng thái `needs_review`, giao diện không hiển thị nguyên văn nội dung AI không khớp dữ liệu nguồn. AI không có API ghi thay đổi kế hoạch hoặc kho.
