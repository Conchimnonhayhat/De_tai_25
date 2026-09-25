---
name: code-review
description: Review codebase for correctness, architecture compliance, security risks, maintainability, and error handling.
---

# Code Review Skill

## Objective
Thực hiện đánh giá toàn diện mã nguồn theo các tiêu chuẩn kỹ thuật phần mềm, phân loại rủi ro và lập báo cáo tài liệu.

## Review Dimensions
1. Correctness: Logic nghiệp vụ, kiểm tra ràng buộc số lượng, kiểm tra thứ tự công đoạn.
2. Requirements Compliance: Tuân thủ đầy đủ FR-01 đến FR-17 và BR-01 đến BR-09.
3. Architecture Compliance: Tuân thủ kiến trúc phân tầng, phân tách ranh giới rõ ràng.
4. Error Handling: Bắt lỗi ngoại lệ, phản hồi mã HTTP phù hợp.
5. Database Access: SQL tham số hóa, quản lý transaction.
6. Test Quality: Độ bao phủ của các ca kiểm thử.
7. Security Risks: SQL Injection, XSS, CSRF, Password hashing.

## Severity Classification
- CRITICAL: Lỗ hổng bảo mật nghiêm trọng hoặc lỗi tính toán sai lệch dữ liệu tài sản.
- HIGH: Lỗi vi phạm nghiệp vụ cốt lõi hoặc thiếu kiểm tra quyền ở các API quan trọng.
- MEDIUM: Vấn đề hiệu năng, trùng lặp mã nguồn hoặc thiếu kiểm tra dữ liệu đầu vào không nghiêm trọng.
- LOW: Thẩm mỹ mã nguồn, đặt tên biến, comment tài liệu.

## Output
- docs/code-review.md
