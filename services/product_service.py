from models.product import SanPham, NguyenLieu, DinhMucNguyenLieu
from database.db import execute_db, query_db, transaction
from math import isfinite
from decimal import Decimal, InvalidOperation
from services.identifiers import normalize_code

class ProductService:
    """Business logic for Products, Raw Materials, and BOM."""

    @staticmethod
    def create_product(product_id: str, name: str, unit: str, description: str = ''):
        product_id = normalize_code(product_id, 'Mã sản phẩm')
        if not product_id or not name or not unit:
            raise ValueError("Mã sản phẩm, tên và đơn vị tính không được để trống")
        if SanPham.get_by_id(product_id):
            raise ValueError(f"Mã sản phẩm {product_id} đã tồn tại")
        
        sql = "INSERT INTO SanPham (MaSanPham, TenSanPham, DonViTinh, MoTa, TrangThai) VALUES (%s, %s, %s, %s, 'Active')"
        execute_db(sql, (product_id.strip(), name.strip(), unit.strip(), description.strip()))
        return SanPham.get_by_id(product_id)

    @staticmethod
    def delete_product(product_id: str):
        """Remove an unused product and its BOM/operations without touching orders."""
        with transaction() as tx:
            product = tx.query('SELECT MaSanPham FROM SanPham WHERE MaSanPham = %s', (product_id,), one_row=True)
            if not product:
                raise ValueError('Sản phẩm không tồn tại hoặc đã được xóa.')
            order = tx.query('SELECT MaDon FROM DonSanXuat WHERE MaSanPham = %s LIMIT 1', (product_id,), one_row=True)
            if order:
                raise ValueError('Không thể xóa: sản phẩm đã được dùng trong đơn sản xuất.')
            for table in ('PhanCong', 'TienDoCongDoan', 'SuDungNguyenLieu', 'LoiSanXuat'):
                linked = tx.query(
                    f'SELECT 1 FROM {table} x JOIN CongDoan c ON x.MaCongDoan = c.MaCongDoan '
                    'WHERE c.MaSanPham = %s LIMIT 1', (product_id,), one_row=True
                )
                if linked:
                    raise ValueError('Không thể xóa: công đoạn của sản phẩm đã có dữ liệu sản xuất.')
            # Schema cascades BOM and unused operations when the product is deleted.
            tx.execute('DELETE FROM SanPham WHERE MaSanPham = %s', (product_id,))

    @staticmethod
    def create_product_with_bom(product_id: str, name: str, unit: str, description: str = '', bom_items=None):
        """Create a product and its per-unit material standards in one transaction."""
        product_id = normalize_code(product_id, 'Mã sản phẩm')
        name = (name or '').strip()
        unit = (unit or '').strip()
        description = (description or '').strip()
        if not product_id or not name or not unit:
            raise ValueError('Mã sản phẩm, tên và đơn vị tính không được để trống.')
        if len(name) > 150 or len(unit) > 20:
            raise ValueError('Mã, tên hoặc đơn vị tính vượt quá độ dài cho phép.')
        prepared = ProductService._prepare_bom_items(bom_items)

        with transaction() as tx:
            if tx.query('SELECT MaSanPham FROM SanPham WHERE MaSanPham = %s', (product_id,), one_row=True):
                raise ValueError(f'Mã sản phẩm {product_id} đã tồn tại.')
            resolved = []
            for material_id, quantity, note in prepared:
                material = tx.query('SELECT DonViTinh FROM NguyenLieu WHERE MaNguyenLieu = %s', (material_id,), one_row=True)
                if not material:
                    raise ValueError(f'Vật tư {material_id} không tồn tại trong kho.')
                # The material's catalog unit is authoritative; no user-supplied unit is stored.
                resolved.append((material_id, quantity, note, material['DonViTinh']))
            tx.execute(
                "INSERT INTO SanPham (MaSanPham, TenSanPham, DonViTinh, MoTa, TrangThai) VALUES (%s, %s, %s, %s, 'Active')",
                (product_id, name, unit, description)
            )
            for material_id, quantity, note, material_unit in resolved:
                tx.execute(
                    'INSERT INTO DinhMucNguyenLieu (MaSanPham, MaNguyenLieu, SoLuongDinhMuc, DonViTinh, GhiChu) VALUES (%s, %s, %s, %s, %s)',
                    (product_id, material_id, quantity, material_unit, note)
                )
        return SanPham.get_by_id(product_id)

    @staticmethod
    def _prepare_bom_items(bom_items):
        prepared, seen = [], set()
        for index, item in enumerate(bom_items or [], start=1):
            material_id = (item.get('material_id') or '').strip().upper()
            raw_qty = str(item.get('quantity') or '').strip()
            note = (item.get('note') or '').strip()
            if not material_id and not raw_qty and not note:
                continue
            if not material_id or not raw_qty:
                raise ValueError(f'Dòng định mức {index}: cần chọn vật tư và nhập số lượng.')
            material_id = normalize_code(material_id, 'Mã vật tư')
            if material_id in seen:
                raise ValueError(f'Vật tư {material_id} bị lặp trong định mức.')
            if len(note) > 255:
                raise ValueError(f'Dòng định mức {index}: ghi chú tối đa 255 ký tự.')
            try:
                quantity = Decimal(raw_qty)
            except InvalidOperation:
                raise ValueError(f'Dòng định mức {index}: số lượng không hợp lệ.') from None
            if (not quantity.is_finite() or quantity <= 0 or
                    quantity > Decimal('99999999999999.9999') or quantity.as_tuple().exponent < -4):
                raise ValueError(f'Dòng định mức {index}: số lượng phải lớn hơn 0 và có tối đa 4 chữ số thập phân.')
            seen.add(material_id)
            prepared.append((material_id, str(quantity), note))
        return prepared

    @staticmethod
    def update_product_with_bom(product_id, name, unit, description='', bom_items=None):
        product_id = normalize_code(product_id, 'Mã sản phẩm')
        name, unit, description = (name or '').strip(), (unit or '').strip(), (description or '').strip()
        if not name or not unit or len(name) > 150 or len(unit) > 20:
            raise ValueError('Tên sản phẩm hoặc đơn vị tính không hợp lệ.')
        prepared = ProductService._prepare_bom_items(bom_items)
        with transaction() as tx:
            if not tx.query('SELECT 1 AS ok FROM SanPham WHERE MaSanPham = %s', (product_id,), one_row=True):
                raise ValueError('Sản phẩm không tồn tại.')
            resolved = []
            for material_id, quantity, note in prepared:
                material = tx.query('SELECT DonViTinh FROM NguyenLieu WHERE MaNguyenLieu = %s',
                                    (material_id,), one_row=True)
                if not material:
                    raise ValueError(f'Vật tư {material_id} không tồn tại trong kho.')
                resolved.append((material_id, quantity, note, material['DonViTinh']))
            tx.execute('UPDATE SanPham SET TenSanPham = %s, DonViTinh = %s, MoTa = %s WHERE MaSanPham = %s',
                       (name, unit, description, product_id))
            tx.execute('DELETE FROM DinhMucNguyenLieu WHERE MaSanPham = %s', (product_id,))
            for material_id, quantity, note, material_unit in resolved:
                tx.execute(
                    'INSERT INTO DinhMucNguyenLieu (MaSanPham, MaNguyenLieu, SoLuongDinhMuc, DonViTinh, GhiChu) '
                    'VALUES (%s, %s, %s, %s, %s)',
                    (product_id, material_id, quantity, material_unit, note)
                )
        return SanPham.get_by_id(product_id)

    @staticmethod
    def create_material(material_id: str, name: str, unit: str, opening_stock: float = 0):
        material_id, name, unit = (material_id or '').strip(), (name or '').strip(), (unit or '').strip()
        material_id = normalize_code(material_id, 'Mã vật tư')
        if not name or not unit or len(name) > 150 or len(unit) > 20:
            raise ValueError('Mã, tên và đơn vị vật tư không hợp lệ.')
        if not isfinite(opening_stock) or opening_stock < 0:
            raise ValueError('Tồn đầu kỳ không được âm.')
        if NguyenLieu.get_by_id(material_id):
            raise ValueError('Mã vật tư đã tồn tại.')
        execute_db(
            "INSERT INTO NguyenLieu (MaNguyenLieu, TenNguyenLieu, DonViTinh, SoLuongTon, TrangThai) VALUES (%s, %s, %s, %s, 'Active')",
            (material_id, name, unit, opening_stock)
        )

    @staticmethod
    def receive_material(material_id: str, quantity: float):
        if not isfinite(quantity) or quantity <= 0:
            raise ValueError('Số lượng nhập kho phải lớn hơn 0.')
        if not NguyenLieu.get_by_id(material_id):
            raise ValueError('Vật tư không tồn tại.')
        execute_db(
            'UPDATE NguyenLieu SET SoLuongTon = SoLuongTon + %s, NgayCapNhat = CURRENT_TIMESTAMP WHERE MaNguyenLieu = %s',
            (quantity, material_id)
        )

    @staticmethod
    def update_material(material_id: str, name: str, unit: str, stock: float, status: str = 'Active'):
        material_id = (material_id or '').strip()
        name = (name or '').strip()
        unit = (unit or '').strip()
        status = (status or 'Active').strip()
        if not name or not unit or len(name) > 150 or len(unit) > 20:
            raise ValueError('Tên và đơn vị tính vật tư không hợp lệ.')
        if not isfinite(stock) or stock < 0:
            raise ValueError('Số lượng tồn kho không được âm.')
        if status not in ('Active', 'Inactive', 'Suspended'):
            raise ValueError('Trạng thái vật tư không hợp lệ.')

        with transaction() as tx:
            mat = tx.query('SELECT MaNguyenLieu FROM NguyenLieu WHERE MaNguyenLieu = %s', (material_id,), one_row=True)
            if not mat:
                raise ValueError('Vật tư không tồn tại.')
            tx.execute(
                'UPDATE NguyenLieu SET TenNguyenLieu = %s, DonViTinh = %s, SoLuongTon = %s, TrangThai = %s, NgayCapNhat = CURRENT_TIMESTAMP WHERE MaNguyenLieu = %s',
                (name, unit, stock, status, material_id)
            )
            # Synchronize unit in BOM if this material is referenced
            tx.execute('UPDATE DinhMucNguyenLieu SET DonViTinh = %s WHERE MaNguyenLieu = %s', (unit, material_id))

    @staticmethod
    def delete_material(material_id: str):
        material_id = (material_id or '').strip()
        with transaction() as tx:
            mat = tx.query('SELECT MaNguyenLieu FROM NguyenLieu WHERE MaNguyenLieu = %s', (material_id,), one_row=True)
            if not mat:
                raise ValueError('Vật tư không tồn tại hoặc đã được xóa.')

            in_bom = tx.query('SELECT 1 FROM DinhMucNguyenLieu WHERE MaNguyenLieu = %s LIMIT 1', (material_id,), one_row=True)
            if in_bom:
                raise ValueError('Không thể xóa: vật tư đang được sử dụng trong Định mức nguyên liệu (BOM).')

            in_used = tx.query('SELECT 1 FROM SuDungNguyenLieu WHERE MaNguyenLieu = %s LIMIT 1', (material_id,), one_row=True)
            if in_used:
                raise ValueError('Không thể xóa: vật tư đã có dữ liệu xuất dùng thực tế trong sản xuất.')

            in_reports = tx.query('SELECT 1 FROM BaoVatTu WHERE MaNguyenLieu = %s LIMIT 1', (material_id,), one_row=True)
            if in_reports:
                raise ValueError('Không thể xóa: vật tư đã có phiếu báo cáo vật tư liên quan.')

            tx.execute('DELETE FROM NguyenLieu WHERE MaNguyenLieu = %s', (material_id,))
            return True


    @staticmethod
    def set_bom(product_id: str, material_id: str, standard_qty: float, unit: str, note: str = ''):
        if standard_qty <= 0:
            raise ValueError("Số lượng định mức nguyên liệu phải lớn hơn 0 (BR-04)")
        if not SanPham.get_by_id(product_id):
            raise ValueError(f"Sản phẩm {product_id} không tồn tại")
        if not NguyenLieu.get_by_id(material_id):
            raise ValueError(f"Nguyên liệu {material_id} không tồn tại")

        # Insert or update BOM
        existing = query_db(
            "SELECT * FROM DinhMucNguyenLieu WHERE MaSanPham = %s AND MaNguyenLieu = %s",
            (product_id, material_id),
            one=True
        )
        if existing:
            sql = """
                UPDATE DinhMucNguyenLieu 
                SET SoLuongDinhMuc = %s, DonViTinh = %s, GhiChu = %s, NgayCapNhat = CURRENT_TIMESTAMP
                WHERE MaSanPham = %s AND MaNguyenLieu = %s
            """
            execute_db(sql, (standard_qty, unit, note, product_id, material_id))
        else:
            sql = """
                INSERT INTO DinhMucNguyenLieu (MaSanPham, MaNguyenLieu, SoLuongDinhMuc, DonViTinh, GhiChu)
                VALUES (%s, %s, %s, %s, %s)
            """
            execute_db(sql, (product_id, material_id, standard_qty, unit, note))

    @staticmethod
    def update_material_stock(material_id: str, delta_qty: float):
        material = NguyenLieu.get_by_id(material_id)
        if not material:
            raise ValueError(f"Nguyên liệu {material_id} không tồn tại")
        new_stock = material.stock + delta_qty
        if new_stock < 0:
            raise ValueError(f"Số lượng tồn kho không đủ (Hiện còn: {material.stock} {material.unit})")
        
        execute_db(
            "UPDATE NguyenLieu SET SoLuongTon = %s, NgayCapNhat = CURRENT_TIMESTAMP WHERE MaNguyenLieu = %s",
            (new_stock, material_id)
        )
        return new_stock
