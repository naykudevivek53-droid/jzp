-- Schema for Jagriti Chowk Sarvajanik Ganesh Mandal Accounting & Management Web App

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'admin', -- admin
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    mobile TEXT,
    role TEXT NOT NULL, -- President, Vice President, Secretary, Volunteer
    address TEXT,
    join_date DATE,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS financial_years (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year_label TEXT UNIQUE NOT NULL, -- '2025', '2026'
    is_archived INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vargani (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year_label TEXT NOT NULL DEFAULT '2026',
    receipt_no TEXT NOT NULL,
    contributor_name TEXT NOT NULL,
    mobile TEXT,
    address TEXT,
    amount DECIMAL(12,2) NOT NULL,
    payment_method TEXT NOT NULL, -- Cash, UPI, Bank
    payment_date DATE NOT NULL,
    collector_name TEXT,
    status TEXT NOT NULL DEFAULT 'Paid', -- Paid, Partial, Pending
    notes TEXT,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mahaprasad_donations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year_label TEXT NOT NULL DEFAULT '2026',
    receipt_no TEXT NOT NULL,
    donor_name TEXT NOT NULL,
    mobile TEXT,
    address TEXT,
    purpose TEXT,
    donation_type TEXT NOT NULL DEFAULT 'Money',
    item_details TEXT,
    amount DECIMAL(12,2) NOT NULL,
    payment_method TEXT NOT NULL,
    payment_date DATE NOT NULL,
    notes TEXT,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mahaprasad_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year_label TEXT NOT NULL DEFAULT '2026',
    item_name TEXT NOT NULL,
    vendor TEXT,
    amount DECIMAL(12,2) NOT NULL,
    payment_method TEXT NOT NULL,
    expense_date DATE NOT NULL,
    bill_no TEXT,
    bill_file TEXT,
    notes TEXT,
    approved_by TEXT,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year_label TEXT NOT NULL DEFAULT '2026',
    category TEXT NOT NULL, -- DJ, Tractor Rent, Band, Dhoti, Room Rent, Ganpati Pata, Utensils, Haar, Gas, Generator, Idol, Pujan, Receipt Book, Permission, Decoration, Transport, Repair, Food, Other
    description TEXT NOT NULL,
    vendor TEXT,
    amount DECIMAL(12,2) NOT NULL,
    payment_method TEXT NOT NULL,
    expense_date DATE NOT NULL,
    bill_no TEXT,
    bill_file TEXT,
    approved_by TEXT,
    notes TEXT,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dj_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year_label TEXT NOT NULL DEFAULT '2026',
    type TEXT NOT NULL, -- INCOME, EXPENSE
    receipt_or_bill_no TEXT,
    person_or_vendor TEXT NOT NULL,
    description TEXT,
    amount DECIMAL(12,2) NOT NULL,
    payment_method TEXT NOT NULL,
    date DATE NOT NULL,
    notes TEXT,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pending_vargani (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year_label TEXT NOT NULL DEFAULT '2026',
    person_name TEXT NOT NULL,
    mobile TEXT,
    expected_amount DECIMAL(12,2) NOT NULL,
    paid_amount DECIMAL(12,2) DEFAULT 0.00,
    remaining_amount DECIMAL(12,2) NOT NULL,
    due_date DATE,
    status TEXT NOT NULL DEFAULT 'Pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year_label TEXT NOT NULL DEFAULT '2026',
    transaction_id TEXT UNIQUE NOT NULL,
    date DATE NOT NULL,
    type TEXT NOT NULL, -- INCOME, EXPENSE
    module TEXT NOT NULL, -- VARGANI, MAHAPRASAD_DONATION, MAHAPRASAD_EXPENSE, OTHER_EXPENSE, DJ_INCOME, DJ_EXPENSE
    category TEXT NOT NULL,
    description TEXT,
    income_amount DECIMAL(12,2) DEFAULT 0.00,
    expense_amount DECIMAL(12,2) DEFAULT 0.00,
    payment_method TEXT NOT NULL,
    reference_no TEXT,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT NOT NULL,
    action TEXT NOT NULL, -- CREATE, UPDATE, DELETE, LOGIN
    record_type TEXT NOT NULL,
    record_id TEXT,
    old_value TEXT,
    new_value TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS receipts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year_label TEXT NOT NULL,
    receipt_no TEXT NOT NULL UNIQUE,
    source_type TEXT NOT NULL,
    source_id INTEGER NOT NULL,
    donor_name TEXT NOT NULL,
    mobile TEXT,
    address TEXT,
    amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    payment_method TEXT,
    payment_date DATE NOT NULL,
    details TEXT,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year_label, source_type, source_id)
);
