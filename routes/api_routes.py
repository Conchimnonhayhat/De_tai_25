from flask import Blueprint, request, jsonify
from services.auth_service import login_required, role_required, AuthService
from services.access_service import can_update_operation
from services.production_service import ProductionService
from services.statistics_service import StatisticsService

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/progress/update', methods=['POST'])
@login_required
@role_required('ToTruong', 'NhanVien')
def update_progress_api():
    data = request.get_json() or request.form
    try:
        order_id = str(data.get('order_id') or '').strip()
        op_id = str(data.get('operation_id') or '').strip()
        add_qty = int(data.get('additional_qty', 0))
        if not can_update_operation(AuthService.get_current_user(), order_id, op_id):
            return jsonify({'status': 'error', 'message': 'Công đoạn không được phân công'}), 403

        result = ProductionService.update_progress(order_id, op_id, add_qty)
        return jsonify({'status': 'ok', 'message': 'Cập nhật tiến độ thành công', 'data': result})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Lỗi xử lý máy chủ'}), 500


@api_bp.route('/defects/record', methods=['POST'])
@login_required
@role_required('ToTruong', 'NhanVien')
def record_defect_api():
    data = request.get_json() or request.form
    try:
        order_id = str(data.get('order_id') or '').strip()
        op_id = str(data.get('operation_id') or '').strip()
        desc = data.get('defect_desc', '')
        qty = int(data.get('defect_qty', 1))
        if not can_update_operation(AuthService.get_current_user(), order_id, op_id):
            return jsonify({'status': 'error', 'message': 'Công đoạn không được phân công'}), 403

        defect_id = ProductionService.record_defect(order_id, op_id, desc, qty)
        return jsonify({'status': 'ok', 'message': 'Ghi nhận lỗi thành công', 'defect_id': defect_id})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Lỗi xử lý máy chủ'}), 500


@api_bp.route('/statistics/summary', methods=['GET'])
@login_required
@role_required('QuanLyXuong')
def get_stats_api():
    order_id = request.args.get('order_id')
    progress = StatisticsService.get_order_progress_summary(order_id)
    defect_stats = StatisticsService.get_defect_rate_statistics(order_id)
    return jsonify({
        'status': 'ok',
        'progress': progress,
        'defects': defect_stats
    })
