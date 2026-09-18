import os
import urllib.parse
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response
from database import query_db, execute_db, get_active_financial_year
from routes.auth import login_required
from utils.number_to_words import amount_to_words_mr, amount_to_words_en

receipts_bp = Blueprint('receipts', __name__, url_prefix='/receipts')

def generate_receipt_number(year, source_type):
    prefix = {'VARGANI': 'VARGANI', 'MAHAPRASAD': 'DONATION', 'DJ_INCOME': 'INCOME'}.get(source_type, 'RECEIPT')
    next_id = (query_db("SELECT COUNT(*) AS count FROM receipts WHERE year_label=? AND source_type=?",
                        (year, source_type), one=True)['count'] or 0) + 1
    candidate = f"{prefix}-{year}-{next_id:04d}"
    while query_db("SELECT id FROM receipts WHERE receipt_no=?", (candidate,), one=True):
        next_id += 1
        candidate = f"{prefix}-{year}-{next_id:04d}"
    return candidate

def save_receipt(year, number, source_type, source_id, name, mobile, address,
                 amount, method, payment_date, details=None):
    """Persist a searchable receipt snapshot without exposing source tables."""
    return execute_db("""INSERT INTO receipts
        (year_label, receipt_no, source_type, source_id, donor_name, mobile, address,
         amount, payment_method, payment_date, details, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (year, number, source_type, source_id, name, mobile, address, amount,
         method, payment_date, details, session.get('username')))

def _receipt(id):
    return query_db("SELECT * FROM receipts WHERE id=?", (id,), one=True)

def normalize_indian_mobile(value):
    digits = ''.join(c for c in str(value or '') if c.isdigit())
    if digits.startswith('0091'):
        digits = digits[4:]
    elif digits.startswith('91') and len(digits) == 12:
        digits = digits[2:]
    elif digits.startswith('0') and len(digits) == 11:
        digits = digits[1:]
    if len(digits) == 10 and digits[0] in '6789':
        return '91' + digits
    return None

@receipts_bp.route('')
@login_required
def index():
    year = request.args.get('year', '').strip() or get_active_financial_year()
    q = request.args.get('q', '').strip()
    source = request.args.get('source_type', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    sql = "SELECT * FROM receipts WHERE year_label=?"
    params = [year]
    if q:
        sql += " AND (receipt_no LIKE ? OR donor_name LIKE ? OR mobile LIKE ?)"
        params.extend(["%"+q+"%"] * 3)
    if source in ('VARGANI', 'MAHAPRASAD'):
        sql += " AND source_type=?"
        params.append(source)
    if date_from:
        sql += " AND payment_date >= ?"
        params.append(date_from)
    if date_to:
        sql += " AND payment_date <= ?"
        params.append(date_to)
    sql += " ORDER BY payment_date DESC, id DESC"
    receipts = query_db(sql, params)
    years = query_db("SELECT year_label FROM financial_years ORDER BY year_label DESC")
    return render_template('receipts/index.html', receipts=receipts, years=years,
                           selected_year=year, q=q, source_type=source,
                           date_from=date_from, date_to=date_to)

@receipts_bp.route('/<int:id>')
@login_required
def view(id):
    receipt = _receipt(id)
    if not receipt:
        flash('पावती सापडली नाही.', 'danger')
        return redirect(url_for('receipts.index'))
    return render_template('receipts/view.html', record=receipt,
                           words_mr=amount_to_words_mr(receipt['amount']),
                           words_en=amount_to_words_en(receipt['amount']),
                           contact=query_db("SELECT value FROM settings WHERE key='contact_number'", one=True),
                           masked_mobile=('****' + str(receipt['mobile'])[-4:]
                                         if receipt.get('mobile') else None))

@receipts_bp.route('/public/<receipt_no>')
def public_view(receipt_no):
    """Public, read-only receipt view with private contact data masked."""
    receipt = query_db(
        "SELECT receipt_no, year_label, source_type, donor_name, amount, payment_method, "
        "payment_date, details FROM receipts WHERE receipt_no=?",
        (receipt_no,), one=True
    )
    if not receipt:
        return ('Receipt not found', 404)
    return render_template(
        'receipts/public_view.html',
        record=receipt,
        words_mr=amount_to_words_mr(receipt['amount']),
        words_en=amount_to_words_en(receipt['amount'])
    )

@receipts_bp.route('/<int:id>/whatsapp')
@login_required
def whatsapp(id):
    receipt = _receipt(id)
    if not receipt:
        flash('पावती सापडली नाही.', 'danger')
        return redirect(url_for('receipts.index'))
    digits = normalize_indian_mobile(receipt.get('mobile'))
    if not digits:
        flash('या पावतीसाठी वैध मोबाईल नंबर उपलब्ध नाही.', 'warning')
        return redirect(url_for('receipts.view', id=id))
    text = (
        "🙏 नमस्कार %s जी,\n\n"
        "जागृती चौक गणेशोत्सव मंडळ\n"
        "गणेशोत्सव %s\n\n"
        "आपली वर्गणी/देणगी यशस्वीरित्या प्राप्त झाली आहे.\n\n"
        "🧾 पावती क्रमांक: %s\n"
        "💰 रक्कम: ₹%.2f\n"
        "📅 दिनांक: %s\n"
        "💳 पेमेंट पद्धत: %s\n\n"
        "आपल्या सहकार्याबद्दल मनःपूर्वक धन्यवाद! 🙏\n\n"
        "जय श्री गणेश! 🕉️"
    ) % (receipt['donor_name'], receipt['year_label'], receipt['receipt_no'],
         float(receipt['amount']), receipt['payment_date'],
         receipt['payment_method'] or '-')
    return redirect("https://api.whatsapp.com/send?phone=%s&text=%s" %
                    (digits, urllib.parse.quote(text)))

@receipts_bp.route('/<int:id>/pdf')
@login_required
def pdf(id):
    receipt = _receipt(id)
    if not receipt:
        return ('Receipt not found', 404)
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen import canvas
        from io import BytesIO
        font_paths = [
            os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts', 'Nirmala.ttf'),
            os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts', 'mangal.ttf'),
            os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts', 'NotoSansDevanagari-Regular.ttf'),
            '/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf',
            '/usr/share/fonts/opentype/noto/NotoSansDevanagari-Regular.ttf',
        ]
        font = next((p for p in font_paths if os.path.exists(p)), None)
        if not font:
            return ('A Devanagari Unicode font is required for PDF generation.', 503)
        pdfmetrics.registerFont(TTFont('ReceiptDevanagari', font))
        stream = BytesIO()
        doc = canvas.Canvas(stream, pagesize=A4)
        doc.setFont('ReceiptDevanagari', 16)
        y = 800
        contact = query_db("SELECT value FROM settings WHERE key='contact_number'", one=True)
        amount_words = amount_to_words_mr(receipt['amount'])
        for line in ('जागृती चौक गणेशोत्सव मंडळ', 'गणेशोत्सव ' + str(receipt['year_label']),
                     'अधिकृत डिजिटल पावती',
                     'पावती क्र.: ' + receipt['receipt_no'],
                     'नाव: ' + receipt['donor_name'],
                     'दिनांक: ' + str(receipt['payment_date']),
                     'रक्कम: ₹ %.2f' % float(receipt['amount']),
                     'अक्षरी: ' + amount_words,
                     'पेमेंट: ' + str(receipt['payment_method'] or ''),
                     'संपर्क: ' + str(contact['value'] if contact else '')):
            doc.drawString(55, y, line)
            y -= 32
        doc.save()
        response = make_response(stream.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=%s.pdf' % receipt['receipt_no']
        return response
    except ImportError:
        return ('PDF support is not installed. Install reportlab.', 503)
