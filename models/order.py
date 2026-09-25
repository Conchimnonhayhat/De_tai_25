import re

from database.db import query_db, execute_db

class DonSanXuat:
    """Production order model."""
    STATUSES = ['Mới tạo', 'Đang thực hiện', 'Hoàn thành', 'Hủy']

    def __init__(self, data: dict):
        self.id = data.get('MaDon')
        self.product_id = data.get('MaSanPham')
        self.product_name = data.get('TenSanPham', '')
        self.quantity_requested = int(data.get('SoLuongYeuCau', 0))
        self.due_date = str(data.get('HanGiao', ''))
        self.status = data.get('TrangThai', 'Mới tạo')
        self.created_at = data.get('NgayTao')
        self.note = data.get('GhiChu', '')

    @classmethod
    def get_all(cls):
        sql = """
            SELECT d.*, s.TenSanPham
            FROM DonSanXuat d
            JOIN SanPham s ON d.MaSanPham = s.MaSanPham
            ORDER BY d.HanGiao ASC, d.MaDon ASC
        """
        rows = query_db(sql)
        return [cls(r) for r in rows]

    @classmethod
    def search(cls, q='', status='', user_id=None, product_id='', operation_id='',
               due_from='', due_to='', leader_id=''):
        where, args = [], []
        if q:
            term = re.sub(r'^(?:đơn\s*)?#\s*', '', q.strip(), flags=re.IGNORECASE)
            escaped = term.replace('!', '!!').replace('%', '!%').replace('_', '!_')
            pattern = f'%{escaped.lower()}%'
            where.append("(LOWER(CAST(d.MaDon AS CHAR)) LIKE %s ESCAPE '!' "
                         "OR LOWER(d.MaSanPham) LIKE %s ESCAPE '!' "
                         "OR LOWER(s.TenSanPham) LIKE %s ESCAPE '!' "
                         "OR LOWER(COALESCE(d.GhiChu, '')) LIKE %s ESCAPE '!')")
            args.extend((pattern,) * 4)
        if status in cls.STATUSES:
            where.append('d.TrangThai = %s')
            args.append(status)
        if product_id:
            where.append('d.MaSanPham = %s')
            args.append(product_id)
        if due_from:
            where.append('d.HanGiao >= %s')
            args.append(due_from)
        if due_to:
            where.append('d.HanGiao <= %s')
            args.append(due_to)
        if user_id is not None:
            where.append('EXISTS (SELECT 1 FROM PhanCong p WHERE p.MaDon = d.MaDon AND p.MaTaiKhoan = %s)')
            args.append(user_id)
        if operation_id or leader_id:
            assignment_conditions = ['p.MaDon = d.MaDon']
            if operation_id:
                assignment_conditions.append('p.MaCongDoan = %s')
                args.append(operation_id)
            if leader_id:
                assignment_conditions.append('p.MaTaiKhoan = %s')
                assignment_conditions.append("t.VaiTro = 'ToTruong'")
                args.append(leader_id)
            join = ' JOIN TaiKhoan t ON t.MaTaiKhoan = p.MaTaiKhoan' if leader_id else ''
            where.append('EXISTS (SELECT 1 FROM PhanCong p' + join + ' WHERE '
                         + ' AND '.join(assignment_conditions) + ')')
        sql = '''SELECT d.*, s.TenSanPham FROM DonSanXuat d
                 JOIN SanPham s ON d.MaSanPham = s.MaSanPham'''
        if where:
            sql += ' WHERE ' + ' AND '.join(where)
        sql += ' ORDER BY d.HanGiao ASC, d.MaDon ASC'
        return [cls(r) for r in query_db(sql, tuple(args))]

    @classmethod
    def get_by_id(cls, order_id: int):
        sql = """
            SELECT d.*, s.TenSanPham
            FROM DonSanXuat d
            JOIN SanPham s ON d.MaSanPham = s.MaSanPham
            WHERE d.MaDon = %s
        """
        row = query_db(sql, (order_id,), one=True)
        return cls(row) if row else None

    @classmethod
    def delete(cls, order_id: str):
        from services.order_service import OrderService
        return OrderService.delete_order(order_id)

    @classmethod
    def update(cls, order_id: str, product_id: str, quantity: int, due_date: str, note: str = '', status: str = None):
        from services.order_service import OrderService
        return OrderService.update_order(order_id, product_id, quantity, due_date, note, status)




class KeHoachSanXuat:
    """Production schedule plan."""
    def __init__(self, data: dict):
        self.id = data.get('MaKeHoach')
        self.order_id = data.get('MaDon')
        self.start_date = str(data.get('NgayBatDau', ''))
        self.end_date = str(data.get('NgayKetThuc', ''))

    @classmethod
    def get_by_order(cls, order_id: int):
        rows = query_db("SELECT * FROM KeHoachSanXuat WHERE MaDon = %s ORDER BY MaKeHoach DESC", (order_id,))
        return [cls(r) for r in rows]
