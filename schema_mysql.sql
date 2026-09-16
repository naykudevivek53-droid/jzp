-- MySQL Production Schema for Jagriti Chowk Sarvajanik Ganesh Mandal Accounting & Management Web App
-- Character Set: utf8mb4, Collation: utf8mb4_unicode_ci

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'member', -- admin, treasurer, member
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    mobile VARCHAR(20),
    role VARCHAR(100) NOT NULL, -- President, Vice President, Treasurer, Secretary, Member, Volunteer
    address TEXT,
    join_date DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS financial_years (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year_label VARCHAR(10) UNIQUE NOT NULL, -- '2025', '2026'
    is_archived TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS vargani (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year_label VARCHAR(10) NOT NULL DEFAULT '2026',
    receipt_no VARCHAR(100) NOT NULL,
    contributor_name VARCHAR(150) NOT NULL,
    mobile VARCHAR(20),
    address TEXT,
    amount DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL, -- Cash, UPI, Bank
    payment_date DATE NOT NULL,
    collector_name VARCHAR(150),
    status VARCHAR(50) NOT NULL DEFAULT 'Paid', -- Paid, Partial, Pending
    notes TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_vargani_year (year_label),
    INDEX idx_vargani_receipt (receipt_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS mahaprasad_donations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year_label VARCHAR(10) NOT NULL DEFAULT '2026',
    receipt_no VARCHAR(100) NOT NULL,
    donor_name VARCHAR(150) NOT NULL,
    mobile VARCHAR(20),
    amount DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_date DATE NOT NULL,
    notes TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_mp_don_year (year_label)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS mahaprasad_expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year_label VARCHAR(10) NOT NULL DEFAULT '2026',
    item_name VARCHAR(255) NOT NULL,
    vendor VARCHAR(150),
    amount DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    expense_date DATE NOT NULL,
    bill_no VARCHAR(100),
    bill_file VARCHAR(255),
    notes TEXT,
    approved_by VARCHAR(100),
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_mp_exp_year (year_label)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year_label VARCHAR(10) NOT NULL DEFAULT '2026',
    category VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    vendor VARCHAR(150),
    amount DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    expense_date DATE NOT NULL,
    bill_no VARCHAR(100),
    bill_file VARCHAR(255),
    approved_by VARCHAR(100),
    notes TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_exp_year (year_label),
    INDEX idx_exp_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dj_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year_label VARCHAR(10) NOT NULL DEFAULT '2026',
    type VARCHAR(20) NOT NULL, -- INCOME, EXPENSE
    receipt_or_bill_no VARCHAR(100),
    person_or_vendor VARCHAR(150) NOT NULL,
    description TEXT,
    amount DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    notes TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_dj_year_type (year_label, type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS pending_vargani (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year_label VARCHAR(10) NOT NULL DEFAULT '2026',
    person_name VARCHAR(150) NOT NULL,
    mobile VARCHAR(20),
    expected_amount DECIMAL(12,2) NOT NULL,
    paid_amount DECIMAL(12,2) DEFAULT 0.00,
    remaining_amount DECIMAL(12,2) NOT NULL,
    due_date DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_pending_year (year_label)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year_label VARCHAR(10) NOT NULL DEFAULT '2026',
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    date DATE NOT NULL,
    type VARCHAR(20) NOT NULL, -- INCOME, EXPENSE
    module VARCHAR(50) NOT NULL, -- VARGANI, MAHAPRASAD_DONATION, MAHAPRASAD_EXPENSE, OTHER_EXPENSE, DJ_INCOME, DJ_EXPENSE
    category VARCHAR(100) NOT NULL,
    description TEXT,
    income_amount DECIMAL(12,2) DEFAULT 0.00,
    expense_amount DECIMAL(12,2) DEFAULT 0.00,
    payment_method VARCHAR(50) NOT NULL,
    reference_no VARCHAR(100),
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tx_year_date (year_label, date),
    INDEX idx_tx_method (payment_method)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    username VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL, -- CREATE, UPDATE, DELETE, LOGIN, LOGOUT
    record_type VARCHAR(100) NOT NULL,
    record_id VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS settings (
    `key` VARCHAR(100) PRIMARY KEY,
    `value` TEXT NOT NULL,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
