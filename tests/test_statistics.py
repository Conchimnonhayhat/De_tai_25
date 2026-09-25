import pytest
from services.statistics_service import StatisticsService
from services.order_service import OrderService

def test_order_progress_summary():
    """Test FR-12: Order progress summary calculates percentage accurately."""
    summary = StatisticsService.get_order_progress_summary(25)
    assert summary is not None
    assert summary['order_id'] == '25'
    assert summary['requested_qty'] == 100
    assert summary['completed_qty'] >= 60
    assert summary['progress_percent'] >= 60.0

def test_productivity_by_operation():
    """Test FR-13: Productivity by operation aggregates recorded outputs."""
    prod = StatisticsService.get_productivity_by_operation()
    assert isinstance(prod, list)
    assert len(prod) > 0
    assert all('TongSanLuong' in p for p in prod)

def test_defect_rate_calculation_br06():
    """Test FR-14 & BR-06: Defect rate equals (Defective / Output) * 100%."""
    stats = StatisticsService.get_defect_rate_statistics(25)
    assert 'defect_rate' in stats
    assert 'total_defective' in stats
    assert 'total_output' in stats
    assert stats['total_output'] > 0
    expected_rate = round((stats['total_defective'] / stats['total_output']) * 100.0, 2)
    assert stats['defect_rate'] == expected_rate

def test_defect_rate_zero_output_handling():
    """Test BR-06: Zero recorded output handled without division by zero."""
    # Create empty order with 0 output
    new_order = OrderService.create_order("SP01", 10, "2026-12-01")
    stats = StatisticsService.get_defect_rate_statistics(new_order.id)
    assert stats['total_output'] == 0
    assert stats['defect_rate'] == 0.0
    assert stats['status'] == "Chưa có dữ liệu"
