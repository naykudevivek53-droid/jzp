from flask import Blueprint, render_template
from database import query_db
from routes.auth import login_required, role_required

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/audit-log')
@login_required
@role_required('admin')
def index():
    logs = query_db("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 200")
    return render_template('audit.html', logs=logs)
