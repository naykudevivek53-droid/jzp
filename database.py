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
from datetime import date

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

def ensure_schema_compatibility():
    """Apply additive migrations needed by running installations."""
    conn = get_db_connection()
    cur = conn.cursor()
    use_mysql = is_mysql_configured()

    if use_mysql:
        cur.execute("""CREATE TABLE IF NOT EXISTS receipts (
            id INT AUTO_INCREMENT PRIMARY KEY, year_label VARCHAR(10) NOT NULL,
            receipt_no VARCHAR(100) NOT NULL UNIQUE, source_type VARCHAR(40) NOT NULL,
            source_id INT NOT NULL, donor_name VARCHAR(150) NOT NULL, mobile VARCHAR(20),
            address TEXT, amount DECIMAL(12,2) NOT NULL DEFAULT 0, payment_method VARCHAR(50),
            payment_date DATE NOT NULL, details TEXT, created_by VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uq_receipt_source (year_label, source_type, source_id),
            INDEX idx_receipts_year_date (year_label, payment_date)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
        cur.execute("SHOW COLUMNS FROM mahaprasad_donations LIKE 'donation_type'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE mahaprasad_donations ADD COLUMN donation_type VARCHAR(20) NOT NULL DEFAULT 'Money'")
        cur.execute("SHOW COLUMNS FROM mahaprasad_donations LIKE 'item_details'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE mahaprasad_donations ADD COLUMN item_details TEXT")
        cur.execute("SHOW COLUMNS FROM mahaprasad_donations LIKE 'address'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE mahaprasad_donations ADD COLUMN address TEXT")
        cur.execute("SHOW COLUMNS FROM mahaprasad_donations LIKE 'purpose'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE mahaprasad_donations ADD COLUMN purpose VARCHAR(255)")
        cur.execute("INSERT IGNORE INTO financial_years (year_label, is_archived) VALUES ('2026', 0)")
        cur.execute("INSERT IGNORE INTO settings (`key`, value, description) VALUES ('active_year', '2026', 'Currently selected financial year')")
        cur.execute("DELETE FROM users WHERE role IN ('treasurer', 'member')")
        cur.execute("DELETE FROM members WHERE role IN ('Treasurer', 'Member')")
        conn.close()
        return

    cur.execute("PRAGMA table_info(mahaprasad_donations)")
    columns = {row[1] for row in cur.fetchall()}
    if 'donation_type' not in columns:
        cur.execute("ALTER TABLE mahaprasad_donations ADD COLUMN donation_type TEXT NOT NULL DEFAULT 'Money'")
    if 'item_details' not in columns:
        cur.execute("ALTER TABLE mahaprasad_donations ADD COLUMN item_details TEXT")
    if 'address' not in columns:
        cur.execute("ALTER TABLE mahaprasad_donations ADD COLUMN address TEXT")
    if 'purpose' not in columns:
        cur.execute("ALTER TABLE mahaprasad_donations ADD COLUMN purpose TEXT")
    cur.execute("""CREATE TABLE IF NOT EXISTS receipts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, year_label TEXT NOT NULL,
        receipt_no TEXT NOT NULL UNIQUE, source_type TEXT NOT NULL, source_id INTEGER NOT NULL,
        donor_name TEXT NOT NULL, mobile TEXT, address TEXT, amount DECIMAL(12,2) NOT NULL DEFAULT 0,
        payment_method TEXT, payment_date DATE NOT NULL, details TEXT, created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, UNIQUE(year_label, source_type, source_id))""")
    cur.execute("INSERT OR IGNORE INTO financial_years (year_label, is_archived) VALUES ('2026', 0)")
    cur.execute("INSERT OR IGNORE INTO settings (key, value, description) VALUES ('active_year', '2026', 'Currently selected financial year')")
    cur.execute("DELETE FROM users WHERE role IN ('treasurer', 'member')")
    cur.execute("DELETE FROM members WHERE role IN ('Treasurer', 'Member')")
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

def get_active_financial_year():
    """Return the configured financial year, falling back safely to the newest year."""
    try:
        configured = query_db("SELECT value FROM settings WHERE key='active_year'", one=True)
        if configured and configured.get('value'):
            year = str(configured['value']).strip()
            if query_db("SELECT id FROM financial_years WHERE year_label=? AND is_archived=0", (year,), one=True):
                return year
        current = query_db(
            "SELECT year_label FROM financial_years WHERE is_archived=0 "
            "ORDER BY year_label DESC, id DESC", one=True)
        if current:
            return str(current['year_label'])
    except Exception:
        pass
    return str(date.today().year)

def set_active_financial_year(year_label):
    """Select an existing, non-archived financial year without changing its data."""
    year_label = str(year_label).strip()
    if not year_label.isdigit() or len(year_label) != 4:
        raise ValueError("Financial year must be a four digit year")
    if not query_db("SELECT id FROM financial_years WHERE year_label=? AND is_archived=0", (year_label,), one=True):
        raise ValueError("Financial year does not exist or is archived")
    execute_db("INSERT OR REPLACE INTO settings (key, value, description) VALUES (?, ?, ?)",
               ('active_year', year_label, 'Currently selected financial year'))
    return year_label

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
