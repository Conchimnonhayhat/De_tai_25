# Tích Hợp Model Context Protocol (MCP Integration)

Dự án: Hệ thống Quản lý Xưởng Sản xuất Nhỏ (Đề tài 25 theo URD)  
Nguồn tham chiếu: `de_tai_25_theo_URD.md` Phần XXIV

---

## 1. Khái Niệm MCP Trong AI-Augmented SDLC
**MCP (Model Context Protocol)** là giao thức tiêu chuẩn mở cho phép các AI Agent (như Codex/Claude/Antigravity) kết nối bảo mật và trao đổi dữ liệu hai chiều với các hệ thống phần mềm, cơ sở dữ liệu và dịch vụ bên ngoài (External Tools & Context Providers).

Khác biệt giữa 4 thành phần:
- **Codex**: AI Agent thực hiện điều phối và giải quyết bài toán phát triển phần mềm.
- **Skill**: Tri thức thủ tục, quy trình và tiêu chuẩn nghiệp vụ (định nghĩa trong `SKILL.md`).
- **Tool**: Thao tác cục bộ trực tiếp trên môi trường làm việc (chạy shell command, chỉnh sửa file, xem cây thư mục).
- **MCP**: Cầu nối giao tiếp tiêu chuẩn hóa với hệ thống quản lý bên ngoài (GitHub Issues, Jira, MySQL Server, Monitoring Service).

---

## 2. Kịch Bản Tích Hợp MCP Trong Bài Thực Hành: GitHub Issue MCP
Trong quá trình phát triển hệ thống xưởng sản xuất, một vấn đề nghiệp vụ được mở trên hệ thống theo dõi lỗi bên ngoài:

> **Issue #25 (GitHub Issue Tracker)**:  
> *Tiêu đề*: `TienDoCongDoan chỉ lưu MaCongDoan nên không phân biệt tiến độ hai đơn cùng sản xuất một loại sản phẩm; cần quyết định khóa liên kết theo đơn.`

### Quy trình Xử lý Sự cố Tự động qua MCP:
```
[ GitHub Issue #25 ]
         │ (Được phát hiện và kéo về)
         ▼
[ MCP GitHub Server ]
         │ Giao thức JSON-RPC
         ▼
[ Codex AI Agent ]
         │ 1. Đọc và phân tích Issue qua MCP
         │ 2. Kích hoạt 'requirements-analysis' & 'database-design' Skill
         │ 3. Xác định vị trí code cần sửa (schema.sql, db.py, models/production.py)
         │ 4. Đề xuất bổ sung MaDon vào TienDoCongDoan
         │ 5. Thực hiện cập nhật mã nguồn (Fix)
         ▼
[ Automated Testing (Tool: pytest) ]
         │ Chạy 30/30 test cases PASS
         ▼
[ Code Review Skill ]
         │
         ▼
[ Đóng Issue & Tạo Pull Request qua MCP ]
```

---

## 3. Cấu Hình MCP Tham Khảo (`mcp_config.json`)
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxxxxxxxxx"
      }
    },
    "mysql": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-mysql"],
      "env": {
        "MYSQL_CONNECTION_URL": "mysql://root:password@localhost:3306/workshop_db"
      }
    }
  }
}
```

## 4. Kết Luận
Việc áp dụng MCP giúp mở rộng phạm vi của Codex từ một công cụ soạn thảo cục bộ thành một **Tác tử kỹ thuật số (Autonomous Agent)** có thể lắng nghe sự kiện từ bên ngoài, tự động kiểm tra quy trình, thực thi kiểm thử và phản hồi kết quả trực tiếp cho nhóm phát triển.
