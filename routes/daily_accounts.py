from flask import Blueprint, render_template, request, session
from database import query_db
from routes.auth import login_required
from datetime import date, datetime, timedelta

daily_bp = Blueprint('daily_accounts', __name__)

@daily_bp.route('/daily-accounts')
@login_required
def index():
    selected_date_str = request.args.get('date', date.today().isoformat())
    year = '2026'

    # Compute overall opening balance (transactions before selected_date)
    prior_income = float(query_db("SELECT SUM(income_amount) as total FROM transactions WHERE year_label=? AND date < ?", (year, selected_date_str), one=True)['total'] or 0)
    prior_expense = float(query_db("SELECT SUM(expense_amount) as total FROM transactions WHERE year_label=? AND date < ?", (year, selected_date_str), one=True)['total'] or 0)
    opening_balance = prior_income - prior_expense

    # Cash Opening
    cash_prior_inc = float(query_db("SELECT SUM(income_amount) as total FROM transactions WHERE year_label=? AND payment_method='Cash' AND date < ?", (year, selected_date_str), one=True)['total'] or 0)
    cash_prior_exp = float(query_db("SELECT SUM(expense_amount) as total FROM transactions WHERE year_label=? AND payment_method='Cash' AND date < ?", (year, selected_date_str), one=True)['total'] or 0)
    cash_opening = cash_prior_inc - cash_prior_exp

    # Today's Cash
    today_cash_inc = float(query_db("SELECT SUM(income_amount) as total FROM transactions WHERE year_label=? AND payment_method='Cash' AND date = ?", (year, selected_date_str), one=True)['total'] or 0)
    today_cash_exp = float(query_db("SELECT SUM(expense_amount) as total FROM transactions WHERE year_label=? AND payment_method='Cash' AND date = ?", (year, selected_date_str), one=True)['total'] or 0)
    cash_closing = cash_opening + today_cash_inc - today_cash_exp

    # Today's UPI
    today_upi_inc = float(query_db("SELECT SUM(income_amount) as total FROM transactions WHERE year_label=? AND payment_method='UPI' AND date = ?", (year, selected_date_str), one=True)['total'] or 0)
    today_upi_exp = float(query_db("SELECT SUM(expense_amount) as total FROM transactions WHERE year_label=? AND payment_method='UPI' AND date = ?", (year, selected_date_str), one=True)['total'] or 0)
    
    total_upi_inc = float(query_db("SELECT SUM(income_amount) as total FROM transactions WHERE year_label=? AND payment_method='UPI' AND date <= ?", (year, selected_date_str), one=True)['total'] or 0)
    total_upi_exp = float(query_db("SELECT SUM(expense_amount) as total FROM transactions WHERE year_label=? AND payment_method='UPI' AND date <= ?", (year, selected_date_str), one=True)['total'] or 0)
    upi_balance = total_upi_inc - total_upi_exp

    # Today's Bank
    today_bank_inc = float(query_db("SELECT SUM(income_amount) as total FROM transactions WHERE year_label=? AND payment_method='Bank' AND date = ?", (year, selected_date_str), one=True)['total'] or 0)
    today_bank_exp = float(query_db("SELECT SUM(expense_amount) as total FROM transactions WHERE year_label=? AND payment_method='Bank' AND date = ?", (year, selected_date_str), one=True)['total'] or 0)
    
    total_bank_inc = float(query_db("SELECT SUM(income_amount) as total FROM transactions WHERE year_label=? AND payment_method='Bank' AND date <= ?", (year, selected_date_str), one=True)['total'] or 0)
    total_bank_exp = float(query_db("SELECT SUM(expense_amount) as total FROM transactions WHERE year_label=? AND payment_method='Bank' AND date <= ?", (year, selected_date_str), one=True)['total'] or 0)
    bank_balance = total_bank_inc - total_bank_exp

    # Total Today Income & Expense
    today_income = today_cash_inc + today_upi_inc + today_bank_inc
    today_expenses = today_cash_exp + today_upi_exp + today_bank_exp
    closing_balance = opening_balance + today_income - today_expenses

    # Fetch Today's Transactions
    today_transactions = query_db("SELECT * FROM transactions WHERE year_label=? AND date=? ORDER BY id DESC", (year, selected_date_str))

    # Fetch Recent dates summary list
    recent_daily_summary = query_db("""
        SELECT date, 
               SUM(income_amount) as total_inc, 
               SUM(expense_amount) as total_exp,
               COUNT(*) as tx_count
        FROM transactions 
        WHERE year_label=? 
        GROUP BY date 
        ORDER BY date DESC 
        LIMIT 15
    """, (year,))

    daily_data = {
        'date': selected_date_str,
        'opening_balance': opening_balance,
        'today_income': today_income,
        'today_expenses': today_expenses,
        'closing_balance': closing_balance,
        'cash_opening': cash_opening,
        'today_cash_inc': today_cash_inc,
        'today_cash_exp': today_cash_exp,
        'cash_closing': cash_closing,
        'today_upi_inc': today_upi_inc,
        'today_upi_exp': today_upi_exp,
        'upi_balance': upi_balance,
        'today_bank_inc': today_bank_inc,
        'today_bank_exp': today_bank_exp,
        'bank_balance': bank_balance
    }

    return render_template('daily/index.html', daily_data=daily_data, today_transactions=today_transactions, recent_summary=recent_daily_summary, selected_date=selected_date_str)
