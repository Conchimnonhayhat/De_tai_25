# Kế Hoạch Kiểm Thử Hệ Thống (Test Plan)

Dự án: Hệ thống Quản lý Xưởng Sản xuất Nhỏ (Đề tài 25 theo URD)  
Framework kiểm thử: `pytest`  
Nguồn tham chiếu: `docs/acceptance-criteria.md`, `docs/requirements.md`

---

## 1. Mục Tiêu Kiểm Thử
- Xác nhận 100% các yêu cầu chức năng cốt lõi (FR-01 đến FR-14) và các quy tắc nghiệp vụ (BR-01 đến BR-06).
- Kiểm tra tính bảo mật phân quyền (RBAC) và kiểm soát truy cập theo vai trò (NFR-03).
- Kiểm tra các ca biên (Edge cases): Số lượng âm/0, tồn kho không đủ, cập nhật sản lượng vượt giới hạn hoặc trái thứ tự công đoạn.
- Đảm bảo tính toán tỷ lệ lỗi (BR-06) không bị crash khi chưa có sản lượng (ZeroDivisionError).

---

## 2. Phạm Vi Kiểm Thử (Scope)

| Nhóm Kiểm Thử | File Test | Số Lượng Ca Kiểm Thử | Trọng Tâm Nghiệp Vụ |
|---|---|---|---|
| **Xác thực & Phân quyền** | `tests/test_auth.py` | 5 test cases | Đăng nhập đúng/sai mật khẩu, redirect chưa đăng nhập, Worker bị chặn (403), Admin được phép |
| **Kho & Định mức (BOM)** | `tests/test_inventory.py` | 5 test cases | Thiết lập BOM, chặn định mức <= 0, kiểm tra tính khả thi vật tư, trừ kho nguyên tử, chặn xuất quá tồn |
| **Quy trình Sản xuất** | `tests/test_production.py` | 6 test cases | Tạo đơn, chặn số lượng <= 0, ràng buộc thứ tự công đoạn BR-03, chặn vượt sản lượng đơn, ghi nhận lỗi |
| **Báo cáo & Thống kê** | `tests/test_statistics.py` | 4 test cases | Tiến độ %, năng suất công đoạn, tỷ lệ lỗi BR-06, xử lý mẫu số = 0 |

---

## 3. Tiêu Chí Đánh Giá
- **Tiêu chí Đạt (Pass Criteria)**: 100% các ca kiểm thử tự động trả về kết quả `PASSED`.
- **Nguyên tắc**: Ca kiểm thử chỉ được ghi nhận PASS khi có lệnh chạy thực tế và log đầu ra từ terminal. Không sửa đổi test assertion để làm giả kết quả PASS.
