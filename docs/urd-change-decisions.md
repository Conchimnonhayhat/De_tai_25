# Quyết định triển khai so với URD gốc

Tài liệu gốc `Detai25.1.docx` là cơ sở đối chiếu. Những điểm dưới đây là quyết định bổ sung hoặc điều chỉnh theo yêu cầu nhóm, không phải câu chữ của URD.

| Nội dung | Quyết định đang triển khai | Lý do |
|---|---|---|
| Mã nghiệp vụ `Ma...` | Dùng `VARCHAR(32)` cho PK/FK; cho phép chữ, số, gạch nối và gạch dưới. Ví dụ `DTC12345`. | Mã tài khoản và các mã khác có thể gồm cả chữ và số, giữ được số 0 đầu. |
| Đăng ký | Tài khoản mới ở trạng thái `Pending`, vai trò rỗng; Admin duyệt và chọn vai trò. | Không tự cấp quyền Nhân viên trước khi kiểm duyệt. |
| Admin | Chỉ quản lý tài khoản, vai trò và trạng thái. | Phân tách quyền quản trị tài khoản khỏi dữ liệu xưởng và kho. |
| Quản lý xưởng | Quản lý sản phẩm/BOM, công đoạn, đơn/kế hoạch, kho, thành viên tổ và duyệt báo cáo. | Chịu trách nhiệm vận hành xưởng và tồn kho. |
| Tổ trưởng | Xem kho, điều phối thành viên tổ trên đơn được giao, báo tiến độ, lỗi, vật tư và cuối ngày. | Tổ trưởng nắm vật tư để chỉ đạo nhân viên nhưng không tự trừ kho. |
| Nhân viên | Chỉ xem/làm công đoạn được giao, báo kết quả và vật tư đã dùng; không xem tồn kho. | Giới hạn truy cập theo công việc. |
| Xuất vật tư | Phiếu `BaoVatTu` chờ Quản lý xưởng duyệt; chỉ khi duyệt mới trừ kho và tạo `SuDungNguyenLieu`. | Có điểm kiểm soát trước khi thay đổi tồn thực tế. |
| Cơ cấu tổ | Bảng `ThanhVienTo`; một nhân viên thuộc một tổ tại một thời điểm. | Ngăn giao việc chồng chéo từ nhiều tổ trưởng. |
| Báo cáo cuối ngày | Bảng `BaoCaoNgay`; Tổ trưởng gửi, Quản lý xưởng xem và duyệt. | Thể hiện luồng báo cáo đã thống nhất. |
| Sản phẩm và BOM | Quản lý xưởng được tạo, sửa; xóa sản phẩm chưa phát sinh đơn hoặc dữ liệu sản xuất. | Sửa sai khi khai báo mà vẫn giữ lịch sử đã sử dụng. |
| Tìm kiếm và lọc | Tài khoản, sản phẩm, đơn, kho và báo cáo có bộ lọc trong phạm vi quyền người xem. | Hỗ trợ tra cứu khi danh sách lớn. |
| AI | Chỉ tư vấn, hiển thị nguồn và cảnh báo khi dữ liệu AI không khớp; không tự lưu đề xuất. | Quản lý xưởng chịu trách nhiệm quyết định cuối cùng. |

Ba bảng `BaoCaoNgay`, `BaoVatTu`, `ThanhVienTo` là phần mở rộng ngoài 11 bảng cốt lõi URD. Cấu trúc thực tế nằm ở `database/schema.sql`, hướng dẫn chuyển CSDL cũ ở `docs/deployment.md`.
