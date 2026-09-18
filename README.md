# जागृती चौक सार्वजनिक गणेश मंडळ — गणेशोत्सव २०२६ हिशोब व्यवस्थापन प्रणाली
## Jagriti Chowk Sarvajanik Ganesh Mandal Accounting & Management Web Application
### 🚀 Production Deployment Guide

A modern, production-ready Ganesh Mandal Accounting & Management application built specifically for local mandals. Formulated upon the real 2025 financial accounts of Jagriti Chowk Ganesh Mandal and engineered to manage 2026 festival collections, donations, expenses, daily accounts, and final balance sheets digitally.

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
   - Includes `python tests/test_2025_archive.py` and live `/api/validate-2025` endpoint to verify exact mathematical accuracy down to the rupee.
3. **2026 Fresh Active Accounts**: Completely isolated 2026 financial year for live festival accounting.
4. **Production Ready & Cloud MySQL Compatible**: Supports remote cloud MySQL (Railway, Render, Aiven, PlanetScale, AWS RDS) or zero-configuration SQLite.
5. **Vargani Management (वर्गणी व्यवस्थापन)**: Searchable contributor table, payment status filters, auto-generated receipt numbers, and printable official receipts with Marathi & English currency word conversions.
6. **Mahaprasad Ledger (महाप्रसाद हिशोब)**: Dedicated ledgers for Mahaprasad donations and Mahaprasad food/groceries/disposal expenses.
7. **Other Expenses (इतर खर्च)**: Categorized expense recording (Idol, Decoration, DJ, Band, Generator, Permissions, Gas, etc.) with bill upload support (`.jpg`, `.png`, `.pdf`).
8. **DJ & Procession Ledger (DJ / मिरवणूक हिशोब)**: Isolated ledger for arrival & immersion procession collection and DJ/band expenses.
9. **Daily Accounts (दैनिक हिशोब)**: Auto-calculated daily opening balance, today's collection, today's expenses, closing balance, and mode-wise (Cash, UPI, Bank) cashbox ledgers.
10. **Automated Final Hishob (अंतिम हिशोब)**: Real-time balance sheet (`Total Income - Total Expenses = Final Balance`). Never hardcoded.
11. **Reports & Exports**: Complete financial summary, category breakdowns, payment method statistics, and Excel (`.xlsx`) export.
12. **Public Transparency Page**: Public board showing aggregate summary numbers and names of contributing persons safely without exposing private phone numbers or addresses.
13. **Audit Trail & Database Backup**: Logs all creations, modifications, and deletions. Allows full database backup export.
14. **Year-wise accounting**: Admins can create and select a new active financial year from Settings. Previous years remain read-only in their own records and are never deleted when switching years.

---

## ☁️ Production Deployment Instructions

You can host this application on any cloud platform such as **Render**, **Railway**, **PythonAnywhere**, **AWS**, or **Heroku** without keeping your local computer running.

### Step 1: Upload Project to GitHub
1. In your project directory, initialize git:
   ```bash
   git init
   git add .
   git commit -m "Production release for Jagriti Chowk Ganesh Mandal 2026"
   ```
2. Create a new repository on [GitHub](https://github.com/new) (e.g. `ganesh-mandal-2026`).
3. Push your code:
   ```bash
   git remote add origin https://github.com/<YOUR-USERNAME>/ganesh-mandal-2026.git
   git branch -M main
   git push -u origin main
   ```

---

### Step 2: Set Up Online Cloud MySQL Database
You can use a managed cloud MySQL database (e.g., from [Railway](https://railway.app), [Aiven](https://aiven.io), [Render](https://render.com), or [PlanetScale]):
1. Create a MySQL database instance.
2. Note down the credentials:
   - `DATABASE_URL` (e.g., `mysql://user:password@host:3306/dbname`) OR
   - `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
3. Use the same managed database and database name on every redeploy. The application only attempts initialization when the database has no `users` table; it does not reseed an existing database. For an intentional first production initialization only, set `ALLOW_DESTRUCTIVE_SEED=true`, deploy once, then remove it or set it to `false`.
   *(Alternatively, you can manually import `schema_mysql.sql` using phpMyAdmin, MySQL Workbench, or the CLI).*

---

### Step 3: Deploy the Flask Application (e.g. on Render / Railway)

#### On Render.com:
1. Click **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Configuration:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --workers=4 --bind 0.0.0.0:$PORT "app:create_app()"`
4. Add **Environment Variables** (under Environment tab):
   - `SECRET_KEY`: *(Generate a secure random string)*
   - `DATABASE_URL`: `mysql://username:password@hostname:3306/dbname`
   - `FLASK_ENV`: `production`
   - `FLASK_DEBUG`: `False`
   - *(Optional persistent disk mount for uploads)*: `UPLOAD_FOLDER`: `/var/data/uploads`
   - Keep `DATABASE_URL` connected to the same managed MySQL database on every deploy.
5. Click **Deploy Web Service**.

#### On Railway.app:
1. Click **New Project** -> **Deploy from GitHub repo**.
2. Add a **MySQL** service from Railway template.
3. Connect `DATABASE_URL` variable between the MySQL service and the web service.
4. Railway automatically detects `Procfile` and launches the Gunicorn server.

---

### Step 4: First Admin Login & Verification
Once deployed, open your live public URL (e.g. `https://ganesh-mandal-2026.onrender.com`):

| Role | Username | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Admin (अध्यक्ष)** | `admin` | `admin123` | Full control (Collections, Expenses, Members, Settings, Delete) |
| **Treasurer (खजिनदार)** | `treasurer` | `treasurer123` | Manage Collections, Donations, Expenses, Daily Accounts, Reports |
| **Member (सदस्य)** | `member` | `member123` | View-only access to Dashboard, Reports, Hishob |

> 🔒 **Security Recommendation**: After your first login, visit **Settings** to update admin credentials or change default passwords.

---

### Step 5: Public Access URLs

- **Main Dashboard & Management**: `https://<YOUR-LIVE-DOMAIN>`
- **Public Transparency Board (No password needed for public/devotees)**:
  `https://<YOUR-LIVE-DOMAIN>/public-transparency`

---

## 🔐 Redeploy and data safety

Redeploying the application code does not delete records when the application keeps using the same database:

- **Recommended production setup:** use managed MySQL and keep the same `DATABASE_URL`. Database records remain outside the web-service container.
- **Production SQLite:** attach a persistent volume and set `DATABASE_PATH` to a file on that volume, such as `/var/data/ganesh_mandal_2026.db`. Do not store the database inside the deployed repository or temporary container filesystem.
- Download the admin database backup from **Settings → Database Backup** before deployments, migrations, or provider changes.
- Keep `SECRET_KEY` unchanged across redeployments so existing login sessions and signed values remain valid.
- Keep `UPLOAD_FOLDER` on persistent storage as well if uploaded bills or receipt files must survive redeploys.

The startup path refuses to seed an existing empty SQLite file, and production seeding is disabled unless `ALLOW_DESTRUCTIVE_SEED=true` is explicitly set. These safeguards prevent an accidental redeploy from overwriting a restored or partially mounted database. Never run `seed_2025_archive.py` against an existing production database; it is a destructive initializer.

If a provider recreates its storage without a persistent volume or managed database, no application code can recover the lost local SQLite file. Restore the latest backup or reconnect the original persistent database before starting the new deployment. The application now refuses to start instead of creating a new empty production database, so a missing Render database configuration is visible immediately rather than appearing to delete records.

## 🗄️ File Uploads & Cloud Storage Note

In production PaaS environments (like Render or Heroku), the local file system is ephemeral (files uploaded during a container session may not persist across restarts).
- **Recommended for Permanent Bill Storage**:
  - Attach a **Persistent Disk Volume** (e.g., Render Disks or Railway Volumes mounted to `/app/uploads`) and set the `UPLOAD_FOLDER=/app/uploads` environment variable.
  - Or connect an S3-compatible cloud bucket (AWS S3, Cloudflare R2) if scaling beyond a single server.

---

## 💻 Local Development / Fallback Run

If running locally on your computer:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Seed database
python seed_2025_archive.py

# 3. Start development server
python app.py
```
Access via `http://localhost:5000` or `http://<YOUR_LOCAL_IP>:5000`.

---

## 📁 Project Structure

```
ganesh_mandal_2026/
├── app.py                      # Production WSGI application factory & entry point
├── config.py                   # Environment configuration loader
├── database.py                 # Remote MySQL + SQLite hybrid database adapter
├── schema.sql                  # SQLite relational schema
├── schema_mysql.sql            # Production MySQL relational schema (InnoDB, utf8mb4)
├── seed_2025_archive.py        # Database seeder (2025 PDF reference + 2026 setup)
├── reset_2026_clean.py         # 2026 reset utility (keeps 2025 historical archive)
├── requirements.txt            # Production dependencies (Gunicorn, PyMySQL, Flask, etc.)
├── Procfile                    # WSGI start command for cloud hosts
├── .env.example                # Sample environment variables for production
├── README.md                   # Production deployment documentation
├── routes/                     # Modular route blueprints
│   ├── auth.py                 # Authentication & language switcher
│   ├── dashboard.py            # Dashboard metrics & Chart.js endpoints
│   ├── vargani.py              # Vargani collection & receipt generator
│   ├── mahaprasad.py           # Mahaprasad donation & expense ledgers
│   ├── expenses.py             # Categorized expenses & bill upload handlers
│   ├── dj_procession.py        # DJ & procession income/expense ledger
│   ├── daily_accounts.py       # Daily cash/UPI/bank ledger
│   ├── transactions.py         # Complete transaction history ledger
│   ├── members.py              # Committee directory
│   ├── pending.py              # Pending collection tracker
│   ├── reports.py              # Reports & Excel export engine
│   ├── archive_2025.py         # 2025 Archive report & verification endpoint
│   ├── public.py               # Public transparency board
│   ├── settings.py             # Admin settings & database backup
│   └── audit.py                # Audit trail logger
├── templates/                  # Responsive Jinja2 bilingual HTML templates
├── static/                     # CSS styling & interactive Chart.js scripts
└── tests/
    └── test_2025_archive.py    # Automated test suite for 2025 PDF figures
```
