# Đặc Tả Yêu Cầu Phần Mềm (Software Requirements Specification)

Hệ thống Quản lý Xưởng Sản xuất Nhỏ có Tích hợp AI (AI_Workshop_System)  
Nguồn tham chiếu: URD `Detai25.1.docx` & `docs/customer-requirement.md`

---

## 1. Yêu cầu Chức năng (Functional Requirements - FR)

| Mã FR | Tên Yêu Cầu | Tác nhân chính | Mô tả chi tiết |
|---|---|---|---|
| **FR-01** | Đăng nhập, đăng xuất và quản lý phiên | Tất cả tác nhân | Xác thực người dùng qua Email/Mật khẩu băm an toàn. Quản lý phiên làm việc và đăng xuất. |
| **FR-02** | Phân quyền người dùng | Admin | Quản trị viên quản lý danh sách tài khoản và phân bổ 3 vai trò: Quản lý xưởng, Tổ trưởng, Nhân viên. |
| **FR-03** | Quản lý danh mục sản phẩm | Quản lý xưởng | Thêm, sửa, xem, chuyển trạng thái kích hoạt của sản phẩm (Mã, Tên, Đơn vị tính, Mô tả). |
| **FR-04** | Quản lý định mức nguyên liệu (BOM) | Quản lý xưởng | Thiết lập lượng nguyên liệu chuẩn cần thiết để sản xuất 1 đơn vị sản phẩm (SoLuongDinhMuc, DonViTinh). |
| **FR-05** | Quản lý đơn sản xuất | Quản lý xưởng | Lập đơn, theo dõi số lượng yêu cầu, hạn giao, trạng thái (Mới tạo, Đang thực hiện, Hoàn thành, Hủy). |
| **FR-06** | Quản lý kế hoạch sản xuất | Quản lý xưởng | Lập kế hoạch thời gian (NgayBatDau, NgayKetThuc) liên kết với Đơn sản xuất. |
| **FR-07** | Quản lý công đoạn sản xuất | Quản lý xưởng, Tổ trưởng | Khai báo quy trình công đoạn cho sản phẩm theo thứ tự thực hiện (ThuTu, TenCongDoan). |
| **FR-08** | Phân công nhân sự cho công đoạn | Quản lý xưởng, Tổ trưởng | Phân công nhân viên phụ trách công đoạn trong ca sản xuất (MaCongDoan, MaTaiKhoan, NgayPhanCong). |
| **FR-09** | Cập nhật tiến độ công đoạn | Tổ trưởng, Nhân viên | Ghi nhận số lượng hoàn thành và cập nhật trạng thái công đoạn (Chưa thực hiện, Đang thực hiện, Hoàn thành). |
| **FR-10** | Ghi nhận lỗi và sản phẩm hỏng | Tổ trưởng, Nhân viên | Ghi nhận mô tả lỗi, số lượng sản phẩm hỏng theo đơn và công đoạn phát sinh. |
| **FR-11** | Theo dõi sử dụng nguyên vật liệu | Tổ trưởng, Nhân viên | Ghi nhận số lượng nguyên liệu thực tế đã tiêu hao theo đơn, công đoạn và nguyên liệu. |
| **FR-12** | Thống kê tiến độ sản xuất | Quản lý xưởng, Tổ trưởng | Báo cáo tiến độ tổng thể của đơn hàng và từng công đoạn dựa trên sản lượng thực tế. |
| **FR-13** | Thống kê năng suất | Quản lý xưởng, Tổ trưởng | Thống kê tổng sản lượng đạt được theo nhân sự/công đoạn trong khoảng thời gian xác định. |
| **FR-14** | Thống kê tỷ lệ lỗi sản xuất | Quản lý xưởng, Tổ trưởng | Tính toán tỷ lệ lỗi theo công thức URD BR-06: (Tổng số hỏng / Tổng sản lượng) * 100%. |
| **FR-15** | AI tóm tắt tiến độ đơn sản xuất | Quản lý xưởng, Tổ trưởng | Trợ lý AI tóm tắt tình trạng tiến độ, công đoạn nghẽn dựa trên dữ liệu CSDL được cấp quyền. |
| **FR-16** | AI phân tích mô tả lỗi sản xuất | Quản lý xưởng, Tổ trưởng | Trợ lý AI phân nhóm mô tả lỗi và đưa ra giả thuyết nguyên nhân kỹ thuật cần kiểm tra. |
| **FR-17** | AI gợi ý thứ tự ưu tiên đơn sản xuất | Quản lý xưởng | Trợ lý AI đề xuất thứ tự ưu tiên xử lý đơn dựa trên hạn giao, tiến độ và tồn kho nguyên liệu. Quản lý xưởng quyết định. |

---

## 2. Yêu cầu Phi chức năng (Non-Functional Requirements - NFR)

- **NFR-01 (Thời gian đáp ứng)**: Thao tác CRUD/truy vấn < 2 giây; gọi dịch vụ AI < 30 giây.
- **NFR-02 (Tính khả dụng)**: Giao diện trực quan, tương thích trình duyệt hiện đại, hiển thị rõ ràng thông báo lỗi khi không thể kết nối.
- **NFR-03 (Bảo mật)**: Mật khẩu lưu dạng băm (PBKDF2/bcrypt/werkzeug). Kiểm soát phân quyền RBAC nghiêm ngặt tại backend cho từng endpoint.
- **NFR-04 (Bảo vệ riêng tư)**: Không gửi thông tin nhạy cảm của nhân sự sang hệ thống AI bên ngoài; chỉ gửi dữ liệu kỹ thuật và mã đơn.
- **NFR-05 (Toàn vẹn dữ liệu)**: Dùng transaction cho các thao tác cập nhật vật tư, tiến độ. Số lượng yêu cầu, hoàn thành, hỏng, tiêu hao phải >= 0.
- **NFR-06 (An toàn AI & Hallucination Prevention)**: Dữ liệu gửi AI phải là snapshot có cấu trúc kèm mã nguồn. AI không được tự ý sửa CSDL. Nếu thiếu dữ liệu phải báo `missing_data`.
- **NFR-07 (Khả năng bảo trì)**: Code tuân thủ mô hình MVC/Service-Repository, tách bạch rõ rệt giữa logic nghiệp vụ và logic tích hợp AI.
- **NFR-08 (Khả năng kiểm thử)**: Cung cấp bộ unit test và integration test tự động (pytest), bao phủ đầy đủ các ranh giới kiểm tra.
- **NFR-09 (Tính truy vết)**: Đảm bảo khả năng truy vết từ FR -> Use Case -> Architecture -> Code -> Test Case.
- **NFR-10 (Quy mô thử nghiệm)**: Thiết kế hỗ trợ tải thử nghiệm ít nhất 10.000 bản ghi dữ liệu mẫu.
- **NFR-11 (Độc lập AI Provider)**: Sử dụng kiến trúc Adapter cho dịch vụ AI, dễ dàng thay thế Gemini bằng các mô hình LLM khác.

---

## 3. Quy tắc Nghiệp vụ (Business Rules - BR)

- **BR-01 (Vòng đời Đơn sản xuất)**: Đơn sản xuất tuân theo chuỗi trạng thái `Mới tạo` -> `Đang thực hiện` -> `Hoàn thành` (hoặc `Đã hủy`).
- **BR-02 (Trạng thái Công đoạn)**: Công đoạn chuyển đổi tuần tự: `Chưa thực hiện` -> `Đang thực hiện` -> `Hoàn thành`.
- **BR-03 (Tính toán Tiến độ)**: Tiến độ công đoạn = Số lượng hoàn thành / Số lượng yêu cầu. Số lượng hoàn thành của công đoạn sau không được vượt quá công đoạn trước liền kề.
- **BR-04 (Quy chuẩn Định mức BOM)**: Định mức nguyên liệu được xác định chính xác cho một (01) đơn vị sản phẩm tiêu chuẩn.
- **BR-05 (Ghi nhận Tiêu hao Nguyên liệu)**: Mỗi lần ghi nhận sử dụng nguyên liệu phải chỉ rõ: Mã đơn, Mã công đoạn, Mã nguyên liệu, Số lượng tiêu hao.
- **BR-06 (Công thức Tỷ lệ Lỗi)**: 
  $$\text{Tỷ lệ lỗi (\%)} = \frac{\sum \text{Số lượng hỏng}}{\sum \text{Tổng sản lượng ghi nhận}} \times 100\%$$
  Nếu tổng sản lượng ghi nhận bằng 0, hiển thị trạng thái `Chưa có dữ liệu`.
- **BR-07 (Ranh giới Dữ liệu AI)**: AI chỉ được đọc snapshot dữ liệu sản xuất thuộc phạm vi quyền của người dùng đang gửi request.
- **BR-08 (Thẩm quyền Quyết định Nhân sự)**: AI chỉ đóng vai trò tư vấn, gợi ý. Quản lý xưởng hoặc Tổ trưởng chịu trách nhiệm duyệt và bấm áp dụng trên hệ thống.
- **BR-09 (Giới hạn Thao tác AI)**: Nghiêm cấm mô hình AI tự ý phát sinh lệnh mua sắm vật tư, tự ý xóa sửa bản ghi CSDL, hoặc tự ý điều chỉnh lịch sản xuất.
