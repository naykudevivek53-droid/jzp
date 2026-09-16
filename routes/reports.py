import io
from flask import Blueprint, render_template, request, send_file, session
from database import query_db, get_active_financial_year
from routes.auth import login_required
from routes.dashboard import get_financial_summary
import openpyxl

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
@login_required
def index():
    report_type = request.args.get('type', 'complete')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    summary = get_financial_summary(get_active_financial_year())

    # Category wise breakdown
    category_summary = query_db("""
        SELECT category, SUM(amount) as total 
        FROM expenses WHERE year_label=(SELECT value FROM settings WHERE key='active_year')
        GROUP BY category
    """)

    # Method wise breakdown
    method_summary = query_db("""
        SELECT payment_method, 
               SUM(income_amount) as total_inc,
               SUM(expense_amount) as total_exp
        FROM transactions WHERE year_label=(SELECT value FROM settings WHERE key='active_year')
        GROUP BY payment_method
    """)

    return render_template('reports/index.html', 
                           summary=summary, 
                           category_summary=category_summary, 
                           method_summary=method_summary,
                           report_type=report_type,
                           start_date=start_date,
                           end_date=end_date)

@reports_bp.route('/hishob-final')
@login_required
def hishob_final():
    summary = get_financial_summary(get_active_financial_year())
    vargani_list = query_db("SELECT * FROM vargani WHERE year_label=(SELECT value FROM settings WHERE key='active_year') ORDER BY id ASC")
    mp_donation_list = query_db("SELECT * FROM mahaprasad_donations WHERE year_label=(SELECT value FROM settings WHERE key='active_year') ORDER BY id ASC")
    dj_income_list = query_db("SELECT * FROM dj_accounts WHERE year_label=(SELECT value FROM settings WHERE key='active_year') AND type='INCOME' ORDER BY id ASC")

    mp_expense_list = query_db("SELECT * FROM mahaprasad_expenses WHERE year_label=(SELECT value FROM settings WHERE key='active_year') ORDER BY id ASC")
    other_expense_list = query_db("SELECT * FROM expenses WHERE year_label=(SELECT value FROM settings WHERE key='active_year') ORDER BY id ASC")
    dj_expense_list = query_db("SELECT * FROM dj_accounts WHERE year_label=(SELECT value FROM settings WHERE key='active_year') AND type='EXPENSE' ORDER BY id ASC")

    return render_template('hishob_final.html',
                           summary=summary,
                           vargani_list=vargani_list,
                           mp_donation_list=mp_donation_list,
                           dj_income_list=dj_income_list,
                           mp_expense_list=mp_expense_list,
                           other_expense_list=other_expense_list,
                           dj_expense_list=dj_expense_list)

@reports_bp.route('/reports/export-excel')
@login_required
def export_excel():
    wb = openpyxl.Workbook()
    
    # Sheet 1: Summary
    ws_summary = wb.active
    ws_summary.title = "Financial Summary"
    
    summary = get_financial_summary(get_active_financial_year())
    ws_summary.append(["जागृती चौक सार्वजनिक गणेश मंडळ - गणेशोत्सव २०२६"])
    ws_summary.append(["वित्तीय सारांश (Financial Summary)"])
    ws_summary.append([])
    ws_summary.append(["शीर्षक (Metric)", "रक्कम (Amount in ₹)"])
    ws_summary.append(["एकूण वर्गणी (Total Vargani)", summary['total_vargani']])
    ws_summary.append(["एकूण महाप्रसाद देणगी (Mahaprasad Donation)", summary['total_mp_donation']])
    ws_summary.append(["एकूण DJ वर्गणी (DJ Collection)", summary['total_dj_income']])
    ws_summary.append(["एकूण जमा (Total Income)", summary['total_income']])
    ws_summary.append([])
    ws_summary.append(["महाप्रसाद खर्च (Mahaprasad Expense)", summary['total_mp_expense']])
    ws_summary.append(["इतर सण खर्च (Other Festival Expense)", summary['total_other_expense']])
    ws_summary.append(["DJ / मिरवणूक खर्च (DJ Expense)", summary['total_dj_expense']])
    ws_summary.append(["एकूण खर्च (Total Expenses)", summary['total_expenses']])
    ws_summary.append([])
    ws_summary.append(["अंतिम शिल्लक (Final Balance)", summary['current_balance']])
    ws_summary.append(["कॅश शिल्लक (Cash Balance)", summary['cash_balance']])
    ws_summary.append(["UPI शिल्लक (UPI Balance)", summary['upi_balance']])
    ws_summary.append(["बँक शिल्लक (Bank Balance)", summary['bank_balance']])

    # Sheet 2: All Transactions
    ws_tx = wb.create_sheet(title="All Transactions")
    ws_tx.append(["ID", "Date", "Type", "Module", "Category", "Description", "Income (₹)", "Expense (₹)", "Payment Method", "Reference No"])
    
    transactions = query_db("SELECT * FROM transactions WHERE year_label=(SELECT value FROM settings WHERE key='active_year') ORDER BY date ASC, id ASC")
    for t in transactions:
        ws_tx.append([
            t['transaction_id'],
            t['date'],
            t['type'],
            t['module'],
            t['category'],
            t['description'],
            float(t['income_amount'] or 0),
            float(t['expense_amount'] or 0),
            t['payment_method'],
            t['reference_no']
        ])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(output, 
                     download_name="Jagriti_Chowk_Ganesh_Mandal_2026_Report.xlsx", 
                     as_attachment=True, 
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
