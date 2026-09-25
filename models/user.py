import secrets

from werkzeug.security import check_password_hash, generate_password_hash

from database.db import query_db, execute_db

class TaiKhoan:
    """Represents a user account in the workshop system."""
    ROLES = ['Admin', 'QuanLyXuong', 'ToTruong', 'NhanVien']
    STATUSES = ['Pending', 'Active', 'Suspended', 'Frozen']

    def __init__(self, data: dict):
        self.id = data.get('MaTaiKhoan')
        self.name = data.get('HoTen')
        self.email = data.get('Email')
        self.password_hash = data.get('MatKhau')
        self.role = data.get('VaiTro')
        self.status = data.get('TrangThai', 'Active')

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def has_role(self, *allowed_roles) -> bool:
        return self.role in allowed_roles

    @classmethod
    def get_by_id(cls, user_id: str):
        row = query_db("SELECT * FROM TaiKhoan WHERE MaTaiKhoan = %s", (user_id,), one=True)
        return cls(row) if row else None

    @classmethod
    def get_by_email(cls, email: str):
        row = query_db(
            "SELECT * FROM TaiKhoan WHERE LOWER(Email) = LOWER(%s)",
            (email,),
            one=True
        )
        return cls(row) if row else None

    @classmethod
    def get_all(cls):
        rows = query_db(
            "SELECT * FROM TaiKhoan WHERE TrangThai <> 'Deleted' ORDER BY MaTaiKhoan ASC"
        )
        return [cls(r) for r in rows]

    @classmethod
    def search(cls, q='', role='', status=''):
        conditions = ["TrangThai <> 'Deleted'"]
        args = []
        if q:
            conditions.append("(LOWER(MaTaiKhoan) LIKE %s OR LOWER(HoTen) LIKE %s OR LOWER(Email) LIKE %s)")
            args.extend((f'%{q.lower()}%', f'%{q.lower()}%', f'%{q.lower()}%'))
        if role == 'Unassigned':
            conditions.append("VaiTro = ''")
        elif role in cls.ROLES:
            conditions.append("VaiTro = %s")
            args.append(role)
        if status in cls.STATUSES:
            conditions.append("TrangThai = %s")
            args.append(status)
        rows = query_db(
            "SELECT * FROM TaiKhoan WHERE " + " AND ".join(conditions) + " ORDER BY MaTaiKhoan ASC",
            tuple(args)
        )
        return [cls(r) for r in rows]

    @classmethod
    def get_pending(cls, q=''):
        conditions = ["TrangThai = 'Pending'"]
        args = []
        if q:
            conditions.append("(LOWER(MaTaiKhoan) LIKE %s OR LOWER(HoTen) LIKE %s OR LOWER(Email) LIKE %s)")
            args.extend((f'%{q.lower()}%', f'%{q.lower()}%', f'%{q.lower()}%'))
        rows = query_db(
            "SELECT * FROM TaiKhoan WHERE " + " AND ".join(conditions) + " ORDER BY MaTaiKhoan DESC",
            tuple(args)
        )
        return [cls(r) for r in rows]

    @classmethod
    def get_system_users(cls, q='', role='', status=''):
        conditions = ["TrangThai <> 'Deleted'", "TrangThai <> 'Pending'"]
        args = []
        if q:
            conditions.append("(LOWER(MaTaiKhoan) LIKE %s OR LOWER(HoTen) LIKE %s OR LOWER(Email) LIKE %s)")
            args.extend((f'%{q.lower()}%', f'%{q.lower()}%', f'%{q.lower()}%'))
        if role in cls.ROLES:
            conditions.append("VaiTro = %s")
            args.append(role)
        if status in cls.STATUSES and status != 'Pending':
            conditions.append("TrangThai = %s")
            args.append(status)
        rows = query_db(
            "SELECT * FROM TaiKhoan WHERE " + " AND ".join(conditions) + " ORDER BY MaTaiKhoan ASC",
            tuple(args)
        )
        return [cls(r) for r in rows]

    @classmethod
    def get_account_counts(cls):
        rows = query_db("SELECT TrangThai FROM TaiKhoan WHERE TrangThai <> 'Deleted'")
        return {
            'system': sum(1 for r in rows if r['TrangThai'] != 'Pending'),
            'pending': sum(1 for r in rows if r['TrangThai'] == 'Pending'),
            'active': sum(1 for r in rows if r['TrangThai'] == 'Active'),
            'locked': sum(1 for r in rows if r['TrangThai'] in ('Suspended', 'Frozen'))
        }

    @classmethod
    def update_role(cls, user_id: str, new_role: str):
        if new_role not in ('QuanLyXuong', 'ToTruong', 'NhanVien'):
            raise ValueError(f"Vai trò không hợp lệ: {new_role}")
        user = cls.get_by_id(user_id)
        if not user or user.status in ('Pending', 'Deleted'):
            raise ValueError('Tài khoản không hợp lệ để đổi vai trò.')
        from database.db import transaction
        with transaction() as tx:
            if user.role == 'NhanVien' and new_role != 'NhanVien':
                tx.execute('DELETE FROM ThanhVienTo WHERE MaNhanVien = %s', (user_id,))
            if user.role == 'ToTruong' and new_role != 'ToTruong':
                tx.execute('DELETE FROM ThanhVienTo WHERE MaToTruong = %s', (user_id,))
            return tx.execute('UPDATE TaiKhoan SET VaiTro = %s WHERE MaTaiKhoan = %s',
                              (new_role, user_id))

    @classmethod
    def update_status(cls, user_id: str, new_status: str):
        if new_status not in cls.STATUSES:
            raise ValueError(f"Trạng thái không hợp lệ: {new_status}")
        user = cls.get_by_id(user_id)
        if not user:
            raise ValueError("Tài khoản không tồn tại.")
        if user.status == 'Deleted':
            raise ValueError('Tài khoản đã xóa không thể kích hoạt lại.')
        if new_status == 'Active' and (not user.role or user.status == 'Pending'):
            raise ValueError("Tài khoản chờ duyệt phải được Admin duyệt và cấp vai trò.")
        return execute_db(
            "UPDATE TaiKhoan SET TrangThai = %s WHERE MaTaiKhoan = %s",
            (new_status, user_id)
        )

    @classmethod
    def approve(cls, user_id: str, role: str):
        if role not in ('QuanLyXuong', 'ToTruong', 'NhanVien'):
            raise ValueError("Vai trò được duyệt không hợp lệ.")
        user = cls.get_by_id(user_id)
        if not user or user.status != 'Pending':
            raise ValueError("Tài khoản không ở trạng thái chờ duyệt.")
        from database.db import transaction
        with transaction() as tx:
            updated = tx.execute(
                "UPDATE TaiKhoan SET VaiTro = %s, TrangThai = 'Active' WHERE MaTaiKhoan = %s AND TrangThai = 'Pending'",
                (role, user_id)
            )
            if updated != 1:
                raise ValueError('Tài khoản không còn chờ duyệt.')

    @classmethod
    def delete(cls, user_id: str):
        # Keep the business code so historical production assignments remain valid,
        # while removing identity/login data and making the original email reusable.
        deleted_email = f"deleted-{user_id}@invalid.local"
        unusable_password = generate_password_hash(secrets.token_urlsafe(32))
        from database.db import transaction
        with transaction() as tx:
            tx.execute('DELETE FROM ThanhVienTo WHERE MaNhanVien = %s OR MaToTruong = %s',
                       (user_id, user_id))
            return tx.execute(
                "UPDATE TaiKhoan SET HoTen = %s, Email = %s, MatKhau = %s, VaiTro = %s, "
                "TrangThai = 'Deleted' WHERE MaTaiKhoan = %s",
                ('Tài khoản đã xóa', deleted_email, unusable_password, 'NhanVien', user_id)
            )
