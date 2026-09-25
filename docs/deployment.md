# Triển khai và chuyển dữ liệu

## Chạy tại máy phát triển

1. Cài các gói trong `requirements.txt` vào môi trường Python của dự án.
2. Tạo `SECRET_KEY` riêng bằng `python -c "import secrets; print(secrets.token_hex(32))"` và đặt vào `.env`. Không dùng khóa mẫu cố định.
3. Để `USE_MYSQL=false` nếu dùng SQLite tại `instance/workshop.db`, rồi chạy `python app.py`. Chế độ debug mặc định tắt; chỉ bật `FLASK_DEBUG=1` ở máy phát triển.
4. Tài khoản mẫu trong `database/seed_data.sql` chỉ dành cho dữ liệu demo. Đổi mật khẩu trước khi đưa ứng dụng cho người khác sử dụng.

Các biểu mẫu POST dùng mã CSRF của phiên đăng nhập. Giao diện AI gửi cùng mã trong header `X-CSRF-Token`. Nếu báo biểu mẫu hết hạn, tải lại trang rồi gửi lại.

## Chuyển CSDL SQLite cũ sang mã chữ-số

Dừng web trước khi chuyển. Từ thư mục gốc dự án, chạy:

```powershell
python database/migrate_sqlite_codes.py
python database/migrate_sqlite_codes.py --apply
```

Lệnh đầu chỉ liệt kê số bản ghi sẽ chuyển. Lệnh thứ hai tự tạo file `instance/workshop.backup-<thời-điểm>.db`, chuyển toàn bộ mã `Ma...` sang `VARCHAR(32)` và kiểm tra số bản ghi, tính toàn vẹn cùng khóa ngoại trước khi thay CSDL cũ. Mã số cũ được giữ nguyên nội dung dưới dạng chuỗi để các liên kết vẫn đúng. Muốn khôi phục, dừng web rồi chép file sao lưu về `instance/workshop.db`.

Không dùng `init_db(force=True)` trên CSDL có dữ liệu thật. Ứng dụng không tự chuyển kiểu khóa trên CSDL cũ; nếu chưa chuyển, nó sẽ báo lỗi rõ ràng khi khởi động.

## MySQL

Đặt `USE_MYSQL=true` cùng `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` trong `.env`. Kết nối lỗi sẽ dừng khởi động; ứng dụng không ghi âm thầm sang SQLite. Schema mới ở `database/schema.sql` dùng mã chuỗi và được tạo khi ứng dụng khởi động. Dữ liệu demo có thể nạp riêng từ `database/seed_data.sql` vào CSDL thử nghiệm.

Máy có dịch vụ MySQL80 đang chạy, nhưng dự án chưa có `.env` hay thông tin CSDL thử nghiệm; vì vậy đường triển khai và chuyển dữ liệu **MySQL cũ** chưa được xác minh. Không chạy trực tiếp schema mới lên CSDL MySQL đang chứa khóa số; cần sao lưu và lập migration riêng cho các khóa ngoại trước.

## Máy chủ web

Khi chạy cho người dùng khác, cấu hình `SECRET_KEY`, HTTPS, quyền CSDL tối thiểu và máy chủ WSGI phù hợp. Ví dụ trên Windows sau khi cài Waitress:

```powershell
waitress-serve --host=127.0.0.1 --port=5000 app:create_app
```
