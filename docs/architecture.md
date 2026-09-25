# Thiết Kế Kiến Trúc Hệ Thống (System Architecture Document)

Dự án: Hệ thống Quản lý Xưởng Sản xuất Nhỏ có Tích hợp AI (AI_Workshop_System)  
Nguồn tham chiếu: `docs/requirements.md`, `docs/user-stories.md`, `docs/acceptance-criteria.md`

---

## 1. Phong Cách Kiến Trúc (Architectural Style)

Hệ thống được thiết kế theo phong cách **Kiến trúc Phân tầng (Layered Architecture)** kết hợp với **Adapter Pattern** cho việc tích hợp AI ngoài:
1. **Presentation Layer (Tầng hiển thị)**: Giao diện Web HTML5/CSS/JavaScript (Vanilla CSS, Responsive UI), tương tác thông qua các biểu mẫu form và Fetch API (JSON).
2. **Routing & Controller Layer (Tầng điều hướng)**: Flask Blueprints tiếp nhận HTTP requests, kiểm tra xác thực phiên (Session), phân quyền vai trò (RBAC) và gọi tầng Service.
3. **Business Service Layer (Tầng nghiệp vụ cốt lõi)**: Chứa toàn bộ các logic kiểm tra trạng thái (BR-01, BR-02), kiểm soát sản lượng công đoạn (BR-03), kiểm tra định mức BOM (BR-04) và tính toán tỷ lệ lỗi (BR-06).
4. **Data Access Layer (Tầng truy cập dữ liệu)**: Thực thi các câu lệnh SQL tham số hóa (Parameterized Queries) nhằm ngăn chặn triệt để SQL Injection, hỗ trợ Database Transactions để đảm bảo tính nguyên tử (Atomicity).
5. **Database Layer (Tầng lưu trữ CSDL)**: Hệ CSDL quan hệ (MySQL cho môi trường chính thức, hỗ trợ SQLite tương thích cho môi trường kiểm thử tự động độc lập).
6. **External AI Integration Layer (Tầng tích hợp AI bên ngoài)**: Cô lập dịch vụ AI (Gemini) bằng các lớp: `Request Analyzer` -> `Data Retrieval` -> `Context Builder` -> `Prompt Builder` -> `Gemini Adapter` -> `Response Validator`. **Gemini tuyệt đối không truy cập trực tiếp CSDL.**

---

## 2. Các Thành Phần Chính & Trách Nhiệm

```
[ Người Dùng (Admin / Manager / Leader / Worker) ]
                      │ HTTP (Browser)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│      Templates (Jinja2)  │  Static (CSS, Vanilla JS)        │
└─────────────────────────────┬───────────────────────────────┘
                              │ JSON / Form Data
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Routing & Controller Layer                 │
│  - auth_routes       - workshop_routes       - ai_routes    │
│  [ RBAC Guard: Session & Role-Based Access Control ]        │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Business Service Layer                   │
│  ├── AuthService        : Xác thực, băm mật khẩu, phân quyền│
│  ├── ProductService     : Quản lý sản phẩm, định mức BOM    │
│  ├── OrderService       : Quản lý đơn sản xuất & kế hoạch   │
│  ├── ProductionService  : Công đoạn, phân công, tiến độ     │
│  │                        sử dụng vật tư, ghi nhận lỗi      │
│  ├── StatisticsService  : Tiến độ %, năng suất, tỷ lệ lỗi   │
│  └── ProductionAIService: Điều phối quy trình trợ lý AI     │
│       ├── RequestAnalyzer                                   │
│       ├── ProductionDataRetriever                           │
│       ├── ContextBuilder                                    │
│       ├── PromptBuilder                                     │
│       └── ResponseValidator                                 │
└───────────────────────┬───────────────────────────┬─────────┘
                        │                           │
                        ▼                           ▼
┌───────────────────────────────┐     ┌───────────────────────┐
│     Data Access Layer (DAO)   │     │ Gemini Service Adapter│
│  - Parameterized Queries      │     │ - Timeout Handling    │
│  - Transaction Management     │     │ - Mock Fallback       │
│  - Connection Pool            │     └───────────┬───────────┘
└───────────────┬───────────────┘                 │ HTTPS
                │ SQL                             ▼
                ▼                     ┌───────────────────────┐
┌───────────────────────────────┐     │  Google Gemini API    │
│      MySQL / SQLite CSDL      │     │  (External AI Cloud)  │
│  (11 bảng dữ liệu URD)        │     └───────────────────────┘
└───────────────────────────────┘
```

---

## 3. Ma Trận Ánh Xạ Requirements -> Architecture Component (Traceability)

| Yêu Cầu (FR) | Thành phần Kiến trúc Đảm nhiệm | Tầng Kiến trúc | Ranh giới Kiểm soát An toàn |
|---|---|---|---|
| **FR-01, FR-02** | `auth_routes`, `AuthService`, `TaiKhoan` DAO | Auth & Security | Băm mật khẩu, Session Cookie HttpOnly |
| **FR-03, FR-04** | `ProductService`, `SanPham` & `DinhMuc` DAO | Core Business | Kiểm tra ràng buộc định mức > 0 |
| **FR-05, FR-06** | `OrderService`, `DonSanXuat` & `KeHoach` DAO | Core Business | Chuyển trạng thái đơn BR-01 |
| **FR-07, FR-08** | `ProductionService`, `CongDoan` & `PhanCong` DAO | Core Business | Kiểm tra phân quyền theo vai trò |
| **FR-09** | `ProductionService`, `TienDoCongDoan` DAO | Core Business | Transaction; Kiểm tra thứ tự công đoạn |
| **FR-10** | `ProductionService`, `LoiSanXuat` DAO | Core Business | Thoát HTML mô tả lỗi (XSS protection) |
| **FR-11** | `ProductionService`, `SuDungNguyenLieu` DAO | Core Business | Trừ kho hoặc đối chiếu định mức BOM |
| **FR-12, 13, 14**| `StatisticsService` | Analytics | Tính toán công thức BR-06, xử lý mẫu số 0 |
| **FR-15, 16, 17**| `ProductionAIService`, `GeminiService` | AI Integration | Snapshot dữ liệu, schema validation, không cấp quyền sửa CSDL |

---

## 4. Ranh Giới Bảo Mật & Luồng Dữ Liệu AI (Security Boundaries)

1. **Ranh giới nội bộ (Trust Boundary)**: Client kết nối qua HTTPS; chỉ các request đã xác thực (Authenticated) và có Role phù hợp mới được chuyển đến Service.
2. **Ranh giới AI (External Boundary)**:
   - Client không gọi trực tiếp Gemini API.
   - API key của Gemini chỉ lưu ở biến môi trường backend (`.env`), không trả về client.
   - Dữ liệu gửi đến Gemini chỉ là snapshot văn bản/số liệu kỹ thuật cần thiết, không gửi mật khẩu, thông tin cá nhân.
   - Kết quả phản hồi từ Gemini phải đi qua `ResponseValidator` trước khi trả về người dùng dưới dạng bản nháp/gợi ý.
