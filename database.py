import os
import re
import urllib.parse
from decimal import Decimal
from config import Config

# Optional PyMySQL support for remote/cloud MySQL
try:
    import pymysql
    import pymysql.cursors
    HAS_PYMYSQL = True
except ImportError:
    HAS_PYMYSQL = False

import sqlite3

def is_mysql_configured():
    if Config.DATABASE_URL:
        db_url = Config.DATABASE_URL.lower()
        if db_url.startswith('mysql') or 'mysql' in db_url:
            return True
    if Config.DB_HOST and Config.DB_NAME and Config.DB_USER:
        return True
    return False

def parse_mysql_params():
    if Config.DATABASE_URL:
        # e.g., mysql://user:password@host:port/dbname
        parsed = urllib.parse.urlparse(Config.DATABASE_URL)
        dbname = parsed.path.lstrip('/')
        # Handle parameters in query string
        if '?' in dbname:
            dbname = dbname.split('?')[0]
        return {
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or 3306,
            'user': parsed.username or 'root',
            'password': parsed.password or '',
            'database': dbname,
            'charset': 'utf8mb4'
        }
    return {
        'host': Config.DB_HOST or 'localhost',
        'port': Config.DB_PORT or 3306,
        'user': Config.DB_USER or 'root',
        'password': Config.DB_PASSWORD or '',
        'database': Config.DB_NAME,
        'charset': 'utf8mb4'
    }

def get_db_connection():
    if is_mysql_configured():
        if not HAS_PYMYSQL:
            raise ImportError("PyMySQL is not installed. Please add pymysql or cryptography to your requirements.")
        params = parse_mysql_params()
        conn = pymysql.connect(
            host=params['host'],
            port=params['port'],
            user=params['user'],
            password=params['password'],
            database=params['database'],
            charset=params['charset'],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return conn
    else:
        # Fallback to local SQLite connection
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def convert_query_to_mysql(query):
    """
    Translates standard ? parameter placeholders to %s for MySQL/PyMySQL,
    and handles SQLite-specific expressions like INSERT OR REPLACE.
    """
    # Replace ? with %s
    converted = query.replace('?', '%s')
    # Handle SQLite specific INSERT OR REPLACE to MySQL standard
    if 'INSERT OR REPLACE INTO' in converted:
        converted = converted.replace('INSERT OR REPLACE INTO', 'REPLACE INTO')
    return converted

def init_db():
    # Ensure upload directories exist
    os.makedirs(Config.BILL_UPLOADS, exist_ok=True)
    os.makedirs(Config.RECEIPT_UPLOADS, exist_ok=True)
    
    conn = get_db_connection()
    use_mysql = is_mysql_configured()

    schema_file = 'schema_mysql.sql' if use_mysql else 'schema.sql'
    schema_path = os.path.join(os.path.dirname(__file__), schema_file)
    if not os.path.exists(schema_path):
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

    with open(schema_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    if use_mysql:
        # For MySQL, execute statements individually
        cur = conn.cursor()
        # Filter out comments and split by semicolon
        statements = re.split(r';\s*\n', sql_content)
        for stmt in statements:
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--'):
                cur.execute(stmt)
        conn.close()
    else:
        conn.executescript(sql_content)
        conn.commit()
        conn.close()

def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cur = conn.cursor()
    use_mysql = is_mysql_configured()

    if use_mysql:
        exec_query = convert_query_to_mysql(query)
        cur.execute(exec_query, args)
        rv = cur.fetchall()
        conn.close()
        # PyMySQL DictCursor returns dict rows directly
        if one:
            return rv[0] if rv else None
        return list(rv)
    else:
        cur.execute(query, args)
        rv = cur.fetchall()
        conn.close()
        if one:
            return dict(rv[0]) if rv else None
        return [dict(row) for row in rv]

def execute_db(query, args=()):
    conn = get_db_connection()
    cur = conn.cursor()
    use_mysql = is_mysql_configured()

    if use_mysql:
        exec_query = convert_query_to_mysql(query)
        cur.execute(exec_query, args)
        last_id = cur.lastrowid
        conn.close()
        return last_id
    else:
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
