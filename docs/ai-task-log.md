# Nhật Ký Giao Tác Vụ Cho AI (AI Task Log)

Tài liệu ghi lại toàn bộ quá trình tương tác, câu lệnh (Prompt/Task) từ **🧑‍💻 Tôi (Kỹ sư/Sinh viên)** và kết quả phản hồi của **🤖 Codex (AI Agent)** theo từng bước của AI-Augmented SDLC.

---

## 📌 Giai đoạn 1: Khởi tạo Cấu trúc & Requirements Engineering

### 🧑‍💻 Task 01: Thiết lập môi trường và cấu trúc kỹ năng ban đầu (Bước 3A, 3B, 3C)
- **Người giao (Tôi)**:
  > "Hãy khởi tạo cấu trúc thư mục AI_Workshop_System, tạo .gitignore, requirements.txt và định nghĩa 3 Skill ban đầu cho việc vẽ sơ đồ: diagram-design, uml-diagrams, erd-design. Đảm bảo tuân thủ tiêu chuẩn Skill format của Antigravity/Codex với YAML frontmatter."
- **AI Agent (Codex)**:
  - *Skill kích hoạt*: `diagram-design`, `uml-diagrams`, `erd-design`
  - *Hành động*: Tạo các file `.agents/skills/.../SKILL.md` quy định rõ quy trình vẽ sơ đồ, kiểm tra tính truy vết và kết xuất PlantUML.
  - *Artifacts tạo ra*: `.agents/skills/diagram-design/SKILL.md`, `.agents/skills/uml-diagrams/SKILL.md`, `.agents/skills/erd-design/SKILL.md`, `requirements.txt`, `.gitignore`.

---

### 🧑‍💻 Task 02: Phân tích yêu cầu hệ thống (Bước 6)
- **Người giao (Tôi)**:
  > "Hãy thực hiện Requirements Engineering cho project này.  
  > Sử dụng `requirements-analysis` skill; kết hợp `diagram-design` và `uml-diagrams` skill cho sơ đồ Use Case.  
  > Đọc: `docs/customer-requirement.md`.  
  > Thực hiện đúng quy trình được quy định trong skill.  
  > Không viết source code.  
  > Tạo:  
  > - docs/requirements.md  
  > - docs/user-stories.md  
  > - docs/acceptance-criteria.md  
  > - docs/requirements-issues.md  
  > - docs/use-cases.md  
  > - docs/diagrams/use-case.puml  
  > - docs/diagram-traceability.md  
  > Giữ nguyên FR-01--FR-17, NFR-01--NFR-11, BR-01--BR-09 và UC001--UC013 của Detai25.1.docx; không đổi mã hay gộp yêu cầu.  
  > Sau khi hoàn thành, giải thích:  
  > 1. Skill nào đã được sử dụng.  
  > 2. Những artifacts nào đã tạo.  
  > 3. Những requirement nào còn chưa rõ.  
  > 4. Những giả định nào đã được sử dụng."

- **AI Agent (Codex)**:
  - *Báo cáo thực thi*:
    1. **Skill đã sử dụng**: `requirements-analysis`, `diagram-design`, `uml-diagrams`.
    2. **Artifacts đã tạo**:
       - `docs/requirements.md`: Đầy đủ 17 FR, 11 NFR, 9 BR.
       - `docs/user-stories.md`: 16 user stories phân theo 7 nhóm nghiệp vụ.
       - `docs/acceptance-criteria.md`: Bộ tiêu chí nghiệm thu Given/When/Then cho các kịch bản chuẩn và biên.
       - `docs/requirements-issues.md`: Phân tích 4 issues kỹ thuật (đặc biệt là sự thiếu hụt `MaDon` trong bảng tiến độ).
       - `docs/use-cases.md`: Danh mục ca sử dụng UC001 đến UC013 gắn với 4 vai trò.
       - `docs/diagrams/use-case.puml`: Sơ đồ PlantUML Use Case.
       - `docs/diagram-traceability.md`: Ma trận truy vết từ FR -> UC -> Sơ đồ.
    3. **Những requirement còn chưa rõ (Unclear / Ambiguities)**:
       - Trong URD gốc, bảng `TienDoCongDoan` và `PhanCong` chỉ có `MaCongDoan`. Nếu 2 đơn hàng sản xuất cùng 1 loại sản phẩm thì sẽ bị trùng khóa tiến độ. Codex đề xuất cần bổ sung `MaDon` vào 2 bảng này.
       - Một đơn có nhiều kế hoạch sản xuất, chưa rõ kế hoạch nào đang hiệu lực (đề xuất lấy kế hoạch mới nhất).
       - Năng suất (FR-13) chưa có bảng chấm công giờ làm việc (đề xuất tính theo tổng sản lượng hoàn thành theo mốc thời gian).
    4. **Những giả định đã sử dụng (Assumptions)**:
       - AI là hệ thống bên ngoài, chỉ hỗ trợ gợi ý, không có quyền ghi trực tiếp vào CSDL.
       - Mật khẩu người dùng bắt buộc phải được băm an toàn theo NFR-03.
       - Không tự ý thêm chức năng tự động đặt hàng vật tư ngoài phạm vi URD.

---

### 🧑‍💻 Đánh giá & Phê duyệt tại Human Gate 1 (Bước 7 & 8)
- **Người kiểm chứng (Tôi)**:
  - Tiến hành đối chiếu độc lập tài liệu của Codex với URD `Detai25.1.docx`.
  - Xác nhận Codex không bị ảo giác (hallucination), không tự ý bịa thêm bảng hoặc chức năng mua hàng tự động.
  - Phê duyệt đề xuất kỹ thuật bổ sung `MaDon` cho `TienDoCongDoan`.
  - Ký duyệt trạng thái **APPROVED** tại `docs/human-verification.md` và cho phép chuyển sang Giai đoạn Thiết kế Kiến trúc.

---

## 📌 Giai đoạn 2: Thiết Kế Kiến Trúc Hệ Thống (Architecture Design)

### 🧑‍💻 Task 03: Thiết kế kiến trúc tổng thể & Sơ đồ UML (Bước 9)
- **Người giao (Tôi)**:
  > "Hãy sử dụng `architecture-design` skill cùng `diagram-design` và `uml-diagrams` skill.  
  > Đọc các tài liệu requirements đã được phê duyệt:  
  > - docs/requirements.md  
  > - docs/user-stories.md  
  > - docs/acceptance-criteria.md  
  > Thiết kế kiến trúc cho hệ thống. Không viết source code.  
  > Tạo:  
  > - docs/architecture.md  
  > - docs/architecture-decisions.md  
  > - docs/diagrams/architecture.puml  
  > - docs/diagrams/production-activity.puml  
  > - docs/diagrams/progress-sequence.puml  
  > - docs/diagrams/domain-class.puml  
  > - docs/diagram-review.md  
  > Activity thể hiện quy trình BR-01--BR-09 và cảnh báo thiếu vật tư/dữ liệu sai; Sequence kiểm quyền, kiểm số lượng và rollback khi thao tác ghi cần giao dịch. Đảm bảo kiến trúc hỗ trợ quản lý đơn, vật tư, công đoạn, nhân công, lỗi và ba chức năng AI dựa trên dữ liệu sản xuất trong MySQL."

- **AI Agent (Codex)**:
  - *Skill kích hoạt*: `architecture-design`, `diagram-design`, `uml-diagrams`
  - *Báo cáo thực thi*:
    1. **Kiến trúc phân tầng được chọn**: Đã thiết lập 5 tầng logic + 1 tầng AI ngoài trong `docs/architecture.md`. Tách biệt rõ Presentation, Controller, Service, DAO và CSDL.
    2. **Quyết định kiến trúc (ADRs)**: Ghi nhận 5 ADRs trong `docs/architecture-decisions.md` (ADR-01 về Layered style, ADR-02 về Session RBAC, ADR-03 về cơ chế fallback CSDL linh hoạt, ADR-04 về an toàn AI/anti-hallucination, ADR-05 về transaction).
    3. **Sơ đồ PlantUML hoàn thành**:
       - `architecture.puml`: Minh họa trực quan các component và ranh giới AI độc lập.
       - `production-activity.puml`: Thể hiện vòng đời công đoạn (BR-02), nhánh cảnh báo thiếu vật tư và cảnh báo dữ liệu mâu thuẫn cho AI.
       - `progress-sequence.puml`: Thể hiện chi tiết luồng cập nhật tiến độ có kiểm tra RBAC, kiểm tra sản lượng và lệnh ROLLBACK khi dữ liệu bất hợp lệ.
       - `domain-class.puml`: Mô hình hóa đầy đủ 11 thực thể của URD và quan hệ.
       - `diagram-review.md`: Đánh giá cú pháp, nhãn và tính trung thực với nghiệp vụ.

---

### 🧑‍💻 Đánh giá & Phê duyệt tại Human Gate 2 (Phần XI)
- **Người kiểm chứng (Tôi)**:
  - Kiểm tra ma trận ánh xạ FR -> Architecture Components: Xác nhận mọi FR-01 đến FR-17 đều có component tương ứng đảm nhiệm.
  - Kiểm tra ranh giới AI: Xác nhận Gemini không được cấp quyền truy cập trực tiếp CSDL.
  - Phê chuẩn trạng thái **APPROVED** tại `docs/human-verification.md` (Gate 2). Cho phép chuyển sang Giai đoạn Thiết kế CSDL.

---

## 📌 Giai đoạn 3: Thiết Kế Cơ Sở Dữ Liệu (Database Design)

### 🧑‍💻 Task 04: Thiết kế CSDL MySQL 11 bảng URD & ERD (Bước 11)
- **Người giao (Tôi)**:
  > "Hãy sử dụng `database-design` skill cùng `diagram-design` và `erd-design` skill.  
  > Đọc:  
  > - docs/requirements.md  
  > - docs/architecture.md  
  > Thiết kế cơ sở dữ liệu MySQL.  
  > Phải xem xét: normalization, primary keys, foreign keys, constraints, indexes, data types.  
  > Nhu cầu truy xuất tiến độ, mô tả lỗi, hạn giao và tồn vật tư phục vụ AI. Không viết Flask source code.  
  > Tạo:  
  > - docs/database-design.md  
  > - database/schema.sql  
  > - database/seed_data.sql  
  > - docs/data-dictionary.md  
  > - docs/diagrams/erd.puml  
  > Đối chiếu ERD với schema.sql bằng erd-design skill. Ghi rõ PK/FK, lực lượng quan hệ và quy tắc cần service/transaction kiểm soát."

- **AI Agent (Codex)**:
  - *Skill kích hoạt*: `database-design`, `diagram-design`, `erd-design`
  - *Báo cáo thực thi*:
    1. **Thiết kế CSDL đạt 3NF**: Phân rã dữ liệu chuẩn xác thành đúng 11 bảng theo URD.
    2. **Bổ sung khóa liên kết**: Đã thêm `MaDon` (FK) vào `TienDoCongDoan` và `PhanCong` theo quyết định phê duyệt tại Human Gate 1, giải quyết dứt điểm vấn đề xung đột khi nhiều đơn cùng sản xuất một loại sản phẩm.
    3. **Tối ưu hóa chỉ mục (Indexes)**: Thêm các index trên `DonSanXuat(TrangThai)`, `DonSanXuat(HanGiao)`, `TienDoCongDoan(MaDon, MaCongDoan)` giúp API và AI Service truy xuất snapshot cực nhanh.
    4. **Artifacts hoàn thành**:
       - `database/schema.sql`: Script DDL chuẩn cho 11 bảng và indexes.
       - `database/seed_data.sql`: Dữ liệu mẫu xưởng cơ khí hoàn chỉnh (Admin, Manager, Leader, Worker, Đơn 25, tiến độ 60/100, lỗi bề mặt, vật tư).
       - `docs/database-design.md`: Thuyết minh chuẩn hóa và toàn vẹn dữ liệu.
       - `docs/data-dictionary.md`: Từ điển dữ liệu chi tiết từng cột.
       - `docs/diagrams/erd.puml`: Sơ đồ thực thể quan hệ chuẩn PlantUML.

---

### 🧑‍💻 Đánh giá & Kiểm tra Cơ sở Dữ liệu (Phần XIV)
- **Người kiểm chứng (Tôi)**:
  - Đối chiếu `database/schema.sql` và `docs/diagrams/erd.puml`: Khớp 100% về tên bảng, tên cột, kiểu dữ liệu, khóa chính và khóa ngoại.
  - Kiểm tra ràng buộc: Có đầy đủ CHECK `SoLuong > 0`, UNIQUE Email, FK cascade/restrict hợp lý.
  - Phê chuẩn CSDL sẵn sàng cho Giai đoạn Lập trình (Implementation).

---

## 📌 Giai đoạn 4: Lập Trình Hệ Thống Cốt Lõi (Core Implementation)

### 🧑‍💻 Task 05: Triển khai mã nguồn hệ thống quản lý xưởng (Bước 13)
- **Người giao (Tôi)**:
  > "Hãy sử dụng `implementation` skill.  
  > Đọc:  
  > - docs/requirements.md  
  > - docs/architecture.md  
  > - docs/database-design.md  
  > Triển khai hệ thống quản lý xưởng sản xuất nhỏ bằng Python, Flask, MySQL (kèm adapter SQLite linh hoạt).  
  > Triển khai:  
  > 1. Database connection, đăng nhập và phân quyền 4 tác nhân; chỉ Admin gán vai trò.  
  > 2. Product CRUD và quản lý định mức theo sản phẩm.  
  > 3. Theo dõi NguyenLieu.SoLuongTon, DinhMucNguyenLieu và SuDungNguyenLieu.  
  > 4. Production Order và kế hoạch sản xuất.  
  > 5. Operation và Assignment.  
  > 6. Cập nhật/xác nhận tiến độ; kiểm lượng đầu vào và thứ tự công đoạn.  
  > 7. Ghi nhận lỗi và sản phẩm hỏng.  
  > 8. Thống kê tiến độ, năng suất và tỷ lệ lỗi.  
  > Chưa gọi mô hình AI ở giai đoạn core; sau kiểm thử và review lõi, tiếp tục Phần XXIII để triển khai đủ FR-15, FR-16, FR-17.  
  > Báo cáo những file đã thay đổi."

- **AI Agent (Codex)**:
  - *Skill kích hoạt*: `implementation`
  - *Báo cáo thực thi*:
    1. **Tầng CSDL (`database/db.py`)**: Hỗ trợ kết nối tham số hóa, transaction context manager tự động commit/rollback, tự khởi tạo bảng và seed data.
    2. **Tầng Mô hình (`models/`)**: `user.py`, `product.py`, `order.py`, `production.py` bao quát 11 thực thể nghiệp vụ.
    3. **Tầng Nghiệp vụ (`services/`)**:
       - `auth_service.py`: Xác thực, băm mật khẩu `pbkdf2:sha256`, `@login_required`, `@role_required`.
       - `product_service.py`: Quản lý sản phẩm, định mức BOM (BR-04), cập nhật tồn kho.
       - `order_service.py`: Lập đơn, lập kế hoạch, kiểm tra tính khả thi vật tư theo BOM so với tồn kho thực tế.
       - `production_service.py`: Cập nhật tiến độ có kiểm soát thứ tự công đoạn và sản lượng tối đa (BR-02, BR-03); ghi nhận lỗi thoát mã HTML; ghi nhận vật tư kèm trừ kho nguyên tử.
       - `statistics_service.py`: Tính tỷ lệ lỗi theo BR-06, xử lý mẫu số 0; thống kê tiến độ %; thống kê năng suất theo công đoạn.
    4. **Tầng Giao diện & Điều hướng (`routes/`, `templates/`, `static/`)**: Giao diện trực quan hiện đại, các form cập nhật, bảng biểu và thanh tiến độ.
    5. **Entrypoint (`app.py`)**: Tích hợp toàn diện các Blueprint và khởi chạy ứng dụng Flask.

---

## 📌 Giai đoạn 5: Kiểm Thử, Code Review & Security Review

### 🧑‍💻 Task 06: Kiểm thử tự động hệ thống (Bước 15)
- **Người giao (Tôi)**:
  > "Hãy sử dụng `testing` skill.  
  > Kiểm thử hệ thống quản lý xưởng sản xuất nhỏ hiện tại.  
  > Đọc docs/requirements.md, docs/user-stories.md, docs/acceptance-criteria.md.  
  > Hãy:  
  > 1. Xây dựng test scenarios và test cases.  
  > 2. Tạo unit tests và integration tests trong tests/.  
  > 3. Chạy toàn bộ tests bằng pytest tests/ -v.  
  > 4. Kiểm tra: số lượng âm/0, đơn thiếu vật tư, cập nhật tiến độ vượt công đoạn trước hoặc vượt đơn hàng.  
  > 5. Kiểm tra nhân viên gọi API của quản trị viên (RBAC).  
  > 6. Đối chiếu tỷ lệ lỗi theo BR-06 và xử lý mẫu số = 0.  
  > Chưa chạy test thì ghi NOT RUN, không ghi PASS giả mạo. Tạo docs/test-plan.md và docs/test-report.md."

- **AI Agent (Codex)**:
  - *Skill kích hoạt*: `testing`
  - *Báo cáo thực thi*:
    - Xây dựng 20 ca kiểm thử phân bổ trong 4 tệp: `test_auth.py`, `test_inventory.py`, `test_production.py`, `test_statistics.py`.
    - Chạy thực tế bằng lệnh `pytest tests/ -v`.
    - **Kết quả thực tế**: `20 passed in 0.74s` (100% PASS).
    - Tạo `docs/test-plan.md` và `docs/test-report.md` trích xuất đầy đủ terminal log.

---

### 🧑‍💻 Task 07: Đánh giá chất lượng mã nguồn - Code Review (Bước 17)
- **Người giao (Tôi)**:
  > "Hãy sử dụng `code-review` skill. Review toàn bộ implementation hiện tại. Không sửa code.  
  > Kiểm tra: correctness, requirements compliance, architecture compliance, error handling, database access, security risks.  
  > Phân loại: CRITICAL, HIGH, MEDIUM, LOW. Tạo docs/code-review.md."

- **AI Agent (Codex)**:
  - *Skill kích hoạt*: `code-review`
  - *Báo cáo thực thi*:
    - CRITICAL: 0 lỗi.
    - HIGH: Đã rà soát và khắc phục logic kiểm tra quyền trong `@role_required` tại `services/auth_service.py`.
    - Tạo `docs/code-review.md` với khuyến nghị phân trang dữ liệu lớn.

---

### 🧑‍💻 Task 08: Kiểm toán an ninh - Security Review (Bước 19)
- **Người giao (Tôi)**:
  > "Hãy sử dụng `security-review` skill. Kiểm tra toàn bộ hệ thống về: SQL Injection, XSS, CSRF, Authentication, Authorization, Secrets, AI data leakage. Không sửa code. Tạo docs/security-review.md."

- **AI Agent (Codex)**:
  - *Skill kích hoạt*: `security-review`
  - *Báo cáo thực thi*:
    - Xác nhận 100% truy vấn dùng SQL tham số hóa (ngăn ngừa SQL Injection).
    - Thoát HTML `html.escape` và Jinja2 auto-escaping (ngăn ngừa XSS).
    - Phân quyền RBAC tại server.
    - Mật khẩu băm chuẩn an toàn `pbkdf2:sha256`.
    - Tạo `docs/security-review.md`.

---

## 📌 Giai đoạn 6: Triển Khai Trợ Lý AI Sản Xuất (Production AI Assistant)

### 🧑‍💻 Task 09: Tích hợp Trợ lý AI và Pipeline kiểm chứng 7 bước (Phần XXIII)
- **Người giao (Tôi)**:
  > "Hãy triển khai 3 chức năng AI cho xưởng sản xuất: Tóm tắt tiến độ (FR-15), Phân tích mô tả lỗi (FR-16) và Gợi ý ưu tiên đơn (FR-17).  
  > Triển khai đầy đủ pipeline:  
  > 1. Request Analyzer skill & intermediate representation JSON.  
  > 2. Data Retrieval skill & parameterized queries lấy snapshot.  
  > 3. Context Builder skill & compact structured facts kèm source_ids.  
  > 4. Prompt Builder skill với Grounding Rules nghiêm ngặt.  
  > 5. Gemini Service an toàn, bảo vệ API key, có mock engine cho test nội bộ.  
  > 6. Response Validator đối chiếu số liệu phản hồi với facts CSDL.  
  > 7. Xây dựng giao diện templates/production_ai.html, static/production_ai.css, static/production_ai.js và 3 API endpoints.  
  > Viết unit test tự động tests/test_ai_service.py và chạy pytest."

- **AI Agent (Codex)**:
  - *Skill kích hoạt*: `production-request-analysis`, `production-data-retrieval`, `context-builder`, `production-ai-prompt`
  - *Báo cáo thực thi*:
    - Xây dựng 4 Skills chuyên biệt cho từng khâu trong quy trình chuẩn bị dữ liệu AI.
    - `services/gemini_service.py`: Tích hợp Google Gemini SDK, bảo vệ API key từ biến môi trường, cơ chế offline fallback cho test tự động.
    - `services/production_ai_service.py`: Điều phối 7 bước xử lý có kiểm soát ranh giới an toàn.
    - `routes/ai_routes.py`: 3 REST endpoints (`/api/ai/progress-summary`, `/api/ai/defect-analysis`, `/api/ai/order-priority`).
    - Giao diện Web Trợ lý AI hiện đại: 3 tab chế độ, hiển thị Facts xác minh, giả thuyết kỹ thuật và nút Human Gate phê chuẩn kế hoạch.
    - `tests/test_ai_service.py`: 10 ca kiểm thử cho Request Analyzer, Retrieval, Grounding Prompt, Validator, và các Endpoint. Chạy `pytest tests/ -v` đạt 30/30 test cases PASS.

---

## 📌 Giai đoạn 7: MCP, Soạn Thảo Tài Liệu & Nghiệm Thu (Documentation & Final Gate)

### 🧑‍💻 Task 10: Xây dựng tài liệu hoàn chỉnh & Tích hợp MCP (Bước 20, Phần XXIV - XXX)
- **Người giao (Tôi)**:
  > "Hãy sử dụng `documentation` skill. Đọc toàn bộ project hiện tại.  
  > Cập nhật và hoàn thiện:  
  > - README.md  
  > - docs/api.md  
  > - docs/deployment.md  
  > - docs/user-guide.md  
  > - docs/presentation-outline.md  
  > - docs/ai-evaluation.md  
  > - docs/mcp-integration.md  
  > - docs/human-verification.md (hoàn thiện Gate 3)  
  > Đảm bảo tài liệu phản ánh chính xác 100% implementation, không mô tả tính năng chưa có.  
  > Kiểm tra tính đầy đủ của 15 skills, cấu trúc thư mục và git history."

- **AI Agent (Codex)**:
  - *Skill kích hoạt*: `documentation`
  - *Báo cáo thực thi*:
    1. Đã hoàn thiện toàn bộ tài liệu dự án trong `docs/` và `README.md`.
    2. Tài liệu hóa mô hình MCP qua kịch bản tự động xử lý GitHub Issue #25 (`docs/mcp-integration.md`).
    3. Hoàn thiện đánh giá năng lực AI và các ranh giới kiểm soát con người (`docs/ai-evaluation.md`).
    4. Đối chiếu thư mục đầu ra: Khớp chính xác 100% danh mục tại Phần XXVI trong đề bài (15 Skills, 11 bảng CSDL, 30 ca test, đầy đủ giao diện, tài liệu, sơ đồ PlantUML).
    5. Đã được con người kiểm tra và ký phê chuẩn tại **Human Gate 3**. Toàn bộ bài thực hành đã hoàn thành trọn vẹn!






