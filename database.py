import sqlite3
import os
from decimal import Decimal
from config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Ensure upload directories exist
    os.makedirs(Config.BILL_UPLOADS, exist_ok=True)
    os.makedirs(Config.RECEIPT_UPLOADS, exist_ok=True)
    
    conn = get_db_connection()
    with open(os.path.join(os.path.dirname(__file__), 'schema.sql'), 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    if one:
        return dict(rv[0]) if rv else None
    return [dict(row) for row in rv]

def execute_db(query, args=()):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id

def log_audit(user_id, username, action, record_type, record_id=None, old_val=None, new_val=None):
    try:
        execute_db(
            """INSERT INTO audit_logs (user_id, username, action, record_type, record_id, old_value, new_value)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, username, action, record_type, str(record_id) if record_id else None, str(old_val) if old_val else None, str(new_val) if new_val else None)
        )
    except Exception as e:
        print(f"Audit log error: {e}")
