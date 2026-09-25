"""End-of-day reports submitted by team leaders and reviewed by managers."""

from datetime import date

from database.db import query_db, execute_db
from services.access_service import can_view_order
from services.identifiers import new_code


class DailyReportService:
    @staticmethod
    def submit(user, order_id, report_date, completed, defective, note):
        if user.role != 'ToTruong' or not can_view_order(user, order_id):
            raise PermissionError('Không có quyền báo cáo cho đơn này.')
        try:
            day = date.fromisoformat(report_date)
        except (TypeError, ValueError):
            raise ValueError('Ngày báo cáo không hợp lệ.')
        if day > date.today():
            raise ValueError('Không thể báo cáo cho ngày trong tương lai.')
        if completed < 0 or defective < 0 or defective > completed:
            raise ValueError('Số lượng báo cáo không hợp lệ.')
        if not (note or '').strip() and completed == 0:
            raise ValueError('Cần nhập kết quả hoặc ghi chú công việc.')
        existing = query_db(
            'SELECT MaBaoCao FROM BaoCaoNgay WHERE MaDon = %s AND MaTaiKhoan = %s AND NgayBaoCao = %s',
            (order_id, user.id, day.isoformat()), one=True
        )
        if existing:
            raise ValueError('Bạn đã nộp báo cáo cho đơn này trong ngày đã chọn.')
        code = new_code('BC')
        execute_db(
            '''INSERT INTO BaoCaoNgay (MaBaoCao, MaDon, MaTaiKhoan, NgayBaoCao, SoLuongHoanThanh, SoLuongHong, GhiChu)
               VALUES (%s, %s, %s, %s, %s, %s, %s)''',
            (code, order_id, user.id, day.isoformat(), completed, defective, (note or '').strip())
        )
        return code

    @staticmethod
    def search(user, q='', status='', report_date=''):
        where, args = [], []
        if user.role == 'ToTruong':
            where.append('r.MaTaiKhoan = %s')
            args.append(user.id)
        elif user.role != 'QuanLyXuong':
            raise PermissionError('Không có quyền xem báo cáo.')
        if q:
            where.append('(CAST(r.MaDon AS CHAR) LIKE %s OR LOWER(t.HoTen) LIKE %s)')
            args.extend((f'%{q}%', f'%{q.lower()}%'))
        if status in ('Pending', 'Reviewed'):
            where.append('r.TrangThai = %s')
            args.append(status)
        if report_date:
            where.append('r.NgayBaoCao = %s')
            args.append(report_date)
        sql = '''SELECT r.*, t.HoTen AS TenToTruong, s.TenSanPham
                 FROM BaoCaoNgay r JOIN TaiKhoan t ON r.MaTaiKhoan = t.MaTaiKhoan
                 JOIN DonSanXuat d ON r.MaDon = d.MaDon
                 JOIN SanPham s ON d.MaSanPham = s.MaSanPham'''
        if where:
            sql += ' WHERE ' + ' AND '.join(where)
        sql += ' ORDER BY r.NgayBaoCao DESC, r.MaBaoCao DESC'
        return query_db(sql, tuple(args))

    @staticmethod
    def review(manager, report_id):
        if manager.role != 'QuanLyXuong':
            raise PermissionError('Chỉ Quản lý xưởng được duyệt báo cáo.')
        report = query_db('SELECT MaBaoCao, TrangThai FROM BaoCaoNgay WHERE MaBaoCao = %s', (report_id,), one=True)
        if not report or report['TrangThai'] != 'Pending':
            raise ValueError('Báo cáo không còn chờ duyệt.')
        execute_db(
            "UPDATE BaoCaoNgay SET TrangThai = 'Reviewed', NgayDuyet = CURRENT_TIMESTAMP, MaNguoiDuyet = %s WHERE MaBaoCao = %s",
            (manager.id, report_id)
        )
