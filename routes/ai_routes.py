from flask import Blueprint, render_template, request, jsonify, session
from services.auth_service import login_required, role_required, AuthService
from services.production_ai_service import ProductionAIService
from models.order import DonSanXuat
from models.product import SanPham

ai_bp = Blueprint('ai', __name__)
ai_service = ProductionAIService()

@ai_bp.route('/ai/assistant')
@login_required
@role_required('QuanLyXuong', 'ToTruong')
def assistant_page():
    user = AuthService.get_current_user()
    orders = DonSanXuat.search(user_id=None if user.role == 'QuanLyXuong' else user.id)
    products = SanPham.get_all()
    model_name = getattr(ai_service.gemini_service, 'model_name', 'gemini-3.5-flash-lite')
    return render_template('production_ai.html', orders=orders, products=products, model_name=model_name)


@ai_bp.route('/api/ai/progress-summary', methods=['POST'])
@login_required
@role_required('QuanLyXuong', 'ToTruong')
def progress_summary_api():
    current_user = AuthService.get_current_user()
    data = request.get_json() or request.form.to_dict()
    data['task_type'] = 'progress_summary'
    
    try:
        result = ai_service.run_production_ai(data, current_user)
        return jsonify(result)
    except PermissionError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 403
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Lỗi xử lý máy chủ'}), 500


@ai_bp.route('/api/ai/defect-analysis', methods=['POST'])
@login_required
@role_required('QuanLyXuong', 'ToTruong')
def defect_analysis_api():
    current_user = AuthService.get_current_user()
    data = request.get_json() or request.form.to_dict()
    data['task_type'] = 'defect_analysis'
    
    try:
        result = ai_service.run_production_ai(data, current_user)
        return jsonify(result)
    except PermissionError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 403
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Lỗi xử lý máy chủ'}), 500


@ai_bp.route('/api/ai/order-priority', methods=['POST'])
@login_required
@role_required('QuanLyXuong')
def order_priority_api():
    current_user = AuthService.get_current_user()
    data = request.get_json() or request.form.to_dict()
    data['task_type'] = 'order_priority'
    
    try:
        result = ai_service.run_production_ai(data, current_user)
        return jsonify(result)
    except PermissionError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 403
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Lỗi xử lý máy chủ'}), 500
