from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from database import query_db, execute_db, log_audit, get_db_connection
from routes.auth import login_required, role_required
from config import Config
import os
import shutil

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def index():
    if request.method == 'POST':
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
    return render_template('settings.html', settings=settings_dict, users=users)

@settings_bp.route('/settings/backup')
@login_required
@role_required('admin')
def download_backup():
    db_file = Config.DATABASE_PATH
    if os.path.exists(db_file):
        return send_file(db_file, download_name="ganesh_mandal_2026_backup.db", as_attachment=True)
    flash('डेटाबेस फाईल सापडली नाही.', 'danger')
    return redirect(url_for('settings.index'))
