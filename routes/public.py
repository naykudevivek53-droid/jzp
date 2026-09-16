from flask import Blueprint, render_template, request, abort
from database import query_db, get_active_financial_year
from routes.dashboard import get_financial_summary

public_bp = Blueprint('public', __name__)

def _public_expense_union(year):
    return """
        SELECT id, 'expenses' AS source, category, description, amount,
               payment_method, vendor, notes, expense_date, bill_no, created_at
        FROM expenses WHERE year_label=?
        UNION ALL
        SELECT id, 'mahaprasad_expenses' AS source, 'महाप्रसाद खर्च' AS category,
               item_name AS description, amount, payment_method, vendor, notes,
               expense_date, bill_no, created_at
        FROM mahaprasad_expenses WHERE year_label=?
        UNION ALL
        SELECT id, 'dj_accounts' AS source, 'DJ / मिरवणूक खर्च' AS category,
               description, amount, payment_method, person_or_vendor AS vendor,
               notes, date AS expense_date, receipt_or_bill_no AS bill_no, created_at
        FROM dj_accounts WHERE year_label=? AND type='EXPENSE'
    """, [year, year, year]

@public_bp.route('/public-transparency')
def index():
    available_years = query_db("SELECT year_label FROM financial_years ORDER BY year_label DESC")
    years = [row['year_label'] for row in available_years]
    if not years:
        years = [get_active_financial_year()]

    requested_year = request.args.get('year')
    show_all_years = not requested_year or requested_year == 'all'
    year = 'all' if show_all_years else requested_year
    if not show_all_years and year not in years:
        year = years[0]

    if show_all_years:
        summary = {
            key: sum(float(get_financial_summary(financial_year).get(key, 0) or 0) for financial_year in years)
            for key in ('total_vargani', 'total_mp_donation', 'total_dj_income',
                        'total_income', 'total_mp_expense', 'total_other_expense',
                        'total_dj_expense', 'total_expenses')
        }
        summary['current_balance'] = summary['total_income'] - summary['total_expenses']
    else:
        summary = get_financial_summary(year)
    year_filter = "" if show_all_years else "WHERE year_label=?"
    dj_year_filter = "WHERE type='EXPENSE'" if show_all_years else "WHERE year_label=? AND type='EXPENSE'"
    year_params = () if show_all_years else (year,)
    
    # Fetch public contributor list (excluding private mobile and address)
    vargani_list = query_db(f"""
        SELECT receipt_no, contributor_name, amount, payment_date, payment_method 
        FROM vargani 
        {year_filter}
        ORDER BY payment_date DESC, id DESC
    """, year_params)

    donor_list = query_db(f"""
        SELECT receipt_no, donor_name, donation_type, item_details, amount, payment_date, payment_method
        FROM mahaprasad_donations 
        {year_filter}
        ORDER BY payment_date DESC, id DESC
    """, year_params)

    expense_list = query_db(f"""
        SELECT id, 'महाप्रसाद खर्च' AS category, item_name AS description,
               vendor, amount, payment_method, notes, expense_date AS expense_date, bill_no
        FROM mahaprasad_expenses
        {year_filter}
        UNION ALL
        SELECT id, category, description, vendor, amount, payment_method, notes, expense_date, bill_no
        FROM expenses
        {year_filter}
        UNION ALL
        SELECT id, 'DJ / मिरवणूक खर्च' AS category, description,
               person_or_vendor AS vendor, amount, payment_method, notes, date AS expense_date,
               receipt_or_bill_no AS bill_no
        FROM dj_accounts
        {dj_year_filter}
        ORDER BY expense_date DESC
    """, year_params + year_params + year_params)
    expense_count = len(expense_list)

    return render_template('public.html', 
                           summary=summary, 
                           vargani_list=vargani_list, 
                           donor_list=donor_list,
                           expense_list=expense_list,
                           expense_count=expense_count,
                           selected_year=year,
                           public_expense_year=None if show_all_years else year,
                           available_years=years)

@public_bp.route('/public/expenses')
def public_expenses():
    available_years = query_db("SELECT year_label FROM financial_years ORDER BY year_label DESC")
    years = [row['year_label'] for row in available_years] or [get_active_financial_year()]
    year = request.args.get('year', years[0])
    if year not in years:
        year = years[0]

    page = max(request.args.get('page', 1, type=int), 1)
    per_page = 25
    filters = []
    filter_params = []
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    category = request.args.get('category', '').strip()
    payment_method = request.args.get('payment_method', '').strip()
    search = request.args.get('search', '').strip()
    if date_from:
        filters.append('expense_date >= ?')
        filter_params.append(date_from)
    if date_to:
        filters.append('expense_date <= ?')
        filter_params.append(date_to)
    if category:
        filters.append('category = ?')
        filter_params.append(category)
    if payment_method:
        filters.append('payment_method = ?')
        filter_params.append(payment_method)
    if search:
        filters.append('(description LIKE ? OR vendor LIKE ? OR notes LIKE ?)')
        term = f'%{search}%'
        filter_params.extend([term, term, term])

    union_sql, union_params = _public_expense_union(year)
    where_sql = f" WHERE {' AND '.join(filters)}" if filters else ''
    total_row = query_db(
        f"SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total FROM ({union_sql}) AS all_expenses{where_sql}",
        union_params + filter_params, one=True
    )
    total_count = int(total_row['count'] or 0)
    total_amount = float(total_row['total'] or 0)
    total_pages = max((total_count + per_page - 1) // per_page, 1)
    page = min(page, total_pages)
    expenses = query_db(
        f"""SELECT * FROM ({union_sql}) AS all_expenses{where_sql}
            ORDER BY expense_date DESC, id DESC, created_at DESC
            LIMIT ? OFFSET ?""",
        union_params + filter_params + [per_page, (page - 1) * per_page]
    )
    categories = query_db(
        f"SELECT DISTINCT category FROM ({union_sql}) AS all_expenses ORDER BY category",
        union_params
    )
    payment_methods = query_db(
        f"SELECT DISTINCT payment_method FROM ({union_sql}) AS all_expenses ORDER BY payment_method",
        union_params
    )
    query_args = request.args.to_dict(flat=True)
    query_args.pop('page', None)
    return render_template(
        'public_expenses.html',
        expenses=expenses, total_count=total_count, total_amount=total_amount,
        page=page, total_pages=total_pages, selected_year=year,
        available_years=years, categories=categories,
        payment_methods=payment_methods, filters=query_args
    )

@public_bp.route('/public/expenses/<int:expense_id>')
def public_expense_detail(expense_id):
    year = request.args.get('year', get_active_financial_year())
    source = request.args.get('source', 'expenses')
    tables = {
        'expenses': ('expenses', 'id, category, description, amount, payment_method, vendor, notes, expense_date, bill_no, created_at'),
        'mahaprasad_expenses': ('mahaprasad_expenses', 'id, item_name AS description, amount, payment_method, vendor, notes, expense_date, bill_no, created_at'),
        'dj_accounts': ('dj_accounts', 'id, description, amount, payment_method, person_or_vendor AS vendor, notes, date AS expense_date, receipt_or_bill_no AS bill_no, created_at'),
    }
    if source not in tables:
        abort(404)
    table, columns = tables[source]
    extra = " AND type='EXPENSE'" if source == 'dj_accounts' else ''
    record = query_db(
        f"SELECT {columns} FROM {table} WHERE id=? AND year_label=?{extra}",
        (expense_id, year), one=True
    )
    if not record:
        abort(404)
    return render_template('public_expense_detail.html', expense=record, selected_year=year, source=source)
