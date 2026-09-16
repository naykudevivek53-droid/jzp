from flask import Blueprint, render_template
from database import query_db
from routes.dashboard import get_financial_summary

public_bp = Blueprint('public', __name__)

@public_bp.route('/public-transparency')
def index():
    summary = get_financial_summary('2026')
    
    # Fetch public contributor list (excluding private mobile and address)
    vargani_list = query_db("""
        SELECT receipt_no, contributor_name, amount, payment_date, payment_method 
        FROM vargani 
        WHERE year_label='2026' 
        ORDER BY payment_date DESC, id DESC
    """)

    donor_list = query_db("""
        SELECT receipt_no, donor_name, amount, payment_date, payment_method 
        FROM mahaprasad_donations 
        WHERE year_label='2026' 
        ORDER BY payment_date DESC, id DESC
    """)

    return render_template('public.html', 
                           summary=summary, 
                           vargani_list=vargani_list, 
                           donor_list=donor_list)
