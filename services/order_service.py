from models.order import DonSanXuat, KeHoachSanXuat
from models.product import SanPham, DinhMucNguyenLieu, NguyenLieu
from database.db import execute_db, query_db, transaction
from services.identifiers import new_code
from datetime import date

class OrderService:
    """Business logic for Production Orders and Production Plans."""

    @staticmethod
    def create_order(product_id: str, quantity: int, due_date: str, note: str = ''):
        if quantity <= 0:
            raise ValueError("Số lượng yêu cầu sản xuất phải lớn hơn 0")
        if not product_id or not due_date:
            raise ValueError("Mã sản phẩm và hạn giao không được để trống")
        try:
            date.fromisoformat(due_date)
        except (TypeError, ValueError):
            raise ValueError('Hạn giao phải có định dạng YYYY-MM-DD.') from None
        if not SanPham.get_by_id(product_id):
            raise ValueError(f"Sản phẩm {product_id} không tồn tại")

        order_id = new_code('DSX')
        with transaction() as tx:
            tx.execute(
                "INSERT INTO DonSanXuat (MaDon, MaSanPham, SoLuongYeuCau, HanGiao, TrangThai, GhiChu) "
                "VALUES (%s, %s, %s, %s, 'Mới tạo', %s)",
                (order_id, product_id, quantity, due_date, note)
            )
            operations = tx.query(
                'SELECT MaCongDoan FROM CongDoan WHERE MaSanPham = %s ORDER BY ThuTu ASC', (product_id,)
            )
            for op in operations:
                tx.execute(
                    "INSERT INTO TienDoCongDoan (MaTienDo, MaCongDoan, MaDon, SoLuongHoanThanh, TrangThai) "
                    "VALUES (%s, %s, %s, 0, 'Chưa thực hiện')",
                    (new_code('TD'), op['MaCongDoan'], order_id)
                )
        return DonSanXuat.get_by_id(order_id)

    @staticmethod
    def create_plan(order_id: str, start_date: str, end_date: str):
        OrderService._validate_plan_dates(start_date, end_date)
        order = DonSanXuat.get_by_id(order_id)
        if not order:
            raise ValueError(f"Đơn sản xuất {order_id} không tồn tại")

        code = new_code('KH')
        execute_db(
            'INSERT INTO KeHoachSanXuat (MaKeHoach, MaDon, NgayBatDau, NgayKetThuc) VALUES (%s, %s, %s, %s)',
            (code, order_id, start_date, end_date)
        )
        return code

    @staticmethod
    def update_plan(plan_id: str, start_date: str, end_date: str):
        OrderService._validate_plan_dates(start_date, end_date)
        plan = query_db('SELECT MaDon FROM KeHoachSanXuat WHERE MaKeHoach = %s', (plan_id,), one=True)
        if not plan:
            raise ValueError('Kế hoạch không tồn tại.')
        execute_db('UPDATE KeHoachSanXuat SET NgayBatDau = %s, NgayKetThuc = %s WHERE MaKeHoach = %s',
                   (start_date, end_date, plan_id))
        return plan['MaDon']

    @staticmethod
    def _validate_plan_dates(start_date, end_date):
        try:
            start, end = date.fromisoformat(start_date), date.fromisoformat(end_date)
        except (TypeError, ValueError):
            raise ValueError('Ngày kế hoạch phải có định dạng YYYY-MM-DD.') from None
        if start > end:
            raise ValueError('Ngày bắt đầu không được sau ngày kết thúc kế hoạch.')

    @staticmethod
    def update_order_status(order_id: str, new_status: str):
        if new_status not in DonSanXuat.STATUSES:
            raise ValueError(f"Trạng thái đơn không hợp lệ: {new_status}")
        order = DonSanXuat.get_by_id(order_id)
        if not order:
            raise ValueError(f"Đơn sản xuất {order_id} không tồn tại")
        
        execute_db("UPDATE DonSanXuat SET TrangThai = %s WHERE MaDon = %s", (new_status, order_id))
        return DonSanXuat.get_by_id(order_id)

    @staticmethod
    def update_order(order_id: str, product_id: str, quantity: int, due_date: str, note: str = '', status: str = None):
        order_id = str(order_id).strip()
        product_id = (product_id or '').strip()
        if quantity <= 0:
            raise ValueError("Số lượng yêu cầu sản xuất phải lớn hơn 0")
        if not product_id or not due_date:
            raise ValueError("Mã sản phẩm và hạn giao không được để trống")
        try:
            date.fromisoformat(due_date)
        except (TypeError, ValueError):
            raise ValueError('Hạn giao phải có định dạng YYYY-MM-DD.') from None
        if not SanPham.get_by_id(product_id):
            raise ValueError(f"Sản phẩm {product_id} không tồn tại")

        with transaction() as tx:
            order = tx.query('SELECT * FROM DonSanXuat WHERE MaDon = %s', (order_id,), one_row=True)
            if not order:
                raise ValueError(f"Đơn sản xuất {order_id} không tồn tại")

            max_completed_row = tx.query(
                'SELECT COALESCE(MAX(SoLuongHoanThanh), 0) AS max_done FROM TienDoCongDoan WHERE MaDon = %s',
                (order_id,), one_row=True
            )
            max_done = int(max_completed_row['max_done']) if max_completed_row else 0
            if quantity < max_done:
                raise ValueError(f"Số lượng yêu cầu ({quantity}) không được nhỏ hơn số lượng đã hoàn thành ({max_done})")

            old_product_id = order['MaSanPham']
            if old_product_id != product_id:
                if max_done > 0:
                    raise ValueError('Không thể đổi sản phẩm khi đơn hàng đã có sản lượng hoàn thành.')
                used = tx.query('SELECT 1 FROM SuDungNguyenLieu WHERE MaDon = %s LIMIT 1', (order_id,), one_row=True)
                if used:
                    raise ValueError('Không thể đổi sản phẩm khi đơn hàng đã phát sinh xuất kho nguyên vật liệu.')
                reports = tx.query('SELECT 1 FROM BaoCaoNgay WHERE MaDon = %s LIMIT 1', (order_id,), one_row=True)
                if reports:
                    raise ValueError('Không thể đổi sản phẩm khi đơn hàng đã có báo cáo hàng ngày.')

                tx.execute('DELETE FROM TienDoCongDoan WHERE MaDon = %s', (order_id,))
                tx.execute('DELETE FROM PhanCong WHERE MaDon = %s', (order_id,))
                operations = tx.query(
                    'SELECT MaCongDoan FROM CongDoan WHERE MaSanPham = %s ORDER BY ThuTu ASC', (product_id,)
                )
                for op in operations:
                    tx.execute(
                        "INSERT INTO TienDoCongDoan (MaTienDo, MaCongDoan, MaDon, SoLuongHoanThanh, TrangThai) "
                        "VALUES (%s, %s, %s, 0, 'Chưa thực hiện')",
                        (new_code('TD'), op['MaCongDoan'], order_id)
                    )

            target_status = status if (status and status in DonSanXuat.STATUSES) else order['TrangThai']
            tx.execute(
                "UPDATE DonSanXuat SET MaSanPham = %s, SoLuongYeuCau = %s, HanGiao = %s, GhiChu = %s, TrangThai = %s WHERE MaDon = %s",
                (product_id, quantity, due_date, note, target_status, order_id)
            )
            return True


    @staticmethod
    def delete_order(order_id: str):
        """Remove a production order and its associated planning/progress/assignments if not yet in active manufacturing."""
        order_id = str(order_id).strip()
        with transaction() as tx:
            order = tx.query('SELECT MaDon, TrangThai FROM DonSanXuat WHERE MaDon = %s', (order_id,), one_row=True)
            if not order:
                raise ValueError(f'Đơn sản xuất {order_id} không tồn tại hoặc đã được xóa.')

            if order['TrangThai'] == 'Hoàn thành':
                raise ValueError('Không thể xóa đơn hàng đã hoàn thành.')

            # Check if any operation already completed any output
            progress = tx.query(
                'SELECT 1 FROM TienDoCongDoan WHERE MaDon = %s AND COALESCE(SoLuongHoanThanh, 0) > 0 LIMIT 1',
                (order_id,), one_row=True
            )
            if progress:
                raise ValueError('Không thể xóa: đơn hàng đã có sản lượng hoàn thành tại công đoạn.')

            # Check if raw materials have been deducted from warehouse
            used = tx.query(
                'SELECT 1 FROM SuDungNguyenLieu WHERE MaDon = %s LIMIT 1',
                (order_id,), one_row=True
            )
            if used:
                raise ValueError('Không thể xóa: đơn hàng đã phát sinh xuất kho nguyên vật liệu thực tế.')

            # Check if daily reports exist
            daily = tx.query(
                'SELECT 1 FROM BaoCaoNgay WHERE MaDon = %s LIMIT 1',
                (order_id,), one_row=True
            )
            if daily:
                raise ValueError('Không thể xóa: đơn hàng đã có báo cáo sản xuất hàng ngày.')

            # Check if material reports exist
            mat_report = tx.query(
                'SELECT 1 FROM BaoVatTu WHERE MaDon = %s LIMIT 1',
                (order_id,), one_row=True
            )
            if mat_report:
                raise ValueError('Không thể xóa: đơn hàng đã có phiếu báo cáo vật tư.')

            # Check if defect logs exist
            defects = tx.query(
                'SELECT 1 FROM LoiSanXuat WHERE MaDon = %s LIMIT 1',
                (order_id,), one_row=True
            )
            if defects:
                raise ValueError('Không thể xóa: đơn hàng đã ghi nhận dữ liệu lỗi sản xuất.')

            # Remove associated scheduling, assignment and progress tracking
            tx.execute('DELETE FROM KeHoachSanXuat WHERE MaDon = %s', (order_id,))
            tx.execute('DELETE FROM PhanCong WHERE MaDon = %s', (order_id,))
            tx.execute('DELETE FROM TienDoCongDoan WHERE MaDon = %s', (order_id,))
            tx.execute('DELETE FROM DonSanXuat WHERE MaDon = %s', (order_id,))
            return True

    @staticmethod
    def check_material_feasibility(order_id: str):
        """
        Calculates theoretical material requirements (BOM * Quantity) 
        and compares with available inventory.
        """
        order = DonSanXuat.get_by_id(order_id)
        if not order:
            raise ValueError(f"Đơn sản xuất {order_id} không tồn tại")

        boms = DinhMucNguyenLieu.get_by_product(order.product_id)
        feasibility = []
        is_sufficient = True

        for b in boms:
            needed = b.standard_qty * order.quantity_requested
            mat = NguyenLieu.get_by_id(b.material_id)
            available = mat.stock if mat else 0.0
            deficit = max(0.0, needed - available)
            if deficit > 0:
                is_sufficient = False
            
            feasibility.append({
                'material_id': b.material_id,
                'material_name': b.material_name,
                'unit': b.unit,
                'needed_quantity': needed,
                'available_quantity': available,
                'deficit': deficit,
                'status': 'Đủ vật tư' if deficit == 0 else f'Thiếu {deficit:.2f} {b.unit}'
            })

        return {
            'order_id': order_id,
            'is_sufficient': is_sufficient,
            'details': feasibility
        }
