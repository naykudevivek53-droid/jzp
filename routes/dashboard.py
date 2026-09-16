from flask import Blueprint, render_template, session, jsonify
from database import query_db
from routes.auth import login_required
from datetime import date

dashboard_bp = Blueprint('dashboard', __name__)

def get_financial_summary(year='2026'):
    # Vargani
    vargani_res = query_db("SELECT SUM(amount) as total FROM vargani WHERE year_label=?", (year,), one=True)
    total_vargani = float(vargani_res['total'] or 0) if vargani_res else 0.0

    # Mahaprasad Donation
    mp_donation_res = query_db("SELECT SUM(amount) as total FROM mahaprasad_donations WHERE year_label=?", (year,), one=True)
    total_mp_donation = float(mp_donation_res['total'] or 0) if mp_donation_res else 0.0

    # DJ Income
    dj_income_res = query_db("SELECT SUM(amount) as total FROM dj_accounts WHERE year_label=? AND type='INCOME'", (year,), one=True)
    total_dj_income = float(dj_income_res['total'] or 0) if dj_income_res else 0.0

    total_income = total_vargani + total_mp_donation + total_dj_income

    # Expenses
    mp_expense_res = query_db("SELECT SUM(amount) as total FROM mahaprasad_expenses WHERE year_label=?", (year,), one=True)
    total_mp_expense = float(mp_expense_res['total'] or 0) if mp_expense_res else 0.0

    other_expense_res = query_db("SELECT SUM(amount) as total FROM expenses WHERE year_label=?", (year,), one=True)
    total_other_expense = float(other_expense_res['total'] or 0) if other_expense_res else 0.0

    dj_expense_res = query_db("SELECT SUM(amount) as total FROM dj_accounts WHERE year_label=? AND type='EXPENSE'", (year,), one=True)
    total_dj_expense = float(dj_expense_res['total'] or 0) if dj_expense_res else 0.0

    total_expenses = total_mp_expense + total_other_expense + total_dj_expense
    current_balance = total_income - total_expenses

    # Breakdown by payment method
    cash_inc = float(query_db("SELECT SUM(income_amount) as total FROM transactions WHERE year_label=? AND payment_method='Cash'", (year,), one=True)['total'] or 0)
    cash_exp = float(query_db("SELECT SUM(expense_amount) as total FROM transactions WHERE year_label=? AND payment_method='Cash'", (year,), one=True)['total'] or 0)
    cash_balance = cash_inc - cash_exp

    upi_inc = float(query_db("SELECT SUM(income_amount) as total FROM transactions WHERE year_label=? AND payment_method='UPI'", (year,), one=True)['total'] or 0)
    upi_exp = float(query_db("SELECT SUM(expense_amount) as total FROM transactions WHERE year_label=? AND payment_method='UPI'", (year,), one=True)['total'] or 0)
    upi_balance = upi_inc - upi_exp

    bank_inc = float(query_db("SELECT SUM(income_amount) as total FROM transactions WHERE year_label=? AND payment_method='Bank'", (year,), one=True)['total'] or 0)
    bank_exp = float(query_db("SELECT SUM(expense_amount) as total FROM transactions WHERE year_label=? AND payment_method='Bank'", (year,), one=True)['total'] or 0)
    bank_balance = bank_inc - bank_exp

    # Additional counts
    contributors_count = query_db("SELECT COUNT(*) as cnt FROM vargani WHERE year_label=?", (year,), one=True)['cnt']
    
    pending_res = query_db("SELECT SUM(remaining_amount) as total FROM pending_vargani WHERE year_label=? AND status!='Paid'", (year,), one=True)
    pending_vargani_total = float(pending_res['total'] or 0) if pending_res else 0.0

    today_str = date.today().isoformat()
    today_inc_res = query_db("SELECT SUM(income_amount) as total FROM transactions WHERE year_label=? AND date=?", (year, today_str), one=True)
    today_collection = float(today_inc_res['total'] or 0) if today_inc_res else 0.0

    today_exp_res = query_db("SELECT SUM(expense_amount) as total FROM transactions WHERE year_label=? AND date=?", (year, today_str), one=True)
    today_expenses = float(today_exp_res['total'] or 0) if today_exp_res else 0.0

    return {
        'total_vargani': total_vargani,
        'total_mp_donation': total_mp_donation,
        'total_dj_income': total_dj_income,
        'total_income': total_income,
        'total_mp_expense': total_mp_expense,
        'total_other_expense': total_other_expense,
        'total_dj_expense': total_dj_expense,
        'total_expenses': total_expenses,
        'current_balance': current_balance,
        'cash_balance': cash_balance,
        'upi_balance': upi_balance,
        'bank_balance': bank_balance,
        'contributors_count': contributors_count,
        'pending_vargani_total': pending_vargani_total,
        'today_collection': today_collection,
        'today_expenses': today_expenses
    }

@dashboard_bp.route('/')
@login_required
def index():
    summary = get_financial_summary('2026')
    recent_transactions = query_db("SELECT * FROM transactions WHERE year_label='2026' ORDER BY date DESC, id DESC LIMIT 10")
    return render_template('dashboard.html', summary=summary, recent_transactions=recent_transactions)

@dashboard_bp.route('/api/dashboard-charts')
@login_required
def dashboard_charts():
    year = '2026'
    
    # 1. Expense Categories Chart
    cat_rows = query_db("""
        SELECT category, SUM(amount) as total FROM (
            SELECT 'महाप्रसाद' as category, amount FROM mahaprasad_expenses WHERE year_label=?
            UNION ALL
            SELECT 'DJ / मिरवणूक' as category, amount FROM dj_accounts WHERE year_label=? AND type='EXPENSE'
            UNION ALL
            SELECT category, amount FROM expenses WHERE year_label=?
        ) GROUP BY category
    """, (year, year, year))

    cat_labels = [row['category'] for row in cat_rows]
    cat_totals = [float(row['total']) for row in cat_rows]

    # 2. Payment Methods Chart
    method_rows = query_db("""
        SELECT payment_method, SUM(income_amount + expense_amount) as total 
        FROM transactions WHERE year_label=? 
        GROUP BY payment_method
    """, (year,))

    method_labels = [row['payment_method'] for row in method_rows]
    method_totals = [float(row['total']) for row in method_rows]

    # 3. Daily Income & Expense Trend Chart
    trend_rows = query_db("""
        SELECT date, SUM(income_amount) as inc, SUM(expense_amount) as exp
        FROM transactions WHERE year_label=?
        GROUP BY date ORDER BY date ASC
    """, (year,))

    trend_dates = [row['date'] for row in trend_rows]
    trend_inc = [float(row['inc']) for row in trend_rows]
    trend_exp = [float(row['exp']) for row in trend_rows]

    return jsonify({
        'categories': {'labels': cat_labels, 'data': cat_totals},
        'payment_methods': {'labels': method_labels, 'data': method_totals},
        'daily_trends': {'dates': trend_dates, 'income': trend_inc, 'expenses': trend_exp}
    })
