from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.auth_service import AuthService, login_required, role_required
from models.user import TaiKhoan
from services.team_service import TeamService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('auth.manage_users' if session.get('user_role') == 'Admin' else 'workshop.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = AuthService.authenticate(email, password)
        if user:
            AuthService.login_user(user)
            flash(f'Chào mừng {user.name} ({user.role}) trở lại!', 'success')
            next_url = request.args.get('next')
            destination = url_for('auth.manage_users' if user.role == 'Admin' else 'workshop.dashboard')
            if user.role != 'Admin' and next_url and next_url.startswith('/') and not next_url.startswith('//'):
                destination = next_url
            return redirect(destination)
        else:
            account = TaiKhoan.get_by_email(email)
            if account and account.status == 'Suspended':
                flash('Tài khoản đã bị tạm dừng. Vui lòng liên hệ quản trị viên.', 'danger')
            elif account and account.status == 'Frozen':
                flash('Tài khoản đã bị đóng băng. Vui lòng liên hệ quản trị viên.', 'danger')
            elif account and account.status == 'Pending':
                flash('Tài khoản đang chờ quản trị viên xét duyệt.', 'warning')
            else:
                flash('Email hoặc mật khẩu không chính xác.', 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('auth.manage_users' if session.get('user_role') == 'Admin' else 'workshop.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        password_confirmation = request.form.get('password_confirmation', '')

        if password != password_confirmation:
            flash('Mật khẩu xác nhận không khớp.', 'danger')
        else:
            try:
                AuthService.register_candidate(name, email, password, request.form.get('account_code', ''))
                flash('Đã gửi đăng ký. Bạn có thể đăng nhập sau khi quản trị viên duyệt và cấp vai trò.', 'success')
                return redirect(url_for('auth.login'))
            except ValueError as exc:
                flash(str(exc), 'danger')
            except Exception:
                flash('Không thể tạo tài khoản. Vui lòng thử lại.', 'danger')

    return render_template('register.html')


@auth_bp.route('/logout', methods=['POST'])
def logout():
    AuthService.logout_user()
    flash('Bạn đã đăng xuất thành công.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/admin/users', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def manage_users():
    # Backward-compatible handler for the original role-update form.
    if request.method == 'POST':
        try:
            user = _get_managed_user(request.form.get('user_id', ''))
            if str(user.id) == str(session.get('user_id')):
                raise ValueError('Bạn không thể thay đổi vai trò của chính mình.')
            TaiKhoan.update_role(user.id, request.form.get('role', ''))
            flash(f'Đã cập nhật vai trò cho {user.name}.', 'success')
        except (TypeError, ValueError) as exc:
            flash(str(exc), 'danger')
        except Exception:
            flash('Không thể cập nhật vai trò tài khoản.', 'danger')
        return redirect(url_for('auth.manage_users'))

    q = request.args.get('q', '').strip()[:100]
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')
    active_tab = request.args.get('tab', 'all')
    if active_tab not in ('all', 'pending', 'system'):
        active_tab = 'all'

    # Query metrics and separated lists
    counts = TaiKhoan.get_account_counts()
    total_system = counts['system']
    total_pending = counts['pending']
    total_active = counts['active']
    total_locked = counts['locked']

    pending_users = TaiKhoan.get_pending(q=q)
    system_users = TaiKhoan.get_system_users(q=q, role=role_filter, status=status_filter)

    if status_filter == 'Pending':
        active_tab = 'pending'
    elif status_filter in ('Active', 'Suspended', 'Frozen') or role_filter:
        if active_tab == 'all':
            active_tab = 'system'

    filter_roles = [r for r in TaiKhoan.ROLES if r]

    return render_template(
        'admin_users.html',
        system_users=system_users,
        pending_users=pending_users,
        users=system_users,
        total_system=total_system,
        total_pending=total_pending,
        total_active=total_active,
        total_locked=total_locked,
        roles=('QuanLyXuong', 'ToTruong', 'NhanVien'),
        leaders=[u for u in TaiKhoan.get_system_users(status='Active') if u.role == 'ToTruong'],
        team_by_worker=TeamService.leader_by_worker(),
        filter_roles=filter_roles,
        statuses=['Active', 'Suspended', 'Frozen'],
        q=q, role_filter=role_filter, status_filter=status_filter,
        active_tab=active_tab
    )


def _get_managed_user(user_id):
    user = TaiKhoan.get_by_id(user_id)
    if not user:
        raise ValueError('Tài khoản không tồn tại.')
    return user


@auth_bp.route('/admin/users/create', methods=['POST'])
@login_required
@role_required('Admin')
def create_user():
    try:
        role = request.form.get('role', '')
        leader_id = request.form.get('leader_id', '').strip()
        if leader_id:
            if role != 'NhanVien':
                raise ValueError('Chỉ tài khoản Nhân viên được gắn vào tổ.')
            TeamService.validate_leader(leader_id)
        user_id = AuthService.create_user(
            request.form.get('name', ''),
            request.form.get('email', ''),
            request.form.get('password', ''),
            role,
            request.form.get('account_code', '')
        )
        if leader_id:
            TeamService.set_leader(AuthService.get_current_user(), user_id, leader_id)
        flash('Thêm tài khoản thành công!', 'success')
    except ValueError as exc:
        flash(str(exc), 'danger')
    except Exception:
        flash('Không thể thêm tài khoản. Vui lòng thử lại.', 'danger')
    tab = request.form.get('tab', request.args.get('tab', 'system'))
    return redirect(url_for('auth.manage_users', tab=tab))


@auth_bp.route('/admin/users/<user_id>/role', methods=['POST'])
@login_required
@role_required('Admin')
def update_user_role(user_id):
    try:
        user = _get_managed_user(user_id)
        if str(user.id) == str(session.get('user_id')):
            raise ValueError('Bạn không thể thay đổi vai trò của chính mình.')
        TaiKhoan.update_role(user.id, request.form.get('role', ''))
        flash(f'Đã cập nhật vai trò cho {user.name}.', 'success')
    except ValueError as exc:
        flash(str(exc), 'danger')
    except Exception:
        flash('Không thể cập nhật vai trò tài khoản.', 'danger')
    tab = request.form.get('tab', request.args.get('tab', 'system'))
    return redirect(url_for('auth.manage_users', tab=tab))


@auth_bp.route('/admin/users/<user_id>/approve', methods=['POST'])
@login_required
@role_required('Admin')
def approve_user(user_id):
    try:
        role = request.form.get('role', '')
        leader_id = request.form.get('leader_id', '').strip()
        if leader_id:
            if role != 'NhanVien':
                raise ValueError('Chỉ tài khoản Nhân viên được gắn vào tổ.')
            TeamService.validate_leader(leader_id)
        TaiKhoan.approve(user_id, role)
        if leader_id:
            TeamService.set_leader(AuthService.get_current_user(), user_id, leader_id)
        flash('Đã duyệt tài khoản và cấp vai trò thành công.', 'success')
    except ValueError as exc:
        flash(str(exc), 'danger')
    tab = request.form.get('tab', request.args.get('tab', 'pending'))
    return redirect(url_for('auth.manage_users', tab=tab))


@auth_bp.route('/admin/users/<user_id>/team', methods=['POST'])
@login_required
@role_required('Admin')
def update_user_team(user_id):
    try:
        TeamService.set_leader(AuthService.get_current_user(), user_id,
                               request.form.get('leader_id', '').strip())
        flash('Đã cập nhật tổ phụ trách cho nhân viên.', 'success')
    except ValueError as exc:
        flash(str(exc), 'danger')
    return redirect(url_for('auth.manage_users', tab='system'))


@auth_bp.route('/admin/users/<user_id>/status', methods=['POST'])
@login_required
@role_required('Admin')
def update_user_status(user_id):
    try:
        user = _get_managed_user(user_id)
        if str(user.id) == str(session.get('user_id')):
            raise ValueError('Bạn không thể khóa hoặc đổi trạng thái của chính mình.')
        new_status = request.form.get('status', '')
        TaiKhoan.update_status(user.id, new_status)
        flash(f'Đã cập nhật trạng thái cho {user.name}.', 'success')
    except ValueError as exc:
        flash(str(exc), 'danger')
    except Exception:
        flash('Không thể cập nhật trạng thái tài khoản.', 'danger')
    tab = request.form.get('tab', request.args.get('tab', 'system'))
    return redirect(url_for('auth.manage_users', tab=tab))


@auth_bp.route('/admin/users/<user_id>/delete', methods=['POST'])
@login_required
@role_required('Admin')
def delete_user(user_id):
    try:
        user = _get_managed_user(user_id)
        if str(user.id) == str(session.get('user_id')):
            raise ValueError('Bạn không thể xóa tài khoản đang đăng nhập.')
        TaiKhoan.delete(user.id)
        flash(f'Đã xóa tài khoản {user.name}.', 'success')
    except ValueError as exc:
        flash(str(exc), 'danger')
    except Exception:
        flash('Không thể xóa tài khoản. Vui lòng thử lại.', 'danger')
    tab = request.form.get('tab', request.args.get('tab', ''))
    if tab:
        return redirect(url_for('auth.manage_users', tab=tab))
    return redirect(url_for('auth.manage_users'))
