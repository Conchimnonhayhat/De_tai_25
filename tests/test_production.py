import pytest
from services.order_service import OrderService
from services.production_service import ProductionService
from models.order import DonSanXuat
from models.production import TienDoCongDoan, LoiSanXuat

def test_create_order_success():
    """Test FR-05: Create order successfully with positive requested quantity."""
    order = OrderService.create_order("SP01", 30, "2026-11-01", "Đơn thử nghiệm QA")
    assert order is not None
    assert order.quantity_requested == 30
    assert order.status == "Mới tạo"

def test_create_order_negative_quantity_rejected():
    """Test rejection of non-positive order quantity."""
    with pytest.raises(ValueError) as exc:
        OrderService.create_order("SP01", -10, "2026-11-01")
    assert "lớn hơn 0" in str(exc.value)

def test_progress_sequential_constraint():
    """
    Test BR-03: An operation cannot record higher completed quantity 
    than its preceding operation.
    """
    order = OrderService.create_order("SP01", 50, "2026-11-10", "Đơn test thứ tự")
    
    # Update Op 101 (Step 1) to 20
    res1 = ProductionService.update_progress(order.id, 101, 20)
    assert res1['completed_qty'] == 20

    # Updating Op 102 (Step 2) to 25 (> 20 of Op 101) must raise ValueError!
    with pytest.raises(ValueError) as exc:
        ProductionService.update_progress(order.id, 102, 25)
    assert "không được vượt quá công đoạn trước" in str(exc.value)

def test_progress_exceeding_order_quantity_rejected():
    """Test progress cannot exceed total requested order quantity."""
    order = OrderService.create_order("SP01", 10, "2026-11-15")
    with pytest.raises(ValueError) as exc:
        ProductionService.update_progress(order.id, 101, 15)
    assert "không được vượt quá số lượng yêu cầu" in str(exc.value)

def test_record_defect_success():
    """Test FR-10: Record defect and defective item count successfully."""
    defect_id = ProductionService.record_defect(25, 101, "Gờ phôi kim loại bén", 3)
    assert defect_id.startswith('LOI')
    defects = LoiSanXuat.get_by_order(25)
    assert any(d.id == defect_id and d.defect_qty == 3 for d in defects)

def test_record_defect_negative_quantity_rejected():
    """Test defect logging with negative quantity is rejected."""
    with pytest.raises(ValueError) as exc:
        ProductionService.record_defect(25, 101, "Lỗi không hợp lệ", -2)
    assert "lớn hơn 0" in str(exc.value)


def test_delete_order_success():
    """Test deleting an order cleanly removes order, plan, assignments and initial progress."""
    order = OrderService.create_order("SP01", 15, "2026-11-20", "Đơn thử nghiệm xóa")
    order_id = order.id
    # Add a plan and assignment
    OrderService.create_plan(order_id, "2026-11-01", "2026-11-15")
    # Verify records exist before delete
    assert DonSanXuat.get_by_id(order_id) is not None
    assert len(TienDoCongDoan.get_by_order(order_id)) > 0

    # Delete order
    assert OrderService.delete_order(order_id) is True

    # Verify records are gone
    assert DonSanXuat.get_by_id(order_id) is None
    assert len(TienDoCongDoan.get_by_order(order_id)) == 0


def test_delete_order_nonexistent_rejected():
    """Test deleting a non-existent order raises ValueError."""
    with pytest.raises(ValueError, match="không tồn tại"):
        OrderService.delete_order("DSX_NONEXISTENT_9999")


def test_delete_order_with_progress_rejected():
    """Test deleting an order with completed output at an operation is rejected."""
    order = OrderService.create_order("SP01", 20, "2026-11-25", "Đơn có tiến độ")
    ProductionService.update_progress(order.id, 101, 5)

    with pytest.raises(ValueError, match="sản lượng hoàn thành"):
        OrderService.delete_order(order.id)


def test_delete_order_with_production_records_rejected():
    """Test deleting an order that already has recorded defects (e.g. seed order 25) is rejected."""
    with pytest.raises(ValueError, match="lỗi sản xuất|hoàn thành|nguyên vật liệu"):
        OrderService.delete_order(25)


def test_update_order_success():
    """Test updating order details (quantity, due date, note, status)."""
    order = OrderService.create_order("SP01", 10, "2026-11-20", "Đơn ban đầu")
    assert OrderService.update_order(order.id, "SP01", 15, "2026-12-05", "Đơn đã sửa ghi chú", "Đang thực hiện") is True
    updated = DonSanXuat.get_by_id(order.id)
    assert updated.quantity_requested == 15
    assert updated.due_date == "2026-12-05"
    assert updated.note == "Đơn đã sửa ghi chú"
    assert updated.status == "Đang thực hiện"


def test_update_order_invalid_inputs_rejected():
    """Test updating order with negative quantity or invalid date is rejected."""
    order = OrderService.create_order("SP01", 10, "2026-11-20")
    with pytest.raises(ValueError, match="lớn hơn 0"):
        OrderService.update_order(order.id, "SP01", -5, "2026-11-20")
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        OrderService.update_order(order.id, "SP01", 10, "invalid-date")


