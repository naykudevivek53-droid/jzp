from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import query_db, execute_db, log_audit
from routes.auth import login_required, role_required
from datetime import date

members_bp = Blueprint('members', __name__)

MANDAL_ROLES = [
    ('President', 'अध्यक्ष (President)'),
    ('Vice President', 'उपाध्यक्ष (Vice President)'),
    ('Secretary', 'सचिव / कार्यवाह (Secretary)'),
    ('Volunteer', 'कार्यकर्ता (Volunteer)')
]

@members_bp.route('/members')
@login_required
def index():
    members = query_db("SELECT * FROM members WHERE role NOT IN ('Treasurer', 'Member') ORDER BY id ASC")
    return render_template('members.html', members=members, roles=MANDAL_ROLES)

@members_bp.route('/members/add', methods=['POST'])
@login_required
@role_required('admin')
def add():
    name = request.form.get('name', '').strip()
    mobile = request.form.get('mobile', '').strip()
    role = request.form.get('role', 'Member')
    address = request.form.get('address', '').strip()
    join_date = request.form.get('join_date', '').strip() or date.today().isoformat()
    status = request.form.get('status', 'active')

    if not name:
        flash('कृपया सदस्याचे नाव प्रविष्ट करा.', 'danger')
        return redirect(url_for('members.index'))

    m_id = execute_db("""
        INSERT INTO members (name, mobile, role, address, join_date, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, mobile, role, address, join_date, status))

    log_audit(session.get('user_id'), session.get('username'), 'CREATE', 'members', m_id, None, f"Name: {name}, Role: {role}")
    flash('नवा सदस्य यशस्वीरित्या जोडला गेला.', 'success')
    return redirect(url_for('members.index'))

@members_bp.route('/members/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete(id):
    execute_db("DELETE FROM members WHERE id = ?", (id,))
    log_audit(session.get('user_id'), session.get('username'), 'DELETE', 'members', id, None, None)
    flash('सदस्य हटवण्यात आला.', 'info')
    return redirect(url_for('members.index'))
