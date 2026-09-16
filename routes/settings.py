import os
import json
import io
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from database import query_db, execute_db, log_audit, get_db_connection, is_mysql_configured, get_active_financial_year, set_active_financial_year
from routes.auth import login_required, role_required
from config import Config

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def index():
    if request.method == 'POST':
        action = request.form.get('action', 'details')
        if action == 'create_year':
            year_label = request.form.get('year_label', '').strip()
            if not year_label.isdigit() or len(year_label) != 4:
                flash('कृपया चार अंकी वित्तीय वर्ष प्रविष्ट करा.', 'danger')
            else:
                try:
                    execute_db("INSERT INTO financial_years (year_label, is_archived) VALUES (?, 0)", (year_label,))
                    set_active_financial_year(year_label)
                    log_audit(session.get('user_id'), session.get('username'), 'CREATE', 'financial_years', year_label, None, year_label)
                    flash(f'वित्तीय वर्ष {year_label} तयार करून निवडले.', 'success')
                except Exception:
                    flash('हे वित्तीय वर्ष आधीपासून अस्तित्वात आहे.', 'warning')
            return redirect(url_for('settings.index'))
        if action == 'select_year':
            try:
                set_active_financial_year(request.form.get('active_year', ''))
                flash('सक्रिय वित्तीय वर्ष अद्ययावत केले.', 'success')
            except ValueError:
                flash('अवैध किंवा संग्रहित वित्तीय वर्ष.', 'danger')
            return redirect(url_for('settings.index'))
        mandal_name_mr = request.form.get('mandal_name_mr', '').strip()
        address = request.form.get('address', '').strip()
        contact_number = request.form.get('contact_number', '').strip()
        receipt_prefix = request.form.get('receipt_prefix', '').strip()

        execute_db("INSERT OR REPLACE INTO settings (key, value) VALUES ('mandal_name_mr', ?)", (mandal_name_mr,))
        execute_db("INSERT OR REPLACE INTO settings (key, value) VALUES ('address', ?)", (address,))
        execute_db("INSERT OR REPLACE INTO settings (key, value) VALUES ('contact_number', ?)", (contact_number,))
        execute_db("INSERT OR REPLACE INTO settings (key, value) VALUES ('receipt_prefix', ?)", (receipt_prefix,))

        log_audit(session.get('user_id'), session.get('username'), 'UPDATE', 'settings', None, None, 'Settings updated')
        flash('सेटिंग्ज अद्ययावत झाल्या.', 'success')
        return redirect(url_for('settings.index'))

    settings_rows = query_db("SELECT * FROM settings")
    settings_dict = {s['key']: s['value'] for s in settings_rows}
    users = query_db("SELECT id, username, full_name, role, status, created_at FROM users")
    years = query_db("SELECT year_label, is_archived FROM financial_years ORDER BY year_label DESC")
    return render_template('settings.html', settings=settings_dict, users=users, years=years,
                           active_year=get_active_financial_year())

@settings_bp.route('/settings/backup')
@login_required
@role_required('admin')
def download_backup():
    if is_mysql_configured():
        # Generate JSON data dump for MySQL environments
        tables = ['users', 'members', 'financial_years', 'vargani', 'mahaprasad_donations', 
                  'mahaprasad_expenses', 'expenses', 'dj_accounts', 'pending_vargani', 'transactions', 'audit_logs', 'settings']
        backup_data = {}
        for table in tables:
            rows = query_db(f"SELECT * FROM {table}")
            # Ensure Decimal and date values are serialized cleanly
            serialized_rows = []
            for row in rows:
                clean_row = {}
                for k, v in row.items():
                    clean_row[k] = str(v) if v is not None else None
                serialized_rows.append(clean_row)
            backup_data[table] = serialized_rows
        
        json_bytes = io.BytesIO(json.dumps(backup_data, indent=2, ensure_ascii=False).encode('utf-8'))
        return send_file(json_bytes, download_name="ganesh_mandal_backup.json", as_attachment=True, mimetype="application/json")
    else:
        db_file = Config.DATABASE_PATH
        if os.path.exists(db_file):
            # SQLite backup API gives a consistent snapshot while the app is running.
            source = get_db_connection()
            snapshot = __import__('sqlite3').connect(':memory:')
            source.backup(snapshot)
            source.close()
            payload = io.BytesIO(snapshot.serialize())
            snapshot.close()
            return send_file(payload, download_name=f"ganesh_mandal_{get_active_financial_year()}_backup.db", as_attachment=True,
                             mimetype='application/x-sqlite3')
        flash('डेटाबेस फाईल सापडली नाही.', 'danger')
        return redirect(url_for('settings.index'))
