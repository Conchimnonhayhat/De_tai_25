"""Business access rules shared by pages, APIs and the AI assistant."""

from database.db import query_db


def visible_order_ids(user):
    if user.role == 'QuanLyXuong':
        return None  # Manager may see every order.
    if user.role not in ('ToTruong', 'NhanVien'):
        return set()
    rows = query_db("SELECT DISTINCT MaDon FROM PhanCong WHERE MaTaiKhoan = %s", (user.id,))
    return {str(row['MaDon']) for row in rows if row['MaDon'] is not None}


def can_view_order(user, order_id):
    allowed = visible_order_ids(user)
    return allowed is None or str(order_id) in allowed


def can_update_operation(user, order_id, operation_id):
    if user.role not in ('ToTruong', 'NhanVien'):
        return False
    if user.role == 'ToTruong':
        return bool(query_db(
            "SELECT 1 AS allowed FROM PhanCong p JOIN TaiKhoan t ON t.MaTaiKhoan = p.MaTaiKhoan "
            "WHERE p.MaDon = %s AND p.MaCongDoan = %s AND p.MaTaiKhoan = %s "
            "AND t.VaiTro = 'ToTruong' AND t.TrangThai = 'Active' LIMIT 1",
            (order_id, operation_id, user.id), one=True
        ))
    row = query_db(
        "SELECT 1 AS allowed FROM PhanCong WHERE MaTaiKhoan = %s AND MaDon = %s AND MaCongDoan = %s LIMIT 1",
        (user.id, order_id, operation_id), one=True
    )
    return bool(row)
