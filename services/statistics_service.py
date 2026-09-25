from database.db import query_db

class StatisticsService:
    """Calculates statistics for progress, productivity, and defect rates."""

    @staticmethod
    def get_order_progress_summary(order_id: str = None):
        """Calculates overall progress percent for one or all active orders."""
        where_clause = "WHERE d.MaDon = %s" if order_id else ""
        args = (order_id,) if order_id else ()

        sql = f"""
            SELECT d.MaDon, d.SoLuongYeuCau, d.HanGiao, d.TrangThai, s.TenSanPham,
                   COALESCE(MIN(t.SoLuongHoanThanh), 0) as SanLuongCongDoanCuoi,
                   COUNT(c.MaCongDoan) as TongSoCongDoan
            FROM DonSanXuat d
            JOIN SanPham s ON d.MaSanPham = s.MaSanPham
            LEFT JOIN CongDoan c ON s.MaSanPham = c.MaSanPham
            LEFT JOIN TienDoCongDoan t ON (c.MaCongDoan = t.MaCongDoan AND d.MaDon = t.MaDon)
            {where_clause}
            GROUP BY d.MaDon, d.SoLuongYeuCau, d.HanGiao, d.TrangThai, s.TenSanPham
            ORDER BY d.HanGiao ASC
        """
        rows = query_db(sql, args)
        results = []

        for r in rows:
            req_qty = int(r['SoLuongYeuCau'])
            # Fetch completed qty at the final operation (max ThuTu)
            final_op_prog = query_db("""
                SELECT t.SoLuongHoanThanh 
                FROM TienDoCongDoan t
                JOIN CongDoan c ON t.MaCongDoan = c.MaCongDoan
                JOIN DonSanXuat d ON t.MaDon = d.MaDon
                WHERE t.MaDon = %s
                ORDER BY c.ThuTu DESC
                LIMIT 1
            """, (r['MaDon'],), one=True)

            completed = int(final_op_prog['SoLuongHoanThanh']) if final_op_prog else 0
            percent = round((completed / req_qty) * 100.0, 1) if req_qty > 0 else 0.0

            results.append({
                'order_id': r['MaDon'],
                'product_name': r['TenSanPham'],
                'requested_qty': req_qty,
                'completed_qty': completed,
                'progress_percent': min(100.0, percent),
                'due_date': str(r['HanGiao']),
                'status': r['TrangThai']
            })

        return results[0] if (order_id and results) else results

    @staticmethod
    def get_productivity_by_operation():
        """Calculates total output produced per operation."""
        sql = """
            SELECT c.TenCongDoan, c.ThuTu, s.TenSanPham,
                   COALESCE(SUM(t.SoLuongHoanThanh), 0) as TongSanLuong
            FROM CongDoan c
            JOIN SanPham s ON c.MaSanPham = s.MaSanPham
            LEFT JOIN TienDoCongDoan t ON c.MaCongDoan = t.MaCongDoan
            GROUP BY c.MaCongDoan, c.TenCongDoan, c.ThuTu, s.TenSanPham
            ORDER BY s.TenSanPham, c.ThuTu ASC
        """
        return query_db(sql)

    @staticmethod
    def get_defect_rate_statistics(order_id: str = None):
        """
        Calculates defect rate based on BR-06:
        Defect Rate (%) = (Total Defective / Total Recorded Output) * 100%.
        Handles division by zero gracefully.
        """
        where_clause = "WHERE d.MaDon = %s" if order_id else ""
        args = (order_id,) if order_id else ()

        # 1. Total defective
        defect_sql = f"""
            SELECT COALESCE(SUM(SoLuongHong), 0) as TongHong
            FROM LoiSanXuat l
            JOIN DonSanXuat d ON l.MaDon = d.MaDon
            {where_clause}
        """
        defect_res = query_db(defect_sql, args, one=True)
        total_defective = int(defect_res['TongHong']) if defect_res else 0

        # 2. Total recorded output
        output_sql = f"""
            SELECT COALESCE(SUM(t.SoLuongHoanThanh), 0) as TongSanLuong
            FROM TienDoCongDoan t
            JOIN DonSanXuat d ON t.MaDon = d.MaDon
            JOIN CongDoan c ON t.MaCongDoan = c.MaCongDoan
            {where_clause}
            {'AND' if where_clause else 'WHERE'} c.ThuTu = (
                SELECT MAX(c2.ThuTu) FROM CongDoan c2 WHERE c2.MaSanPham = d.MaSanPham
            )
        """
        output_res = query_db(output_sql, args, one=True)
        total_output = int(output_res['TongSanLuong']) if output_res else 0

        if total_output == 0:
            return {
                'total_defective': total_defective,
                'total_output': 0,
                'defect_rate': 0.0,
                'status': 'Chưa có dữ liệu',
                'formula_note': 'Mẫu số bằng 0 (chưa có sản lượng ghi nhận theo BR-06)'
            }

        rate = round((total_defective / total_output) * 100.0, 2)
        return {
            'total_defective': total_defective,
            'total_output': total_output,
            'defect_rate': rate,
            'status': f"{rate}%",
            'formula_note': f"({total_defective} / {total_output}) * 100% = {rate}%"
        }
