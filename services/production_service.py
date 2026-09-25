from math import isfinite
from datetime import date
from models.order import DonSanXuat
from models.production import CongDoan, PhanCong, TienDoCongDoan, LoiSanXuat, SuDungNguyenLieu
from models.product import NguyenLieu
from database.db import execute_db, query_db, transaction
from services.identifiers import new_code
from services.access_service import can_update_operation

class ProductionService:
    """Core manufacturing business logic: Operations, Progress, Defects, and Materials."""

    @staticmethod
    def assign_workers(actor, operation_id: str, user_ids, order_id: str, assign_date: str):
        """Assign several people to one operation, with all rows committed together."""
        if actor.role not in ('QuanLyXuong', 'ToTruong'):
            raise PermissionError('Bạn không có quyền phân công nhân sự.')
        user_ids = [str(value).strip() for value in user_ids if str(value).strip()]
        if not user_ids:
            raise ValueError('Hãy chọn ít nhất một nhân viên.')
        if len(user_ids) > 30:
            raise ValueError('Mỗi lần chỉ phân công tối đa 30 người.')
        if len(set(user_ids)) != len(user_ids):
            raise ValueError('Một nhân viên chỉ được chọn một lần trong biểu mẫu.')
        if actor.role == 'QuanLyXuong' and len(user_ids) != 1:
            raise ValueError('Mỗi công đoạn chỉ giao cho một Tổ trưởng phụ trách.')
        try:
            date.fromisoformat(assign_date)
        except (TypeError, ValueError):
            raise ValueError('Ngày phân công không hợp lệ.') from None
        if actor.role == 'ToTruong' and not can_update_operation(actor, order_id, operation_id):
            raise PermissionError('Tổ trưởng chưa được giao công đoạn này.')

        with transaction() as tx:
            operation = tx.query(
                'SELECT 1 AS ok FROM DonSanXuat d '
                'JOIN CongDoan c ON c.MaSanPham = d.MaSanPham '
                'WHERE d.MaDon = %s AND c.MaCongDoan = %s',
                (order_id, operation_id), one_row=True
            )
            if not operation:
                raise ValueError('Công đoạn không thuộc sản phẩm của đơn này.')
            if actor.role == 'QuanLyXuong' and tx.query(
                "SELECT 1 AS ok FROM PhanCong p JOIN TaiKhoan t ON t.MaTaiKhoan = p.MaTaiKhoan "
                "WHERE p.MaDon = %s AND p.MaCongDoan = %s AND t.VaiTro = 'ToTruong' LIMIT 1",
                (order_id, operation_id), one_row=True
            ):
                raise ValueError('Công đoạn đã có Tổ trưởng phụ trách. Hãy gỡ phân công cũ trước.')
            names = []
            for user_id in user_ids:
                worker = tx.query(
                    'SELECT HoTen, VaiTro, TrangThai FROM TaiKhoan WHERE MaTaiKhoan = %s',
                    (user_id,), one_row=True
                )
                expected_role = 'ToTruong' if actor.role == 'QuanLyXuong' else 'NhanVien'
                if not worker or worker['TrangThai'] != 'Active' or worker['VaiTro'] != expected_role:
                    raise ValueError('Danh sách có tài khoản không hoạt động hoặc không được phân công.')
                if actor.role == 'ToTruong':
                    member = tx.query(
                        'SELECT 1 AS ok FROM ThanhVienTo WHERE MaToTruong = %s AND MaNhanVien = %s',
                        (actor.id, user_id), one_row=True
                    )
                    if worker['VaiTro'] != 'NhanVien' or not member:
                        raise PermissionError('Tổ trưởng chỉ được giao việc cho nhân viên trong tổ mình.')
                existing = tx.query(
                    'SELECT 1 AS ok FROM PhanCong WHERE MaDon = %s AND MaCongDoan = %s AND MaTaiKhoan = %s',
                    (order_id, operation_id, user_id), one_row=True
                )
                if existing:
                    raise ValueError(f'{worker["HoTen"]} đã được giao công đoạn này trong đơn.')
                names.append(worker['HoTen'])

            for user_id in user_ids:
                tx.execute(
                    'INSERT INTO PhanCong (MaPhanCong, MaCongDoan, MaTaiKhoan, MaDon, NgayPhanCong) '
                    'VALUES (%s, %s, %s, %s, %s)',
                    (new_code('PC'), operation_id, user_id, order_id, assign_date)
                )
        return names

    @staticmethod
    def create_operation(product_id: str, name: str, step_order: int, description: str = ''):
        if not name or step_order <= 0:
            raise ValueError("Tên công đoạn và thứ tự (lớn hơn 0) không được để trống")
        code = new_code('CD')
        with transaction() as tx:
            if not tx.query('SELECT MaSanPham FROM SanPham WHERE MaSanPham = %s', (product_id,), one_row=True):
                raise ValueError('Sản phẩm không tồn tại.')
            steps = tx.query('SELECT ThuTu FROM CongDoan WHERE MaSanPham = %s ORDER BY ThuTu', (product_id,))
            if step_order != len(steps) + 1:
                raise ValueError('Thứ tự công đoạn mới phải nối tiếp công đoạn hiện có.')
            started = tx.query(
                "SELECT 1 AS ok FROM DonSanXuat d LEFT JOIN TienDoCongDoan t ON d.MaDon = t.MaDon "
                "WHERE d.MaSanPham = %s AND (d.TrangThai <> 'Mới tạo' OR t.SoLuongHoanThanh > 0) LIMIT 1",
                (product_id,), one_row=True
            )
            if started:
                raise ValueError('Không thể thêm công đoạn khi sản phẩm đã có đơn bắt đầu sản xuất.')
            tx.execute(
                "INSERT INTO CongDoan (MaCongDoan, MaSanPham, TenCongDoan, ThuTu, MoTa, TrangThai) "
                "VALUES (%s, %s, %s, %s, %s, 'Active')",
                (code, product_id, name.strip(), step_order, (description or '').strip())
            )
            orders = tx.query('SELECT MaDon FROM DonSanXuat WHERE MaSanPham = %s', (product_id,))
            for order in orders:
                tx.execute(
                    "INSERT INTO TienDoCongDoan (MaTienDo, MaCongDoan, MaDon, SoLuongHoanThanh, TrangThai) "
                    "VALUES (%s, %s, %s, 0, 'Chưa thực hiện')",
                    (new_code('TD'), code, order['MaDon'])
                )
        return code

    @staticmethod
    def assign_worker(operation_id: int, user_id: int, order_id: int, assign_date: str):
        if not assign_date:
            raise ValueError("Ngày phân công không được để trống")
        return PhanCong.create(operation_id, user_id, order_id, assign_date)

    @staticmethod
    def update_progress(order_id: int, operation_id: int, additional_qty: int):
        """
        Updates progress for a specific operation of an order.
        Enforces BR-02, BR-03 and transactional consistency.
        """
        if additional_qty <= 0:
            raise ValueError("Số lượng hoàn thành bổ sung phải lớn hơn 0")

        order = DonSanXuat.get_by_id(order_id)
        if not order:
            raise ValueError(f"Đơn sản xuất {order_id} không tồn tại")
        if order.status == 'Hủy':
            raise ValueError('Không thể cập nhật tiến độ của đơn đã hủy.')

        with transaction() as tx:
            # 1. Fetch current operation details
            op = tx.query(
                "SELECT * FROM CongDoan WHERE MaCongDoan = %s AND MaSanPham = %s",
                (operation_id, order.product_id),
                one_row=True
            )
            if not op:
                raise ValueError(f"Công đoạn {operation_id} không thuộc sản phẩm của đơn {order_id}")

            current_order_step = int(op['ThuTu'])

            # 2. Fetch current progress
            prog = tx.query(
                "SELECT * FROM TienDoCongDoan WHERE MaDon = %s AND MaCongDoan = %s",
                (order_id, operation_id),
                one_row=True
            )
            current_completed = int(prog['SoLuongHoanThanh']) if prog else 0
            new_completed = current_completed + additional_qty

            if new_completed > order.quantity_requested:
                raise ValueError(
                    f"Tổng sản lượng hoàn thành ({new_completed}) không được vượt quá số lượng yêu cầu của đơn ({order.quantity_requested})"
                )

            # 3. Check preceding operation constraint (BR-03)
            if current_order_step > 1:
                prev_op = tx.query(
                    "SELECT MaCongDoan FROM CongDoan WHERE MaSanPham = %s AND ThuTu = %s",
                    (order.product_id, current_order_step - 1),
                    one_row=True
                )
                if prev_op:
                    prev_prog = tx.query(
                        "SELECT SoLuongHoanThanh FROM TienDoCongDoan WHERE MaDon = %s AND MaCongDoan = %s",
                        (order_id, prev_op['MaCongDoan']),
                        one_row=True
                    )
                    prev_completed = int(prev_prog['SoLuongHoanThanh']) if prev_prog else 0
                    if new_completed > prev_completed:
                        raise ValueError(
                            f"Sản lượng công đoạn {op['TenCongDoan']} ({new_completed}) không được vượt quá công đoạn trước liền kề ({prev_completed})"
                        )

            # 4. Determine status
            status = 'Hoàn thành' if new_completed >= order.quantity_requested else 'Đang thực hiện'

            # 5. Persist progress
            if prog:
                tx.execute(
                    "UPDATE TienDoCongDoan SET SoLuongHoanThanh = %s, TrangThai = %s, NgayCapNhat = CURRENT_TIMESTAMP WHERE MaTienDo = %s",
                    (new_completed, status, prog['MaTienDo'])
                )
            else:
                tx.execute(
                    "INSERT INTO TienDoCongDoan (MaTienDo, MaCongDoan, MaDon, SoLuongHoanThanh, TrangThai) VALUES (%s, %s, %s, %s, %s)",
                    (new_code('TD'), operation_id, order_id, new_completed, status)
                )

            # 6. Check if order status should update
            if order.status == 'Mới tạo':
                tx.execute("UPDATE DonSanXuat SET TrangThai = 'Đang thực hiện' WHERE MaDon = %s", (order_id,))

            # Check if all operations completed 100%
            all_progs = tx.query("SELECT SoLuongHoanThanh FROM TienDoCongDoan WHERE MaDon = %s", (order_id,))
            all_ops = tx.query("SELECT COUNT(*) as cnt FROM CongDoan WHERE MaSanPham = %s", (order.product_id,), one_row=True)
            if len(all_progs) == all_ops['cnt'] and all(p['SoLuongHoanThanh'] >= order.quantity_requested for p in all_progs):
                tx.execute("UPDATE DonSanXuat SET TrangThai = 'Hoàn thành' WHERE MaDon = %s", (order_id,))

        return {'order_id': order_id, 'operation_id': operation_id, 'completed_qty': new_completed, 'status': status}

    @staticmethod
    def record_defect(order_id: int, operation_id: int, defect_desc: str, defect_qty: int):
        if defect_qty <= 0:
            raise ValueError("Số lượng sản phẩm hỏng phải lớn hơn 0")
        if not defect_desc or not defect_desc.strip():
            raise ValueError("Mô tả lỗi không được để trống")

        order = DonSanXuat.get_by_id(order_id)
        if not order or not query_db(
            'SELECT 1 AS ok FROM CongDoan WHERE MaCongDoan = %s AND MaSanPham = %s',
            (operation_id, order.product_id), one=True
        ):
            raise ValueError('Công đoạn không thuộc sản phẩm của đơn này.')
        if defect_qty > order.quantity_requested:
            raise ValueError('Số lượng sản phẩm hỏng không được vượt số lượng yêu cầu.')
        defect_id = new_code('LOI')
        execute_db(
            'INSERT INTO LoiSanXuat (MaLoi, MaDon, MaCongDoan, MoTaLoi, SoLuongHong) VALUES (%s, %s, %s, %s, %s)',
            (defect_id, order_id, operation_id, defect_desc.strip(), defect_qty)
        )
        return defect_id

    @staticmethod
    def record_material_usage(order_id: int, operation_id: int, material_id: str, quantity_used: float):
        if not isinstance(quantity_used, (int, float)) or not isfinite(quantity_used) or quantity_used <= 0:
            raise ValueError("Số lượng nguyên liệu sử dụng phải lớn hơn 0")

        order = DonSanXuat.get_by_id(order_id)
        if not order or not query_db(
            'SELECT 1 AS ok FROM CongDoan WHERE MaCongDoan = %s AND MaSanPham = %s',
            (operation_id, order.product_id), one=True
        ):
            raise ValueError('Công đoạn không thuộc sản phẩm của đơn này.')

        material = NguyenLieu.get_by_id(material_id)
        if not material:
            raise ValueError(f"Nguyên liệu {material_id} không tồn tại")

        with transaction() as tx:
            # The stock condition and subtraction are one atomic statement.
            updated = tx.execute(
                'UPDATE NguyenLieu SET SoLuongTon = SoLuongTon - %s, NgayCapNhat = CURRENT_TIMESTAMP '
                'WHERE MaNguyenLieu = %s AND SoLuongTon >= %s',
                (quantity_used, material_id, quantity_used)
            )
            if updated != 1:
                raise ValueError('Tồn kho nguyên liệu không đủ để xuất.')
            tx.execute(
                "INSERT INTO SuDungNguyenLieu (MaSuDung, MaDon, MaCongDoan, MaNguyenLieu, SoLuongSuDung) VALUES (%s, %s, %s, %s, %s)",
                (new_code('SD'), order_id, operation_id, material_id, quantity_used)
            )

        return True
