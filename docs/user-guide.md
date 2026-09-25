# Sổ Tay Hướng Dẫn Sử Dụng (User Guide)

Hệ thống Quản lý Xưởng Sản xuất Nhỏ có Tích hợp AI (AI Workshop System)

---

## 1. Dành Cho Quản Trị Viên (Admin)
1. **Đăng nhập**: Sử dụng tài khoản `admin@workshop.edu.vn` (Mật khẩu: `123456`).
2. **Phân quyền người dùng (FR-02)**:
   - Truy cập menu **Quản Lý Phân Quyền** trên thanh điều hướng bên trái.
   - Danh sách tài khoản hiển thị đầy đủ ID, Họ tên, Email và Vai trò hiện tại.
   - Để thay đổi vai trò: Chọn vai trò mong muốn trong danh sách thả xuống (`QuanLyXuong`, `ToTruong`, `NhanVien`) và nhấn nút **Lưu**.
   - Người tự đăng ký có trạng thái **Chờ duyệt**, chưa được đăng nhập. Tìm họ trong danh sách, chọn vai trò nghiệp vụ và bấm **Duyệt**.
   - Khi thêm hoặc duyệt tài khoản **Nhân viên**, có thể chọn **Tổ trưởng phụ trách**. Với nhân viên đã có tài khoản, dùng cột **Tổ phụ trách** để gắn hoặc chuyển sang tổ khác. Mỗi nhân viên thuộc tối đa một tổ; một Tổ trưởng có thể phụ trách nhiều nhân viên.
   - Admin chỉ xem và quản lý tài khoản. Các màn hình sản xuất, kho, thống kê và AI không cấp quyền cho Admin.

---

## 2. Dành Cho Quản Lý Xưởng (Workshop Manager)
1. **Quản lý Sản phẩm & Định mức vật tư (FR-03, FR-04)**:
   - Vào menu **Sản Phẩm & Định Mức**.
   - Khai báo mã sản phẩm, tên, đơn vị tính và mô tả quy cách.
   - Trong phần **Định mức nguyên vật liệu (BOM)**, chọn vật tư đã khai báo trong kho, nhập số lượng định mức dùng cho **1 đơn vị sản phẩm** (BR-04) và ghi chú nếu cần. Bấm **Thêm định mức vật tư** để tạo nhiều dòng; bấm **Xóa** để bỏ dòng. Đơn vị vật tư lấy theo danh mục kho.
   - Bấm **Lưu sản phẩm & định mức**. Hệ thống kiểm tra vật tư, số lượng dương và vật tư không trùng; nếu có lỗi, sản phẩm và định mức đều chưa được lưu. Nếu kho chưa có vật tư, vào **Kho Nguyên Vật Liệu** khai báo vật tư trước.
   - Xem bảng định mức vật tư và số lượng cần thiết cho 1 đơn vị sản phẩm (BOM).
   - Với sản phẩm đã tạo, bấm **Sửa sản phẩm & định mức BOM** để đổi thông tin, thêm/sửa/xóa dòng định mức; bấm **Thêm bước** để khai báo quy trình công đoạn theo thứ tự 1, 2, 3... trước khi giao việc.
   - Nếu tạo nhầm sản phẩm, tìm sản phẩm trong danh sách và bấm **Xóa**, rồi xác nhận. Hệ thống xóa sản phẩm cùng định mức và công đoạn chưa sử dụng. Sản phẩm đã có đơn sản xuất hoặc dữ liệu công đoạn không thể xóa để giữ lịch sử sản xuất.
2. **Tiếp nhận Đơn hàng & Kế hoạch (FR-05, FR-06)**:
   - Vào menu **Đơn Hàng Sản Xuất**.
   - Tạo đơn mới bằng cách chọn sản phẩm, số lượng đặt, hạn giao hàng.
   - Trong thẻ đơn, thêm kế hoạch bằng ngày bắt đầu/kết thúc; kế hoạch đã có có thể sửa. Mã đơn và các mã bản ghi mới là chuỗi chữ-số.
   - Hệ thống tự động hiển thị hộp đánh giá **Khả thi vật tư**: Báo xanh nếu kho đủ vật tư theo số lượng cần dùng, báo đỏ nếu thiếu kèm số lượng thiếu hụt cụ thể.
3. **Sử dụng Trợ lý AI Sản xuất (FR-15, FR-16, FR-17)**:
   - Vào menu **Trợ Lý AI Sản Xuất**.
   - Chuyển đổi giữa 3 tab: Tóm tắt tiến độ, Phân tích lỗi, Gợi ý ưu tiên.
   - Nhấn nút **Phân Tích Với Trợ Lý AI**: Xem bản tóm tắt, số liệu facts xác minh, giả thuyết nguyên nhân kỹ thuật và các đề xuất xếp hạng đơn.
   - Gợi ý AI chỉ để tham khảo. Muốn đổi kế hoạch thật, bấm **Mở đơn và kế hoạch** rồi tự sửa kế hoạch; giao diện không tự lưu đề xuất AI.
4. **Xử lý báo cáo cuối ngày**: Vào **Báo Cáo Cuối Ngày**, tìm theo đơn, ngày hoặc trạng thái rồi xác nhận các báo cáo Tổ trưởng đã nộp.
5. **Quản lý kho**: Vào **Kho Nguyên Vật Liệu** để thêm mã vật tư, nhập thêm số lượng và tra cứu tồn. Khi Tổ trưởng/Nhân viên báo vật tư đã dùng, vào đơn trong **Điều Hành Công Đoạn**, đối chiếu phiếu rồi bấm **Duyệt và trừ kho**. Mỗi phiếu chỉ được duyệt một lần.
6. **Thành viên tổ**: Vào **Thành Viên Tổ** để thêm/gỡ nhân viên thuộc từng Tổ trưởng. Tổ trưởng chỉ giao việc cho nhân viên đang hoạt động trong tổ mình.
7. **Giao công đoạn**: Trong **Điều Hành Công Đoạn**, chọn công đoạn, ngày và một Tổ trưởng phụ trách. Tổ trưởng đó mới có thể phân việc cho thành viên tổ mình ở công đoạn đã nhận. Nếu cần đổi Tổ trưởng, gỡ phân công nhân viên trong công đoạn trước.

---

## 3. Dành Cho Tổ Trưởng (Team Leader)
1. **Điều hành ca sản xuất (FR-08, FR-09)**:
   - Vào menu **Điều Hành Công Đoạn**.
   - Chọn đơn hàng đang thực hiện ở thanh bộ lọc trên cùng.
   - Bấm nút **Cập Nhật Sản Lượng** trong công đoạn được giao để nhập số lượng sản phẩm hoàn thành; dùng phần **Phân Công Nhân Viên** và **Thêm nhân viên** để giao công đoạn đó cho nhiều thành viên tổ trong một lần.
2. **Ghi nhận sự cố và xem vật tư (FR-10, FR-11)**:
   - Tại màn hình Điều Hành Công Đoạn: Sử dụng form **Ghi Nhận Lỗi** khi phát hiện sản phẩm bị trầy xước, cong vênh, ghi rõ số lượng hỏng.
   - Xem danh mục tồn kho để điều phối nhân viên; Tổ trưởng không được ghi giảm tồn kho.
   - Nếu phát sinh vật tư đã dùng, chọn công đoạn và vật tư trong danh sách cần dùng rồi **Gửi phiếu báo vật tư**. Phiếu chờ Quản lý xưởng duyệt, chưa trừ tồn.
3. **Báo cáo cuối ngày**: Vào **Báo Cáo Cuối Ngày**, chọn đơn được phân công, nhập sản lượng, số hỏng và ghi chú rồi gửi Quản lý xưởng.

---

## 4. Dành Cho Nhân Viên (Worker)
1. **Xem công việc & Báo cáo sản lượng**:
   - Đăng nhập tài khoản nhân viên `worker@workshop.edu.vn`.
   - Xem công đoạn được phân công trong đơn hàng.
   - Cập nhật số lượng hoàn thành và báo cáo lỗi nếu có phát sinh.
   - Có thể báo lượng vật tư đã dùng theo công đoạn được giao; chỉ thấy tên và đơn vị vật tư liên quan, không thấy số tồn. Quản lý xưởng là người duyệt và ghi xuất kho.
   - Chỉ xem các đơn và công đoạn được phân công. Không truy cập kho hoặc báo cáo toàn xưởng.

## 5. Tìm kiếm và lọc

- **Tài khoản**: mã, tên/email, vai trò, trạng thái; chỉ Admin được sử dụng.
- **Sản phẩm**: mã hoặc tên; dành cho Quản lý xưởng và Tổ trưởng.
- **Đơn sản xuất**: từ khóa (mã đơn, mã/tên sản phẩm hoặc ghi chú), sản phẩm, trạng thái, công đoạn được giao, Tổ trưởng phụ trách và khoảng hạn giao. Có thể kết hợp các tiêu chí; kết quả vẫn theo quyền của người đăng nhập. Có thể nhập mã theo dạng `Đơn #25`.
- **Kho**: mã hoặc tên vật tư, còn hàng, sắp hết, hết hàng; Quản lý xưởng và Tổ trưởng được xem.
- **Báo cáo cuối ngày**: mã đơn/tên Tổ trưởng, ngày và trạng thái.

## 6. Tài khoản demo hai tổ

Mật khẩu mặc định cho các tài khoản demo dưới đây: `123456`.

| Tổ | Vai trò | Mã | Email đăng nhập |
| --- | --- | --- | --- |
| 1 | Tổ trưởng có sẵn | `3` | `leader@workshop.edu.vn` |
| 1 | Nhân viên | `4` | `worker@workshop.edu.vn` |
| 1 | Nhân viên | `NVDEMO11` | `demo.worker1a@workshop.edu.vn` |
| 1 | Nhân viên | `NVDEMO12` | `demo.worker1b@workshop.edu.vn` |
| 2 | Tổ trưởng | `TTDEMO02` | `demo.leader2@workshop.edu.vn` |
| 2 | Nhân viên | `NVDEMO21` | `demo.worker2a@workshop.edu.vn` |
| 2 | Nhân viên | `NVDEMO22` | `demo.worker2b@workshop.edu.vn` |

Để thử: đăng nhập Quản lý xưởng, giao một công đoạn cho `TTDEMO02`; sau đó đăng nhập `demo.leader2@workshop.edu.vn` và phân công `NVDEMO21`, `NVDEMO22` cho chính công đoạn đó.
