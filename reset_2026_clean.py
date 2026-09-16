import sqlite3
from database import get_db_connection

def reset_2026_clean():
    conn = get_db_connection()
    cur = conn.cursor()

    tables = ['vargani', 'mahaprasad_donations', 'mahaprasad_expenses', 
              'expenses', 'dj_accounts', 'pending_vargani', 'transactions']
    
    for t in tables:
        cur.execute(f"DELETE FROM {t} WHERE year_label='2026'")

    conn.commit()
    conn.close()
    print("2026 Financial Year has been reset to clean slate (₹0 Income, ₹0 Expense). 2025 Archive data remains untouched!")

if __name__ == '__main__':
    reset_2026_clean()
