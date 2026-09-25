from database.db import query_db, execute_db
from services.identifiers import new_code

class CongDoan:
    """Manufacturing operation / stage."""
    def __init__(self, data: dict):
        self.id = data.get('MaCongDoan')
        self.product_id = data.get('MaSanPham')
        self.name = data.get('TenCongDoan')
        self.step_order = int(data.get('ThuTu', 1))
        self.description = data.get('MoTa', '')
        self.status = data.get('TrangThai', 'Active')

    @classmethod
    def get_by_product(cls, product_id: str):
        rows = query_db("SELECT * FROM CongDoan WHERE MaSanPham = %s ORDER BY ThuTu ASC", (product_id,))
        return [cls(r) for r in rows]


class PhanCong:
    """Work assignment for an operation."""
    def __init__(self, data: dict):
        self.id = data.get('MaPhanCong')
        self.operation_id = data.get('MaCongDoan')
        self.operation_name = data.get('TenCongDoan', '')
        self.user_id = data.get('MaTaiKhoan')
        self.user_name = data.get('HoTen', '')
        self.order_id = data.get('MaDon')
        self.date = str(data.get('NgayPhanCong', ''))

    @classmethod
    def get_by_order(cls, order_id: str):
        sql = """
            SELECT p.*, t.HoTen, c.TenCongDoan
            FROM PhanCong p
            JOIN TaiKhoan t ON p.MaTaiKhoan = t.MaTaiKhoan
            JOIN CongDoan c ON p.MaCongDoan = c.MaCongDoan
            WHERE p.MaDon = %s
            ORDER BY c.ThuTu ASC
        """
        rows = query_db(sql, (order_id,))
        return [cls(r) for r in rows]

    @classmethod
    def exists(cls, operation_id: str, user_id: str, order_id: str) -> bool:
        row = query_db(
            "SELECT 1 AS ok FROM PhanCong WHERE MaCongDoan = %s AND MaTaiKhoan = %s AND MaDon = %s LIMIT 1",
            (operation_id, user_id, order_id), one=True
        )
        return bool(row)

    @classmethod
    def create(cls, operation_id: str, user_id: str, order_id: str, assign_date: str):
        valid = query_db(
            'SELECT 1 AS ok FROM DonSanXuat d JOIN CongDoan c ON c.MaSanPham = d.MaSanPham '
            'WHERE d.MaDon = %s AND c.MaCongDoan = %s',
            (order_id, operation_id), one=True
        )
        if not valid:
            raise ValueError('Công đoạn không thuộc sản phẩm của đơn này.')
        worker = query_db(
            "SELECT 1 AS ok FROM TaiKhoan WHERE MaTaiKhoan = %s AND TrangThai = 'Active' "
            "AND VaiTro IN ('ToTruong', 'NhanVien')",
            (user_id,), one=True
        )
        if not worker:
            raise ValueError('Chỉ được phân công tài khoản đang hoạt động thuộc tổ trưởng/nhân viên.')
        if cls.exists(operation_id, user_id, order_id):
            raise ValueError("Nhân viên đã được phân công cho công đoạn này trong đơn hàng này.")
        code = new_code('PC')
        execute_db(
            "INSERT INTO PhanCong (MaPhanCong, MaCongDoan, MaTaiKhoan, MaDon, NgayPhanCong) VALUES (%s, %s, %s, %s, %s)",
            (code, operation_id, user_id, order_id, assign_date)
        )
        return code

    @classmethod
    def delete_assignment(cls, assignment_id: str):
        return execute_db("DELETE FROM PhanCong WHERE MaPhanCong = %s", (assignment_id,))



class TienDoCongDoan:
    """Progress record for an operation in an order."""
    def __init__(self, data: dict):
        self.id = data.get('MaTienDo')
        self.operation_id = data.get('MaCongDoan')
        self.operation_name = data.get('TenCongDoan', '')
        self.step_order = int(data.get('ThuTu', 1))
        self.order_id = data.get('MaDon')
        self.completed_qty = int(data.get('SoLuongHoanThanh', 0))
        self.status = data.get('TrangThai', 'Chưa thực hiện')
        self.updated_at = data.get('NgayCapNhat')

    @classmethod
    def get_by_order(cls, order_id: int):
        sql = """
            SELECT t.*, c.TenCongDoan, c.ThuTu
            FROM TienDoCongDoan t
            JOIN CongDoan c ON t.MaCongDoan = c.MaCongDoan
            WHERE t.MaDon = %s
            ORDER BY c.ThuTu ASC
        """
        rows = query_db(sql, (order_id,))
        return [cls(r) for r in rows]


class SuDungNguyenLieu:
    """Material consumption record."""
    def __init__(self, data: dict):
        self.id = data.get('MaSuDung')
        self.order_id = data.get('MaDon')
        self.operation_id = data.get('MaCongDoan')
        self.operation_name = data.get('TenCongDoan', '')
        self.material_id = data.get('MaNguyenLieu')
        self.material_name = data.get('TenNguyenLieu', '')
        self.quantity_used = float(data.get('SoLuongSuDung', 0.0))
        self.unit = data.get('DonViTinh', '')
        self.recorded_at = data.get('NgayGhiNhan')

    @classmethod
    def get_by_order(cls, order_id: int):
        sql = """
            SELECT s.*, n.TenNguyenLieu, n.DonViTinh, c.TenCongDoan
            FROM SuDungNguyenLieu s
            JOIN NguyenLieu n ON s.MaNguyenLieu = n.MaNguyenLieu
            JOIN CongDoan c ON s.MaCongDoan = c.MaCongDoan
            WHERE s.MaDon = %s
            ORDER BY s.NgayGhiNhan DESC
        """
        rows = query_db(sql, (order_id,))
        return [cls(r) for r in rows]


class LoiSanXuat:
    """Production defect record."""
    def __init__(self, data: dict):
        self.id = data.get('MaLoi')
        self.order_id = data.get('MaDon')
        self.operation_id = data.get('MaCongDoan')
        self.operation_name = data.get('TenCongDoan', '')
        self.defect_desc = data.get('MoTaLoi', '')
        self.defect_qty = int(data.get('SoLuongHong', 1))
        self.recorded_at = data.get('NgayGhiNhan')

    @classmethod
    def get_all(cls):
        sql = """
            SELECT l.*, c.TenCongDoan
            FROM LoiSanXuat l
            JOIN CongDoan c ON l.MaCongDoan = c.MaCongDoan
            ORDER BY l.NgayGhiNhan DESC
        """
        rows = query_db(sql)
        return [cls(r) for r in rows]

    @classmethod
    def get_by_order(cls, order_id: int):
        sql = """
            SELECT l.*, c.TenCongDoan
            FROM LoiSanXuat l
            JOIN CongDoan c ON l.MaCongDoan = c.MaCongDoan
            WHERE l.MaDon = %s
            ORDER BY l.NgayGhiNhan DESC
        """
        rows = query_db(sql, (order_id,))
        return [cls(r) for r in rows]
