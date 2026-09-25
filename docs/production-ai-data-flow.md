# Luồng Dữ Liệu Chi Tiết Của Trợ Lý AI (Production AI Data Flow)

---

## 1. Luồng Tóm Tắt Tiến Độ (Progress Summary Data Flow)
1. **Input**: `POST /api/ai/progress-summary` với `{"order_ids": [25]}`.
2. **Intent**: `task_type: "progress_summary", order_ids: [25]`.
3. **Database Snapshot**:
   - `DonSanXuat(MaDon=25, SoLuongYeuCau=100, HanGiao=2026-09-30, TrangThai='Đang thực hiện')`.
   - `TienDoCongDoan`: Công đoạn 101 đạt 80, 102 đạt 75, 103 đạt 70, 104 đạt 60.
4. **Facts**:
   - `requested_quantity: 100`
   - `final_completed_quantity: 60`
   - `progress_percent: 60.0%`
   - `source_ids: ["DonSanXuat:25", "TienDoCongDoan:1", "TienDoCongDoan:2", "TienDoCongDoan:3", "TienDoCongDoan:4"]`
5. **AI Inference & Validation**: Gemini sinh bản tóm tắt diễn giải; Validator đối chiếu 60/100 khớp hoàn toàn snapshot.
6. **Output**: Hiển thị trên giao diện người dùng.

---

## 2. Luồng Phân Tích Lỗi (Defect Analysis Data Flow)
1. **Input**: `POST /api/ai/defect-analysis` với `{"order_ids": [25]}`.
2. **Database Snapshot**:
   - `LoiSanXuat(MaLoi=1, MoTaLoi="Vết xước kim loại...", SoLuongHong=2)`.
   - `LoiSanXuat(MaLoi=2, MoTaLoi="Bề mặt trầy xước nhẹ...", SoLuongHong=3)`.
3. **Facts & Context**:
   - `total_defective: 5`
   - `defect_records: [{"id": 1, "desc": "..."}, {"id": 2, "desc": "..."}]`
4. **AI Inference**: Gom 2 lỗi vào nhóm "Khuyết tật bề mặt/xước cơ học", đề xuất kiểm tra đồ gá dao cắt.
5. **Validation**: Kiểm tra source_ids `["LoiSanXuat:1", "LoiSanXuat:2"]`, đảm bảo các giả thuyết được dán nhãn `Giả thuyết cần xác minh`.

---

## 3. Luồng Gợi Ý Ưu Tiên Đơn (Order Priority Data Flow)
1. **Input**: `POST /api/ai/order-priority` với `{"max_suggestions": 3}`.
2. **Database Snapshot**: Toàn bộ các đơn hàng chưa hoàn thành, kèm ngày hạn giao và kết quả đối chiếu vật tư theo BOM.
3. **AI Inference**: Xếp hạng các đơn hàng kèm giải thích nguyên nhân.
4. **Validation**: Đảm bảo số lượng gợi ý <= 3 và không có mã đơn hàng giả mạo.
