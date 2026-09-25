# HỆ THỐNG QUẢN LÝ XƯỞNG SẢN XUẤT NHỎ CÓ TÍCH HỢP AI (AI WORKSHOP SYSTEM)
> **Dự án thực hành AI-Augmented Software Development Life Cycle (SDLC) - Đề tài 25 theo URD**

[![Python 3.12](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Flask 3.0](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![MySQL 8.0+](https://img.shields.io/badge/Database-MySQL%20%2F%20SQLite-orange.svg)]()
[![AI-Augmented SDLC](https://img.shields.io/badge/AI--Augmented-SDLC%20with%20Codex-purple.svg)]()

---

## 📖 1. Giới Thiệu Dự Án
Dự án được xây dựng dựa trên yêu cầu của đề tài **"Hệ thống Quản lý Xưởng Sản xuất Nhỏ có Tích hợp AI"** (Đề tài 25) và tài liệu URD `Detai25.1.docx`. 

Điểm cốt lõi của bài thực hành không phải là dùng AI như một công cụ sinh code thông thường, mà **tổ chức Codex thành một AI Agent** thực hiện các quy trình SDLC có kiểm soát thông qua:
1. **15 Skills chuyên biệt** được quản lý theo chuẩn Antigravity/Codex tại `.agents/skills/`.
2. **Tools & Terminal**: Thực thi lệnh, linting, kiểm thử tự động `pytest`.
3. **MCP (Model Context Protocol)**: Mô hình hóa tích hợp luồng xử lý issue tracker ngoài.
4. **Các điểm kiểm soát của con người (Human Gates 1, 2, 3)**: Kiểm chứng độc lập các artifact do AI sinh ra trước khi chuyển giai đoạn.

---

## 👥 2. Các Tác Nhân Hệ Thống (URD Actors)
- **Quản trị viên (Admin)**: Duyệt đăng ký, cấp vai trò, khóa và quản lý tài khoản. Không truy cập dữ liệu sản xuất hoặc kho.
- **Quản lý xưởng (Manager)**: Quản lý sản phẩm/BOM, công đoạn, đơn/kế hoạch, kho và thành viên tổ; duyệt phiếu vật tư đã dùng, xem thống kê và báo cáo cuối ngày.
- **Tổ trưởng (Team Leader)**: Xem tồn kho, điều phối nhân viên trong tổ trên các đơn được giao, cập nhật tiến độ/lỗi và gửi báo cáo cuối ngày.
- **Nhân viên (Worker)**: Làm công đoạn được giao, cập nhật tiến độ/lỗi và báo lượng vật tư đã dùng; không truy cập kho hoặc tự trừ tồn.
- **Trợ lý AI (External Gemini)**: Tóm tắt tiến độ, phân tích mô tả lỗi, gợi ý thứ tự ưu tiên đơn. AI **không có quyền trực tiếp cập nhật CSDL**.

---

## 🏗️ 3. Cấu Trúc Dự Án Hoàn Chỉnh

```
AI_Workshop_System/
├── .agents/skills/                  # 15 Skills chuẩn hóa
│   ├── diagram-design/              # Vẽ và chuẩn hóa sơ đồ
│   ├── uml-diagrams/                # Sơ đồ UML (Use Case, Activity, Sequence, Class)
│   ├── erd-design/                  # Sơ đồ thực thể quan hệ ERD
│   ├── requirements-analysis/       # Kỹ thuật phân tích yêu cầu (FR, NFR, BR)
│   ├── architecture-design/         # Thiết kế kiến trúc phân tầng & ADR
│   ├── database-design/             # Thiết kế CSDL 3NF 11 bảng
│   ├── implementation/              # Quy chuẩn lập trình an toàn
│   ├── testing/                     # Thiết kế & thực thi kiểm thử tự động
│   ├── code-review/                 # Đánh giá mã nguồn (CRITICAL/HIGH/MED/LOW)
│   ├── security-review/             # Kiểm toán an ninh OWASP
│   ├── production-request-analysis/ # Chuẩn hóa intent AI
│   ├── production-data-retrieval/   # Truy xuất snapshot CSDL an toàn
│   ├── context-builder/             # Đóng gói facts và source_ids
│   ├── production-ai-prompt/        # Prompt engineering chống ảo giác
│   └── documentation/               # Soạn thảo tài liệu chuẩn xác
├── docs/
│   ├── customer-requirement.md      # Yêu cầu gốc từ xưởng
│   ├── requirements.md              # Đặc tả FR-01 -> FR-17, NFR-01 -> NFR-11, BR-01 -> BR-09
│   ├── user-stories.md              # 16 user stories chuẩn
│   ├── acceptance-criteria.md       # Tiêu chí nghiệm thu Given-When-Then
│   ├── requirements-issues.md       # Báo cáo xử lý thiếu MaDon trong tiến độ
│   ├── use-cases.md                 # 13 ca sử dụng UC001 -> UC013
│   ├── architecture.md              # Kiến trúc phân tầng 6 layer
│   ├── architecture-decisions.md    # 5 quyết định kiến trúc ADR-01 -> ADR-05
│   ├── database-design.md           # Thuyết minh chuẩn hóa và các bảng bổ sung
│   ├── data-dictionary.md           # Từ điển dữ liệu
│   ├── diagrams/                    # Các file mã nguồn PlantUML (.puml)
│   │   ├── use-case.puml
│   │   ├── architecture.puml
│   │   ├── production-activity.puml
│   │   ├── progress-sequence.puml
│   │   ├── domain-class.puml
│   │   ├── erd.puml
│   │   └── production-ai-flow.puml
│   ├── diagram-traceability.md      # Ma trận truy vết sơ đồ
│   ├── diagram-review.md            # Báo cáo đánh giá chất lượng sơ đồ
│   ├── production-ai-requirements.md# Đặc tả trợ lý AI
│   ├── production-ai-functional-requirements.md # Phân rã FR-AI-001 -> 007
│   ├── production-ai-user-stories.md
│   ├── production-ai-acceptance-criteria.md
│   ├── production-ai-requirements-issues.md
│   ├── production-ai-architecture.md
│   ├── production-ai-data-flow.md
│   ├── production-request-analysis.md
│   ├── ai-task-log.md               # Nhật ký đối thoại đóng giả Tôi & Codex
│   ├── ai-evaluation.md             # Đánh giá năng lực của AI trong SDLC
│   ├── human-verification.md        # Biên bản Human Gate 1, 2, 3
│   ├── test-plan.md                 # Kế hoạch kiểm thử
│   ├── test-report.md               # Kết quả kiểm thử mới nhất
│   ├── urd-change-decisions.md      # Các quyết định bổ sung so với URD
│   ├── code-review.md               # Báo cáo Code Review
│   ├── security-review.md           # Báo cáo Security Review
│   ├── api.md                       # Tài liệu API endpoints
│   ├── deployment.md                # Hướng dẫn triển khai
│   ├── user-guide.md                # Sách hướng dẫn sử dụng 4 vai trò
│   ├── presentation-outline.md      # Dàn ý thuyết trình bảo vệ
│   └── mcp-integration.md           # Tài liệu tích hợp MCP
├── database/
│   ├── schema.sql                   # 11 bảng URD và các bảng cho quyết định bổ sung
│   ├── migrate_sqlite_codes.py      # Sao lưu và đổi mã số cũ sang mã chuỗi
│   ├── seed_data.sql                # Dữ liệu mẫu xưởng cơ khí
│   └── db.py                        # Database connection pool & transactions
├── models/                          # Data Models (TaiKhoan, SanPham, Don, ...)
├── routes/                          # Flask Blueprints (auth, workshop, api, ai)
├── services/                        # Business Logic & Production AI Service
├── templates/                       # Web UI HTML5 Jinja2 Templates
├── static/                          # CSS & Vanilla JS
├── tests/                           # Kiểm thử tự động pytest
├── app.py                           # Flask Application Entrypoint
├── requirements.txt
└── README.md
```

---

## 🚀 4. Hướng Dẫn Cài Đặt & Chạy Ứng Dụng

### Bước 1: Kích hoạt môi trường Python
```bash
# Tạo môi trường ảo (nếu chưa có)
python -m venv venv

# Kích hoạt môi trường (Windows PowerShell)
venv\Scripts\Activate.ps1

# Cài đặt thư viện
pip install -r requirements.txt
```

### Bước 2: Chạy ứng dụng Flask
```bash
python app.py
```
Ứng dụng khởi tạo CSDL SQLite mới với dữ liệu demo tại `http://localhost:5000`. Nếu đã có CSDL SQLite dùng khóa số, chạy công cụ chuyển dữ liệu trong [hướng dẫn triển khai](docs/deployment.md) trước khi mở web.

---

## 🔑 5. Tài Khoản Thử Nghiệm Mặc Định (Mật khẩu: `123456`)

| Vai Trò | Email Đăng Nhập | Quyền Hạn Chính |
|---|---|---|
| **Quản trị viên** | `admin@workshop.edu.vn` | Chỉ quản lý và duyệt tài khoản |
| **Quản lý xưởng** | `manager@workshop.edu.vn` | Tạo sản phẩm/đơn, nhập và ghi dùng vật tư, báo cáo, thống kê, AI |
| **Tổ trưởng** | `leader@workshop.edu.vn` | Xem kho, công đoạn được giao, báo cáo cuối ngày, AI có phạm vi |
| **Nhân viên** | `worker@workshop.edu.vn` | Công đoạn được giao; không truy cập kho |

Người tự đăng ký có trạng thái **Chờ duyệt** và chưa có vai trò. Admin chọn một trong ba vai trò nghiệp vụ để kích hoạt tài khoản. Các danh sách tài khoản, sản phẩm, đơn, kho và báo cáo cuối ngày có tìm kiếm và bộ lọc; kết quả của Tổ trưởng và Nhân viên vẫn giới hạn theo phân công.

---

## 🧪 6. Chạy Kiểm Thử Tự Động (Automated Testing)
Hệ thống cung cấp bộ kiểm thử tự động toàn diện bao quát xác thực, ràng buộc tuần tự tiến độ, trừ kho vật tư, tỷ lệ lỗi và Trợ lý AI:

```bash
pytest tests/ -v
```
Kiểm thử dùng CSDL riêng, không đặt lại dữ liệu của web đang chạy. Xem lần chạy mới nhất trong `docs/test-report.md`.

---

## 🤖 7. Điểm Sáng Trợ Lý AI Sản Xuất (Phần XXIII)
- **Tóm tắt tiến độ đơn (FR-15)**: Tự động trích xuất snapshot và giải thích tình trạng đơn hàng.
- **Phân tích mô tả lỗi (FR-16)**: Phân cụm các mô tả lỗi và đưa ra giả thuyết nguyên nhân kỹ thuật.
- **Gợi ý ưu tiên đơn (FR-17)**: Phân tích hạn giao, tiến độ và tồn kho nguyên liệu để đề xuất thứ tự ưu tiên; Quản lý xưởng mở đơn và tự sửa kế hoạch sau khi xem gợi ý.
- **Kiểm tra đầu ra AI**: Hệ thống đối chiếu mã đơn, nguồn và các số liệu có cấu trúc với snapshot CSDL; kết quả không khớp được đánh dấu cần kiểm tra. AI không có quyền ghi CSDL. Khi chưa có kết nối Gemini, giao diện cho biết đang dùng quy tắc cục bộ.
