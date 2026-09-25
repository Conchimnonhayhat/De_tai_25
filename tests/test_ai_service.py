import json
import pytest
from services.production_ai_service import ProductionAIService
from services.gemini_service import GeminiService
from models.user import TaiKhoan

def test_request_analyzer_progress_summary():
    """Test Request Analyzer parses progress summary intent."""
    intent = ProductionAIService.analyze_request({'order_id': 25, 'prompt': 'Tóm tắt Đơn 25'}, None)
    assert intent['task_type'] == 'progress_summary'
    assert intent['order_ids'] == ['25']

def test_request_analyzer_priority_intent():
    """Test Request Analyzer recognizes order priority keywords."""
    intent = ProductionAIService.analyze_request({'prompt': 'Gợi ý 3 đơn cần ưu tiên tuần này'}, None)
    assert intent['task_type'] == 'order_priority'

def test_request_analyzer_defect_intent():
    """Test Request Analyzer recognizes defect analysis keywords."""
    intent = ProductionAIService.analyze_request({'prompt': 'Phân tích các lỗi và nguyên nhân'}, None)
    assert intent['task_type'] == 'defect_analysis'


def test_explicit_ai_task_is_not_reclassified_by_prompt():
    intent = ProductionAIService.analyze_request(
        {'task_type': 'progress_summary', 'prompt': 'Có lỗi gì ở đơn này?'}, None
    )
    assert intent['task_type'] == 'progress_summary'

def test_data_retrieval_progress_snapshot():
    """Test Data Retriever extracts exact snapshot and source IDs."""
    manager = TaiKhoan.get_by_email("manager@workshop.edu.vn")
    intent = {'task_type': 'progress_summary', 'order_ids': [25]}
    snapshot = ProductionAIService.retrieve_production_snapshot(intent, manager)
    
    assert snapshot['has_data'] is True
    facts = snapshot['facts']
    assert facts['order_id'] == '25'
    assert facts['SoLuongYeuCau'] == 100
    assert facts['SoLuongHoanThanh'] >= 60
    assert any("DonSanXuat:25" in s for s in snapshot['source_ids'])

def test_prompt_builder_contains_grounding_rules():
    """Test Prompt Builder enforces anti-hallucination rules."""
    intent = {'task_type': 'progress_summary'}
    context = {'facts': {'order_id': 25}}
    prompt = ProductionAIService.build_prompt(intent, context)
    assert "CHỈ sử dụng dữ liệu trong CONTEXT" in prompt
    assert "KHÔNG ĐƯỢC tự tạo số lượng" in prompt

def test_response_validator_malformed_json_handling():
    """Test Response Validator marks status needs_review when raw AI response is not JSON."""
    intent = {'task_type': 'progress_summary'}
    snapshot = {'facts': {'order_id': 25}, 'source_ids': ['DonSanXuat:25']}
    invalid_raw = "Tôi nghĩ đơn 25 đã hoàn thành xong rồi."
    
    val = ProductionAIService.validate_ai_response(invalid_raw, intent, snapshot)
    assert val['status'] == 'needs_review'
    assert 'facts' in val
    assert val['facts']['order_id'] == 25
    assert invalid_raw not in val['summary']


def test_validator_rejects_fabricated_code_in_summary():
    intent = {'task_type': 'progress_summary'}
    snapshot = {'facts': {'order_id': 'DSX00025', 'SoLuongYeuCau': 100},
                'source_ids': ['DonSanXuat:DSX00025']}
    response = json.dumps({'task_type': 'progress_summary',
                           'summary': 'Đơn DSX99999 đang chờ thực hiện.'})
    validated = ProductionAIService.validate_ai_response(response, intent, snapshot)
    assert validated['status'] == 'needs_review'
    assert 'DSX99999' not in validated['summary']

def test_api_progress_summary_endpoint(auth_client):
    """Test FR-15: POST /api/ai/progress-summary returns validated JSON."""
    res = auth_client.post('/api/ai/progress-summary', json={'order_id': 25})
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'ok'
    assert data['task_type'] == 'progress_summary'
    assert 'summary' in data
    assert 'facts' in data
    assert data['facts']['order_id'] == '25'
    assert len(data['source_ids']) > 0

def test_api_defect_analysis_endpoint(auth_client):
    """Test FR-16: POST /api/ai/defect-analysis returns defect groups and hypotheses."""
    res = auth_client.post('/api/ai/defect-analysis', json={'order_id': 25})
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'ok'
    assert data['task_type'] == 'defect_analysis'
    assert 'hypotheses' in data
    assert len(data['hypotheses']) > 0

def test_api_order_priority_endpoint(auth_client):
    """Test FR-17: POST /api/ai/order-priority returns recommendations."""
    res = auth_client.post('/api/ai/order-priority', json={'max_suggestions': 3})
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'ok'
    assert data['task_type'] == 'order_priority'
    assert 'recommendations' in data
    assert len(data['recommendations']) > 0


def test_ai_api_rejects_invalid_suggestion_count(auth_client):
    response = auth_client.post('/api/ai/order-priority', json={'max_suggestions': 0})
    assert response.status_code == 400

def test_worker_forbidden_from_order_priority(worker_client):
    """Test Worker cannot access order priority (Manager/Admin only according to URD)."""
    res = worker_client.post('/api/ai/order-priority', json={'max_suggestions': 3})
    assert res.status_code == 403


def test_validator_rejects_fabricated_order_and_quantity():
    intent = {'task_type': 'order_priority', 'max_suggestions': 3}
    snapshot = {
        'facts': {'candidate_count': 1}, 'source_ids': ['DonSanXuat:DSX00025'],
        'candidate_orders': [{'MaDon': 'DSX00025', 'HanGiao': '2026-09-30',
                              'material_status': 'Đủ vật tư'}],
    }
    response = json.dumps({
        'status': 'ok', 'task_type': 'order_priority',
        'summary': 'Đơn DSX99999 cần 9999 sản phẩm.',
        'recommendations': [{'order_id': 'DSX99999', 'due_date': '2026-09-30',
                             'material_constraint': 'Đủ vật tư'}],
    })
    validated = ProductionAIService.validate_ai_response(response, intent, snapshot)
    assert validated['status'] == 'needs_review'
    assert 'DSX99999' not in validated['summary']
    assert validated['data_issues']


def test_local_defect_analysis_separates_descriptions():
    context = {
        'facts': {'total_defective': 5}, 'source_ids': ['LoiSanXuat:L1', 'LoiSanXuat:L2'],
        'defect_records': [
            {'id': 'L1', 'order_id': 'DSX1', 'desc': 'Vết xước bề mặt', 'qty': 2},
            {'id': 'L2', 'order_id': 'DSX1', 'desc': 'Mối hàn bị nứt', 'qty': 3},
        ],
    }
    result = json.loads(GeminiService()._generate_grounded_fallback('defect_analysis', context))
    assert len(result['groups']) == 2
    assert sorted(group['count'] for group in result['groups']) == [2, 3]


def test_defect_validator_accepts_source_record_ids_from_snapshot():
    intent = {'task_type': 'defect_analysis', 'max_suggestions': 3}
    snapshot = {
        'facts': {'total_defective': 2},
        'source_ids': ['LoiSanXuat:4'],
        'defect_records': [{'id': '4', 'order_id': '25', 'qty': 2}],
    }
    response = json.dumps({
        'task_type': 'defect_analysis',
        'summary': 'Ghi nhận 2 sản phẩm lỗi của đơn 25.',
        'groups': [{'group_name': 'Lỗi bề mặt', 'count': 2,
                    'affected_orders': ['25'], 'source_record_ids': ['4']}],
        'hypotheses': ['Giả thuyết cần xác minh: kiểm tra bề mặt.'],
    })
    result = ProductionAIService.validate_ai_response(response, intent, snapshot)
    assert result['status'] == 'ok'
    assert result['groups'][0]['source_record_ids'] == ['LoiSanXuat:4']


def test_local_priority_changes_when_material_is_short():
    candidates = [
        {'MaDon': 'DSX1', 'TenSanPham': 'A', 'HanGiao': '2026-12-31',
         'progress_percent': 20.0, 'material_status': 'Đủ vật tư'},
        {'MaDon': 'DSX2', 'TenSanPham': 'B', 'HanGiao': '2026-12-31',
         'progress_percent': 20.0, 'material_status': 'Đủ vật tư'},
    ]
    context = {'candidate_orders': candidates, 'facts': {'candidate_count': 2}, 'max_suggestions': 2}
    service = GeminiService()
    candidates[1]['material_status'] = 'Cảnh báo: Thiếu vật tư'
    result = json.loads(service._generate_grounded_fallback('order_priority', context))
    assert result['recommendations'][0]['order_id'] == 'DSX2'


def test_gemini_model_configuration(monkeypatch):
    """Test GeminiService defaults to gemini-3.5-flash-lite and respects GEMINI_MODEL env."""
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    service = GeminiService()
    assert service.model_name == "gemini-3.5-flash-lite"
    assert service.client is None

    monkeypatch.setenv("GEMINI_MODEL", "custom-gemini-model")
    service2 = GeminiService()
    assert service2.model_name == "custom-gemini-model"
