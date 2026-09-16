from flask import Blueprint, render_template, jsonify
from database import query_db
from routes.auth import login_required
from routes.dashboard import get_financial_summary

archive_bp = Blueprint('archive_2025', __name__)

@archive_bp.route('/archive-2025')
@login_required
def index():
    summary_2025 = get_financial_summary('2025')
    vargani_2025 = query_db("SELECT * FROM vargani WHERE year_label='2025' ORDER BY id ASC")
    mp_donations_2025 = query_db("SELECT * FROM mahaprasad_donations WHERE year_label='2025' ORDER BY id ASC")
    mp_expenses_2025 = query_db("SELECT * FROM mahaprasad_expenses WHERE year_label='2025' ORDER BY id ASC")
    other_expenses_2025 = query_db("SELECT * FROM expenses WHERE year_label='2025' ORDER BY id ASC")
    dj_incomes_2025 = query_db("SELECT * FROM dj_accounts WHERE year_label='2025' AND type='INCOME' ORDER BY id ASC")
    dj_expenses_2025 = query_db("SELECT * FROM dj_accounts WHERE year_label='2025' AND type='EXPENSE' ORDER BY id ASC")

    return render_template('archive_2025.html',
                           summary=summary_2025,
                           vargani=vargani_2025,
                           mp_donations=mp_donations_2025,
                           mp_expenses=mp_expenses_2025,
                           other_expenses=other_expenses_2025,
                           dj_incomes=dj_incomes_2025,
                           dj_expenses=dj_expenses_2025)

@archive_bp.route('/comparison')
@login_required
def comparison():
    summary_2025 = get_financial_summary('2025')
    summary_2026 = get_financial_summary('2026')
    return render_template('comparison.html', s25=summary_2025, s26=summary_2026)

@archive_bp.route('/api/validate-2025')
@login_required
def validate_2025():
    s = get_financial_summary('2025')
    
    expected = {
        'total_vargani': 89338.00,
        'total_mp_donation': 22861.00,
        'total_mp_expense': 20234.00,
        'total_other_expense': 78261.00,
        'total_dj_income': 38900.00,
        'total_dj_expense': 38300.00,
        'current_balance': 14304.00
    }

    discrepancies = []
    for k, exp_val in expected.items():
        actual_val = s.get(k, 0.0)
        if abs(actual_val - exp_val) > 0.01:
            discrepancies.append({
                'metric': k,
                'expected': exp_val,
                'actual': actual_val,
                'diff': actual_val - exp_val
            })

    is_valid = len(discrepancies) == 0
    return jsonify({
        'status': 'PASS' if is_valid else 'FAIL',
        'is_valid': is_valid,
        'expected': expected,
        'actual': {k: s.get(k, 0.0) for k in expected},
        'discrepancies': discrepancies
    })
