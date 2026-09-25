# Đặc Tả Module Phân Tích Yêu Cầu (Production Request Analysis Specification)

---

## 1. Định Dạng Cấu Trúc Ý Định (Structured Intent Schema)

```json
{
    "task_type": "progress_summary | defect_analysis | order_priority",
    "order_ids": [25],
    "date_from": "2026-09-01",
    "date_to": "2026-09-30",
    "include_materials": true,
    "max_suggestions": 3,
    "user_role": "QuanLyXuong",
    "keywords": ["tiến độ", "Đơn 25"]
}
```

## 2. Quy Tắc Ánh Xạ
- Yêu cầu chứa "tiến độ", "tóm tắt đơn" -> `task_type = "progress_summary"`.
- Yêu cầu chứa "lỗi", "hỏng", "nguyên nhân" -> `task_type = "defect_analysis"`.
- Yêu cầu chứa "ưu tiên", "gợi ý đơn", "kế hoạch" -> `task_type = "order_priority"`.
- Trích xuất số nguyên trong câu (ví dụ: "Đơn 25") vào `order_ids = [25]`.
