import re
from functools import wraps

from flask import session, redirect, url_for, flash, abort, jsonify, request
from werkzeug.security import generate_password_hash

from models.user import TaiKhoan
from database.db import execute_db
from services.identifiers import new_code, normalize_code


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

class AuthService:
    """Manages authentication, session tracking, and role-based permissions."""
    
    @staticmethod
    def authenticate(email: str, password: str):
        user = TaiKhoan.get_by_email(email)
        if not user or user.status != 'Active':
            return None
        if not user.check_password(password):
            return None
        return user

    @staticmethod
    def create_user(name: str, email: str, password: str, role: str = 'NhanVien', account_code: str = ''):
        name = (name or '').strip()
        email = (email or '').strip().lower()

        if len(name) < 2 or len(name) > 100:
            raise ValueError("Họ và tên phải có từ 2 đến 100 ký tự.")
        if len(email) > 100 or not EMAIL_PATTERN.match(email):
            raise ValueError("Email không đúng định dạng.")
        if len(password or '') < 6:
            raise ValueError("Mật khẩu phải có ít nhất 6 ký tự.")
        if role not in ('QuanLyXuong', 'ToTruong', 'NhanVien'):
            raise ValueError(f"Vai trò không hợp lệ: {role}")
        if TaiKhoan.get_by_email(email):
            raise ValueError("Email đã tồn tại trong hệ thống.")
        
        code = normalize_code(account_code or new_code('DTC'), 'Mã tài khoản')
        if TaiKhoan.get_by_id(code):
            raise ValueError('Mã tài khoản đã tồn tại.')
        pwd_hash = generate_password_hash(password)
        sql = "INSERT INTO TaiKhoan (MaTaiKhoan, HoTen, Email, MatKhau, VaiTro, TrangThai) VALUES (%s, %s, %s, %s, %s, 'Active')"
        execute_db(sql, (code, name, email, pwd_hash, role))
        return code

    @staticmethod
    def register_candidate(name: str, email: str, password: str, account_code: str = ''):
        """Public registration creates no business role or login permission."""
        name = (name or '').strip()
        email = (email or '').strip().lower()
        if len(name) < 2 or len(name) > 100:
            raise ValueError("Họ và tên phải có từ 2 đến 100 ký tự.")
        if len(email) > 100 or not EMAIL_PATTERN.match(email):
            raise ValueError("Email không đúng định dạng.")
        if len(password or '') < 6:
            raise ValueError("Mật khẩu phải có ít nhất 6 ký tự.")
        if TaiKhoan.get_by_email(email):
            raise ValueError("Email đã tồn tại trong hệ thống.")
        code = normalize_code(account_code or new_code('DTC'), 'Mã tài khoản')
        if TaiKhoan.get_by_id(code):
            raise ValueError('Mã tài khoản đã tồn tại.')
        execute_db(
            "INSERT INTO TaiKhoan (MaTaiKhoan, HoTen, Email, MatKhau, VaiTro, TrangThai) VALUES (%s, %s, %s, %s, %s, %s)",
            (code, name, email, generate_password_hash(password), '', 'Pending')
        )
        return code

    @staticmethod
    def login_user(user: TaiKhoan):
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_email'] = user.email
        session['user_role'] = user.role

    @staticmethod
    def logout_user():
        session.clear()

    @staticmethod
    def get_current_user():
        user_id = session.get('user_id')
        if not user_id:
            return None
        return TaiKhoan.get_by_id(user_id)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = AuthService.get_current_user() if 'user_id' in session else None
        if not user or user.status != 'Active':
            was_logged_in = 'user_id' in session
            blocked_status = user.status if user else None
            session.clear()
            if request.path.startswith('/api/'):
                message = 'Tài khoản đã bị vô hiệu hóa' if blocked_status else 'Vui lòng đăng nhập'
                return jsonify({'error': 'Unauthorized', 'message': message}), 401
            if was_logged_in and blocked_status:
                flash('Tài khoản của bạn đã bị tạm dừng hoặc đóng băng.', 'danger')
            else:
                flash('Vui lòng đăng nhập để tiếp tục.', 'warning')
            return redirect(url_for('auth.login', next=request.url))

        # Keep session identity and permissions synchronized after admin changes.
        session['user_name'] = user.name
        session['user_email'] = user.email
        session['user_role'] = user.role
        return f(*args, **kwargs)
    return decorated_function


def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = AuthService.get_current_user() if 'user_id' in session else None
            if not user or user.status != 'Active':
                session.clear()
                if request.path.startswith('/api/'):
                    return jsonify({'error': 'Unauthorized', 'message': 'Vui lòng đăng nhập'}), 401
                return redirect(url_for('auth.login'))
            session['user_role'] = user.role
            if user.role not in allowed_roles:
                if request.path.startswith('/api/'):
                    return jsonify({'error': 'Forbidden', 'message': 'Bạn không có quyền thực hiện thao tác này'}), 403
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
