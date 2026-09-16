from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from database import query_db, log_audit
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('कृपया प्रथम लॉगिन करा.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session or session['user_role'] not in roles:
                flash('या क्रियेसाठी तुम्हाला परवानगी नाही.', 'danger')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = query_db("SELECT * FROM users WHERE username = ? AND status = 'active'", (username,), one=True)
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['user_role'] = user['role']
            session.setdefault('lang', 'mr')

            log_audit(user['id'], user['username'], 'LOGIN', 'users', user['id'], None, 'User logged in')
            flash(f"सुस्वागतम्, {user['full_name']}!", 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('अवैध वापरकर्ता नाव किंवा पासवर्ड. कृपया पुन्हा प्रयत्न करा.', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    if 'user_id' in session:
        log_audit(session.get('user_id'), session.get('username'), 'LOGOUT', 'users', session.get('user_id'), None, 'User logged out')
    session.clear()
    flash('तुम्ही यशस्वीरीत्या बाहेर पडला आहात.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/lang/<lang_code>')
def set_language(lang_code):
    if lang_code in ['mr', 'en']:
        session['lang'] = lang_code
    return redirect(request.referrer or url_for('dashboard.index'))
