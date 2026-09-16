from flask import Blueprint, render_template, request, session, make_response
from database import query_db
from routes.auth import login_required

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/transactions')
@login_required
def index():
    type_filter = request.args.get('type', '').strip()
    payment_filter = request.args.get('payment_method', '').strip()
    module_filter = request.args.get('module', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    search = request.args.get('q', '').strip()

    sql = "SELECT * FROM transactions WHERE year_label='2026'"
    params = []

    if type_filter:
        sql += " AND type = ?"
        params.append(type_filter)

    if payment_filter:
        sql += " AND payment_method = ?"
        params.append(payment_filter)

    if module_filter:
        sql += " AND module = ?"
        params.append(module_filter)

    if start_date:
        sql += " AND date >= ?"
        params.append(start_date)

    if end_date:
        sql += " AND date <= ?"
        params.append(end_date)

    if search:
        sql += " AND (description LIKE ? OR reference_no LIKE ? OR category LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    sql += " ORDER BY date DESC, id DESC"
    transactions = query_db(sql, params)

    total_inc = sum(float(t['income_amount'] or 0) for t in transactions)
    total_exp = sum(float(t['expense_amount'] or 0) for t in transactions)
    net_total = total_inc - total_exp

    return render_template('transactions.html', 
                           transactions=transactions, 
                           total_inc=total_inc, 
                           total_exp=total_exp, 
                           net_total=net_total,
                           type_filter=type_filter,
                           payment_filter=payment_filter,
                           module_filter=module_filter,
                           start_date=start_date,
                           end_date=end_date,
                           search=search)
