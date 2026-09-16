import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from database import query_db, execute_db, log_audit
from routes.auth import login_required, role_required
from config import Config
from datetime import date

expenses_bp = Blueprint('expenses', __name__)

EXPENSE_CATEGORIES = [
    ('Idol', 'गणपती मूर्ती (Idol)'),
    ('Decoration', 'डेकोरेसन / मंडप (Decoration)'),
    ('DJ', 'DJ / साऊंड सिस्टम (DJ)'),
    ('Tractor Rent', 'ट्रॅक्टर भाडे (Tractor Rent)'),
    ('Band', 'बँड / ढोल ताशा (Band)'),
    ('Pujan', 'पूजा साहित्य (Pujan)'),
    ('Haar', 'हार / फुले (Haar/Flowers)'),
    ('Generator', 'जनरेटर (Generator)'),
    ('Gas', 'गॅस सिलेंडर (Gas)'),
    ('Permission', 'परवानगी / कायदेशीर (Permission)'),
    ('Receipt Book', 'पावती पुस्तक छपाई (Receipt Book)'),
    ('Utensils', 'भांडी / साहित्य (Utensils)'),
    ('Dhoti', 'धोती / वस्त्रे (Dhoti)'),
    ('Room Rent', 'रूम भाडे (Room Rent)'),
    ('Ganpati Pata', 'गणपती पाटा /्यासपीठ (Platform)'),
    ('Transport', 'वाहतूक खर्च (Transport)'),
    ('Repair', 'दुरुस्ती (Repair)'),
    ('Food', 'अन्न / अल्पोपहार (Food)'),
    ('Other', 'इतर खर्च (Other)')
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@expenses_bp.route('/expenses')
@login_required
def index():
    category_filter = request.args.get('category', '').strip()
    
    sql = "SELECT * FROM expenses WHERE year_label='2026'"
    params = []
    
    if category_filter:
        sql += " AND category = ?"
        params.append(category_filter)
        
    sql += " ORDER BY expense_date DESC, id DESC"
    records = query_db(sql, params)

    total_res = query_db("SELECT SUM(amount) as total FROM expenses WHERE year_label='2026'", one=True)
    total_amount = float(total_res['total'] or 0) if total_res else 0.0

    return render_template('expenses/index.html', records=records, total_amount=total_amount, categories=EXPENSE_CATEGORIES, category_filter=category_filter)

@expenses_bp.route('/expenses/add', methods=['POST'])
@login_required
@role_required('admin', 'treasurer')
def add():
    category = request.form.get('category', 'Other')
    description = request.form.get('description', '').strip()
    vendor = request.form.get('vendor', '').strip()
    amount_str = request.form.get('amount', '0').strip()
    payment_method = request.form.get('payment_method', 'Cash')
    expense_date = request.form.get('expense_date', '').strip() or date.today().isoformat()
    bill_no = request.form.get('bill_no', '').strip()
    approved_by = request.form.get('approved_by', '').strip() or session.get('full_name')
    notes = request.form.get('notes', '').strip()

    if not description:
        flash('कृपया खर्चाचा तपशील / वर्णन प्रविष्ट करा.', 'danger')
        return redirect(url_for('expenses.index'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash('कृपया वैध रक्कम भरा.', 'danger')
        return redirect(url_for('expenses.index'))

    # Handle Bill File Upload
    bill_filename = None
    if 'bill_file' in request.files:
        file = request.files['bill_file']
        if file and file.filename != '' and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            safe_name = f"bill_{int(date.today().strftime('%Y%m%d%H%M%S'))}_{secure_filename(file.filename)}"
            os.makedirs(Config.BILL_UPLOADS, exist_ok=True)
            file.save(os.path.join(Config.BILL_UPLOADS, safe_name))
            bill_filename = safe_name

    exp_id = execute_db("""
        INSERT INTO expenses (year_label, category, description, vendor, amount, payment_method, expense_date, bill_no, bill_file, approved_by, notes, created_by)
        VALUES ('2026', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (category, description, vendor, amount, payment_method, expense_date, bill_no, bill_filename, approved_by, notes, session.get('username')))

    tx_id = f"TX-2026-EXP{exp_id:04d}"
    execute_db("""
        INSERT INTO transactions (year_label, transaction_id, date, type, module, category, description, income_amount, expense_amount, payment_method, reference_no, created_by)
        VALUES ('2026', ?, ?, 'EXPENSE', 'OTHER_EXPENSE', ?, ?, 0.00, ?, ?, ?, ?)
    """, (tx_id, expense_date, category, description, amount, payment_method, bill_no or f"EXP-{exp_id}", session.get('username')))

    log_audit(session.get('user_id'), session.get('username'), 'CREATE', 'expenses', exp_id, None, f"Category: {category}, Amount: ₹{amount}")

    flash('खर्च यशस्वीरित्या नोंदवला गेला.', 'success')
    return redirect(url_for('expenses.index'))

@expenses_bp.route('/expenses/bill/<filename>')
@login_required
def view_bill(filename):
    return send_from_directory(Config.BILL_UPLOADS, filename)

@expenses_bp.route('/expenses/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete(id):
    record = query_db("SELECT * FROM expenses WHERE id = ?", (id,), one=True)
    if record:
        execute_db("DELETE FROM expenses WHERE id = ?", (id,))
        if record['bill_file']:
            filepath = os.path.join(Config.BILL_UPLOADS, record['bill_file'])
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"File delete error: {e}")
        log_audit(session.get('user_id'), session.get('username'), 'DELETE', 'expenses', id, str(record), None)
        flash('खर्च नोंद रद्द केली गेली.', 'info')
    return redirect(url_for('expenses.index'))
