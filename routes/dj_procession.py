from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import query_db, get_active_financial_year, execute_db, log_audit
from routes.receipts import save_receipt, generate_receipt_number
from routes.auth import login_required, role_required
from datetime import date

dj_bp = Blueprint('dj_procession', __name__)

@dj_bp.route('/dj-procession')
@login_required
def index():
    incomes = query_db("""
        SELECT dj_accounts.*, receipts.id AS receipt_id
        FROM dj_accounts
        LEFT JOIN receipts ON receipts.source_type='DJ_INCOME'
            AND receipts.source_id=dj_accounts.id
        WHERE dj_accounts.year_label=(SELECT value FROM settings WHERE key='active_year')
            AND dj_accounts.type='INCOME'
        ORDER BY dj_accounts.date DESC, dj_accounts.id DESC
    """)
    expenses = query_db("SELECT * FROM dj_accounts WHERE year_label=(SELECT value FROM settings WHERE key='active_year') AND type='EXPENSE' ORDER BY date DESC, id DESC")

    inc_total_res = query_db("SELECT SUM(amount) as total FROM dj_accounts WHERE year_label=(SELECT value FROM settings WHERE key='active_year') AND type='INCOME'", one=True)
    exp_total_res = query_db("SELECT SUM(amount) as total FROM dj_accounts WHERE year_label=(SELECT value FROM settings WHERE key='active_year') AND type='EXPENSE'", one=True)

    income_total = float(inc_total_res['total'] or 0) if inc_total_res else 0.0
    expense_total = float(exp_total_res['total'] or 0) if exp_total_res else 0.0
    net_dj_balance = income_total - expense_total

    return render_template('dj/index.html', incomes=incomes, expenses=expenses, income_total=income_total, expense_total=expense_total, net_dj_balance=net_dj_balance)

@dj_bp.route('/dj-procession/income/add', methods=['POST'])
@login_required
@role_required('admin')
def add_income():
    receipt_no = request.form.get('receipt_no', '').strip()
    person_name = request.form.get('person_name', '').strip()
    description = request.form.get('description', '').strip()
    amount_str = request.form.get('amount', '0').strip()
    payment_method = request.form.get('payment_method', 'Cash')
    entry_date = request.form.get('entry_date', '').strip() or date.today().isoformat()
    notes = request.form.get('notes', '').strip()

    if not person_name:
        flash('कृपया वर्गणीदार किंवा समूहाचे नाव प्रविष्ट करा.', 'danger')
        return redirect(url_for('dj_procession.index'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash('कृपया वैध रक्कम भरा.', 'danger')
        return redirect(url_for('dj_procession.index'))

    dj_id = execute_db("""
        INSERT INTO dj_accounts (year_label, type, receipt_or_bill_no, person_or_vendor, description, amount, payment_method, date, notes, created_by)
        VALUES ((SELECT value FROM settings WHERE key='active_year'), 'INCOME', ?, ?, ?, ?, ?, ?, ?, ?)
    """, (receipt_no, person_name, description, amount, payment_method, entry_date, notes, session.get('username')))
    receipt_no = receipt_no or generate_receipt_number(get_active_financial_year(), 'DJ_INCOME')
    execute_db("UPDATE dj_accounts SET receipt_or_bill_no=? WHERE id=?", (receipt_no, dj_id))

    tx_id = f"TX-{get_active_financial_year()}-DJI{dj_id:04d}"
    execute_db("""
        INSERT INTO transactions (year_label, transaction_id, date, type, module, category, description, income_amount, expense_amount, payment_method, reference_no, created_by)
        VALUES ((SELECT value FROM settings WHERE key='active_year'), ?, ?, 'INCOME', 'DJ_INCOME', 'DJ वर्गणी', ?, ?, 0.00, ?, ?, ?)
    """, (tx_id, entry_date, f"DJ वर्गणी - {person_name}", amount, payment_method, receipt_no or f"DJI-{dj_id}", session.get('username')))

    log_audit(session.get('user_id'), session.get('username'), 'CREATE', 'dj_accounts_income', dj_id, None, f"Amount: ₹{amount}")
    save_receipt(get_active_financial_year(), receipt_no, 'DJ_INCOME', dj_id,
                 person_name, request.form.get('mobile', '').strip(), None,
                 amount, payment_method, entry_date, description or notes)
    flash('DJ / मिरवणूक वर्गणी जमा झाली.', 'success')
    receipt = query_db("SELECT id FROM receipts WHERE source_type='DJ_INCOME' AND source_id=?", (dj_id,), one=True)
    return redirect(url_for('receipts.view', id=receipt['id']))

@dj_bp.route('/dj-procession/income/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_income(id):
    record = query_db(
        "SELECT * FROM dj_accounts WHERE id=? AND type='INCOME'", (id,), one=True
    )
    if not record:
        return ('DJ collection not found', 404)
    if request.method == 'POST':
        person_name = request.form.get('person_name', '').strip()
        description = request.form.get('description', '').strip()
        mobile = request.form.get('mobile', '').strip()
        payment_method = request.form.get('payment_method', 'Cash').strip()
        entry_date = request.form.get('entry_date', '').strip() or record['date']
        notes = request.form.get('notes', '').strip()
        try:
            amount = float(request.form.get('amount', '0').strip())
            if not person_name or amount <= 0:
                raise ValueError
        except ValueError:
            flash('कृपया नाव आणि वैध रक्कम भरा.', 'danger')
            return redirect(url_for('dj_procession.edit_income', id=id))

        execute_db(
            """UPDATE dj_accounts
               SET person_or_vendor=?, description=?, amount=?, payment_method=?,
                   date=?, notes=?
               WHERE id=? AND type='INCOME'""",
            (person_name, description, amount, payment_method, entry_date, notes, id)
        )
        execute_db(
            """UPDATE transactions
               SET date=?, description=?, income_amount=?, payment_method=?
               WHERE module='DJ_INCOME' AND reference_no=?""",
            (entry_date, f'DJ वर्गणी - {person_name}', amount, payment_method,
             record['receipt_or_bill_no'])
        )
        execute_db(
            """UPDATE receipts
               SET donor_name=?, mobile=?, amount=?, payment_method=?,
                   payment_date=?, details=?
               WHERE source_type='DJ_INCOME' AND source_id=?""",
            (person_name, mobile, amount, payment_method, entry_date,
             description or notes, id)
        )
        log_audit(
            session.get('user_id'), session.get('username'), 'UPDATE',
            'dj_accounts_income', id, str(record),
            f'Updated DJ collection {record["receipt_or_bill_no"]}'
        )
        flash('DJ वर्गणी माहिती अद्ययावत झाली.', 'success')
        return redirect(url_for('dj_procession.index'))
    receipt = query_db(
        "SELECT mobile FROM receipts WHERE source_type='DJ_INCOME' AND source_id=?",
        (id,), one=True
    )
    return render_template(
        'dj/edit_income.html', record=record, mobile=(receipt or {}).get('mobile', '')
    )

@dj_bp.route('/dj-procession/income/<int:id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_income(id):
    record = query_db(
        "SELECT * FROM dj_accounts WHERE id=? AND type='INCOME'", (id,), one=True
    )
    if not record:
        return ('DJ collection not found', 404)
    execute_db(
        "DELETE FROM transactions WHERE module='DJ_INCOME' AND reference_no=?",
        (record['receipt_or_bill_no'],)
    )
    execute_db(
        "DELETE FROM receipts WHERE source_type='DJ_INCOME' AND source_id=?",
        (id,)
    )
    execute_db("DELETE FROM dj_accounts WHERE id=? AND type='INCOME'", (id,))
    log_audit(
        session.get('user_id'), session.get('username'), 'DELETE',
        'dj_accounts_income', id, str(record), 'Deleted DJ collection'
    )
    flash('DJ वर्गणी नोंद हटवली गेली.', 'info')
    return redirect(url_for('dj_procession.index'))

@dj_bp.route('/dj-procession/expense/add', methods=['POST'])
@login_required
@role_required('admin')
def add_expense():
    bill_no = request.form.get('bill_no', '').strip()
    vendor_name = request.form.get('vendor_name', '').strip()
    description = request.form.get('description', '').strip()
    amount_str = request.form.get('amount', '0').strip()
    payment_method = request.form.get('payment_method', 'Cash')
    entry_date = request.form.get('entry_date', '').strip() or date.today().isoformat()
    notes = request.form.get('notes', '').strip()

    if not vendor_name:
        flash('कृपया विक्रेत्याचे नाव भरणी करा.', 'danger')
        return redirect(url_for('dj_procession.index'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash('कृपया वैध रक्कम प्रविष्ट करा.', 'danger')
        return redirect(url_for('dj_procession.index'))

    dj_id = execute_db("""
        INSERT INTO dj_accounts (year_label, type, receipt_or_bill_no, person_or_vendor, description, amount, payment_method, date, notes, created_by)
        VALUES ((SELECT value FROM settings WHERE key='active_year'), 'EXPENSE', ?, ?, ?, ?, ?, ?, ?, ?)
    """, (bill_no, vendor_name, description, amount, payment_method, entry_date, notes, session.get('username')))

    tx_id = f"TX-{get_active_financial_year()}-DJE{dj_id:04d}"
    execute_db("""
        INSERT INTO transactions (year_label, transaction_id, date, type, module, category, description, income_amount, expense_amount, payment_method, reference_no, created_by)
        VALUES ((SELECT value FROM settings WHERE key='active_year'), ?, ?, 'EXPENSE', 'DJ_EXPENSE', 'DJ खर्च', ?, 0.00, ?, ?, ?, ?)
    """, (tx_id, entry_date, f"DJ खर्च - {vendor_name}", amount, payment_method, bill_no or f"DJE-{dj_id}", session.get('username')))

    log_audit(session.get('user_id'), session.get('username'), 'CREATE', 'dj_accounts_expense', dj_id, None, f"Amount: ₹{amount}")
    flash('DJ / मिरवणूक खर्च यशस्वीरित्या नोंदवला गेला.', 'success')
    return redirect(url_for('dj_procession.index'))
