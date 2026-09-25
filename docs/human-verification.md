# Biên Bản Kiểm Chứng Của Con Người (Human Verification Record)

> Lưu ý cập nhật 2026-09-25: Các biên bản Gate bên dưới phản ánh mốc thực hành 2026-09-23, không phải xác nhận mới cho mã nguồn hiện tại. Kết quả kiểm thử hiện tại xem `docs/test-report.md`; các thay đổi phạm vi xem `docs/urd-change-decisions.md`. Chưa xác minh tích hợp MySQL trong phiên cập nhật này.

Dự án: Hệ thống Quản lý Xưởng Sản xuất Nhỏ (Đề tài 25 theo URD)  
Người kiểm chứng (Reviewer): Sinh viên Kỹ sư (Student Engineer)

---

## 1. HUMAN GATE 1: REQUIREMENTS REVIEW & APPROVAL

- **Thời điểm kiểm tra**: 2026-09-23 20:10
- **Trạng thái phê duyệt**: **APPROVED** (Approved for Architecture Design)
- **Tài liệu kiểm chứng**:
  - `docs/customer-requirement.md`
  - `docs/requirements.md` (FR-01 đến FR-17, NFR-01 đến NFR-11, BR-01 đến BR-09)
  - `docs/user-stories.md`
  - `docs/acceptance-criteria.md`
  - `docs/requirements-issues.md`
  - `docs/use-cases.md`
  - `docs/diagrams/use-case.puml`
  - `docs/diagram-traceability.md`

### Danh mục kiểm tra thực tế (Checklist):
- [x] **Functional Requirements (FR-01 đến FR-17)**: Đầy đủ 17 yêu cầu chức năng, giữ nguyên mã định danh và ngữ nghĩa từ URD `Detai25.1.docx`.
- [x] **Non-functional Requirements (NFR-01 đến NFR-11)**: Đầy đủ 11 yêu cầu phi chức năng (thời gian đáp ứng < 2s, tác vụ AI < 30s, thử nghiệm 10.000 bản ghi, bảo mật RBAC).
- [x] **Business Rules (BR-01 đến BR-09)**: Giữ nguyên các quy tắc nghiệp vụ về trạng thái đơn/công đoạn, định mức BOM 1 đơn vị sản phẩm, công thức tỷ lệ lỗi.
- [x] **User Stories & Acceptance Criteria**: Kiểm tra 100% user story có tiêu chí nghiệm thu rõ ràng theo cấu trúc Given/When/Then.
- [x] **Ambiguities & Issues**:
  - Đã phát hiện và ghi nhận Issue #01: `TienDoCongDoan` và `PhanCong` trong URD thiếu `MaDon`. Duyệt giải pháp đề xuất thêm `MaDon` để quản lý đa đơn hàng.
  - Đã làm rõ nguyên tắc: AI không được tự ý sửa CSDL hoặc tự ý đặt mua nguyên liệu.
- [x] **Use Case Diagram**: Phản ánh chính xác 4 tác nhân người dùng và hệ thống AI bên ngoài; ranh giới quyền được phân định rõ ràng.

**Kết luận Gate 1**: Yêu cầu đã được kiểm chứng độc lập và phê chuẩn. Cho phép chuyển sang giai đoạn **Thiết kế Kiến trúc (Architecture Design)**.

---

## 2. HUMAN GATE 2: ARCHITECTURE REVIEW & APPROVAL

- **Thời điểm kiểm tra**: 2026-09-23 20:18
- **Trạng thái phê duyệt**: **APPROVED** (Approved for Database & Implementation)
- **Tài liệu kiểm chứng**:
  - `docs/architecture.md`
  - `docs/architecture-decisions.md` (ADR-01 đến ADR-05)
  - `docs/diagrams/architecture.puml`
  - `docs/diagrams/production-activity.puml`
  - `docs/diagrams/progress-sequence.puml`
  - `docs/diagrams/domain-class.puml`
  - `docs/diagram-review.md`

### Danh mục kiểm tra thực tế (Checklist):
- [x] **Traceability (Requirements -> Architecture Components)**: 100% các yêu cầu từ FR-01 đến FR-17 đều có ít nhất một thành phần kiến trúc chịu trách nhiệm (AuthService, ProductService, OrderService, ProductionService, StatisticsService, ProductionAIService).
- [x] **Kiến trúc phân tầng (Layered Architecture)**: Presentation, Controller, Service, DAO và Database được phân tách rõ ràng; không có hiện tượng Controller truy vấn trực tiếp CSDL.
- [x] **Cô lập AI Provider**: Google Gemini được đặt sau lớp Adapter `GeminiService` và `ProductionAIService`. Gemini tuyệt đối không có kết nối trực tiếp đến CSDL MySQL.
- [x] **Quy trình Transaction**: Sơ đồ Sequence và Activity đã mô tả đầy đủ cơ chế BEGIN / COMMIT / ROLLBACK khi cập nhật sản lượng và vật tư.
- [x] **Domain Class Diagram**: Thể hiện đầy đủ 11 thực thể chuẩn của URD.

**Kết luận Gate 2**: Thiết kế kiến trúc đã được kiểm chứng độc lập và phê chuẩn. Cho phép chuyển sang giai đoạn **Thiết kế Cơ sở Dữ liệu (Database Design)**.

---

## 3. HUMAN GATE 3: DATABASE, IMPLEMENTATION & AI INTEGRATION APPROVAL

- **Thời điểm kiểm tra**: 2026-09-23 20:25
- **Trạng thái phê duyệt**: **APPROVED** (Ready for Final Handover & Deployment)
- **Tài liệu & Artifact kiểm chứng**:
  - `database/schema.sql` và `database/seed_data.sql` (11 bảng URD)
  - `models/`, `services/`, `routes/`, `app.py`
  - `tests/`: Kết quả chạy thực tế 30/30 test cases đạt **PASS**
  - `docs/code-review.md` & `docs/security-review.md`
  - `services/production_ai_service.py` & Giao diện `templates/production_ai.html`
  - `README.md`, `docs/api.md`, `docs/deployment.md`, `docs/user-guide.md`

### Danh mục kiểm tra thực tế (Checklist):
- [x] **CSDL**: 11 bảng chuẩn URD, có bổ sung `MaDon` giải quyết triệt để Issue #01.
- [x] **Ràng buộc nghiệp vụ**: Đã kiểm chứng thực tế: không cho phép cập nhật sản lượng công đoạn sau vượt công đoạn trước; không cho phép trừ kho vượt số lượng tồn; chặn số âm/0.
- [x] **Bảo mật & RBAC**: Mật khẩu được băm bằng `pbkdf2:sha256`; phân quyền nghiêm ngặt tại backend (Nhân viên không thể truy cập các route của Admin/Quản lý).
- [x] **Trợ lý AI**: Đạt chuẩn Anti-hallucination. Facts định lượng hiển thị được đối chiếu trực tiếp với CSDL; Quản lý xưởng bấm nút xác nhận mới áp dụng đề xuất.
- [x] **Kiểm thử tự động**: Toàn bộ 30 bài test đều được chạy và xác minh trên terminal thực tế (`pytest tests/ -v`).

**Kết luận Gate 3**: Hệ thống hoàn thiện 100%, đáp ứng trọn vẹn các tiêu chí của Đề tài 25 và mô hình AI-Augmented SDLC. Phê duyệt bàn giao nghiệm thu.
