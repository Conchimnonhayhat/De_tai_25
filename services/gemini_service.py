"""
Gemini Service Adapter
Handles communication with Google Gemini API securely.
Includes fallback inference engine for offline development and local automated tests.
"""

import os
import json
import logging
from datetime import date
from html import unescape
from typing import Dict, Any
from typing import Literal

from pydantic import BaseModel

from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

logger = logging.getLogger(__name__)


class ProgressResponse(BaseModel):
    task_type: Literal['progress_summary']
    summary: str
    delays: list[str]


class DefectGroup(BaseModel):
    group_name: str
    count: int
    affected_orders: list[str]
    source_record_ids: list[str]


class DefectResponse(BaseModel):
    task_type: Literal['defect_analysis']
    summary: str
    groups: list[DefectGroup]
    hypotheses: list[str]


class PriorityRecommendation(BaseModel):
    rank: int
    order_id: str
    product_name: str
    due_date: str
    reason: str
    material_constraint: str


class PriorityResponse(BaseModel):
    task_type: Literal['order_priority']
    summary: str
    recommendations: list[PriorityRecommendation]


RESPONSE_SCHEMAS = {
    'progress_summary': ProgressResponse,
    'defect_analysis': DefectResponse,
    'order_priority': PriorityResponse,
}

class GeminiService:
    """Encapsulates interaction with the Gemini AI Provider."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        self.client = None
        self.last_source = 'local_rules'

        placeholder_keys = ("", "your_key_here", "your_gemini_api_key_here", "YOUR_GEMINI_API_KEY")
        if self.api_key and self.api_key not in placeholder_keys:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Google GenAI client: {e}")
                self.client = None

    def generate_content(self, prompt: str, task_type: str = "progress_summary", context: Dict[str, Any] = None) -> str:
        """
        Sends prompt to Gemini API or falls back to grounded local inference 
        if API key is unavailable or fails.
        """
        # In automated testing environments, always use grounded fallback for deterministic test execution
        if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING") == "true":
            self.last_source = 'local_rules'
            return self._generate_grounded_fallback(task_type, context)

        try:
            from flask import current_app, has_app_context
            if has_app_context() and current_app.config.get("TESTING"):
                self.last_source = 'local_rules'
                return self._generate_grounded_fallback(task_type, context)
        except Exception:
            pass

        if self.client:
            try:
                from google.genai import types
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type='application/json',
                        response_schema=RESPONSE_SCHEMAS.get(task_type),
                    ),
                )
                if response and response.text:
                    self.last_source = 'gemini'
                    return response.text
            except Exception as e:
                logger.error(f"Gemini API call failed, falling back to local grounded response: {e}")

        # Intelligent grounded fallback using the verified snapshot context
        self.last_source = 'local_rules'
        return self._generate_grounded_fallback(task_type, context)

    def _generate_grounded_fallback(self, task_type: str, context: Dict[str, Any] = None) -> str:
        """Generates deterministic, schema-compliant JSON strictly grounded in context."""
        context = context or {}
        facts = context.get('facts', {})
        source_ids = context.get('source_ids', [])
        missing_data = context.get('missing_data', [])
        data_issues = context.get('data_issues', [])

        if task_type == 'progress_summary':
            order_id = facts.get('order_id', 'N/A')
            req = facts.get('SoLuongYeuCau', 0)
            comp = facts.get('SoLuongHoanThanh', 0)
            pct = facts.get('progress_percent', 0.0)
            due = facts.get('HanGiao', 'Chưa rõ')
            try:
                overdue = date.fromisoformat(str(due)) < date.today() and pct < 100
            except ValueError:
                overdue = False
            assessment = ('Đơn đã quá hạn, cần người quản lý kiểm tra.' if overdue else
                          'Đơn đã hoàn thành theo số lượng ghi nhận.' if pct >= 100 else
                          'Cần tiếp tục theo dõi các công đoạn và hạn giao.')

            summary_text = (
                f"Đơn hàng #{order_id} hiện đã hoàn thành {comp}/{req} sản phẩm ({pct}% tiến độ) "
                f"theo dữ liệu công đoạn hiện có. Hạn bàn giao theo kế hoạch là {due}. "
                + assessment
            )

            res = {
                "status": "ok" if not data_issues else "needs_review",
                "task_type": "progress_summary",
                "summary": summary_text,
                "facts": facts,
                "delays": [f"Cần theo dõi hạn giao {due}"] if pct < 100 else [],
                "source_ids": source_ids,
                "missing_data": missing_data,
                "data_issues": data_issues
            }
            return json.dumps(res, ensure_ascii=False)

        elif task_type == 'defect_analysis':
            defect_records = context.get('defect_records', [])
            total_hong = facts.get('total_defective', 0)
            categories = {
                'Bề mặt, trầy xước hoặc sơn': ('xước', 'trầy', 'bề mặt', 'sơn', 'rỉ'),
                'Hàn, mối nối hoặc nứt': ('hàn', 'mối', 'nứt', 'khớp'),
                'Kích thước hoặc hình dạng': ('kích thước', 'lệch', 'cong', 'sai số'),
            }
            grouped = {}
            for record in defect_records:
                description = unescape(str(record.get('desc', ''))).lower()
                category = next((name for name, terms in categories.items()
                                 if any(term in description for term in terms)), 'Lỗi khác cần phân loại')
                group = grouped.setdefault(category, {'group_name': category, 'count': 0,
                                                     'affected_orders': set(), 'source_record_ids': []})
                group['count'] += int(record.get('qty', 0))
                group['affected_orders'].add(record.get('order_id'))
                group['source_record_ids'].append(f"LoiSanXuat:{record.get('id')}")
            groups = [{**group, 'affected_orders': sorted(group['affected_orders'])}
                      for group in grouped.values()]
            hypotheses = [f'Giả thuyết cần xác minh: kiểm tra quy trình và thiết bị liên quan nhóm {name.lower()}.'
                          for name in grouped]

            res = {
                "status": "ok",
                "task_type": "defect_analysis",
                "summary": f"Đã ghi nhận {total_hong} sản phẩm hỏng trong {len(groups)} nhóm mô tả lỗi.",
                "groups": groups,
                "hypotheses": hypotheses,
                "facts": facts,
                "source_ids": source_ids,
                "missing_data": missing_data,
                "data_issues": data_issues
            }
            return json.dumps(res, ensure_ascii=False)

        elif task_type == 'order_priority':
            candidate_orders = context.get('candidate_orders', [])
            recommendations = []
            limit = min(5, max(1, int(context.get('max_suggestions', 3))))

            def priority(order):
                try:
                    days = (date.fromisoformat(str(order['HanGiao'])) - date.today()).days
                except (ValueError, KeyError):
                    days = 9999
                shortage = 'Thiếu' in order.get('material_status', '')
                score = max(0, 30 - days) * 2 + (100 - float(order.get('progress_percent', 0))) / 10
                return score + (15 if shortage else 0)

            for idx, o in enumerate(sorted(candidate_orders, key=priority, reverse=True)[:limit], start=1):
                status = o.get('material_status', 'Chưa rõ vật tư')
                recommendations.append({
                    "rank": idx,
                    "order_id": o.get('MaDon'),
                    "product_name": o.get('TenSanPham'),
                    "due_date": o.get('HanGiao'),
                    "reason": f"Hạn giao {o.get('HanGiao')}, tiến độ {o.get('progress_percent', 0)}%, {status.lower()}",
                    "material_constraint": status
                })

            res = {
                "status": "ok",
                "task_type": "order_priority",
                "summary": f"Đề xuất ưu tiên {len(recommendations)} đơn sản xuất căn cứ theo hạn giao và vật tư khả dụng.",
                "recommendations": recommendations,
                "facts": facts,
                "source_ids": source_ids,
                "missing_data": missing_data,
                "data_issues": data_issues
            }
            return json.dumps(res, ensure_ascii=False)

        return json.dumps({"status": "no_data", "summary": "Không có dữ liệu phù hợp", "facts": {}})
