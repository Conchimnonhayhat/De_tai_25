# Kiến Trúc Trợ Lý AI Sản Xuất (Production AI Architecture)

Thiết kế kiến trúc tích hợp an toàn theo quy chuẩn AI-Augmented SDLC.

---

## 1. Luồng Xử Lý 7 Bước (The 7-Step Controlled AI Pipeline)

```
[ User Request via Web UI ]
           │
           ▼
[ 1. Production AI API (Role & Auth Check) ]
           │
           ▼
[ 2. Request Analyzer ] ────► Tạo Validated Structured Intent
           │
           ▼
[ 3. Production Data Retriever ] ───► Parameterized SQL ───► [ MySQL / CSDL ]
           │                                                        │
           ▼                                                        ▼
[ 4. Context Builder ] ◄──────────────────────────────── Snapshot Dữ Liệu
           │ (Đóng gói Compact Context & source_ids)
           ▼
[ 5. Prompt Builder ]
           │ (Grounding Rules + Context + Format JSON Schema)
           ▼
[ 6. Gemini Service Adapter ] ────► HTTPS ────► [ Google Gemini API ]
           │                                            │
           ▼ ◄──────────────────────────────────────────┘
[ 7. Response Validator ] (Đối chiếu Facts & Schema)
           │
           ▼
[ Human Review Staging Area on Web UI ] ───► Quản lý xưởng bấm Áp dụng
```

---

## 2. Chi Tiết Trách Nhiệm Từng Module

1. **Request Analyzer**: Chuẩn hóa input tự nhiên hoặc các bộ lọc form thành `Structured Intent` có cấu trúc:
   ```json
   {
       "task_type": "progress_summary",
       "order_ids": [25],
       "date_from": null,
       "date_to": null,
       "max_suggestions": 3
   }
   ```
2. **Production Data Retriever**: Sử dụng SQL có tham số để trích xuất chính xác các bản ghi trong phạm vi quyền hạn.
3. **Context Builder**: Làm sạch dữ liệu, tính toán các facts định lượng (tổng số lượng, tỷ lệ %, số lượng thiếu hụt), gắn mã nguồn `source_ids`.
4. **Prompt Builder**: Xây dựng system prompt hướng dẫn Gemini đóng vai trợ lý quản lý xưởng, áp đặt quy tắc nghiêm cấm bịa đặt số liệu.
5. **Gemini Service**: Đảm nhiệm kết nối mạng qua HTTPS, kiểm soát timeout và bảo mật API key.
6. **Response Validator**: Kiểm tra JSON trả về từ Gemini, so sánh các số liệu trong câu trả lời với facts gốc từ CSDL. Nếu có sai lệch, đánh dấu `needs_review`.
