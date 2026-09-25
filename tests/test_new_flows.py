"""End-to-end checks for business codes and the missing workshop workflows."""

from database.db import query_db
from models.order import DonSanXuat, KeHoachSanXuat
from models.production import CongDoan, PhanCong
from models.product import DinhMucNguyenLieu, SanPham
from models.user import TaiKhoan
from services.auth_service import AuthService
from services.order_service import OrderService
from services.access_service import can_update_operation
from services.team_service import TeamService
import pytest


def test_alphanumeric_account_waits_for_approval(app):
    candidate = app.test_client()
    response = candidate.post('/register', data={
        'account_code': 'DTC12345', 'name': 'Nhân viên mã chữ số',
        'email': 'pytest-dtc12345@example.com', 'password': 'secret123',
        'password_confirmation': 'secret123',
    })
    assert response.status_code == 302
    user = TaiKhoan.get_by_id('DTC12345')
    assert user and user.status == 'Pending' and user.role == ''
    assert candidate.post('/login', data={'email': user.email, 'password': 'secret123'}).status_code == 200

    admin = app.test_client()
    with admin.session_transaction() as sess:
        sess['user_id'] = '1'
    assert admin.post('/admin/users/DTC12345/approve', data={'role': 'NhanVien'}).status_code == 302
    assert TaiKhoan.get_by_id('DTC12345').status == 'Active'
    assert candidate.post('/login', data={'email': user.email, 'password': 'secret123'}).status_code == 302


def test_new_product_can_be_edited_planned_and_produced(app):
    manager = app.test_client()
    with manager.session_transaction() as sess:
        sess['user_id'] = '2'
    created = manager.post('/products', data={
        'product_id': 'SPFLOW25', 'name': 'Sản phẩm thử luồng', 'unit': 'Cái', 'desc': 'Bản đầu',
        'bom_material_id[]': ['NL01'], 'bom_quantity[]': ['0.1250'], 'bom_note[]': ['Thép'],
    })
    assert created.status_code == 302
    assert SanPham.get_by_id('SPFLOW25')
    manager.get('/products')
    with manager.session_transaction() as sess:
        token = sess['_product_delete_token']
    edited = manager.post('/products/SPFLOW25/edit', data={
        'delete_token': token, 'name': 'Sản phẩm đã sửa', 'unit': 'Bộ', 'desc': 'Bản mới',
        'bom_material_id[]': ['NL01'], 'bom_quantity[]': ['0.2500'], 'bom_note[]': ['Đã chỉnh'],
    })
    assert edited.status_code == 302
    assert SanPham.get_by_id('SPFLOW25').name == 'Sản phẩm đã sửa'
    assert DinhMucNguyenLieu.get_by_product('SPFLOW25')[0].standard_qty == 0.25

    assert manager.post('/products/SPFLOW25/operations', data={
        'name': 'Cắt thử', 'step_order': 1, 'desc': 'Bước đầu',
    }).status_code == 302
    operation = CongDoan.get_by_product('SPFLOW25')[0]
    assert operation.id.startswith('CD')
    assert manager.post('/orders', data={
        'product_id': 'SPFLOW25', 'quantity': 3, 'due_date': '2026-12-01',
    }).status_code == 200
    order = DonSanXuat.search(q='SPFLOW25')[-1]
    assert order.id.startswith('DSX')
    assert manager.post(f'/orders/{order.id}/plans', data={
        'start_date': '2026-11-01', 'end_date': '2026-11-30',
    }).status_code == 302
    assert KeHoachSanXuat.get_by_order(order.id)
    assert manager.post('/production/assign', data={
        'order_id': order.id, 'operation_id': operation.id, 'user_id': '3',
        'assign_date': '2026-11-01',
    }).status_code == 302
    leader = app.test_client()
    with leader.session_transaction() as sess:
        sess['user_id'] = '3'
    assert leader.post('/production/assign', data={
        'order_id': order.id, 'operation_id': operation.id, 'user_id': '4',
        'assign_date': '2026-11-01',
    }).status_code == 302
    assert PhanCong.exists(operation.id, '4', order.id)

    worker = app.test_client()
    with worker.session_transaction() as sess:
        sess['user_id'] = '4'
    assert worker.post('/production', data={
        'action': 'update_progress', 'order_id': order.id,
        'operation_id': operation.id, 'additional_qty': 3,
    }).status_code == 302
    assert DonSanXuat.get_by_id(order.id).status == 'Hoàn thành'


def test_worker_material_report_only_deducts_after_manager_approval(app):
    worker = app.test_client()
    manager = app.test_client()
    with worker.session_transaction() as sess:
        sess['user_id'] = '4'
    with manager.session_transaction() as sess:
        sess['user_id'] = '2'
    stock_before = query_db("SELECT SoLuongTon FROM NguyenLieu WHERE MaNguyenLieu = 'NL02'", one=True)['SoLuongTon']
    page = worker.get('/production?order_id=25').get_data(as_text=True)
    assert 'Báo vật tư đã dùng' in page
    assert 'Tồn:' not in page
    assert worker.post('/production', data={
        'action': 'report_material', 'order_id': '25', 'operation_id': '102',
        'material_id': 'NL02', 'quantity_used': '1.2500',
    }).status_code == 302
    report = query_db("SELECT * FROM BaoVatTu WHERE MaTaiKhoan = '4' ORDER BY NgayBaoCao DESC LIMIT 1", one=True)
    assert report['TrangThai'] == 'Pending'
    assert query_db("SELECT SoLuongTon FROM NguyenLieu WHERE MaNguyenLieu = 'NL02'", one=True)['SoLuongTon'] == stock_before
    assert manager.post(f"/material-reports/{report['MaBaoVatTu']}/approve").status_code == 302
    stock_after = query_db("SELECT SoLuongTon FROM NguyenLieu WHERE MaNguyenLieu = 'NL02'", one=True)['SoLuongTon']
    assert stock_after == stock_before - 1.25
    assert manager.post(f"/material-reports/{report['MaBaoVatTu']}/approve").status_code == 302
    assert query_db("SELECT SoLuongTon FROM NguyenLieu WHERE MaNguyenLieu = 'NL02'", one=True)['SoLuongTon'] == stock_after


def test_csrf_rejects_unprotected_form_post(app):
    app.config['TESTING'] = False
    client = app.test_client()
    client.get('/login')
    assert client.post('/login', data={
        'email': 'manager@workshop.edu.vn', 'password': '123456',
    }).status_code == 400
    with client.session_transaction() as sess:
        token = sess['_csrf_token']
    assert client.post('/login', data={
        'csrf_token': token, 'email': 'manager@workshop.edu.vn', 'password': '123456',
    }).status_code == 302
    assert client.post('/products/SP01/operations', data={
        'name': 'Không hợp lệ', 'step_order': 9,
    }).status_code == 400


def test_leader_assigns_only_own_team_on_own_order(app):
    leader, manager, admin = (app.test_client() for _ in range(3))
    for client, user_id in ((leader, '3'), (manager, '2'), (admin, '1')):
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
    assert TeamService.is_member('3', '4')
    assert admin.get('/teams').status_code == 403
    assert manager.get('/teams').status_code == 200
    response = leader.post('/production/assign', data={
        'order_id': '25', 'operation_id': '101', 'user_id': '4', 'assign_date': '2026-09-25',
    })
    assert response.status_code == 302
    assert PhanCong.exists('101', '4', '25')

    stranger_id = AuthService.create_user('Ngoài tổ', 'pytest-outside-team@example.com', 'secret123')
    assert leader.post('/production/assign', data={
        'order_id': '25', 'operation_id': '101', 'user_id': stranger_id,
        'assign_date': '2026-09-25',
    }).status_code == 403
    assert leader.post('/production/assign', data={
        'order_id': '26', 'operation_id': '101', 'user_id': '4',
        'assign_date': '2026-09-25',
    }).status_code == 403
    assignment = next(item for item in PhanCong.get_by_order('25')
                      if item.operation_id == '101' and item.user_id == '4')
    PhanCong.delete_assignment(assignment.id)


def test_leader_assigns_multiple_workers_to_one_operation_atomically(app):
    manager, leader = app.test_client(), app.test_client()
    with manager.session_transaction() as sess:
        sess['user_id'] = '2'
    with leader.session_transaction() as sess:
        sess['user_id'] = '3'
    order = OrderService.create_order('SP01', 5, '2026-12-20')
    first = AuthService.create_user('Nhân viên một', 'pytest-assign-one@example.com', 'secret123')
    second = AuthService.create_user('Nhân viên hai', 'pytest-assign-two@example.com', 'secret123')
    third = AuthService.create_user('Nhân viên ba', 'pytest-assign-three@example.com', 'secret123')
    admin = TaiKhoan.get_by_id('1')
    for worker_id in (first, second, third):
        TeamService.set_leader(admin, worker_id, '3')
    assert manager.post('/production/assign', data={
        'order_id': order.id, 'operation_id': '101',
        'user_id': '3', 'assign_date': '2026-09-25',
    }).status_code == 302

    page = leader.get(f'/production?order_id={order.id}').get_data(as_text=True)
    assert 'id="add-assignment-user"' in page
    assert 'name="user_ids[]"' in page

    response = leader.post('/production/assign', data={
        'order_id': order.id, 'operation_id': '101',
        'user_ids[]': [first, second], 'assign_date': '2026-09-25',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Đã phân công 2 người' in response.get_data(as_text=True)
    assert PhanCong.exists('101', first, order.id)
    assert PhanCong.exists('101', second, order.id)

    duplicate = leader.post('/production/assign', data={
        'order_id': order.id, 'operation_id': '101',
        'user_ids[]': [third, first], 'assign_date': '2026-09-25',
    })
    assert duplicate.status_code == 302
    assert not PhanCong.exists('101', third, order.id)


def test_leader_batch_assignment_rejects_outsider_without_partial_save(app):
    manager, leader = app.test_client(), app.test_client()
    for client, user_id in ((manager, '2'), (leader, '3')):
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
    order = OrderService.create_order('SP01', 5, '2026-12-21')
    assert manager.post('/production/assign', data={
        'order_id': order.id, 'operation_id': '101',
        'user_id': '3', 'assign_date': '2026-09-25',
    }).status_code == 302
    outsider = AuthService.create_user('Ngoài tổ thử', 'pytest-batch-outsider@example.com', 'secret123')

    response = leader.post('/production/assign', data={
        'order_id': order.id, 'operation_id': '101',
        'user_ids[]': ['4', outsider], 'assign_date': '2026-09-25',
    })
    assert response.status_code == 403
    assert not PhanCong.exists('101', '4', order.id)
    assert not PhanCong.exists('101', outsider, order.id)


def test_manager_gives_one_operation_to_leader_then_leader_delegates_team(app):
    manager, first_leader, second_leader = (app.test_client() for _ in range(3))
    for client, user_id in ((manager, '2'), (first_leader, '3'), (second_leader, 'TTDEMO02')):
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
    order = OrderService.create_order('SP01', 6, '2026-12-22')

    manager_page = manager.get(f'/production?order_id={order.id}').get_data(as_text=True)
    assert 'Tổ trưởng phụ trách' in manager_page
    assert 'id="add-assignment-user"' not in manager_page
    assert manager.post('/production/assign', data={
        'order_id': order.id, 'operation_id': '101', 'user_id': 'NVDEMO11',
        'assign_date': '2026-09-25',
    }).status_code == 302
    assert not PhanCong.exists('101', 'NVDEMO11', order.id)

    assert manager.post('/production/assign', data={
        'order_id': order.id, 'operation_id': '101', 'user_id': '3',
        'assign_date': '2026-09-25',
    }).status_code == 302
    assert PhanCong.exists('101', '3', order.id)
    assert not can_update_operation(TaiKhoan.get_by_id('3'), order.id, '102')
    assert first_leader.post('/production/assign', data={
        'order_id': order.id, 'operation_id': '102', 'user_id': 'NVDEMO11',
        'assign_date': '2026-09-25',
    }).status_code == 403
    assert first_leader.post('/production/assign', data={
        'order_id': order.id, 'operation_id': '101',
        'user_ids[]': ['NVDEMO11', 'NVDEMO12'], 'assign_date': '2026-09-25',
    }).status_code == 302
    assert PhanCong.exists('101', 'NVDEMO11', order.id)
    assert PhanCong.exists('101', 'NVDEMO12', order.id)
    leader_assignment = next(a for a in PhanCong.get_by_order(order.id)
                             if a.operation_id == '101' and a.user_id == '3')
    removal = manager.post(f'/production/unassign/{leader_assignment.id}',
                           data={'order_id': order.id}, follow_redirects=True)
    assert 'Hãy gỡ phân công nhân viên' in removal.get_data(as_text=True)
    assert PhanCong.exists('101', '3', order.id)

    assert manager.post('/production/assign', data={
        'order_id': order.id, 'operation_id': '101', 'user_id': 'TTDEMO02',
        'assign_date': '2026-09-25',
    }).status_code == 302
    assert not PhanCong.exists('101', 'TTDEMO02', order.id)
    assert manager.post('/production/assign', data={
        'order_id': order.id, 'operation_id': '102', 'user_id': 'TTDEMO02',
        'assign_date': '2026-09-25',
    }).status_code == 302
    assert second_leader.post('/production/assign', data={
        'order_id': order.id, 'operation_id': '102',
        'user_ids[]': ['NVDEMO21', 'NVDEMO22'], 'assign_date': '2026-09-25',
    }).status_code == 302
    assert PhanCong.exists('102', 'NVDEMO21', order.id)
    assert PhanCong.exists('102', 'NVDEMO22', order.id)


def test_admin_can_set_and_transfer_worker_team_from_account_page(app):
    admin, manager = app.test_client(), app.test_client()
    for client, user_id in ((admin, '1'), (manager, '2')):
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
    assert admin.post('/admin/users/create', data={
        'account_code': 'NVTEAMTEST', 'name': 'Nhân viên thử tổ',
        'email': 'pytest-team-account@example.com', 'password': 'secret123',
        'role': 'NhanVien', 'leader_id': '3',
    }).status_code == 302
    assert TeamService.is_member('3', 'NVTEAMTEST')
    assert manager.post('/admin/users/NVTEAMTEST/team', data={'leader_id': 'TTDEMO02'}).status_code == 403
    assert admin.post('/admin/users/NVTEAMTEST/team', data={'leader_id': 'TTDEMO02'}).status_code == 302
    assert TeamService.is_member('TTDEMO02', 'NVTEAMTEST')
    assert not TeamService.is_member('3', 'NVTEAMTEST')


def test_seeded_demo_teams_have_working_accounts(app):
    for email, code in (
        ('demo.leader2@workshop.edu.vn', 'TTDEMO02'),
        ('demo.worker1a@workshop.edu.vn', 'NVDEMO11'),
        ('demo.worker1b@workshop.edu.vn', 'NVDEMO12'),
        ('demo.worker2a@workshop.edu.vn', 'NVDEMO21'),
        ('demo.worker2b@workshop.edu.vn', 'NVDEMO22'),
    ):
        assert AuthService.authenticate(email, '123456').id == code
    assert TeamService.is_member('3', 'NVDEMO11')
    assert TeamService.is_member('TTDEMO02', 'NVDEMO21')


def test_worker_cannot_be_in_two_teams(app):
    manager = TaiKhoan.get_by_id('2')
    another_leader = AuthService.create_user('Tổ trưởng thứ hai', 'pytest-leader-two@example.com', 'secret123')
    from database.db import execute_db
    execute_db("UPDATE TaiKhoan SET VaiTro = 'ToTruong', TrangThai = 'Active' WHERE MaTaiKhoan = %s",
               (another_leader,))
    with pytest.raises(ValueError, match='tổ khác'):
        TeamService.add(manager, another_leader, '4')


def test_order_rejects_invalid_due_date(app):
    from services.order_service import OrderService
    with pytest.raises(ValueError, match='YYYY-MM-DD'):
        OrderService.create_order('SP01', 5, '2026-99-99')


def test_deleted_account_cannot_be_reactivated(app):
    code = AuthService.create_user('Tài khoản xóa', 'pytest-deleted@example.com', 'secret123')
    TaiKhoan.delete(code)
    with pytest.raises(ValueError, match='không thể kích hoạt'):
        TaiKhoan.update_status(code, 'Active')
    with pytest.raises(ValueError, match='không hợp lệ'):
        TaiKhoan.update_role(code, 'QuanLyXuong')


def test_manager_can_delete_production_order(app):
    manager = app.test_client()
    with manager.session_transaction() as sess:
        sess['user_id'] = '2'

    # Create an order
    assert manager.post('/orders', data={
        'product_id': 'SP01', 'quantity': 8, 'due_date': '2026-12-15', 'note': 'Đơn sắp xóa',
    }).status_code == 200

    order_row = query_db("SELECT MaDon FROM DonSanXuat WHERE GhiChu = %s", ('Đơn sắp xóa',), one=True)
    order = DonSanXuat.get_by_id(order_row['MaDon'])
    assert order is not None

    # Get the order delete token
    manager.get('/orders')
    with manager.session_transaction() as sess:
        del_token = sess['_order_delete_token']

    # Manager deletes order
    res = manager.post(f'/orders/{order.id}/delete', data={'delete_token': del_token})
    assert res.status_code == 302
    assert DonSanXuat.get_by_id(order.id) is None


def test_non_manager_cannot_delete_order(app):
    worker = app.test_client()
    with worker.session_transaction() as sess:
        sess['user_id'] = '4'
    res = worker.post('/orders/25/delete', data={'delete_token': 'dummy'})
    assert res.status_code == 403


def test_manager_can_edit_production_order(app):
    manager = app.test_client()
    with manager.session_transaction() as sess:
        sess['user_id'] = '2'

    # Create an order
    assert manager.post('/orders', data={
        'product_id': 'SP01', 'quantity': 5, 'due_date': '2026-11-20', 'note': 'Bản gốc',
    }).status_code == 200
    order_row = query_db("SELECT MaDon FROM DonSanXuat WHERE GhiChu = %s", ('Bản gốc',), one=True)
    order = DonSanXuat.get_by_id(order_row['MaDon'])

    # Edit the order
    res = manager.post(f'/orders/{order.id}/edit', data={
        'product_id': 'SP01', 'quantity': 12, 'due_date': '2026-12-25',
        'note': 'Đã sửa qua web', 'status': 'Đang thực hiện'
    })
    assert res.status_code == 302
    updated = DonSanXuat.get_by_id(order.id)
    assert updated.quantity_requested == 12
    assert updated.due_date == '2026-12-25'
    assert updated.note == 'Đã sửa qua web'
    assert updated.status == 'Đang thực hiện'


def test_non_manager_cannot_edit_order(app):
    worker = app.test_client()
    with worker.session_transaction() as sess:
        sess['user_id'] = '4'
    res = worker.post('/orders/25/edit', data={
        'product_id': 'SP01', 'quantity': 99, 'due_date': '2026-12-31'
    })
    assert res.status_code == 403
