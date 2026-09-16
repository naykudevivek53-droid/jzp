from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import query_db, get_active_financial_year, execute_db, log_audit
from routes.auth import login_required, role_required

pending_bp = Blueprint('pending', __name__)

@pending_bp.route('/pending-vargani')
@login_required
def index():
    records = query_db("SELECT * FROM pending_vargani WHERE year_label=(SELECT value FROM settings WHERE key='active_year') ORDER BY due_date ASC, id DESC")
    
    totals_res = query_db("""
        SELECT 
            SUM(expected_amount) as total_expected,
            SUM(paid_amount) as total_paid,
            SUM(remaining_amount) as total_remaining
        FROM pending_vargani WHERE year_label=(SELECT value FROM settings WHERE key='active_year')
    """, one=True)

    summary = {
        'expected': float(totals_res['total_expected'] or 0),
        'paid': float(totals_res['total_paid'] or 0),
        'remaining': float(totals_res['total_remaining'] or 0)
    }

    return render_template('pending.html', records=records, summary=summary)

@pending_bp.route('/pending-vargani/add', methods=['POST'])
@login_required
@role_required('admin')
def add():
    person_name = request.form.get('person_name', '').strip()
    mobile = request.form.get('mobile', '').strip()
    expected_str = request.form.get('expected_amount', '0').strip()
    paid_str = request.form.get('paid_amount', '0').strip()
    due_date = request.form.get('due_date', '').strip()
    notes = request.form.get('notes', '').strip()

    if not person_name:
        flash('कृपया व्यक्तीचे नाव प्रविष्ट करा.', 'danger')
        return redirect(url_for('pending.index'))

    try:
        expected = float(expected_str)
        paid = float(paid_str)
        remaining = expected - paid
        if expected <= 0 or remaining < 0:
            raise ValueError
    except ValueError:
        flash('कृपया वैध रकमा प्रविष्ट करा.', 'danger')
        return redirect(url_for('pending.index'))

    status = 'Paid' if remaining == 0 else ('Partial' if paid > 0 else 'Pending')

    p_id = execute_db("""
        INSERT INTO pending_vargani (year_label, person_name, mobile, expected_amount, paid_amount, remaining_amount, due_date, status, notes)
        VALUES ((SELECT value FROM settings WHERE key='active_year'), ?, ?, ?, ?, ?, ?, ?, ?)
    """, (person_name, mobile, expected, paid, remaining, due_date, status, notes))

    log_audit(session.get('user_id'), session.get('username'), 'CREATE', 'pending_vargani', p_id, None, f"Remaining: ₹{remaining}")
    flash('थकीत वर्गणी नोंद यशस्वीरित्या जोडली गेली.', 'success')
    return redirect(url_for('pending.index'))

@pending_bp.route('/pending-vargani/update/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def update(id):
    add_paid_str = request.form.get('add_paid', '0').strip()
    record = query_db("SELECT * FROM pending_vargani WHERE id = ?", (id,), one=True)
    if not record:
        flash('नोंद सापडली नाही.', 'danger')
        return redirect(url_for('pending.index'))

    try:
        add_paid = float(add_paid_str)
        if add_paid <= 0:
            raise ValueError
    except ValueError:
        flash('कृपया वैध जमा रक्कम भरा.', 'danger')
        return redirect(url_for('pending.index'))

    new_paid = float(record['paid_amount']) + add_paid
    expected = float(record['expected_amount'])
    new_remaining = expected - new_paid
    if new_remaining < 0:
        new_remaining = 0
        new_paid = expected

    new_status = 'Paid' if new_remaining == 0 else 'Partial'

    execute_db("""
        UPDATE pending_vargani 
        SET paid_amount = ?, remaining_amount = ?, status = ?
        WHERE id = ?
    """, (new_paid, new_remaining, new_status, id))

    log_audit(session.get('user_id'), session.get('username'), 'UPDATE', 'pending_vargani', id, str(record['paid_amount']), str(new_paid))
    flash(f"जमा रक्कम अद्ययावत झाली. उर्वरित थकीत: ₹{new_remaining}", 'success')
    return redirect(url_for('pending.index'))
