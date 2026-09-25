from database.db import query_db, execute_db

class SanPham:
    """Product model."""
    def __init__(self, data: dict):
        self.id = data.get('MaSanPham')
        self.name = data.get('TenSanPham')
        self.unit = data.get('DonViTinh')
        self.description = data.get('MoTa', '')
        self.status = data.get('TrangThai', 'Active')
        self.created_at = data.get('NgayTao')

    @classmethod
    def get_all(cls):
        rows = query_db("SELECT * FROM SanPham ORDER BY MaSanPham ASC")
        return [cls(r) for r in rows]

    @classmethod
    def search(cls, q=''):
        if not q:
            return cls.get_all()
        rows = query_db(
            "SELECT * FROM SanPham WHERE LOWER(MaSanPham) LIKE %s OR LOWER(TenSanPham) LIKE %s ORDER BY MaSanPham ASC",
            (f'%{q.lower()}%', f'%{q.lower()}%')
        )
        return [cls(r) for r in rows]

    @classmethod
    def get_by_id(cls, product_id: str):
        row = query_db("SELECT * FROM SanPham WHERE MaSanPham = %s", (product_id,), one=True)
        return cls(row) if row else None


class NguyenLieu:
    """Raw material model."""
    def __init__(self, data: dict):
        self.id = data.get('MaNguyenLieu')
        self.name = data.get('TenNguyenLieu')
        self.unit = data.get('DonViTinh')
        self.stock = float(data.get('SoLuongTon', 0.0))
        self.status = data.get('TrangThai', 'Active')
        self.updated_at = data.get('NgayCapNhat')

    @classmethod
    def get_all(cls):
        rows = query_db("SELECT * FROM NguyenLieu ORDER BY MaNguyenLieu ASC")
        return [cls(r) for r in rows]

    @classmethod
    def search(cls, q='', stock_filter=''):
        where, args = [], []
        if q:
            where.append("(LOWER(MaNguyenLieu) LIKE %s OR LOWER(TenNguyenLieu) LIKE %s)")
            args.extend((f'%{q.lower()}%', f'%{q.lower()}%'))
        if stock_filter == 'low':
            where.append('SoLuongTon > 0 AND SoLuongTon < 50')
        elif stock_filter == 'empty':
            where.append('SoLuongTon <= 0')
        elif stock_filter == 'available':
            where.append('SoLuongTon > 0')
        sql = 'SELECT * FROM NguyenLieu' + (' WHERE ' + ' AND '.join(where) if where else '') + ' ORDER BY MaNguyenLieu ASC'
        return [cls(r) for r in query_db(sql, tuple(args))]

    @classmethod
    def get_by_id(cls, material_id: str):
        row = query_db("SELECT * FROM NguyenLieu WHERE MaNguyenLieu = %s", (material_id,), one=True)
        return cls(row) if row else None


class DinhMucNguyenLieu:
    """Bill of Materials (BOM) specification for 1 unit of product."""
    def __init__(self, data: dict):
        self.product_id = data.get('MaSanPham')
        self.material_id = data.get('MaNguyenLieu')
        self.material_name = data.get('TenNguyenLieu', '')
        self.standard_qty = float(data.get('SoLuongDinhMuc', 0.0))
        self.unit = data.get('DonViTinh')
        self.note = data.get('GhiChu', '')

    @classmethod
    def get_by_product(cls, product_id: str):
        sql = """
            SELECT d.*, n.TenNguyenLieu 
            FROM DinhMucNguyenLieu d
            JOIN NguyenLieu n ON d.MaNguyenLieu = n.MaNguyenLieu
            WHERE d.MaSanPham = %s
            ORDER BY d.MaNguyenLieu ASC
        """
        rows = query_db(sql, (product_id,))
        return [cls(r) for r in rows]
