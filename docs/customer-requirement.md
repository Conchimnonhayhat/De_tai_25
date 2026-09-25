# Yêu Cầu Khách Hàng - Quản Lý Xưởng Sản Xuất Nhỏ

Nguồn yêu cầu nghiệp vụ: Detai25.1.docx (URD của nhóm). Hệ thống quản lý sản phẩm, định mức, đơn, kế hoạch, công đoạn, nhân sự, tiến độ, lỗi, vật tư và thống kê cho xưởng sản xuất nhỏ.

## 1. Tác nhân hệ thống
Hệ thống có bốn tác nhân người dùng và một hệ thống ngoài:
- **Quản trị viên (Admin)**: Đăng nhập, đăng xuất, quản lý tài khoản và phân quyền 3 vai trò Quản lý xưởng, Tổ trưởng, Nhân viên (FR-01, FR-02; UC001, UC002). Chỉ Admin thay đổi vai trò.
- **Quản lý xưởng**: Quản lý danh mục sản phẩm, định mức nguyên liệu theo sản phẩm, đơn sản xuất và kế hoạch sản xuất; theo dõi công đoạn, phân công, vật tư và thống kê tổng hợp; sử dụng ba chức năng AI và quyết định thứ tự ưu tiên (UC003--UC006, UC009--UC013).
- **Tổ trưởng**: Theo dõi công đoạn được giao, phân công nhân sự theo quyền, cập nhật tiến độ, ghi nhận lỗi, ghi nhận sử dụng nguyên liệu, xem thống kê và sử dụng AI tóm tắt/phân tích lỗi (UC006--UC012 theo phạm vi quyền).
- **Nhân viên**: Xem công việc được phân công; cập nhật tiến độ, ghi nhận lỗi/sản phẩm hỏng và lượng nguyên liệu sử dụng theo quyền (UC007--UC009).
- **Dịch vụ AI bên ngoài**: Hệ thống ngoài (Gemini qua backend) hỗ trợ tóm tắt, phân tích lỗi, gợi ý ưu tiên; AI không có quyền tự thay đổi dữ liệu nghiệp vụ.

## 2. Các yêu cầu chức năng (FR-01 đến FR-17)
- **FR-01**: Đăng nhập, đăng xuất và quản lý phiên.
- **FR-02**: Admin phân quyền ba vai trò nghiệp vụ (Quản lý xưởng, Tổ trưởng, Nhân viên).
- **FR-03**: Quản lý danh mục sản phẩm.
- **FR-04**: Quản lý định mức nguyên liệu theo sản phẩm (BOM) cho một đơn vị sản phẩm.
- **FR-05**: Quản lý đơn sản xuất.
- **FR-06**: Quản lý kế hoạch sản xuất gắn với đơn sản xuất.
- **FR-07**: Quản lý công đoạn sản xuất thuộc sản phẩm.
- **FR-08**: Phân công nhân sự cho công đoạn.
- **FR-09**: Cập nhật tiến độ từng công đoạn (số lượng hoàn thành, trạng thái).
- **FR-10**: Ghi nhận lỗi sản xuất và số lượng sản phẩm hỏng.
- **FR-11**: Theo dõi sử dụng nguyên vật liệu theo đơn, công đoạn, nguyên liệu.
- **FR-12**: Thống kê tiến độ sản xuất.
- **FR-13**: Thống kê năng suất từ sản lượng ghi nhận.
- **FR-14**: Thống kê tỷ lệ lỗi theo công thức URD.
- **FR-15**: AI tóm tắt tiến độ đơn sản xuất.
- **FR-16**: AI phân tích mô tả lỗi và nhóm nguyên nhân thường gặp.
- **FR-17**: AI gợi ý thứ tự ưu tiên theo hạn giao, tiến độ và tình trạng nguyên liệu (Quản lý xưởng quyết định).

## 3. Các yêu cầu phi chức năng (NFR-01 đến NFR-11)
- **NFR-01 (Hiệu năng)**: Thời gian phản hồi thao tác quản trị < 2 giây; tác vụ AI < 30 giây.
- **NFR-02 (Khả dụng)**: Hệ thống hoạt động ổn định, có thông báo thân thiện khi lỗi.
- **NFR-03 (Bảo mật)**: Mật khẩu băm an toàn, kiểm soát truy cập theo vai trò (RBAC).
- **NFR-04 (Riêng tư)**: Dữ liệu nhân sự và thông tin nội bộ không được chia sẻ trái phép.
- **NFR-05 (Tin cậy dữ liệu)**: Dữ liệu giao dịch tính toán nhất quán, kiểm soát số lượng không âm.
- **NFR-06 (An toàn AI)**: AI hoạt động dưới dạng trợ lý, không tự động ghi dữ liệu nghiệp vụ; cảnh báo khi thiếu hoặc mâu thuẫn dữ liệu.
- **NFR-07 (Bảo trì)**: Kiến trúc phân lớp rõ ràng, mã nguồn tuân thủ coding convention.
- **NFR-08 (Kiểm thử)**: Hệ thống có kiểm thử tự động bao phủ logic nghiệp vụ cốt lõi.
- **NFR-09 (Truy vết)**: Yêu cầu, ca sử dụng, mã nguồn và ca kiểm thử có liên kết truy vết rõ ràng.
- **NFR-10 (Khả năng chịu tải demo)**: Hỗ trợ thử nghiệm ít nhất 10.000 bản ghi thử nghiệm.
- **NFR-11 (Thay thế AI)**: Kiến trúc AI provider độc lập, có thể thay đổi provider mà không sửa logic lõi.

## 4. Các quy tắc nghiệp vụ (BR-01 đến BR-09)
- **BR-01**: Trạng thái đơn sản xuất: Mới tạo -> Đang thực hiện -> Hoàn thành -> Đã hủy.
- **BR-02**: Trạng thái công đoạn: Chưa thực hiện -> Đang thực hiện -> Hoàn thành.
- **BR-03**: Tiến độ tính toán dựa trên số lượng hoàn thành thực tế so với số lượng yêu cầu của đơn.
- **BR-04**: Định mức nguyên liệu tính trên 1 đơn vị sản phẩm hoàn chỉnh.
- **BR-05**: Lượng nguyên liệu sử dụng thực tế được ghi nhận chi tiết theo từng đơn, công đoạn và nguyên liệu.
- **BR-06**: Tỷ lệ lỗi (%) = (Tổng số lượng hỏng / Tổng sản lượng ghi nhận) * 100%. Nếu mẫu số = 0, hiển thị chưa có dữ liệu.
- **BR-07**: AI chỉ tóm tắt, phân tích trên dữ liệu mà người dùng hiện tại có thẩm quyền truy cập.
- **BR-08**: AI gợi ý nhưng người có thẩm quyền (Quản lý/Tổ trưởng) đưa ra quyết định cuối cùng.
- **BR-09**: Không tự động đặt mua vật tư hay tự động dời lịch sản xuất khi chưa có phê duyệt của Quản lý xưởng.

## 5. Các điểm chưa chốt / Cần làm rõ từ URD
- `TienDoCongDoan` và `PhanCong` trong URD gốc chỉ có `MaCongDoan`, chưa có `MaDon`. Khi một sản phẩm được sản xuất trong nhiều đơn khác nhau, cần bổ sung `MaDon` để phân biệt tiến độ giữa các đơn.
- Một đơn có thể có nhiều `KeHoachSanXuat`, cần quy định kế hoạch nào đang hiệu lực (ví dụ kế hoạch mới nhất hoặc theo trạng thái).
- Không tự động thêm các chức năng ngoài phạm vi (như tự động đặt mua vật tư).
