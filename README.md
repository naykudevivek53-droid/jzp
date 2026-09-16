# जागृती चौक सार्वजनिक गणेश मंडळ — गणेशोत्सव २०२६ हिशोब व्यवस्थापन प्रणाली
## Jagriti Chowk Sarvajanik Ganesh Mandal Accounting & Management Web Application

A complete, modern, production-ready Ganesh Mandal Accounting & Management application built specifically for local mandals. Formulated upon the real 2025 financial accounts of Jagriti Chowk Ganesh Mandal and engineered to manage 2026 festival collections, donations, expenses, daily accounts, and final balance sheets digitally.

---

## 🌟 Key Features

1. **Bilingual UI (मराठी & English)**: Complete Marathi language support using *Noto Sans Devanagari* font with instant English toggle.
2. **2025 PDF Historical Archive & Automated Validation Suite**:
   - Seeded with exact historical totals from the supplied 2025 PDF reference:
     - Main Vargani Total: **₹89,338**
     - Mahaprasad Donation Total: **₹22,861**
     - Mahaprasad Expense Total: **₹20,234**
     - Other Expense Total: **₹78,261**
     - DJ/Procession Collection Total: **₹38,900**
     - DJ Expense Total: **₹38,300**
     - Calculated Final Remaining Balance: **₹14,304**
   - Includes `pytest tests/test_2025_archive.py` and live `/api/validate-2025` endpoint to verify exact mathematical accuracy down to the rupee.
3. **2026 Fresh Active Accounts**: Completely isolated 2026 financial year for live festival accounting.
4. **Vargani Management (वर्गणी व्यवस्थापन)**: Searchable contributor table, payment status filters, auto-generated receipt numbers, and printable official receipts with Marathi & English currency word conversions.
5. **Mahaprasad Ledger (महाप्रसाद हिशोब)**: Dedicated ledgers for Mahaprasad donations and Mahaprasad food/groceries/disposal expenses.
6. **Other Expenses (इतर खर्च)**: Categorized expense recording (Idol, Decoration, DJ, Band, Generator, Permissions, Gas, etc.) with bill upload support (`.jpg`, `.png`, `.pdf`).
7. **DJ & Procession Ledger (DJ / मिरवणूक हिशोब)**: Isolated ledger for arrival & immersion procession collection and DJ/band expenses.
8. **Daily Accounts (दैनिक हिशोब)**: Auto-calculated daily opening balance, today's collection, today's expenses, closing balance, and mode-wise (Cash, UPI, Bank) cashbox ledgers.
9. **Automated Final Hishob (अंतिम हिशोब)**: Real-time balance sheet (`Total Income - Total Expenses = Final Balance`). Never hardcoded.
10. **Reports & Exports**: Complete financial summary, category breakdowns, payment method statistics, and Excel (`.xlsx`) export.
11. **Public Transparency Page**: Public board showing aggregate summary numbers without exposing private phone numbers or addresses.
12. **Audit Trail & Database Backup**: Logs all creations, modifications, and deletions. Allows full database backup export.

---

## 🚀 Installation & Quick Start

### 1. Requirements
- Python 3.9+
- `pip` (Python Package Manager)

### 2. Install Dependencies
```bash
cd C:\Users\nayku\.gemini\antigravity\scratch\ganesh_mandal_2026
pip install -r requirements.txt
```

### 3. Seed Database & Run 2025 Validation Tests
```bash
# Seed initial database with users, 2025 archive data, and sample 2026 entries
python seed_2025_archive.py

# Run automated 2025 verification tests
pytest tests/test_2025_archive.py
```

### 4. Start Flask Server
```bash
python app.py
```
Open your web browser and navigate to: **`http://127.0.0.1:5000`**

---

## 🔑 Demo Accounts

| Role | Username | Password | Access Rights |
| :--- | :--- | :--- | :--- |
| **Admin (अध्यक्ष)** | `admin` | `admin123` | Full access (Vargani, Expenses, Members, Settings, Audit Log, Deletions) |
| **Treasurer (खजिनदार)** | `treasurer` | `treasurer123` | Add/Manage Collections, Donations, Expenses, Daily Accounts, Reports |
| **Member (सदस्य)** | `member` | `member123` | Read-only view of Dashboard, Vargani, Expenses, Reports |

---

## 📁 Project Structure

```
ganesh_mandal_2026/
├── app.py                      # Main Flask application entry point
├── config.py                   # App configuration & upload directories
├── database.py                 # SQLite database helper & audit logger
├── schema.sql                  # Relational database schema with DECIMAL money fields
├── seed_2025_archive.py        # Database seeder (2025 PDF totals + 2026 setup)
├── requirements.txt            # Python dependencies
├── .env.example                # Sample environment variables
├── README.md                   # Complete documentation
├── models/                     # Data calculations and helper functions
├── utils/
│   ├── translations.py         # Marathi & English bilingual translation dictionary
│   └── number_to_words.py      # Currency amount to words converter (Marathi & English)
├── routes/
│   ├── auth.py                 # Authentication, Login, Logout, Language switcher
│   ├── dashboard.py            # Financial summary cards, Chart.js metrics
│   ├── vargani.py              # Vargani collection & printable receipt engine
│   ├── mahaprasad.py           # Mahaprasad donation & expense ledgers
│   ├── expenses.py             # Categorized expense ledger & bill uploads
│   ├── dj_procession.py        # Dedicated DJ income & expense ledgers
│   ├── daily_accounts.py       # Daily cash/UPI/bank balance calculator
│   ├── transactions.py         # Complete transaction history ledger
│   ├── members.py              # Mandal member directory
│   ├── pending.py              # Pending collection tracker
│   ├── reports.py              # Reports generator & Excel export engine
│   ├── archive_2025.py         # 2025 Archive view, comparison & validation API
│   ├── public.py               # Public transparency board
│   ├── settings.py             # Admin settings & database backup exporter
│   └── audit.py                # Audit log viewer
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Responsive Bootstrap 5 layout & mobile navigation
│   ├── login.html              # Login portal
│   ├── dashboard.html          # Main financial dashboard with Chart.js canvas
│   ├── hishob_final.html       # Automated Final Hishob balance sheet
│   ├── archive_2025.html       # 2025 Archive report & live test runner UI
│   ├── comparison.html         # 2025 vs 2026 financial comparison
│   ├── public.html             # Public transparency board
│   ├── vargani/                # Collection table & receipt templates
│   ├── mahaprasad/             # Mahaprasad templates
│   ├── expenses/               # Expense templates
│   ├── dj/                     # DJ ledger templates
│   ├── daily/                  # Daily account templates
│   └── reports/                # Report templates
├── static/
│   ├── css/custom.css          # Saffron/Gold Ganesh Mandal design system
│   └── js/main.js              # Chart.js visualizers & receipt print handlers
├── tests/
│   └── test_2025_archive.py    # Automated verification tests for 2025 PDF figures
└── uploads/
    ├── bills/                  # Expense bill attachments
    └── receipts/               # Saved receipt documents
```
