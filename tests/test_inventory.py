import pytest
from services.product_service import ProductService
from services.production_service import ProductionService
from services.order_service import OrderService
from models.product import NguyenLieu, DinhMucNguyenLieu, SanPham


def test_manager_creates_product_with_bom(auth_client):
    response = auth_client.post('/products', data={
        'product_id': 'SP-BOM-TEST', 'name': 'Sản phẩm thử', 'unit': 'Cái', 'desc': 'Thử định mức',
        'bom_material_id[]': ['NL01', 'NL02'],
        'bom_quantity[]': ['2.500', '4'],
        'bom_note[]': ['Thép', 'Bu lông'],
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'SP-BOM-TEST' in response.get_data(as_text=True)
    assert SanPham.get_by_id('SP-BOM-TEST') is not None
    boms = DinhMucNguyenLieu.get_by_product('SP-BOM-TEST')
    assert [(b.material_id, b.standard_qty, b.unit) for b in boms] == [
        ('NL01', 2.5, NguyenLieu.get_by_id('NL01').unit),
        ('NL02', 4.0, NguyenLieu.get_by_id('NL02').unit),
    ]


def test_invalid_bom_does_not_create_product(auth_client):
    response = auth_client.post('/products', data={
        'product_id': 'SP-BOM-BAD', 'name': 'Sản phẩm lỗi', 'unit': 'Cái',
        'bom_material_id[]': ['NL01', 'NL01'],
        'bom_quantity[]': ['1', '2'],
        'bom_note[]': ['', ''],
    })
    assert response.status_code == 200
    assert 'bị lặp' in response.get_data(as_text=True)
    assert SanPham.get_by_id('SP-BOM-BAD') is None


def test_missing_material_keeps_product_and_bom_unsaved(auth_client):
    response = auth_client.post('/products', data={
        'product_id': 'SP-BOM-MISSING', 'name': 'Sản phẩm thiếu vật tư', 'unit': 'Cái',
        'bom_material_id[]': ['NL01', 'NOT-A-MATERIAL'],
        'bom_quantity[]': ['1', '2'],
        'bom_note[]': ['', ''],
    })
    assert response.status_code == 200
    assert SanPham.get_by_id('SP-BOM-MISSING') is None


def test_manager_deletes_unused_product_and_its_bom(auth_client):
    ProductService.create_product_with_bom('SP-DELETE-TEST', 'Sản phẩm tạo nhầm', 'Cái', bom_items=[
        {'material_id': 'NL01', 'quantity': '1.5', 'note': ''}
    ])
    page = auth_client.get('/products')
    assert b'/products/SP-DELETE-TEST/delete' in page.data
    with auth_client.session_transaction() as sess:
        token = sess['_product_delete_token']
    response = auth_client.post('/products/SP-DELETE-TEST/delete', data={'delete_token': token}, follow_redirects=True)
    assert response.status_code == 200
    assert 'Đã xóa sản phẩm SP-DELETE-TEST' in response.get_data(as_text=True)
    assert SanPham.get_by_id('SP-DELETE-TEST') is None
    assert DinhMucNguyenLieu.get_by_product('SP-DELETE-TEST') == []


def test_cannot_delete_product_used_by_order(auth_client):
    auth_client.get('/products')
    with auth_client.session_transaction() as sess:
        token = sess['_product_delete_token']
    response = auth_client.post('/products/SP01/delete', data={'delete_token': token}, follow_redirects=True)
    assert 'đã được dùng trong đơn sản xuất' in response.get_data(as_text=True)
    assert SanPham.get_by_id('SP01') is not None


def test_delete_requires_manager_and_valid_token(app, auth_client):
    ProductService.create_product('SP-DELETE-GUARD', 'Sản phẩm bảo vệ', 'Cái')
    leader = app.test_client()
    with leader.session_transaction() as sess:
        sess['user_id'] = 3
        sess['user_role'] = 'ToTruong'
    assert leader.post('/products/SP-DELETE-GUARD/delete', data={'delete_token': 'anything'}).status_code == 403
    assert auth_client.post('/products/SP-DELETE-GUARD/delete', data={'delete_token': 'wrong'}).status_code == 400
    assert SanPham.get_by_id('SP-DELETE-GUARD') is not None

def test_bom_setting_success():
    """Test FR-04: BOM setting for 1 unit of product."""
    ProductService.set_bom("SP02", "NL03", 2.0, "lít", "Sơn khung thép")
    boms = DinhMucNguyenLieu.get_by_product("SP02")
    assert any(b.material_id == "NL03" and b.standard_qty == 2.0 for b in boms)

def test_bom_negative_quantity_rejected():
    """Test BOM with negative quantity is rejected (BR-04)."""
    with pytest.raises(ValueError) as exc:
        ProductService.set_bom("SP01", "NL01", -5.0, "kg")
    assert "lớn hơn 0" in str(exc.value)

def test_material_feasibility_check():
    """Test OrderService material feasibility computation."""
    feas = OrderService.check_material_feasibility(25)
    assert 'is_sufficient' in feas
    assert 'details' in feas
    assert len(feas['details']) >= 3

def test_material_usage_deducts_stock():
    """Test FR-11: Recording material usage atomically deducts inventory stock."""
    mat_before = NguyenLieu.get_by_id("NL04")
    initial_stock = mat_before.stock

    ProductionService.record_material_usage(25, 102, "NL04", 10.0)

    mat_after = NguyenLieu.get_by_id("NL04")
    assert mat_after.stock == initial_stock - 10.0

def test_material_usage_insufficient_stock_rejected():
    """Test material usage exceeding available stock is rejected."""
    with pytest.raises(ValueError) as exc:
        ProductionService.record_material_usage(25, 101, "NL01", 999999.0)
    assert "không đủ" in str(exc.value)


def test_manager_updates_material_success(auth_client):
    """Test updating material details (name, unit, stock, status)."""
    ProductService.create_material('NL-EDIT-TEST', 'Tên ban đầu', 'kg', 50.0)
    response = auth_client.post('/inventory/NL-EDIT-TEST/edit', data={
        'name': 'Tên đã cập nhật', 'unit': 'tấn', 'stock': '75.5', 'status': 'Active'
    }, follow_redirects=True)
    assert response.status_code == 200
    mat = NguyenLieu.get_by_id('NL-EDIT-TEST')
    assert mat.name == 'Tên đã cập nhật'
    assert mat.unit == 'tấn'
    assert mat.stock == 75.5


def test_manager_deletes_unused_material_success(auth_client):
    """Test deleting an unused material successfully removes it."""
    ProductService.create_material('NL-DEL-TEST', 'Vật tư tạo nhầm', 'cái', 10.0)
    assert NguyenLieu.get_by_id('NL-DEL-TEST') is not None
    response = auth_client.post('/inventory/NL-DEL-TEST/delete', follow_redirects=True)
    assert response.status_code == 200
    assert NguyenLieu.get_by_id('NL-DEL-TEST') is None


def test_cannot_delete_material_used_in_bom():
    """Test rejecting deletion of a raw material referenced in a product BOM."""
    with pytest.raises(ValueError, match="Định mức nguyên liệu"):
        ProductService.delete_material('NL01')


def test_non_manager_cannot_edit_or_delete_material(app):
    """Test worker role cannot edit or delete materials (403 Forbidden)."""
    worker = app.test_client()
    with worker.session_transaction() as sess:
        sess['user_id'] = 4
        sess['user_role'] = 'NhanVien'
    assert worker.post('/inventory/NL01/edit', data={'name': 'Hack', 'unit': 'kg', 'stock': '10'}).status_code == 403
    assert worker.post('/inventory/NL01/delete').status_code == 403

