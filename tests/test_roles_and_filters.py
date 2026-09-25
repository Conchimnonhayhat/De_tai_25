"""Checks the practical separation of duties and scoped list filters."""

from datetime import date

from database.db import query_db
from models.user import TaiKhoan
from models.order import DonSanXuat
from services.order_service import OrderService


def login(client, email):
    response = client.post('/login', data={'email': email, 'password': '123456'})
    assert response.status_code == 302


def test_admin_only_manages_accounts(admin_client):
    assert admin_client.get('/admin/users').status_code == 200
    for path in ('/dashboard', '/products', '/orders', '/production', '/inventory',
                 '/statistics', '/daily-reports', '/ai/assistant'):
        assert admin_client.get(path).status_code == 403, path
    assert admin_client.post('/api/progress/update', json={
        'order_id': 25, 'operation_id': 101, 'additional_qty': 1
    }).status_code == 403


def test_registration_requires_admin_approval(app):
    client = app.test_client()
    admin_client = app.test_client()
    email = 'pytest-pending-review@example.com'
    response = client.post('/register', data={
        'name': 'Người chờ duyệt', 'email': email,
        'password': 'secret123', 'password_confirmation': 'secret123', 'role': 'Admin'
    })
    assert response.status_code == 302
    user = TaiKhoan.get_by_email(email)
    assert (user.role, user.status) == ('', 'Pending')
    assert client.post('/login', data={'email': email, 'password': 'secret123'}).status_code == 200
    login(admin_client, 'admin@workshop.edu.vn')
    assert admin_client.post(f'/admin/users/{user.id}/approve', data={'role': 'NhanVien'}).status_code == 302
    user = TaiKhoan.get_by_email(email)
    assert (user.role, user.status) == ('NhanVien', 'Active')
    assert client.post('/login', data={'email': email, 'password': 'secret123'}).status_code == 302


def test_worker_cannot_see_or_change_unassigned_work(worker_client):
    assert worker_client.get('/inventory').status_code == 403
    assert worker_client.get('/statistics').status_code == 403
    assert worker_client.get('/ai/assistant').status_code == 403
    assert worker_client.get('/production?order_id=26').status_code == 403
    response = worker_client.get('/orders?q=26')
    assert response.status_code == 200
    assert 'Đơn #26' not in response.get_data(as_text=True)
    before = query_db("SELECT SoLuongTon FROM NguyenLieu WHERE MaNguyenLieu = 'NL01'", one=True)['SoLuongTon']
    assert worker_client.post('/api/progress/update', json={
        'order_id': 25, 'operation_id': 101, 'additional_qty': 1
    }).status_code == 403
    assert worker_client.post('/production', data={
        'action': 'record_material', 'order_id': 25, 'operation_id': 102,
        'material_id': 'NL01', 'quantity_used': 1
    }).status_code == 403
    after = query_db("SELECT SoLuongTon FROM NguyenLieu WHERE MaNguyenLieu = 'NL01'", one=True)['SoLuongTon']
    assert after == before


def test_leader_can_see_stock_but_cannot_bypass_ai_priority(client):
    login(client, 'leader@workshop.edu.vn')
    assert client.get('/inventory').status_code == 200
    assert client.post('/production', data={
        'action': 'record_material', 'order_id': 25, 'operation_id': 101,
        'material_id': 'NL01', 'quantity_used': 1
    }).status_code == 403
    assert client.post('/api/ai/progress-summary', json={'order_id': 26}).status_code == 403
    assert client.post('/api/ai/progress-summary', json={'prompt': 'gợi ý ưu tiên đơn'}).status_code == 403


def test_only_manager_can_create_and_receive_material(app):
    manager, leader, admin, worker = (app.test_client() for _ in range(4))
    for client, email in ((manager, 'manager@workshop.edu.vn'), (leader, 'leader@workshop.edu.vn'),
                          (admin, 'admin@workshop.edu.vn'), (worker, 'worker@workshop.edu.vn')):
        login(client, email)
    payload = {'action': 'create', 'material_id': 'NL-ROLE-TEST', 'name': 'Vật tư kiểm thử',
               'unit': 'cái', 'opening_stock': 5}
    for client in (leader, admin, worker):
        assert client.post('/inventory', data=payload).status_code == 403
    assert manager.post('/inventory', data=payload).status_code == 302
    assert manager.post('/inventory', data={
        'action': 'receive', 'material_id': 'NL-ROLE-TEST', 'quantity': 3
    }).status_code == 302
    assert query_db("SELECT SoLuongTon FROM NguyenLieu WHERE MaNguyenLieu = 'NL-ROLE-TEST'", one=True)['SoLuongTon'] == 8


def test_search_and_filter_respect_scope(app):
    auth_client, worker_client, admin_client = (app.test_client() for _ in range(3))
    login(auth_client, 'manager@workshop.edu.vn')
    login(worker_client, 'worker@workshop.edu.vn')
    login(admin_client, 'admin@workshop.edu.vn')
    assert 'SP02' in auth_client.get('/products?q=SP02').get_data(as_text=True)
    assert 'SP01' not in auth_client.get('/products?q=SP02').get_data(as_text=True)
    orders = auth_client.get('/orders?status=Mới+tạo&q=26').get_data(as_text=True)
    assert 'Đơn #26' in orders and 'Đơn #25' not in orders
    assert 'Đơn #26' not in worker_client.get('/orders?q=26').get_data(as_text=True)
    material = auth_client.get('/inventory?q=NL03').get_data(as_text=True)
    table_rows = material.split('<tbody>', 1)[1].split('</tbody>', 1)[0]
    assert 'NL03' in table_rows and 'NL01' not in table_rows
    accounts = admin_client.get('/admin/users?role=ToTruong&q=leader').get_data(as_text=True)
    assert 'leader@workshop.edu.vn' in accounts and 'worker@workshop.edu.vn' not in accounts


def test_order_filters_combine_dates_product_operation_and_leader(app):
    manager, leader, worker = (app.test_client() for _ in range(3))
    for client, user_id in ((manager, '2'), (leader, '3'), (worker, '4')):
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
    order = OrderService.create_order('SP01', 7, '2027-04-05', 'Đơn lọc thử nghiệm')
    for user_id, operation_id in (('3', '101'), ('TTDEMO02', '102')):
        assert manager.post('/production/assign', data={
            'order_id': order.id, 'operation_id': operation_id,
            'user_id': user_id, 'assign_date': '2027-04-01',
        }).status_code == 302

    assert [o.id for o in DonSanXuat.search(q=f'Đơn #{order.id}', product_id='SP01',
                                            due_from='2027-04-05', due_to='2027-04-05',
                                            operation_id='101', leader_id='3')] == [order.id]
    assert not DonSanXuat.search(q=order.id, operation_id='102', leader_id='3')
    assert not DonSanXuat.search(q=order.id, due_from='2027-04-06')
    assert not DonSanXuat.search(q=order.id, product_id='SP02')
    assert not DonSanXuat.search(q=order.id, user_id='4')
    assert not DonSanXuat.search(q='%')

    page = leader.get('/orders', query_string={
        'q': f'Đơn #{order.id}', 'product_id': 'SP01', 'operation_id': '101',
        'leader_id': '3', 'due_from': '2027-04-01', 'due_to': '2027-04-06',
    }).get_data(as_text=True)
    assert f'Đơn #{order.id}' in page
    assert 'name="operation_id"' in page and 'name="leader_id"' in page
    assert f'Đơn #{order.id}' not in worker.get('/orders', query_string={'q': order.id}).get_data(as_text=True)


def test_daily_report_leader_submits_manager_reviews(app):
    client, auth_client, worker_client = (app.test_client() for _ in range(3))
    login(client, 'leader@workshop.edu.vn')
    login(auth_client, 'manager@workshop.edu.vn')
    login(worker_client, 'worker@workshop.edu.vn')
    day = date.today().isoformat()
    submitted = client.post('/daily-reports', data={
        'order_id': 25, 'report_date': day, 'completed': 4,
        'defective': 1, 'note': 'Đã kiểm tra công đoạn cắt.'
    })
    assert submitted.status_code == 302
    manager_view = auth_client.get(f'/daily-reports?date={day}&status=Pending')
    assert manager_view.status_code == 200
    assert 'Đã kiểm tra công đoạn cắt.' in manager_view.get_data(as_text=True)
    report = query_db('SELECT MaBaoCao FROM BaoCaoNgay WHERE MaDon = 25 AND MaTaiKhoan = 3', one=True)
    assert auth_client.post(f"/daily-reports/{report['MaBaoCao']}/review").status_code == 302
    assert query_db('SELECT TrangThai FROM BaoCaoNgay WHERE MaBaoCao = %s',
                    (report['MaBaoCao'],), one=True)['TrangThai'] == 'Reviewed'
    assert worker_client.get('/daily-reports').status_code == 403
