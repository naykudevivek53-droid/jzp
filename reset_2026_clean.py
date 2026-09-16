import os
from database import get_db_connection, is_mysql_configured

def reset_2026_clean():
    if os.environ.get('RESET_CONFIRM') != 'RESET_ALL_DATA':
        raise RuntimeError(
            'Refusing destructive reset. Set RESET_CONFIRM=RESET_ALL_DATA '
            'to delete financial and test data while preserving users/settings.'
        )

    conn = get_db_connection()
    cur = conn.cursor()
    use_mysql = is_mysql_configured()

    tables = [
        'receipts', 'vargani', 'mahaprasad_donations', 'mahaprasad_expenses',
        'expenses', 'dj_accounts', 'pending_vargani', 'transactions'
    ]
    for t in tables:
        cur.execute(f"DELETE FROM {t} WHERE year_label='2026'")

    if use_mysql:
        cur.execute("DELETE FROM financial_years WHERE year_label='2026'")
        cur.execute("INSERT IGNORE INTO financial_years (year_label, is_archived) VALUES ('2026', 0)")
        cur.execute("UPDATE settings SET value='2026' WHERE `key`='active_year'")
    else:
        cur.execute("DELETE FROM financial_years WHERE year_label='2026'")
        cur.execute("INSERT OR IGNORE INTO financial_years (year_label, is_archived) VALUES ('2026', 0)")
        cur.execute("INSERT OR REPLACE INTO settings (`key`, value, description) VALUES ('active_year', '2026', 'Currently selected financial year')")
        conn.commit()
    conn.close()
    print("2026 financial/test data was deleted. All 2025 data, admin users, settings, and schema were preserved.")

if __name__ == '__main__':
    reset_2026_clean()
