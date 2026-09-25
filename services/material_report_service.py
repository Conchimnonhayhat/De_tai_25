"""Reports of material use are separate from approved inventory movements."""

from decimal import Decimal, InvalidOperation

from database.db import query_db, transaction
from services.access_service import can_update_operation, can_view_order
from services.identifiers import new_code


class MaterialReportService:
    @staticmethod
    def submit(user, order_id, operation_id, material_id, quantity):
        if user.role not in ('ToTruong', 'NhanVien') or not can_update_operation(user, order_id, operation_id):
            raise PermissionError('Công đoạn không được phân công cho bạn.')
        try:
            amount = Decimal(str(quantity))
        except (InvalidOperation, TypeError):
            raise ValueError('Số lượng vật tư không hợp lệ.') from None
        if (not amount.is_finite() or amount <= 0 or
                amount > Decimal('99999999999999.9999') or amount.as_tuple().exponent < -4):
            raise ValueError('Số lượng vật tư phải lớn hơn 0, tối đa 4 chữ số thập phân.')
        valid = query_db(
            'SELECT 1 AS ok FROM DonSanXuat d '
            'JOIN CongDoan c ON c.MaSanPham = d.MaSanPham '
            'JOIN DinhMucNguyenLieu b ON b.MaSanPham = d.MaSanPham '
            'WHERE d.MaDon = %s AND c.MaCongDoan = %s AND b.MaNguyenLieu = %s',
            (order_id, operation_id, material_id), one=True
        )
        if not valid:
            raise ValueError('Vật tư hoặc công đoạn không thuộc sản phẩm của đơn này.')
        code = new_code('BVT')
        with transaction() as tx:
            tx.execute(
                'INSERT INTO BaoVatTu (MaBaoVatTu, MaDon, MaCongDoan, MaNguyenLieu, MaTaiKhoan, SoLuongBaoCao) '
                'VALUES (%s, %s, %s, %s, %s, %s)',
                (code, order_id, operation_id, material_id, user.id, str(amount))
            )
        return code

    @staticmethod
    def get_by_order(user, order_id):
        if not can_view_order(user, order_id):
            raise PermissionError('Không có quyền xem đơn này.')
        if user.role == 'QuanLyXuong':
            where, args = 'r.MaDon = %s', (order_id,)
        elif user.role in ('ToTruong', 'NhanVien'):
            where, args = 'r.MaDon = %s AND r.MaTaiKhoan = %s', (order_id, user.id)
        else:
            raise PermissionError('Không có quyền xem phiếu vật tư.')
        return query_db(
            'SELECT r.*, n.TenNguyenLieu, n.DonViTinh, t.HoTen AS NguoiBao '
            'FROM BaoVatTu r JOIN NguyenLieu n ON r.MaNguyenLieu = n.MaNguyenLieu '
            'JOIN TaiKhoan t ON r.MaTaiKhoan = t.MaTaiKhoan '
            f'WHERE {where} ORDER BY r.NgayBaoCao DESC, r.MaBaoVatTu DESC', args
        )

    @staticmethod
    def approve(manager, report_id):
        if manager.role != 'QuanLyXuong':
            raise PermissionError('Chỉ Quản lý xưởng được duyệt xuất kho.')
        with transaction() as tx:
            claimed = tx.execute(
                "UPDATE BaoVatTu SET TrangThai = 'Processing' WHERE MaBaoVatTu = %s AND TrangThai = 'Pending'",
                (report_id,)
            )
            if claimed != 1:
                raise ValueError('Phiếu không còn chờ duyệt hoặc không tồn tại.')
            report = tx.query('SELECT * FROM BaoVatTu WHERE MaBaoVatTu = %s', (report_id,), one_row=True)
            used = tx.execute(
                'UPDATE NguyenLieu SET SoLuongTon = SoLuongTon - %s, NgayCapNhat = CURRENT_TIMESTAMP '
                'WHERE MaNguyenLieu = %s AND SoLuongTon >= %s',
                (report['SoLuongBaoCao'], report['MaNguyenLieu'], report['SoLuongBaoCao'])
            )
            if used != 1:
                raise ValueError('Tồn kho không đủ để duyệt phiếu vật tư.')
            usage_id = new_code('SD')
            tx.execute(
                'INSERT INTO SuDungNguyenLieu (MaSuDung, MaDon, MaCongDoan, MaNguyenLieu, SoLuongSuDung) '
                'VALUES (%s, %s, %s, %s, %s)',
                (usage_id, report['MaDon'], report['MaCongDoan'], report['MaNguyenLieu'], report['SoLuongBaoCao'])
            )
            tx.execute(
                "UPDATE BaoVatTu SET TrangThai = 'Approved', NgayDuyet = CURRENT_TIMESTAMP, "
                'MaNguoiDuyet = %s, MaSuDung = %s WHERE MaBaoVatTu = %s',
                (manager.id, usage_id, report_id)
            )
        return report['MaDon']
