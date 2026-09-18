from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import query_db, execute_db, log_audit, get_active_financial_year
from routes.auth import login_required, role_required
from datetime import date
from routes.receipts import save_receipt, generate_receipt_number

mahaprasad_bp = Blueprint('mahaprasad', __name__)

def generate_mp_receipt_no():
    year = get_active_financial_year()
    return generate_receipt_number(year, 'MAHAPRASAD')

@mahaprasad_bp.route('/mahaprasad')
@login_required
def index():
    donations = query_db("SELECT * FROM mahaprasad_donations WHERE year_label=(SELECT value FROM settings WHERE key='active_year') ORDER BY payment_date DESC, id DESC")
    expenses = query_db("SELECT * FROM mahaprasad_expenses WHERE year_label=(SELECT value FROM settings WHERE key='active_year') ORDER BY expense_date DESC, id DESC")

    donation_total_res = query_db("SELECT SUM(amount) as total FROM mahaprasad_donations WHERE year_label=(SELECT value FROM settings WHERE key='active_year')", one=True)
    expense_total_res = query_db("SELECT SUM(amount) as total FROM mahaprasad_expenses WHERE year_label=(SELECT value FROM settings WHERE key='active_year')", one=True)

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
@role_required('admin')
def add_donation():
    receipt_no = request.form.get('receipt_no', '').strip() or generate_mp_receipt_no()
    donor_name = request.form.get('donor_name', '').strip()
    mobile = request.form.get('mobile', '').strip()
    address = request.form.get('address', '').strip()
    purpose = request.form.get('purpose', '').strip()
    donation_type = request.form.get('donation_type', 'Money').strip()
    item_details = request.form.get('item_details', '').strip()
    amount_str = request.form.get('amount', '0').strip()
    payment_method = request.form.get('payment_method', 'Cash')
    payment_date = request.form.get('payment_date', '').strip() or date.today().isoformat()
    notes = request.form.get('notes', '').strip()

    if not donor_name:
        flash('कृपया देणगीदाराचे नाव भरणी करा.', 'danger')
        return redirect(url_for('mahaprasad.index'))

    if donation_type not in ('Money', 'Items'):
        flash('कृपया देणगीचा प्रकार निवडा.', 'danger')
        return redirect(url_for('mahaprasad.index'))

    if donation_type == 'Items' and not item_details:
        flash('कृपया दिलेल्या साहित्याचा तपशील भरा.', 'danger')
        return redirect(url_for('mahaprasad.index'))

    try:
        amount = float(amount_str or 0)
        if donation_type == 'Money' and amount <= 0:
            raise ValueError
        if amount < 0:
            raise ValueError
    except ValueError:
        flash('कृपया वैध रक्कम भरा.', 'danger')
        return redirect(url_for('mahaprasad.index'))

    if query_db("SELECT id FROM mahaprasad_donations WHERE receipt_no=? AND year_label=?",
                (receipt_no, get_active_financial_year()), one=True):
        flash(f"पावती क्रमांक '{receipt_no}' आधीपासून अस्तित्वात आहे.", 'danger')
        return redirect(url_for('mahaprasad.index'))

    mp_id = execute_db("""
        INSERT INTO mahaprasad_donations (year_label, receipt_no, donor_name, mobile, address, purpose, donation_type, item_details, amount, payment_method, payment_date, notes, created_by)
        VALUES ((SELECT value FROM settings WHERE key='active_year'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (receipt_no, donor_name, mobile, address, purpose, donation_type, item_details, amount, payment_method, payment_date, notes, session.get('username')))

    if donation_type == 'Money' and amount > 0:
        tx_id = f"TX-{get_active_financial_year()}-MPD{mp_id:04d}"
        execute_db("""
            INSERT INTO transactions (year_label, transaction_id, date, type, module, category, description, income_amount, expense_amount, payment_method, reference_no, created_by)
            VALUES ((SELECT value FROM settings WHERE key='active_year'), ?, ?, 'INCOME', 'MAHAPRASAD_DONATION', 'महाप्रसाद देणगी', ?, ?, 0.00, ?, ?, ?)
        """, (tx_id, payment_date, f"महाप्रसाद देणगी - {donor_name}", amount, payment_method, receipt_no, session.get('username')))

    log_audit(session.get('user_id'), session.get('username'), 'CREATE', 'mahaprasad_donations', mp_id, None, f"Amount: ₹{amount}")
    save_receipt(get_active_financial_year(), receipt_no, 'MAHAPRASAD', mp_id,
                 donor_name, mobile, address, amount, payment_method, payment_date,
                 'महाप्रसाद देणगी' + (f' - {purpose}' if purpose else '') +
                 (f' - {item_details}' if item_details else '') +
                 (f' - {notes}' if notes else ''))
    flash('महाप्रसाद देणगी यशस्वीरित्या नोंदवली गेली.', 'success')
    return redirect(url_for('receipts.view', id=query_db(
        "SELECT id FROM receipts WHERE source_type='MAHAPRASAD' AND source_id=?",
        (mp_id,), one=True)['id']))

@mahaprasad_bp.route('/mahaprasad/expense/add', methods=['POST'])
@login_required
@role_required('admin')
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
        VALUES ((SELECT value FROM settings WHERE key='active_year'), ?, ?, ?, ?, ?, ?, ?, ?)
    """, (item_name, vendor, amount, payment_method, expense_date, bill_no, notes, session.get('username')))

    tx_id = f"TX-{get_active_financial_year()}-MPE{mpe_id:04d}"
    execute_db("""
        INSERT INTO transactions (year_label, transaction_id, date, type, module, category, description, income_amount, expense_amount, payment_method, reference_no, created_by)
        VALUES ((SELECT value FROM settings WHERE key='active_year'), ?, ?, 'EXPENSE', 'MAHAPRASAD_EXPENSE', 'महाप्रसाद खर्च', ?, 0.00, ?, ?, ?, ?)
    """, (tx_id, expense_date, f"महाप्रसाद खर्च - {item_name}", amount, payment_method, bill_no or f"MPE-{mpe_id}", session.get('username')))

    log_audit(session.get('user_id'), session.get('username'), 'CREATE', 'mahaprasad_expenses', mpe_id, None, f"Amount: ₹{amount}")
    flash('महाप्रसाद खर्च यशस्वीरित्या नोंदवला गेला.', 'success')
    return redirect(url_for('mahaprasad.index'))

@mahaprasad_bp.route('/mahaprasad/donation/<int:donation_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_donation(donation_id):
    donation = query_db("SELECT * FROM mahaprasad_donations WHERE id=?", (donation_id,), one=True)
    if not donation:
        return ('Donation not found', 404)
    if request.method == 'POST':
        mobile = request.form.get('mobile', '').strip()
        payment_method = request.form.get('payment_method', 'Cash').strip()
        notes = request.form.get('notes', '').strip()
        execute_db(
            "UPDATE mahaprasad_donations SET mobile=?, payment_method=?, notes=? WHERE id=?",
            (mobile, payment_method, notes, donation_id)
        )
        details = 'महाप्रसाद देणगी'
        if donation['purpose']:
            details += f" - {donation['purpose']}"
        if donation['item_details']:
            details += f" - {donation['item_details']}"
        if notes:
            details += f" - {notes}"
        execute_db(
            "UPDATE receipts SET mobile=?, payment_method=?, details=? WHERE source_type='MAHAPRASAD' AND source_id=?",
            (mobile, payment_method, details, donation_id)
        )
        execute_db(
            "UPDATE transactions SET payment_method=? WHERE module='MAHAPRASAD_DONATION' AND reference_no=?",
            (payment_method, donation['receipt_no'])
        )
        log_audit(session.get('user_id'), session.get('username'), 'UPDATE',
                  'mahaprasad_donations', donation_id, str(donation),
                  f'Updated mobile and payment method for {donation["receipt_no"]}')
        flash('देणगीची मोबाईल आणि पेमेंट माहिती अद्ययावत झाली.', 'success')
        return redirect(url_for('mahaprasad.index'))
    return render_template('mahaprasad/edit_donation.html', donation=donation)
