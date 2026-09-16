from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import query_db, execute_db, log_audit
from routes.auth import login_required, role_required
from datetime import date

mahaprasad_bp = Blueprint('mahaprasad', __name__)

def generate_mp_receipt_no():
    res = query_db("SELECT MAX(id) as max_id FROM mahaprasad_donations", one=True)
    next_id = (res['max_id'] or 0) + 1
    return f"MPD-2026-{next_id:04d}"

@mahaprasad_bp.route('/mahaprasad')
@login_required
def index():
    donations = query_db("SELECT * FROM mahaprasad_donations WHERE year_label='2026' ORDER BY payment_date DESC, id DESC")
    expenses = query_db("SELECT * FROM mahaprasad_expenses WHERE year_label='2026' ORDER BY expense_date DESC, id DESC")

    donation_total_res = query_db("SELECT SUM(amount) as total FROM mahaprasad_donations WHERE year_label='2026'", one=True)
    expense_total_res = query_db("SELECT SUM(amount) as total FROM mahaprasad_expenses WHERE year_label='2026'", one=True)

    donation_total = float(donation_total_res['total'] or 0) if donation_total_res else 0.0
    expense_total = float(expense_total_res['total'] or 0) if expense_total_res else 0.0
    net_mp_balance = donation_total - expense_total

    auto_receipt = generate_mp_receipt_no()
    return render_template('mahaprasad/index.html', 
                           donations=donations, 
                           expenses=expenses, 
                           donation_total=donation_total, 
                           expense_total=expense_total, 
                           net_mp_balance=net_mp_balance,
                           auto_receipt=auto_receipt)

@mahaprasad_bp.route('/mahaprasad/donation/add', methods=['POST'])
@login_required
@role_required('admin', 'treasurer')
def add_donation():
    receipt_no = request.form.get('receipt_no', '').strip() or generate_mp_receipt_no()
    donor_name = request.form.get('donor_name', '').strip()
    mobile = request.form.get('mobile', '').strip()
    amount_str = request.form.get('amount', '0').strip()
    payment_method = request.form.get('payment_method', 'Cash')
    payment_date = request.form.get('payment_date', '').strip() or date.today().isoformat()
    notes = request.form.get('notes', '').strip()

    if not donor_name:
        flash('कृपया देणगीदाराचे नाव भरणी करा.', 'danger')
        return redirect(url_for('mahaprasad.index'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash('कृपया वैध रक्कम भरा.', 'danger')
        return redirect(url_for('mahaprasad.index'))

    mp_id = execute_db("""
        INSERT INTO mahaprasad_donations (year_label, receipt_no, donor_name, mobile, amount, payment_method, payment_date, notes, created_by)
        VALUES ('2026', ?, ?, ?, ?, ?, ?, ?, ?)
    """, (receipt_no, donor_name, mobile, amount, payment_method, payment_date, notes, session.get('username')))

    tx_id = f"TX-2026-MPD{mp_id:04d}"
    execute_db("""
        INSERT INTO transactions (year_label, transaction_id, date, type, module, category, description, income_amount, expense_amount, payment_method, reference_no, created_by)
        VALUES ('2026', ?, ?, 'INCOME', 'MAHAPRASAD_DONATION', 'महाप्रसाद देणगी', ?, ?, 0.00, ?, ?, ?)
    """, (tx_id, payment_date, f"महाप्रसाद देणगी - {donor_name}", amount, payment_method, receipt_no, session.get('username')))

    log_audit(session.get('user_id'), session.get('username'), 'CREATE', 'mahaprasad_donations', mp_id, None, f"Amount: ₹{amount}")
    flash('महाप्रसाद देणगी यशस्वीरित्या नोंदवली गेली.', 'success')
    return redirect(url_for('mahaprasad.index'))

@mahaprasad_bp.route('/mahaprasad/expense/add', methods=['POST'])
@login_required
@role_required('admin', 'treasurer')
def add_expense():
    item_name = request.form.get('item_name', '').strip()
    vendor = request.form.get('vendor', '').strip()
    amount_str = request.form.get('amount', '0').strip()
    payment_method = request.form.get('payment_method', 'Cash')
    expense_date = request.form.get('expense_date', '').strip() or date.today().isoformat()
    bill_no = request.form.get('bill_no', '').strip()
    notes = request.form.get('notes', '').strip()

    if not item_name:
        flash('कृपया खर्चाचे नाव भरा.', 'danger')
        return redirect(url_for('mahaprasad.index'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash('कृपया वैध रक्कम प्रविष्ट करा.', 'danger')
        return redirect(url_for('mahaprasad.index'))

    mpe_id = execute_db("""
        INSERT INTO mahaprasad_expenses (year_label, item_name, vendor, amount, payment_method, expense_date, bill_no, notes, created_by)
        VALUES ('2026', ?, ?, ?, ?, ?, ?, ?, ?)
    """, (item_name, vendor, amount, payment_method, expense_date, bill_no, notes, session.get('username')))

    tx_id = f"TX-2026-MPE{mpe_id:04d}"
    execute_db("""
        INSERT INTO transactions (year_label, transaction_id, date, type, module, category, description, income_amount, expense_amount, payment_method, reference_no, created_by)
        VALUES ('2026', ?, ?, 'EXPENSE', 'MAHAPRASAD_EXPENSE', 'महाप्रसाद खर्च', ?, 0.00, ?, ?, ?, ?)
    """, (tx_id, expense_date, f"महाप्रसाद खर्च - {item_name}", amount, payment_method, bill_no or f"MPE-{mpe_id}", session.get('username')))

    log_audit(session.get('user_id'), session.get('username'), 'CREATE', 'mahaprasad_expenses', mpe_id, None, f"Amount: ₹{amount}")
    flash('महाप्रसाद खर्च यशस्वीरित्या नोंदवला गेला.', 'success')
    return redirect(url_for('mahaprasad.index'))
