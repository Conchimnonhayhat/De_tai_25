import pytest
from services.auth_service import AuthService
from models.user import TaiKhoan
from database.db import execute_db


@pytest.fixture(autouse=True)
def clean_account_feature_test_data():
    """Keep account-management tests isolated from the shared seeded database."""
    execute_db("DELETE FROM TaiKhoan WHERE Email LIKE %s", ("pytest-%",))
    yield
    execute_db("DELETE FROM TaiKhoan WHERE Email LIKE %s", ("pytest-%",))

def test_user_authentication_success():
    """Test FR-01: Valid user authentication with correct email and password."""
    user = AuthService.authenticate("manager@workshop.edu.vn", "123456")
    assert user is not None
    assert user.name == "Nguyễn Văn Quản Lý"
    assert user.role == "QuanLyXuong"

def test_user_authentication_failure():
    """Test FR-01: Authentication fails with wrong password."""
    user = AuthService.authenticate("manager@workshop.edu.vn", "wrong_password")
    assert user is None

def test_unauthenticated_access_redirect(client):
    """Test unauthenticated user accessing dashboard is redirected to login."""
    res = client.get('/dashboard')
    assert res.status_code == 302
    assert '/login' in res.headers['Location']

def test_worker_cannot_access_admin_route(worker_client):
    """Test FR-02 & NFR-03: Worker role is forbidden (403) from admin user management."""
    res = worker_client.get('/admin/users')
    assert res.status_code == 403

def test_admin_can_access_admin_route(admin_client):
    """Test FR-02: Admin role can successfully access user management."""
    res = admin_client.get('/admin/users')
    assert res.status_code == 200
    assert b"Danh S\xc3\xa1ch T\xc3\xa0i Kho\xe1\xba\xa3n" in res.data


def test_public_registration_waits_for_admin_approval(client):
    response = client.post('/register', data={
        'name': 'Nhân Viên Mới',
        'email': 'PYTEST-REGISTER@EXAMPLE.COM',
        'password': 'secret123',
        'password_confirmation': 'secret123',
        'role': 'Admin',  # Must be ignored by the server.
    })

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/login')
    user = TaiKhoan.get_by_email('pytest-register@example.com')
    assert user is not None
    assert user.role == ''
    assert user.status == 'Pending'
    assert user.check_password('secret123')
    assert AuthService.authenticate('pytest-register@example.com', 'secret123') is None


def test_admin_can_create_privileged_account(admin_client):
    response = admin_client.post('/admin/users/create', data={
        'name': 'Quản Lý Mới',
        'email': 'pytest-manager@example.com',
        'password': 'secret123',
        'role': 'QuanLyXuong',
    })

    assert response.status_code == 302
    user = TaiKhoan.get_by_email('pytest-manager@example.com')
    assert user is not None
    assert user.role == 'QuanLyXuong'


@pytest.mark.parametrize('status', ['Suspended', 'Frozen'])
def test_suspended_or_frozen_account_cannot_login(client, status):
    AuthService.create_user(
        f'Tài Khoản {status}',
        f'pytest-{status.lower()}@example.com',
        'secret123'
    )
    user = TaiKhoan.get_by_email(f'pytest-{status.lower()}@example.com')
    TaiKhoan.update_status(user.id, status)

    response = client.post('/login', data={
        'email': user.email,
        'password': 'secret123',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert 'đăng nhập' in response.get_data(as_text=True).lower()
    with client.session_transaction() as session_data:
        assert 'user_id' not in session_data


def test_freezing_account_invalidates_existing_session(client):
    AuthService.create_user(
        'Nhân Viên Có Phiên',
        'pytest-session@example.com',
        'secret123'
    )
    user = TaiKhoan.get_by_email('pytest-session@example.com')
    with client.session_transaction() as session_data:
        session_data['user_id'] = user.id
        session_data['user_name'] = user.name
        session_data['user_email'] = user.email
        session_data['user_role'] = user.role

    TaiKhoan.update_status(user.id, 'Frozen')
    response = client.get('/dashboard')

    assert response.status_code == 302
    assert '/login' in response.headers['Location']
    with client.session_transaction() as session_data:
        assert 'user_id' not in session_data


def test_admin_can_delete_account(admin_client):
    AuthService.create_user(
        'Tài Khoản Cần Xóa',
        'pytest-delete@example.com',
        'secret123'
    )
    user = TaiKhoan.get_by_email('pytest-delete@example.com')

    response = admin_client.post(f'/admin/users/{user.id}/delete')

    assert response.status_code == 302
    assert TaiKhoan.get_by_email('pytest-delete@example.com') is None
    # Deletion anonymizes the old row, so its email can be safely reused.
    AuthService.create_user(
        'Tài Khoản Đăng Ký Lại',
        'pytest-delete@example.com',
        'new-secret123'
    )
    assert TaiKhoan.get_by_email('pytest-delete@example.com').role == 'NhanVien'


def test_admin_cannot_disable_or_delete_own_account(admin_client):
    status_response = admin_client.post('/admin/users/1/status', data={'status': 'Frozen'})
    delete_response = admin_client.post('/admin/users/1/delete')

    assert status_response.status_code == 302
    assert delete_response.status_code == 302
    admin = TaiKhoan.get_by_id(1)
    assert admin is not None
    assert admin.status == 'Active'


def test_separated_pending_and_system_accounts(admin_client):
    """Test that pending approval accounts and system accounts are separated cleanly."""
    AuthService.register_candidate('Người Đăng Ký Chờ', 'pytest-sep-pending@example.com', 'secret123')
    AuthService.create_user('Nhân Viên Nội Bộ', 'pytest-sep-system@example.com', 'secret123', 'NhanVien')

    pending_user = TaiKhoan.get_by_email('pytest-sep-pending@example.com')
    system_user = TaiKhoan.get_by_email('pytest-sep-system@example.com')

    assert pending_user is not None and pending_user.status == 'Pending'
    assert system_user is not None and system_user.status == 'Active'

    # Model methods separation
    pending_list = TaiKhoan.get_pending()
    assert any(u.email == 'pytest-sep-pending@example.com' for u in pending_list)
    assert not any(u.email == 'pytest-sep-system@example.com' for u in pending_list)

    system_list = TaiKhoan.get_system_users()
    assert any(u.email == 'pytest-sep-system@example.com' for u in system_list)
    assert not any(u.email == 'pytest-sep-pending@example.com' for u in system_list)

    # Admin UI view separation
    response = admin_client.get('/admin/users')
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    assert 'Danh Sách Tài Khoản Chờ Phê Duyệt' in html
    assert 'Danh Sách Tài Khoản Hệ Thống' in html
    assert 'pytest-sep-pending@example.com' in html
    assert 'pytest-sep-system@example.com' in html

    # Approve the pending account -> now it moves to system users
    approve_res = admin_client.post(f'/admin/users/{pending_user.id}/approve', data={'role': 'ToTruong'})
    assert approve_res.status_code == 302

    pending_list_after = TaiKhoan.get_pending()
    system_list_after = TaiKhoan.get_system_users()
    assert not any(u.email == 'pytest-sep-pending@example.com' for u in pending_list_after)
    assert any(u.email == 'pytest-sep-pending@example.com' for u in system_list_after)

