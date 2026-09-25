---
name: security-review
description: Audit software implementation for security vulnerabilities, injection flaws, access control breaches, and data leakage.
---

# Security Review Skill

## Objective
Kiểm toán bảo mật toàn bộ hệ thống phần mềm, đặc biệt chú trọng các khía cạnh an ninh web và an toàn tích hợp mô hình AI.

## Security Checklist
1. SQL Injection: Kiểm tra 100% các câu truy vấn cơ sở dữ liệu có sử dụng tham số (%s / ?) thay vì cộng chuỗi.
2. Cross-Site Scripting (XSS): Kiểm tra việc thoát ký tự HTML đặc biệt trong các trường nhập tự do (mô tả lỗi, ghi chú).
3. CSRF & Session Security: Kiểm tra cờ HttpOnly, SameSite của cookie phiên.
4. Authentication & Password Storage: Đảm bảo mật khẩu lưu dạng băm an toàn (PBKDF2/scrypt/bcrypt), không lưu plain-text.
5. Authorization (RBAC): Kiểm tra quyền hạn tại backend cho từng endpoint, không phụ thuộc vào ẩn hiện giao diện client.
6. Secrets & Environment Variables: Đảm bảo khóa bí mật (SECRET_KEY, GEMINI_API_KEY) lưu trong .env và không bị commit vào Git.
7. AI Data Leakage & Prompt Injection: Đảm bảo chỉ gửi snapshot kỹ thuật cần thiết, không gửi thông tin nhạy cảm của người dùng sang dịch vụ AI bên ngoài; kiểm tra xử lý dữ liệu độc hại trong prompt.

## Output
- docs/security-review.md
