"""Workshop manager controls which workers belong to each team leader."""

from database.db import execute_db, query_db, transaction
from models.user import TaiKhoan


class TeamService:
    @staticmethod
    def validate_leader(leader_id):
        leader = TaiKhoan.get_by_id(leader_id)
        if not leader or leader.role != 'ToTruong' or leader.status != 'Active':
            raise ValueError('Tổ trưởng được chọn không hợp lệ hoặc chưa hoạt động.')
        return leader

    @staticmethod
    def leader_by_worker():
        return {str(row['MaNhanVien']): str(row['MaToTruong']) for row in query_db(
            'SELECT MaNhanVien, MaToTruong FROM ThanhVienTo'
        )}

    @staticmethod
    def set_leader(admin, worker_id, leader_id):
        """Account administrator assigns or transfers a worker to one leader."""
        if admin.role != 'Admin':
            raise PermissionError('Chỉ Quản trị viên được gắn nhân viên vào tổ trong quản lý tài khoản.')
        worker = TaiKhoan.get_by_id(worker_id)
        if not worker or worker.role != 'NhanVien' or worker.status != 'Active':
            raise ValueError('Chỉ gắn nhân viên đang hoạt động vào tổ.')
        if leader_id:
            TeamService.validate_leader(leader_id)
        with transaction() as tx:
            tx.execute('DELETE FROM ThanhVienTo WHERE MaNhanVien = %s', (worker_id,))
            if leader_id:
                tx.execute('INSERT INTO ThanhVienTo (MaToTruong, MaNhanVien) VALUES (%s, %s)',
                           (leader_id, worker_id))

    @staticmethod
    def is_member(leader_id, worker_id):
        return bool(query_db(
            'SELECT 1 AS ok FROM ThanhVienTo WHERE MaToTruong = %s AND MaNhanVien = %s',
            (leader_id, worker_id), one=True
        ))

    @staticmethod
    def members(leader_id):
        return [TaiKhoan(row) for row in query_db(
            "SELECT t.* FROM TaiKhoan t JOIN ThanhVienTo m ON t.MaTaiKhoan = m.MaNhanVien "
            "WHERE m.MaToTruong = %s AND t.VaiTro = 'NhanVien' AND t.TrangThai = 'Active' "
            'ORDER BY t.HoTen', (leader_id,)
        )]

    @staticmethod
    def assignments():
        return query_db(
            'SELECT m.MaToTruong, m.MaNhanVien, l.HoTen AS TenToTruong, w.HoTen AS TenNhanVien '
            'FROM ThanhVienTo m JOIN TaiKhoan l ON m.MaToTruong = l.MaTaiKhoan '
            'JOIN TaiKhoan w ON m.MaNhanVien = w.MaTaiKhoan '
            'ORDER BY l.HoTen, w.HoTen'
        )

    @staticmethod
    def add(manager, leader_id, worker_id):
        if manager.role != 'QuanLyXuong':
            raise PermissionError('Chỉ Quản lý xưởng được quản lý thành viên tổ.')
        leader, worker = TaiKhoan.get_by_id(leader_id), TaiKhoan.get_by_id(worker_id)
        if not leader or leader.role != 'ToTruong' or leader.status != 'Active':
            raise ValueError('Tổ trưởng không hợp lệ hoặc chưa hoạt động.')
        if not worker or worker.role != 'NhanVien' or worker.status != 'Active':
            raise ValueError('Nhân viên không hợp lệ hoặc chưa hoạt động.')
        if TeamService.is_member(leader_id, worker_id):
            raise ValueError('Nhân viên đã thuộc tổ này.')
        current_team = query_db(
            'SELECT MaToTruong FROM ThanhVienTo WHERE MaNhanVien = %s',
            (worker_id,), one=True
        )
        if current_team:
            raise ValueError('Nhân viên đã thuộc một tổ khác; hãy gỡ khỏi tổ cũ trước.')
        execute_db('INSERT INTO ThanhVienTo (MaToTruong, MaNhanVien) VALUES (%s, %s)',
                   (leader_id, worker_id))

    @staticmethod
    def remove(manager, leader_id, worker_id):
        if manager.role != 'QuanLyXuong':
            raise PermissionError('Chỉ Quản lý xưởng được quản lý thành viên tổ.')
        execute_db('DELETE FROM ThanhVienTo WHERE MaToTruong = %s AND MaNhanVien = %s',
                   (leader_id, worker_id))
