from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.exceptions import HTTPException
from services.auth_service import login_required, role_required, AuthService
from services.access_service import can_view_order, can_update_operation
from models.product import SanPham, NguyenLieu, DinhMucNguyenLieu
from models.order import DonSanXuat, KeHoachSanXuat
from models.production import CongDoan, PhanCong, TienDoCongDoan, LoiSanXuat, SuDungNguyenLieu
from models.user import TaiKhoan
from services.order_service import OrderService
from services.product_service import ProductService
from services.production_service import ProductionService
from services.statistics_service import StatisticsService
from services.daily_report_service import DailyReportService
from services.material_report_service import MaterialReportService
from services.team_service import TeamService
from database.db import query_db
from datetime import date
from secrets import token_urlsafe
from hmac import compare_digest

workshop_bp = Blueprint('workshop', __name__)

@workshop_bp.route('/dashboard')
@login_required
@role_required('QuanLyXuong', 'ToTruong', 'NhanVien')
def dashboard():
    user = AuthService.get_current_user()
    orders = DonSanXuat.search(user_id=None if user.role == 'QuanLyXuong' else user.id)
    products = SanPham.get_all() if user.role != 'NhanVien' else []
    materials = NguyenLieu.get_all() if user.role != 'NhanVien' else []
    defects = LoiSanXuat.get_all() if user.role == 'QuanLyXuong' else []
    allowed_ids = {o.id for o in orders}
    progress_summary = [p for p in StatisticsService.get_order_progress_summary() if p['order_id'] in allowed_ids]
    defect_stats = StatisticsService.get_defect_rate_statistics() if user.role == 'QuanLyXuong' else {'defect_rate': 0, 'total_defective': 0, 'total_output': 0}

    return render_template(
        'dashboard.html',
        orders=orders,
        products=products,
        materials=materials,
        defects=defects,
        progress_summary=progress_summary,
        defect_stats=defect_stats
    )


@workshop_bp.route('/products', methods=['GET', 'POST'])
@login_required
@role_required('QuanLyXuong', 'ToTruong')
def products():
    form_data = {}
    bom_rows = [{'material_id': '', 'quantity': '', 'note': ''}]
    if request.method == 'POST':
        # Only Quản lý xưởng can create products (BR / URD rules)
        if session.get('user_role') != 'QuanLyXuong':
            flash('Chỉ Quản lý xưởng mới có quyền tạo sản phẩm.', 'danger')
            return redirect(url_for('workshop.products'))
        
        form_data = {key: request.form.get(key, '') for key in ('product_id', 'name', 'unit', 'desc')}
        material_ids = request.form.getlist('bom_material_id[]')
        quantities = request.form.getlist('bom_quantity[]')
        notes = request.form.getlist('bom_note[]')
        if len(material_ids) == len(quantities) == len(notes):
            bom_rows = [dict(material_id=material_id, quantity=quantity, note=note)
                        for material_id, quantity, note in zip(material_ids, quantities, notes)]
            if not bom_rows:
                bom_rows = [{'material_id': '', 'quantity': '', 'note': ''}]
        try:
            if len(material_ids) != len(quantities) or len(material_ids) != len(notes):
                raise ValueError('Danh sách định mức vật tư chưa đầy đủ.')
            ProductService.create_product_with_bom(
                form_data['product_id'], form_data['name'], form_data['unit'], form_data['desc'], bom_rows
            )
            flash(f"Đã tạo sản phẩm {form_data['product_id'].strip()} cùng định mức vật tư (BOM) thành công.", 'success')
            return redirect(url_for('workshop.products', q=form_data['product_id'].strip()))
        except Exception as e:
            flash(f'Lỗi tạo sản phẩm: {str(e)}', 'danger')

    q = request.args.get('q', '').strip()[:100]
    all_products = SanPham.search(q)
    boms = {}
    operations_by_product = {}
    for p in all_products:
        boms[p.id] = DinhMucNguyenLieu.get_by_product(p.id)
        operations_by_product[p.id] = CongDoan.get_by_product(p.id)

    materials = NguyenLieu.get_all()
    if session.get('user_role') == 'QuanLyXuong' and '_product_delete_token' not in session:
        session['_product_delete_token'] = token_urlsafe(32)
    return render_template('products.html', products=all_products, boms=boms, operations_by_product=operations_by_product,
                           materials=materials, q=q,
                           form_data=form_data, bom_rows=bom_rows,
                           bom_product_count=sum(bool(rows) for rows in boms.values()),
                           operation_product_count=sum(bool(rows) for rows in operations_by_product.values()))


@workshop_bp.route('/products/<product_id>/delete', methods=['POST'])
@login_required
@role_required('QuanLyXuong')
def delete_product(product_id):
    expected = session.get('_product_delete_token', '')
    provided = request.form.get('delete_token', '')
    if not expected or not compare_digest(expected, provided):
        abort(400)
    try:
        ProductService.delete_product(product_id)
        flash(f'Đã xóa sản phẩm {product_id} và danh sách vật tư đi kèm.', 'success')
    except ValueError as exc:
        flash(str(exc), 'danger')
    return redirect(url_for('workshop.products'))


@workshop_bp.route('/products/<product_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('QuanLyXuong')
def edit_product(product_id):
    product = SanPham.get_by_id(product_id)
    if not product:
        abort(404)
    if '_product_delete_token' not in session:
        session['_product_delete_token'] = token_urlsafe(32)
    rows = [dict(material_id=b.material_id, quantity=b.standard_qty, note=b.note or '')
            for b in DinhMucNguyenLieu.get_by_product(product_id)]
    if request.method == 'POST':
        if not compare_digest(session['_product_delete_token'], request.form.get('delete_token', '')):
            abort(400)
        material_ids = request.form.getlist('bom_material_id[]')
        quantities = request.form.getlist('bom_quantity[]')
        notes = request.form.getlist('bom_note[]')
        rows = [dict(material_id=m, quantity=q, note=n)
                for m, q, n in zip(material_ids, quantities, notes)]
        try:
            if not (len(material_ids) == len(quantities) == len(notes)):
                raise ValueError('Danh sách định mức vật tư chưa đầy đủ.')
            ProductService.update_product_with_bom(
                product_id, request.form.get('name'), request.form.get('unit'),
                request.form.get('desc'), rows
            )
            flash(f'Đã cập nhật sản phẩm {product_id} cùng định mức vật tư (BOM) thành công.', 'success')
            return redirect(url_for('workshop.products', q=product_id))
        except ValueError as exc:
            flash(str(exc), 'danger')
    return render_template('product_edit.html', product=product, rows=rows or [dict(material_id='', quantity='', note='')],
                           materials=NguyenLieu.get_all())


@workshop_bp.route('/products/<product_id>/operations', methods=['POST'])
@login_required
@role_required('QuanLyXuong')
def create_operation(product_id):
    try:
        op_name = request.form.get('name', '').strip()
        step_order = int(request.form.get('step_order', 0))
        code = ProductionService.create_operation(
            product_id, op_name,
            step_order, request.form.get('desc', '')
        )
        flash(f'Đã thêm công đoạn "{op_name}" (Bước {step_order}).', 'success')
    except (TypeError, ValueError) as exc:
        flash(str(exc), 'danger')
    return redirect(url_for('workshop.products', q=product_id))


@workshop_bp.route('/orders', methods=['GET', 'POST'])
@login_required
@role_required('QuanLyXuong', 'ToTruong', 'NhanVien')
def orders():
    if request.method == 'POST':
        if session.get('user_role') != 'QuanLyXuong':
            flash('Chỉ Quản lý xưởng mới có quyền tạo đơn sản xuất.', 'danger')
            return redirect(url_for('workshop.orders'))

        product_id = request.form.get('product_id')
        qty = request.form.get('quantity', '0')
        due_date = request.form.get('due_date')
        note = request.form.get('note', '')

        try:
            OrderService.create_order(product_id, int(qty), due_date, note)
            flash('Tạo đơn sản xuất mới thành công!', 'success')
        except Exception as e:
            flash(f'Lỗi tạo đơn: {str(e)}', 'danger')

    user = AuthService.get_current_user()
    q = request.args.get('q', '').strip()[:100]
    status_filter = request.args.get('status', '')
    product_filter = request.args.get('product_id', '').strip()[:32]
    operation_filter = request.args.get('operation_id', '').strip()[:32]
    leader_filter = request.args.get('leader_id', '').strip()[:32]
    due_from = request.args.get('due_from', '').strip()
    due_to = request.args.get('due_to', '').strip()
    scope_id = None if user.role == 'QuanLyXuong' else user.id
    visible_orders = DonSanXuat.search(user_id=scope_id)
    filter_products = sorted({o.product_id: o.product_name for o in visible_orders}.items())
    assignment_scope = '' if scope_id is None else ' AND p.MaTaiKhoan = %s'
    assignment_args = () if scope_id is None else (scope_id,)
    operation_options = query_db(
        'SELECT DISTINCT c.MaCongDoan AS id, c.TenCongDoan AS name, '
        'c.MaSanPham AS product_id, c.ThuTu AS step_order '
        'FROM PhanCong p JOIN CongDoan c ON c.MaCongDoan = p.MaCongDoan '
        'WHERE 1 = 1' + assignment_scope + ' ORDER BY c.MaSanPham, c.ThuTu',
        assignment_args
    )
    leader_scope = '' if scope_id is None else (
        ' AND EXISTS (SELECT 1 FROM PhanCong mine WHERE mine.MaDon = p.MaDon '
        'AND mine.MaTaiKhoan = %s)'
    )
    leader_options = query_db(
        "SELECT DISTINCT t.MaTaiKhoan AS id, t.HoTen AS name FROM PhanCong p "
        "JOIN TaiKhoan t ON t.MaTaiKhoan = p.MaTaiKhoan WHERE t.VaiTro = 'ToTruong'"
        + leader_scope + ' ORDER BY t.HoTen', assignment_args
    )
    try:
        if due_from:
            date.fromisoformat(due_from)
        if due_to:
            date.fromisoformat(due_to)
        if due_from and due_to and due_from > due_to:
            raise ValueError('Ngày bắt đầu phải trước hoặc bằng ngày kết thúc.')
        all_orders = DonSanXuat.search(q, status_filter, scope_id, product_filter,
                                       operation_filter, due_from, due_to, leader_filter)
    except ValueError as exc:
        flash(f'Khoảng hạn giao không hợp lệ: {exc}', 'danger')
        all_orders = []
    all_products = SanPham.get_all() if user.role == 'QuanLyXuong' else []
    plans = {o.id: KeHoachSanXuat.get_by_order(o.id) for o in all_orders}
    
    feasibilities = {}
    if user.role == 'QuanLyXuong':
        for o in all_orders:
            feasibilities[o.id] = OrderService.check_material_feasibility(o.id)

    if session.get('user_role') == 'QuanLyXuong' and '_order_delete_token' not in session:
        session['_order_delete_token'] = token_urlsafe(32)

    return render_template('orders.html', orders=all_orders, products=all_products, plans=plans,
                           feasibilities=feasibilities,
                           q=q, status_filter=status_filter, order_statuses=DonSanXuat.STATUSES,
                           product_filter=product_filter, operation_filter=operation_filter,
                           leader_filter=leader_filter, due_from=due_from, due_to=due_to,
                           filter_products=filter_products, operation_options=operation_options,
                           leader_options=leader_options)


@workshop_bp.route('/orders/<order_id>/delete', methods=['POST'])
@login_required
@role_required('QuanLyXuong')
def delete_order(order_id):
    expected = session.get('_order_delete_token', '')
    provided = request.form.get('delete_token', '')
    if not expected or not compare_digest(expected, provided):
        abort(400)
    try:
        OrderService.delete_order(order_id)
        flash(f'Đã xóa đơn sản xuất #{order_id} thành công.', 'success')
    except ValueError as exc:
        flash(str(exc), 'danger')
    return redirect(url_for('workshop.orders'))


@workshop_bp.route('/orders/<order_id>/edit', methods=['POST'])
@login_required
@role_required('QuanLyXuong')
def edit_order(order_id):
    product_id = request.form.get('product_id')
    qty = request.form.get('quantity', '0')
    due_date = request.form.get('due_date')
    note = request.form.get('note', '')
    status = request.form.get('status')
    try:
        OrderService.update_order(order_id, product_id, int(qty), due_date, note, status)
        flash(f'Đã cập nhật đơn sản xuất #{order_id} thành công.', 'success')
    except (TypeError, ValueError) as exc:
        flash(str(exc), 'danger')
    return redirect(url_for('workshop.orders', q=order_id))


@workshop_bp.route('/orders/<order_id>/plans', methods=['POST'])
@login_required
@role_required('QuanLyXuong')
def create_plan(order_id):
    try:
        OrderService.create_plan(order_id, request.form.get('start_date', ''), request.form.get('end_date', ''))
        flash('Đã tạo kế hoạch sản xuất.', 'success')
    except ValueError as exc:
        flash(str(exc), 'danger')
    return redirect(url_for('workshop.orders', q=order_id))


@workshop_bp.route('/plans/<plan_id>/edit', methods=['POST'])
@login_required
@role_required('QuanLyXuong')
def update_plan(plan_id):
    try:
        order_id = OrderService.update_plan(plan_id, request.form.get('start_date', ''),
                                             request.form.get('end_date', ''))
        flash('Đã cập nhật kế hoạch sản xuất.', 'success')
        return redirect(url_for('workshop.orders', q=order_id))
    except ValueError as exc:
        flash(str(exc), 'danger')
        return redirect(url_for('workshop.orders'))


@workshop_bp.route('/production', methods=['GET', 'POST'])
@login_required
@role_required('QuanLyXuong', 'ToTruong', 'NhanVien')
def production():
    user = AuthService.get_current_user()
    all_orders = DonSanXuat.search(user_id=None if user.role == 'QuanLyXuong' else user.id)
    order_id = request.args.get('order_id')
    order_id = order_id if order_id is not None else (all_orders[0].id if all_orders else None)
    if order_id is not None and not can_view_order(user, order_id):
        abort(403)
    order = DonSanXuat.get_by_id(order_id)
    if order_id is not None and not order:
        abort(404)

    if request.method == 'POST':
        action = request.form.get('action')
        try:
            target_order_id = request.form.get('order_id', '').strip()
            op_id = request.form.get('operation_id', '').strip()
            if not can_view_order(user, target_order_id):
                abort(403)
            if action in ('update_progress', 'record_defect', 'report_material') and not can_update_operation(user, target_order_id, op_id):
                abort(403)
            if action == 'record_material' and user.role != 'QuanLyXuong':
                abort(403)
            if action == 'update_progress':
                add_qty = int(request.form.get('additional_qty', 0))
                res = ProductionService.update_progress(target_order_id, op_id, add_qty)
                flash(f"Đã cập nhật tiến độ công đoạn! Tổng đạt: {res['completed_qty']}", 'success')
            
            elif action == 'record_defect':
                defect_desc = request.form.get('defect_desc')
                defect_qty = int(request.form.get('defect_qty', 1))
                ProductionService.record_defect(target_order_id, op_id, defect_desc, defect_qty)
                flash('Đã ghi nhận lỗi sản xuất và sản phẩm hỏng thành công!', 'success')

            elif action == 'record_material':
                mat_id = request.form.get('material_id')
                used_qty = float(request.form.get('quantity_used', 0.0))
                ProductionService.record_material_usage(target_order_id, op_id, mat_id, used_qty)
                flash('Đã ghi nhận sử dụng nguyên vật liệu và trừ kho thành công!', 'success')
            elif action == 'report_material':
                MaterialReportService.submit(user, target_order_id, op_id,
                                             request.form.get('material_id', ''),
                                             request.form.get('quantity_used', ''))
                flash('Đã gửi phiếu báo vật tư cho Quản lý xưởng duyệt.', 'success')
            else:
                abort(400)
        except HTTPException:
            raise
        except Exception as e:
            flash(f'Lỗi thao tác sản xuất: {str(e)}', 'danger')

        return redirect(url_for('workshop.production', order_id=request.form.get('order_id', order_id)))

    operations = CongDoan.get_by_product(order.product_id) if order else []
    progress_list = TienDoCongDoan.get_by_order(order.id) if order else []
    defects = LoiSanXuat.get_by_order(order.id) if order else []
    materials_used = SuDungNguyenLieu.get_by_order(order.id) if order else []
    material_reports = MaterialReportService.get_by_order(user, order.id) if order else []
    bom_options = DinhMucNguyenLieu.get_by_product(order.product_id) if order else []
    all_materials = NguyenLieu.get_all() if user.role == 'QuanLyXuong' else []
    assignments = PhanCong.get_by_order(order.id) if order else []
    editable_operation_ids = {op.id for op in operations if can_update_operation(user, order.id, op.id)} if order else set()
    if user.role == 'NhanVien':
        operations = [op for op in operations if op.id in editable_operation_ids]
        progress_list = [progress for progress in progress_list if progress.operation_id in editable_operation_ids]
        defects = [defect for defect in defects if defect.operation_id in editable_operation_ids]

    # Manager appoints one leader; that leader assigns only members of their team.
    assignable_workers = []
    if user.role == 'QuanLyXuong' and order:
        all_workers = TaiKhoan.get_system_users()
        assignable_workers = [w for w in all_workers if w.status == 'Active' and w.role == 'ToTruong']
    elif user.role == 'ToTruong' and order:
        assignable_workers = TeamService.members(user.id)
        assignments = [a for a in assignments if a.operation_id in editable_operation_ids]
    removable_assignment_ids = {
        assignment.id for assignment in assignments
        if user.role == 'QuanLyXuong' or
        (user.role == 'ToTruong' and assignment.operation_id in editable_operation_ids
         and TeamService.is_member(user.id, assignment.user_id))
    }

    return render_template(
        'production.html',
        order=order,
        all_orders=all_orders,
        operations=operations,
        progress_list=progress_list,
        defects=defects,
        materials_used=materials_used,
        material_reports=material_reports,
        bom_options=bom_options,
        all_materials=all_materials,
        editable_operation_ids=editable_operation_ids,
        assignments=assignments,
        assignable_workers=assignable_workers,
        removable_assignment_ids=removable_assignment_ids,
        today=date.today().isoformat()
    )


@workshop_bp.route('/material-reports/<report_id>/approve', methods=['POST'])
@login_required
@role_required('QuanLyXuong')
def approve_material_report(report_id):
    try:
        order_id = MaterialReportService.approve(AuthService.get_current_user(), report_id)
        flash('Đã duyệt phiếu và ghi xuất kho một lần.', 'success')
        return redirect(url_for('workshop.production', order_id=order_id))
    except ValueError as exc:
        flash(str(exc), 'danger')
        return redirect(url_for('workshop.production'))


@workshop_bp.route('/inventory', methods=['GET', 'POST'])
@login_required
@role_required('QuanLyXuong', 'ToTruong')
def inventory():
    if request.method == 'POST':
        if session.get('user_role') != 'QuanLyXuong':
            abort(403)
        try:
            action = request.form.get('action')
            if action == 'create':
                ProductService.create_material(
                    request.form.get('material_id'), request.form.get('name'),
                    request.form.get('unit'), float(request.form.get('opening_stock', 0))
                )
                flash('Đã thêm vật tư vào danh mục kho.', 'success')
            elif action == 'receive':
                ProductService.receive_material(
                    request.form.get('material_id'), float(request.form.get('quantity', 0))
                )
                flash('Đã ghi nhận vật tư nhập kho.', 'success')
            else:
                abort(400)
        except HTTPException:
            raise
        except ValueError as exc:
            flash(str(exc), 'danger')
        return redirect(url_for('workshop.inventory'))
    q = request.args.get('q', '').strip()[:100]
    stock_filter = request.args.get('stock', '')
    materials = NguyenLieu.search(q, stock_filter)
    return render_template('inventory.html', materials=materials, all_materials=NguyenLieu.get_all(),
                           q=q, stock_filter=stock_filter)


@workshop_bp.route('/inventory/<material_id>/edit', methods=['POST'])
@login_required
@role_required('QuanLyXuong')
def edit_material(material_id):
    try:
        name = request.form.get('name', '')
        unit = request.form.get('unit', '')
        stock = float(request.form.get('stock', 0))
        status = request.form.get('status', 'Active')
        ProductService.update_material(material_id, name, unit, stock, status)
        flash(f'Đã cập nhật thông tin vật tư {material_id}.', 'success')
    except (TypeError, ValueError) as exc:
        flash(str(exc), 'danger')
    return redirect(url_for('workshop.inventory', q=material_id))


@workshop_bp.route('/inventory/<material_id>/delete', methods=['POST'])
@login_required
@role_required('QuanLyXuong')
def delete_material(material_id):
    try:
        ProductService.delete_material(material_id)
        flash(f'Đã xóa vật tư {material_id} khỏi kho.', 'success')
    except ValueError as exc:
        flash(str(exc), 'danger')
    return redirect(url_for('workshop.inventory'))


@workshop_bp.route('/statistics')
@login_required
@role_required('QuanLyXuong')
def statistics():
    progress_summary = StatisticsService.get_order_progress_summary()
    productivity = StatisticsService.get_productivity_by_operation()
    defect_stats = StatisticsService.get_defect_rate_statistics()

    return render_template(
        'statistics.html',
        progress_summary=progress_summary,
        productivity=productivity,
        defect_stats=defect_stats
    )


@workshop_bp.route('/daily-reports', methods=['GET', 'POST'])
@login_required
@role_required('QuanLyXuong', 'ToTruong')
def daily_reports():
    user = AuthService.get_current_user()
    if request.method == 'POST':
        if user.role != 'ToTruong':
            abort(403)
        try:
            DailyReportService.submit(
                user, request.form.get('order_id', '').strip(),
                request.form.get('report_date', ''),
                int(request.form.get('completed', 0)),
                int(request.form.get('defective', 0)),
                request.form.get('note', '')
            )
            flash('Đã gửi báo cáo cuối ngày cho Quản lý xưởng.', 'success')
        except (ValueError, PermissionError) as exc:
            flash(str(exc), 'danger')
        return redirect(url_for('workshop.daily_reports'))
    q = request.args.get('q', '').strip()[:100]
    status_filter = request.args.get('status', '')
    report_date = request.args.get('date', '')
    reports = DailyReportService.search(user, q, status_filter, report_date)
    orders = DonSanXuat.search(user_id=user.id) if user.role == 'ToTruong' else []
    return render_template('daily_reports.html', reports=reports, orders=orders, q=q,
                           status_filter=status_filter, report_date=report_date, today=date.today().isoformat())


@workshop_bp.route('/daily-reports/<report_id>/review', methods=['POST'])
@login_required
@role_required('QuanLyXuong')
def review_daily_report(report_id):
    try:
        DailyReportService.review(AuthService.get_current_user(), report_id)
        flash('Đã xác nhận báo cáo cuối ngày.', 'success')
    except ValueError as exc:
        flash(str(exc), 'danger')
    return redirect(url_for('workshop.daily_reports'))


@workshop_bp.route('/production/assign', methods=['POST'])
@login_required
@role_required('QuanLyXuong', 'ToTruong')
def assign_worker():
    try:
        actor = AuthService.get_current_user()
        order_id = request.form.get('order_id', '').strip()
        operation_id = request.form.get('operation_id', '').strip()
        user_ids = request.form.getlist('user_ids[]')
        if not user_ids and request.form.get('user_id'):
            user_ids = [request.form.get('user_id')]
        assign_date = request.form.get('assign_date', date.today().isoformat())
        names = ProductionService.assign_workers(actor, operation_id, user_ids, order_id, assign_date)
        flash(f'Đã phân công {len(names)} người vào công đoạn trong Đơn #{order_id}.', 'success')
    except PermissionError:
        abort(403)
    except ValueError as exc:
        flash(str(exc), 'danger')
    except HTTPException:
        raise
    except Exception:
        flash('Không thể phân công nhân viên. Vui lòng thử lại.', 'danger')
    return redirect(url_for('workshop.production', order_id=request.form.get('order_id')))


@workshop_bp.route('/production/unassign/<assignment_id>', methods=['POST'])
@login_required
@role_required('QuanLyXuong', 'ToTruong')
def unassign_worker(assignment_id):
    try:
        actor = AuthService.get_current_user()
        assignment = query_db('SELECT p.MaDon, p.MaCongDoan, p.MaTaiKhoan, t.VaiTro '
                              'FROM PhanCong p JOIN TaiKhoan t ON t.MaTaiKhoan = p.MaTaiKhoan '
                              'WHERE p.MaPhanCong = %s',
                              (assignment_id,), one=True)
        if not assignment:
            raise ValueError('Phân công không tồn tại.')
        if actor.role == 'ToTruong' and (
                not can_update_operation(actor, assignment['MaDon'], assignment['MaCongDoan']) or
                not TeamService.is_member(actor.id, assignment['MaTaiKhoan'])):
            abort(403)
        if actor.role == 'QuanLyXuong' and assignment['VaiTro'] == 'ToTruong' and query_db(
                'SELECT 1 AS ok FROM PhanCong WHERE MaDon = %s AND MaCongDoan = %s '
                'AND MaTaiKhoan <> %s LIMIT 1',
                (assignment['MaDon'], assignment['MaCongDoan'], assignment['MaTaiKhoan']), one=True):
            raise ValueError('Hãy gỡ phân công nhân viên của công đoạn trước khi gỡ Tổ trưởng.')
        PhanCong.delete_assignment(assignment_id)
        flash('Đã gỡ phân công nhân viên khỏi công đoạn.', 'success')
    except HTTPException:
        raise
    except ValueError as exc:
        flash(str(exc), 'danger')
    except Exception:
        flash('Không thể gỡ phân công. Vui lòng thử lại.', 'danger')
    return redirect(url_for('workshop.production', order_id=request.form.get('order_id')))


@workshop_bp.route('/teams', methods=['GET', 'POST'])
@login_required
@role_required('QuanLyXuong')
def teams():
    manager = AuthService.get_current_user()
    if request.method == 'POST':
        try:
            TeamService.add(manager, request.form.get('leader_id', ''), request.form.get('worker_id', ''))
            flash('Đã thêm nhân viên vào tổ.', 'success')
        except ValueError as exc:
            flash(str(exc), 'danger')
        return redirect(url_for('workshop.teams'))
    users = TaiKhoan.get_system_users(status='Active')
    return render_template('teams.html', leaders=[u for u in users if u.role == 'ToTruong'],
                           workers=[u for u in users if u.role == 'NhanVien'],
                           memberships=TeamService.assignments())


@workshop_bp.route('/teams/<leader_id>/<worker_id>/remove', methods=['POST'])
@login_required
@role_required('QuanLyXuong')
def remove_team_member(leader_id, worker_id):
    TeamService.remove(AuthService.get_current_user(), leader_id, worker_id)
    flash('Đã gỡ nhân viên khỏi tổ.', 'success')
    return redirect(url_for('workshop.teams'))
