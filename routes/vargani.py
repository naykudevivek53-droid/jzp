from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import query_db, execute_db, log_audit
from routes.auth import login_required, role_required
from utils.number_to_words import amount_to_words_mr, amount_to_words_en
from datetime import date

vargani_bp = Blueprint('vargani', __name__)

def generate_receipt_no():
    res = query_db("SELECT MAX(id) as max_id FROM vargani", one=True)
    next_id = (res['max_id'] or 0) + 1
    return f"JCM-2026-{next_id:04d}"

@vargani_bp.route('/vargani')
@login_required
def index():
    q = request.args.get('q', '').strip()
    payment_method = request.args.get('payment_method', '').strip()
    status = request.args.get('status', '').strip()

    sql = "SELECT * FROM vargani WHERE year_label='2026'"
    params = []

    if q:
        sql += " AND (contributor_name LIKE ? OR mobile LIKE ? OR receipt_no LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])

    if payment_method:
        sql += " AND payment_method = ?"
        params.append(payment_method)

    if status:
        sql += " AND status = ?"
        params.append(status)

    sql += " ORDER BY payment_date DESC, id DESC"
    records = query_db(sql, params)

    # Totals summary
    totals_res = query_db("""
        SELECT 
            SUM(amount) as total_amount,
            SUM(CASE WHEN status='Paid' THEN amount ELSE 0 END) as paid_amount,
            SUM(CASE WHEN status='Pending' THEN amount ELSE 0 END) as pending_amount,
            COUNT(*) as count
        FROM vargani WHERE year_label='2026'
    """, one=True)

    summary = {
        'total': float(totals_res['total_amount'] or 0),
        'paid': float(totals_res['paid_amount'] or 0),
        'pending': float(totals_res['pending_amount'] or 0),
        'count': totals_res['count'] or 0
    }

    auto_receipt = generate_receipt_no()
    return render_template('vargani/index.html', records=records, summary=summary, auto_receipt=auto_receipt, q=q, payment_method=payment_method, status=status)

@vargani_bp.route('/vargani/add', methods=['POST'])
@login_required
@role_required('admin', 'treasurer')
def add():
    receipt_no = request.form.get('receipt_no', '').strip() or generate_receipt_no()
    contributor_name = request.form.get('contributor_name', '').strip()
    mobile = request.form.get('mobile', '').strip()
    address = request.form.get('address', '').strip()
    amount_str = request.form.get('amount', '0').strip()
    payment_method = request.form.get('payment_method', 'Cash')
    payment_date = request.form.get('payment_date', '').strip() or date.today().isoformat()
    collector_name = request.form.get('collector_name', '').strip() or session.get('full_name')
    status = request.form.get('status', 'Paid')
    notes = request.form.get('notes', '').strip()

    if not contributor_name:
        flash('कृपया वर्गणीदाराचे नाव प्रविष्ट करा.', 'danger')
        return redirect(url_for('vargani.index'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash('कृपया वैध रक्कम प्रविष्ट करा.', 'danger')
        return redirect(url_for('vargani.index'))

    # Check duplicate receipt
    existing = query_db("SELECT id FROM vargani WHERE receipt_no = ? AND year_label='2026'", (receipt_no,), one=True)
    if existing:
        flash(f"पावती क्रमांक '{receipt_no}' आधीपासून अस्तित्वात आहे.", 'danger')
        return redirect(url_for('vargani.index'))

    vargani_id = execute_db("""
        INSERT INTO vargani (year_label, receipt_no, contributor_name, mobile, address, amount, payment_method, payment_date, collector_name, status, notes, created_by)
        VALUES ('2026', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (receipt_no, contributor_name, mobile, address, amount, payment_method, payment_date, collector_name, status, notes, session.get('username')))

    # Record Transaction
    tx_id = f"TX-2026-V{vargani_id:04d}"
    execute_db("""
        INSERT INTO transactions (year_label, transaction_id, date, type, module, category, description, income_amount, expense_amount, payment_method, reference_no, created_by)
        VALUES ('2026', ?, ?, 'INCOME', 'VARGANI', 'वर्गणी', ?, ?, 0.00, ?, ?, ?)
    """, (tx_id, payment_date, f"वर्गणी - {contributor_name}", amount, payment_method, receipt_no, session.get('username')))

    log_audit(session.get('user_id'), session.get('username'), 'CREATE', 'vargani', vargani_id, None, f"Amount: ₹{amount}, Receipt: {receipt_no}")

    flash(f"वर्गणी यशस्‍वीरीत्‍या जमा झाली. पावती क्र: {receipt_no}", 'success')
    return redirect(url_for('vargani.receipt', id=vargani_id))

@vargani_bp.route('/vargani/receipt/<int:id>')
@login_required
def receipt(id):
    record = query_db("SELECT * FROM vargani WHERE id = ?", (id,), one=True)
    if not record:
        flash('पावती सापडली नाही.', 'danger')
        return redirect(url_for('vargani.index'))

    words_mr = amount_to_words_mr(record['amount'])
    words_en = amount_to_words_en(record['amount'])
    return render_template('vargani/receipt.html', record=record, words_mr=words_mr, words_en=words_en)

@vargani_bp.route('/vargani/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete(id):
    record = query_db("SELECT * FROM vargani WHERE id = ?", (id,), one=True)
    if record:
        execute_db("DELETE FROM vargani WHERE id = ?", (id,))
        execute_db("DELETE FROM transactions WHERE reference_no = ?", (record['receipt_no'],))
        log_audit(session.get('user_id'), session.get('username'), 'DELETE', 'vargani', id, str(record), None)
        flash('वर्गणी पावती हटवण्यात आली.', 'info')
    return redirect(url_for('vargani.index'))
