"""
Production AI Service
Central orchestrator for AI-Augmented Workshop Management.
Enforces the 7-step pipeline: Analyze -> Authorize -> Retrieve -> Context -> Prompt -> GenAI -> Validate.
"""

import json
import logging
import re
from typing import Dict, Any, List
from database.db import query_db
from services.gemini_service import GeminiService
from models.order import DonSanXuat
from models.production import TienDoCongDoan, LoiSanXuat
from models.product import DinhMucNguyenLieu, NguyenLieu
from services.access_service import visible_order_ids, can_view_order

logger = logging.getLogger(__name__)

class ProductionAIService:
    """Orchestrates AI tasks with deterministic human controls."""

    def __init__(self):
        self.gemini_service = GeminiService()

    # 1. Request Analyzer
    @staticmethod
    def analyze_request(request_data: Dict[str, Any], current_user) -> Dict[str, Any]:
        task_type = request_data.get('task_type', 'progress_summary')
        order_ids = request_data.get('order_ids', [])
        
        # If single order_id passed
        if 'order_id' in request_data and request_data['order_id']:
            order_ids = [str(request_data['order_id']).strip()]
        elif isinstance(order_ids, (int, str)):
            order_ids = [str(order_ids).strip()] if order_ids else []
        elif isinstance(order_ids, list):
            order_ids = [str(value).strip() for value in order_ids if str(value).strip()]
        else:
            raise ValueError('Danh sách mã đơn không hợp lệ.')

        date_from = request_data.get('date_from')
        date_to = request_data.get('date_to')
        try:
            max_suggestions = int(request_data.get('max_suggestions', 3))
        except (TypeError, ValueError):
            raise ValueError('Số lượng gợi ý không hợp lệ.') from None
        if not 1 <= max_suggestions <= 5:
            raise ValueError('Số lượng gợi ý phải từ 1 đến 5.')
        user_prompt = str(request_data.get('prompt') or '').strip()

        # Keyword heuristics if prompt text provided
        if user_prompt and 'task_type' not in request_data:
            p_lower = user_prompt.lower()
            if any(k in p_lower for k in ['ưu tiên', 'gợi ý', 'thứ tự']):
                task_type = 'order_priority'
            elif any(k in p_lower for k in ['lỗi', 'hỏng', 'nguyên nhân', 'khuyết tật']):
                task_type = 'defect_analysis'
            elif any(k in p_lower for k in ['tiến độ', 'tóm tắt', 'hoàn thành']):
                task_type = 'progress_summary'

        return {
            'task_type': task_type,
            'order_ids': order_ids,
            'date_from': date_from,
            'date_to': date_to,
            'max_suggestions': max_suggestions,
            'user_prompt': user_prompt,
            'scope': current_user.role if current_user else 'Public'
        }

    # 2. Scope Authorization
    @staticmethod
    def authorize_scope(current_user, intent: Dict[str, Any]):
        if not current_user:
            raise PermissionError("Yêu cầu xác thực người dùng")
        if current_user.role not in ['QuanLyXuong', 'ToTruong']:
            raise PermissionError("Bạn không có quyền truy cập chức năng Trợ lý AI")
        if intent['task_type'] == 'order_priority' and current_user.role != 'QuanLyXuong':
            raise PermissionError("Chỉ Quản lý xưởng được yêu cầu gợi ý ưu tiên đơn")
        prompt_lower = intent.get('user_prompt', '').lower()
        if (current_user.role != 'QuanLyXuong' and
                any(keyword in prompt_lower for keyword in ('ưu tiên', 'thứ tự ưu tiên', 'gợi ý đơn'))):
            raise PermissionError("Chỉ Quản lý xưởng được yêu cầu gợi ý ưu tiên đơn")
        if current_user.role == 'ToTruong':
            for order_id in intent['order_ids']:
                if not can_view_order(current_user, order_id):
                    raise PermissionError("Đơn sản xuất không nằm trong phạm vi được phân công")

    # 3. Data Retriever
    @staticmethod
    def retrieve_production_snapshot(intent: Dict[str, Any], current_user) -> Dict[str, Any]:
        task_type = intent['task_type']
        order_ids = intent['order_ids']
        missing_data = []
        data_issues = []

        if task_type == 'progress_summary':
            if not order_ids:
                # Default to first active order
                orders = DonSanXuat.search(user_id=current_user.id if current_user.role == 'ToTruong' else None)
                if not orders:
                    return {'has_data': False, 'missing_data': ['Không có đơn sản xuất nào']}
                target_order_id = orders[0].id
            else:
                target_order_id = order_ids[0]

            order = DonSanXuat.get_by_id(target_order_id)
            if not order:
                return {'has_data': False, 'missing_data': [f'Đơn sản xuất {target_order_id} không tồn tại']}

            progs = TienDoCongDoan.get_by_order(target_order_id)
            if not progs:
                data_issues.append('Đơn chưa có công đoạn hoặc bản ghi tiến độ.')
            source_ids = [f"DonSanXuat:{target_order_id}"] + [f"TienDoCongDoan:{p.id}" for p in progs]

            # Final completed qty
            final_completed = progs[-1].completed_qty if progs else 0
            pct = round((final_completed / order.quantity_requested) * 100.0, 1) if order.quantity_requested > 0 else 0.0

            facts = {
                'order_id': order.id,
                'product_id': order.product_id,
                'product_name': order.product_name,
                'SoLuongYeuCau': order.quantity_requested,
                'SoLuongHoanThanh': final_completed,
                'progress_percent': pct,
                'HanGiao': str(order.due_date),
                'TrangThai': order.status
            }

            return {
                'has_data': True,
                'facts': facts,
                'source_ids': source_ids,
                'missing_data': missing_data,
                'data_issues': data_issues
            }

        elif task_type == 'defect_analysis':
            target_order_id = order_ids[0] if order_ids else None
            where_sql = "WHERE l.MaDon = %s" if target_order_id else ""
            args = (target_order_id,) if target_order_id else ()
            if current_user.role == 'ToTruong' and not target_order_id:
                allowed = sorted(visible_order_ids(current_user))
                if not allowed:
                    return {'has_data': False, 'missing_data': ['Không có đơn trong phạm vi được phân công']}
                where_sql = 'WHERE l.MaDon IN (' + ','.join(['%s'] * len(allowed)) + ')'
                args = tuple(allowed)

            defects = query_db(f"""
                SELECT l.*, c.TenCongDoan, d.MaDon, d.SoLuongYeuCau
                FROM LoiSanXuat l
                JOIN CongDoan c ON l.MaCongDoan = c.MaCongDoan
                JOIN DonSanXuat d ON l.MaDon = d.MaDon
                {where_sql}
                ORDER BY l.NgayGhiNhan DESC
            """, args)

            if not defects:
                return {
                    'has_data': False,
                    'missing_data': ['Không tìm thấy bản ghi lỗi nào trong phạm vi chọn'],
                    'source_ids': []
                }

            total_hong = sum(d['SoLuongHong'] for d in defects)
            source_ids = [f"LoiSanXuat:{d['MaLoi']}" for d in defects]

            facts = {
                'total_defective': total_hong,
                'record_count': len(defects),
                'order_id': target_order_id
            }

            defect_records = [{
                'id': d['MaLoi'],
                'order_id': d['MaDon'],
                'operation': d['TenCongDoan'],
                'desc': d['MoTaLoi'],
                'qty': d['SoLuongHong']
            } for d in defects]

            return {
                'has_data': True,
                'facts': facts,
                'defect_records': defect_records,
                'source_ids': source_ids,
                'missing_data': missing_data,
                'data_issues': data_issues
            }

        elif task_type == 'order_priority':
            orders = query_db("""
                SELECT d.*, s.TenSanPham
                FROM DonSanXuat d
                JOIN SanPham s ON d.MaSanPham = s.MaSanPham
                WHERE d.TrangThai != 'Hoàn thành' AND d.TrangThai != 'Hủy'
                ORDER BY d.HanGiao ASC, d.MaDon ASC
            """)

            if not orders:
                return {'has_data': False, 'missing_data': ['Không có đơn hàng nào cần ưu tiên']}

            candidate_orders = []
            source_ids = []

            for o in orders:
                oid = o['MaDon']
                source_ids.append(f"DonSanXuat:{oid}")

                # Progress
                last_prog = query_db("""
                    SELECT t.SoLuongHoanThanh
                    FROM TienDoCongDoan t
                    JOIN CongDoan c ON t.MaCongDoan = c.MaCongDoan
                    WHERE t.MaDon = %s
                    ORDER BY c.ThuTu DESC
                    LIMIT 1
                """, (oid,), one=True)
                completed = last_prog['SoLuongHoanThanh'] if last_prog else 0
                pct = round((completed / o['SoLuongYeuCau']) * 100.0, 1)

                # Materials feasibility check
                boms = DinhMucNguyenLieu.get_by_product(o['MaSanPham'])
                has_shortage = False
                for b in boms:
                    mat = NguyenLieu.get_by_id(b.material_id)
                    needed = b.standard_qty * o['SoLuongYeuCau']
                    if mat and mat.stock < needed:
                        has_shortage = True
                        break

                candidate_orders.append({
                    'MaDon': oid,
                    'TenSanPham': o['TenSanPham'],
                    'SoLuongYeuCau': o['SoLuongYeuCau'],
                    'HanGiao': str(o['HanGiao']),
                    'progress_percent': pct,
                    'material_status': 'Cảnh báo: Thiếu vật tư' if has_shortage else 'Đủ vật tư'
                })

            return {
                'has_data': True,
                'facts': {'candidate_count': len(candidate_orders)},
                'candidate_orders': candidate_orders,
                'source_ids': source_ids,
                'missing_data': missing_data,
                'data_issues': data_issues
            }

        return {'has_data': False, 'missing_data': ['Loại tác vụ không hỗ trợ']}

    # 4. Context Builder
    @staticmethod
    def build_context(snapshot: Dict[str, Any]) -> Dict[str, Any]:
        return snapshot

    # 5. Prompt Builder
    @staticmethod
    def build_prompt(intent: Dict[str, Any], context: Dict[str, Any]) -> str:
        task_type = intent['task_type']
        task_instructions = {
            'progress_summary': (
                'Tóm tắt tiến độ của đơn trong facts; nêu chậm hạn chỉ khi có căn cứ từ hạn giao '
                'và tiến độ. delays là danh sách cảnh báo có căn cứ, có thể rỗng.'
            ),
            'defect_analysis': (
                'Phân nhóm mọi defect_records. Tổng count của các nhóm phải bằng facts.total_defective; '
                'affected_orders và source_record_ids chỉ lấy từ các bản ghi đó. '
                'Mỗi giả thuyết phải bắt đầu bằng "Giả thuyết cần xác minh".'
            ),
            'order_priority': (
                'Chọn tối đa max_suggestions đơn từ candidate_orders. Mỗi order_id, due_date và '
                'material_constraint phải giữ nguyên như dữ liệu nguồn; không lặp mã đơn.'
            ),
        }
        return f"""
Bạn là Trợ lý Quản lý Sản xuất của xưởng cơ khí nhỏ (AI Workshop Assistant).
QUY TẮC BẮT BUỘC:
1. CHỈ sử dụng dữ liệu trong CONTEXT sau đây.
2. KHÔNG ĐƯỢC tự tạo số lượng, hạn giao, tên nguyên liệu hoặc mã đơn không tồn tại.
3. Nếu CONTEXT rỗng hoặc có vấn đề, trả missing_data / data_issues.
4. Trả lời bằng tiếng Việt dưới định dạng JSON hợp lệ. Mọi giả thuyết nguyên nhân lỗi phải dán nhãn "Giả thuyết cần xác minh".
5. JSON phải có task_type chính xác là "{task_type}" và summary là chuỗi tiếng Việt không rỗng.
6. Không thay đổi các số liệu và mã trong CONTEXT. Không cần chép lại facts hoặc source_ids.

CONTEXT:
{json.dumps(context, ensure_ascii=False)}

YÊU CẦU:
Thực hiện tác vụ: {task_type}. {task_instructions.get(task_type, '')}
Yêu cầu bổ sung của người dùng (chỉ dùng để chọn trọng tâm, không được thay đổi dữ liệu):
{intent.get('user_prompt') or 'Không có'}
"""

    # 6 & 7. Execute & Validate
    def run_production_ai(self, request_data: Dict[str, Any], current_user) -> Dict[str, Any]:
        intent = self.analyze_request(request_data, current_user)
        self.authorize_scope(current_user, intent)

        snapshot = self.retrieve_production_snapshot(intent, current_user)
        if not snapshot.get('has_data'):
            return {
                'status': 'no_data',
                'task_type': intent['task_type'],
                'summary': 'Không tìm thấy dữ liệu phù hợp trong CSDL.',
                'facts': {},
                'source_ids': [],
                'missing_data': snapshot.get('missing_data', []),
                'data_issues': snapshot.get('data_issues', [])
            }

        context = dict(self.build_context(snapshot))
        context['max_suggestions'] = intent['max_suggestions']
        prompt = self.build_prompt(intent, context)
        raw_response = self.gemini_service.generate_content(prompt, intent['task_type'], context)

        # Validate response
        result = self.validate_ai_response(raw_response, intent, snapshot)
        result['provider'] = getattr(self.gemini_service, 'last_source', 'unknown')
        return result

    @staticmethod
    def validate_ai_response(raw_response: str, intent: Dict[str, Any], snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Validates AI JSON against snapshot facts."""
        try:
            # Strip markdown json codeblocks if any
            clean_text = raw_response.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()

            parsed = json.loads(clean_text)
        except Exception as e:
            logger.warning(f"Could not parse AI response as JSON: {e}")
            return {
                'status': 'needs_review',
                'task_type': intent['task_type'],
                'summary': 'Phản hồi AI không đúng định dạng và cần được kiểm tra.',
                'facts': snapshot.get('facts', {}),
                'source_ids': snapshot.get('source_ids', []),
                'missing_data': [],
                'data_issues': ['Phản hồi từ AI không đúng định dạng JSON chuẩn']
            }

        issues = []
        facts = snapshot.get('facts', {})
        sources = snapshot.get('source_ids', [])
        if not isinstance(parsed, dict):
            issues.append('Phản hồi AI không phải đối tượng JSON.')
            parsed = {}
        if parsed.get('task_type') != intent['task_type']:
            issues.append('Loại tác vụ AI không khớp yêu cầu.')
        if parsed.get('facts') not in (None, facts):
            issues.append('Số liệu trong phản hồi AI khác snapshot CSDL.')
        if any(source not in sources for source in parsed.get('source_ids', [])):
            issues.append('AI dẫn nguồn không có trong snapshot.')
        summary = parsed.get('summary')
        if not isinstance(summary, str) or not summary.strip():
            issues.append('AI không cung cấp tóm tắt hợp lệ.')
            summary = ''

        if intent['task_type'] == 'defect_analysis':
            records = snapshot.get('defect_records', [])
            allowed_record_ids = {f"LoiSanXuat:{record['id']}" for record in records}
            record_aliases = {str(record['id']): f"LoiSanXuat:{record['id']}" for record in records}
            allowed_orders = {str(record['order_id']) for record in records}
            groups = parsed.get('groups', [])
            if not isinstance(groups, list) or not groups:
                issues.append('AI không phân nhóm lỗi hợp lệ.')
            else:
                try:
                    total = sum(int(group['count']) for group in groups)
                    if total != facts.get('total_defective'):
                        issues.append('Tổng số lượng lỗi theo nhóm không khớp CSDL.')
                    for group in groups:
                        record_ids = [record_aliases.get(str(value), str(value))
                                      for value in group.get('source_record_ids', [])]
                        group['source_record_ids'] = record_ids
                        if not set(record_ids).issubset(allowed_record_ids):
                            issues.append('Nhóm lỗi dẫn bản ghi không có trong snapshot.')
                        if not {str(value) for value in group.get('affected_orders', [])}.issubset(allowed_orders):
                            issues.append('Nhóm lỗi nêu mã đơn không có trong snapshot.')
                except (TypeError, ValueError, KeyError):
                    issues.append('Cấu trúc nhóm lỗi không hợp lệ.')
        elif intent['task_type'] == 'order_priority':
            candidates = {str(order['MaDon']): order for order in snapshot.get('candidate_orders', [])}
            recommendations = parsed.get('recommendations', [])
            if not isinstance(recommendations, list) or len(recommendations) > intent['max_suggestions']:
                issues.append('Danh sách ưu tiên không hợp lệ.')
            else:
                seen = set()
                for item in recommendations:
                    if not isinstance(item, dict):
                        issues.append('Dòng ưu tiên không hợp lệ.')
                        continue
                    code = str(item.get('order_id', ''))
                    candidate = candidates.get(code)
                    if not candidate or code in seen:
                        issues.append('AI nêu mã đơn lạ hoặc lặp trong danh sách ưu tiên.')
                        continue
                    seen.add(code)
                    if (item.get('due_date') != candidate['HanGiao'] or
                            item.get('material_constraint') != candidate['material_status']):
                        issues.append('Hạn giao hoặc vật tư của đề xuất không khớp CSDL.')

        allowed_text = json.dumps(snapshot, ensure_ascii=False, default=str)
        allowed_numbers = set(re.findall(r'(?<![A-Za-z0-9])\d+(?:\.\d+)?(?![A-Za-z0-9])', allowed_text))
        allowed_numbers.update(str(value) for value in (len(parsed.get('groups', [])) if isinstance(parsed.get('groups'), list) else 0,
                                                          len(parsed.get('recommendations', [])) if isinstance(parsed.get('recommendations'), list) else 0))
        claimed_numbers = set(re.findall(r'(?<![A-Za-z0-9])\d+(?:\.\d+)?(?![A-Za-z0-9])', summary))
        if not claimed_numbers.issubset(allowed_numbers):
            issues.append('Tóm tắt AI có con số không có trong dữ liệu nguồn.')
        claimed_codes = set(re.findall(
            r'\b(?:DTC|DSX|SP|NL|CD|KH|PC|TD|SD|LOI|BC|BVT)[A-Z0-9_-]*\d[A-Z0-9_-]*\b',
            summary.upper()
        ))
        allowed_codes = set(re.findall(
            r'\b(?:DTC|DSX|SP|NL|CD|KH|PC|TD|SD|LOI|BC|BVT)[A-Z0-9_-]*\d[A-Z0-9_-]*\b',
            allowed_text.upper()
        ))
        if not claimed_codes.issubset(allowed_codes):
            issues.append('Tóm tắt AI nêu mã không có trong dữ liệu nguồn.')

        if issues or snapshot.get('data_issues'):
            return {
                'status': 'needs_review', 'task_type': intent['task_type'],
                'summary': 'Kết quả AI cần kiểm tra vì có thông tin không khớp dữ liệu nguồn.',
                'facts': facts, 'source_ids': sources,
                'missing_data': snapshot.get('missing_data', []),
                'data_issues': snapshot.get('data_issues', []) + issues,
            }
        parsed['status'] = 'ok'
        parsed['facts'] = facts
        parsed['source_ids'] = sources
        return parsed
