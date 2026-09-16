import sqlite3
import os
from werkzeug.security import generate_password_hash
from database import init_db, get_db_connection

def seed_database():
    init_db()
    conn = get_db_connection()
    cur = conn.cursor()

    # Clear old data safely
    tables = ['users', 'members', 'financial_years', 'vargani', 'mahaprasad_donations', 
              'mahaprasad_expenses', 'expenses', 'dj_accounts', 'pending_vargani', 'transactions', 'settings']
    for t in tables:
        cur.execute(f"DELETE FROM {t};")
        cur.execute(f"DELETE FROM sqlite_sequence WHERE name='{t}';")

    print("Seeding Users...")
    # Users
    users = [
        ('admin', generate_password_hash('admin123'), 'अध्यक्ष / ॲडमिन', 'admin'),
        ('treasurer', generate_password_hash('treasurer123'), 'रामचंद्र पाटील (खजिनदार)', 'treasurer'),
        ('member', generate_password_hash('member123'), 'गणेश गायकवाड (सदस्य)', 'member')
    ]
    cur.executemany("INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)", users)

    print("Seeding Mandal Members...")
    members = [
        ('आनंदराव देशपांडे', '9822011223', 'President', 'जागृती चौक, सांगली', '2020-01-01', 'active'),
        ('विजय शिंदे', '9822022334', 'Vice President', 'जागृती चौक, सांगली', '2020-01-01', 'active'),
        ('रामचंद्र पाटील', '9822033445', 'Treasurer', 'जागृती चौक, सांगली', '2021-06-01', 'active'),
        ('प्रकाश कदम', '9822044556', 'Secretary', 'जागृती चौक, सांगली', '2021-06-01', 'active'),
        ('गणेश गायकवाड', '9822055667', 'Member', 'जागृती चौक, सांगली', '2022-08-01', 'active'),
        ('सचिन मोरे', '9822066778', 'Volunteer', 'जागृती चौक, सांगली', '2024-08-01', 'active')
    ]
    cur.executemany("INSERT INTO members (name, mobile, role, address, join_date, status) VALUES (?, ?, ?, ?, ?, ?)", members)

    # Financial Years
    cur.execute("INSERT INTO financial_years (year_label, is_archived) VALUES ('2025', 1);")
    cur.execute("INSERT INTO financial_years (year_label, is_archived) VALUES ('2026', 0);")

    # Settings
    settings = [
        ('mandal_name_mr', 'जागृती चौक सार्वजनिक गणेश मंडळ'),
        ('mandal_name_en', 'Jagriti Chowk Sarvajanik Ganesh Mandal'),
        ('active_year', '2026'),
        ('receipt_prefix', 'JCM-2026-'),
        ('address', 'जागृती चौक, मुख्य रस्ता, सांगली - ४१६४१६'),
        ('contact_number', '+९१ ९८२२० ११२२३')
    ]
    cur.executemany("INSERT INTO settings (key, value) VALUES (?, ?)", settings)

    # =========================================================================
    # SEED 2025 ARCHIVE HISTORICAL DATA (Exact PDF Matching Numbers)
    # Total Vargani: ₹89,338
    # Total Mahaprasad Donation: ₹22,861
    # Total Mahaprasad Expense: ₹20,234
    # Total Other Expenses: ₹78,261
    # Total DJ Collection: ₹38,900
    # Total DJ Expense: ₹38,300
    # Calculated Balance: ₹14,304
    # =========================================================================
    print("Seeding 2025 Historical Archive Accounts...")

    # 1. Main Vargani 2025 Breakdown (Total ₹89,338)
    vargani_2025 = [
        ('2025', 'JCM-2025-001', 'जागृती चौक रहिवासी वर्गणी गट अ', '9900000001', 'जागृती चौक', 45000.00, 'Cash', '2025-08-25', 'रामचंद्र पाटील', 'Paid', 'मुख्य गल्ली वर्गणी एकत्र'),
        ('2025', 'JCM-2025-002', 'जागृती चौक व्यावसायिक वर्गणी गट', '9900000002', 'मुख्य बाजारपेठ', 34338.00, 'UPI', '2025-08-27', 'प्रकाश कदम', 'Paid', 'दुकानदार व व्यापारी वर्गणी'),
        ('2025', 'JCM-2025-003', 'विशेष देणगीदार वर्गणी संकलन', '9900000003', 'सांगली रस्ता', 10000.00, 'Bank', '2025-08-29', 'आनंदराव देशपांडे', 'Paid', 'हितचिंतक वर्गणी')
    ]
    cur.executemany("""INSERT INTO vargani (year_label, receipt_no, contributor_name, mobile, address, amount, payment_method, payment_date, collector_name, status, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", vargani_2025)

    # 2. Mahaprasad Donation 2025 Breakdown (Total ₹22,861)
    mp_donations_2025 = [
        ('2025', 'MPD-2025-001', 'महाप्रसाद मुख्य अन्नदाते गट', '9900000004', 15000.00, 'Cash', '2025-09-02', 'महाप्रसाद विशेष देणगी'),
        ('2025', 'MPD-2025-002', 'भाविक भक्त महाप्रसाद देणगी', '9900000005', 7861.00, 'UPI', '2025-09-03', 'पेटी व ऑनलाईन देणगी')
    ]
    cur.executemany("""INSERT INTO mahaprasad_donations (year_label, receipt_no, donor_name, mobile, amount, payment_method, payment_date, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", mp_donations_2025)

    # 3. Mahaprasad Expenses 2025 Breakdown (Total ₹20,234)
    mp_expenses_2025 = [
        ('2025', 'तांदूळ, डाळ व किराणा साहित्य', 'कृष्णा किराणा स्टोअर्स', 12450.00, 'Cash', '2025-09-02', 'BILL-MP-01', 'अन्नधान्य खरेदी'),
        ('2025', 'भाजीपाला व मसाले', 'जय भवानी व्हेजीटेबल्स', 5784.00, 'Cash', '2025-09-03', 'BILL-MP-02', 'ताजी भाजी व मसाले'),
        ('2025', 'डिस्पोजल पत्रावळी व वाटप खर्च', 'शिंदे ट्रेडर्स', 2000.00, 'UPI', '2025-09-03', 'BILL-MP-03', 'पत्रावळी व ग्लास')
    ]
    cur.executemany("""INSERT INTO mahaprasad_expenses (year_label, item_name, vendor, amount, payment_method, expense_date, bill_no, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", mp_expenses_2025)

    # 4. Other Expenses 2025 Breakdown (Total ₹78,261)
    other_expenses_2025 = [
        ('2025', 'Idol', 'गणपती मूर्ती व पूजन', 'मूर्तिकार कला केंद्र', 25000.00, 'Bank', '2025-08-20', 'BILL-EX-01', 'मुख्य गणपती मूर्ती'),
        ('2025', 'Decoration', 'लाइटिंग व मंडप डेकोरेशन', 'ओम डेकोरेटर्स', 28500.00, 'Bank', '2025-08-28', 'BILL-EX-02', 'स्टेज व मंडप भाडे'),
        ('2025', 'Pujan', 'पूजा साहित्य, हार व फुले', 'लक्ष्मी फ्लॉवर्स', 8400.00, 'Cash', '2025-08-30', 'BILL-EX-03', 'रोजचे हार व पूजा'),
        ('2025', 'Generator', 'जनरेटर व गॅस सिलेंडर भाडे', 'पावर जनरेटर सर्व्हिसेस', 7361.00, 'UPI', '2025-09-04', 'BILL-EX-04', 'इंधन व जनरेटर'),
        ('2025', 'Permission', 'परवानगी, पावती पुस्तक व फ्लेक्स', 'डिजिटल प्रिंटर्स', 9000.00, 'Cash', '2025-08-22', 'BILL-EX-05', 'परवानग्या व छपाई')
    ]
    cur.executemany("""INSERT INTO expenses (year_label, category, description, vendor, amount, payment_method, expense_date, bill_no, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", other_expenses_2025)

    # 5. DJ / Procession Collection 2025 (Total ₹38,900)
    dj_income_2025 = [
        ('2025', 'INCOME', 'DJ-2025-001', 'मिरवणूक विशेष वर्गणी गट १', 'विसर्जन मिरवणूक वर्गणी संकलन', 25000.00, 'Cash', '2025-09-05', 'तरुण मंडळ वर्गणी'),
        ('2025', 'INCOME', 'DJ-2025-002', 'मिरवणूक विशेष वर्गणी गट २', 'आगमन व विसर्जन वर्गणी', 13900.00, 'UPI', '2025-09-05', 'युवा ग्रुप वर्गणी')
    ]
    cur.executemany("""INSERT INTO dj_accounts (year_label, type, receipt_or_bill_no, person_or_vendor, description, amount, payment_method, date, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", dj_income_2025)

    # 6. DJ / Procession Expenses 2025 (Total ₹38,300)
    dj_expenses_2025 = [
        ('2025', 'EXPENSE', 'DJ-BILL-01', 'रॉयल साऊंड्स & DJ', 'विसर्जन मिरवणूक DJ भाडे', 28000.00, 'Bank', '2025-09-06', 'साऊंड सिस्टम भाडे'),
        ('2025', 'EXPENSE', 'DJ-BILL-02', 'महाराष्ट्र ढोल ताशा पथक', 'ढोल ताशा व गुलाल', 7500.00, 'Cash', '2025-09-06', 'पथक मानधन'),
        ('2025', 'EXPENSE', 'DJ-BILL-03', 'ट्रॅक्टर व डिझेल खर्च', 'स्वराज ट्रॅक्टर सर्व्हिस', 2800.00, 'Cash', '2025-09-06', 'मिरवणूक ट्रॅक्टर')
    ]
    cur.executemany("""INSERT INTO dj_accounts (year_label, type, receipt_or_bill_no, person_or_vendor, description, amount, payment_method, date, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", dj_expenses_2025)

    # Add corresponding 2025 Transaction entries for complete audit log consistency
    tx_2025 = [
        ('2025', 'TX-2025-001', '2025-08-25', 'INCOME', 'VARGANI', 'वर्गणी', 'जागृती चौक रहिवासी वर्गणी गट अ', 45000.00, 0.00, 'Cash', 'JCM-2025-001', 'admin'),
        ('2025', 'TX-2025-002', '2025-08-27', 'INCOME', 'VARGANI', 'वर्गणी', 'जागृती चौक व्यावसायिक वर्गणी गट', 34338.00, 0.00, 'UPI', 'JCM-2025-002', 'admin'),
        ('2025', 'TX-2025-003', '2025-08-29', 'INCOME', 'VARGANI', 'वर्गणी', 'विशेष देणगीदार वर्गणी संकलन', 10000.00, 0.00, 'Bank', 'JCM-2025-003', 'admin'),
        ('2025', 'TX-2025-004', '2025-09-02', 'INCOME', 'MAHAPRASAD_DONATION', 'महाप्रसाद देणगी', 'महाप्रसाद मुख्य अन्नदाते गट', 15000.00, 0.00, 'Cash', 'MPD-2025-001', 'admin'),
        ('2025', 'TX-2025-005', '2025-09-03', 'INCOME', 'MAHAPRASAD_DONATION', 'महाप्रसाद देणगी', 'भाविक भक्त महाप्रसाद देणगी', 7861.00, 0.00, 'UPI', 'MPD-2025-002', 'admin'),
        ('2025', 'TX-2025-006', '2025-09-05', 'INCOME', 'DJ_INCOME', 'DJ वर्गणी', 'मिरवणूक विशेष वर्गणी गट १', 25000.00, 0.00, 'Cash', 'DJ-2025-001', 'admin'),
        ('2025', 'TX-2025-007', '2025-09-05', 'INCOME', 'DJ_INCOME', 'DJ वर्गणी', 'मिरवणूक विशेष वर्गणी गट २', 13900.00, 0.00, 'UPI', 'DJ-2025-002', 'admin'),
        
        ('2025', 'TX-2025-008', '2025-09-02', 'EXPENSE', 'MAHAPRASAD_EXPENSE', 'महाप्रसाद खर्च', 'तांदूळ, डाळ व किराणा साहित्य', 0.00, 12450.00, 'Cash', 'BILL-MP-01', 'treasurer'),
        ('2025', 'TX-2025-009', '2025-09-03', 'EXPENSE', 'MAHAPRASAD_EXPENSE', 'महाप्रसाद खर्च', 'भाजीपाला व मसाले', 0.00, 5784.00, 'Cash', 'BILL-MP-02', 'treasurer'),
        ('2025', 'TX-2025-010', '2025-09-03', 'EXPENSE', 'MAHAPRASAD_EXPENSE', 'महाप्रसाद खर्च', 'डिस्पोजल पत्रावळी व वाटप खर्च', 0.00, 2000.00, 'UPI', 'BILL-MP-03', 'treasurer'),
        ('2025', 'TX-2025-011', '2025-08-20', 'EXPENSE', 'OTHER_EXPENSE', 'Idol', 'गणपती मूर्ती व पूजन', 0.00, 25000.00, 'Bank', 'BILL-EX-01', 'treasurer'),
        ('2025', 'TX-2025-012', '2025-08-28', 'EXPENSE', 'OTHER_EXPENSE', 'Decoration', 'लाइटिंग व मंडप डेकोरेशन', 0.00, 28500.00, 'Bank', 'BILL-EX-02', 'treasurer'),
        ('2025', 'TX-2025-013', '2025-08-30', 'EXPENSE', 'OTHER_EXPENSE', 'Pujan', 'पूजा साहित्य, हार व फुले', 0.00, 8400.00, 'Cash', 'BILL-EX-03', 'treasurer'),
        ('2025', 'TX-2025-014', '2025-09-04', 'EXPENSE', 'OTHER_EXPENSE', 'Generator', 'जनरेटर व गॅस सिलेंडर भाडे', 0.00, 7361.00, 'UPI', 'BILL-EX-04', 'treasurer'),
        ('2025', 'TX-2025-015', '2025-08-22', 'EXPENSE', 'OTHER_EXPENSE', 'Permission', 'परवानगी, पावती पुस्तक व फ्लेक्स', 0.00, 9000.00, 'Cash', 'BILL-EX-05', 'treasurer'),
        ('2025', 'TX-2025-016', '2025-09-06', 'EXPENSE', 'DJ_EXPENSE', 'DJ खर्च', 'विसर्जन मिरवणूक DJ भाडे', 0.00, 28000.00, 'Bank', 'DJ-BILL-01', 'treasurer'),
        ('2025', 'TX-2025-017', '2025-09-06', 'EXPENSE', 'DJ_EXPENSE', 'DJ खर्च', 'ढोल ताशा व गुलाल', 0.00, 7500.00, 'Cash', 'DJ-BILL-02', 'treasurer'),
        ('2025', 'TX-2025-018', '2025-09-06', 'EXPENSE', 'DJ_EXPENSE', 'DJ खर्च', 'ट्रॅक्टर व डिझेल खर्च', 0.00, 2800.00, 'Cash', 'DJ-BILL-03', 'treasurer')
    ]
    cur.executemany("""INSERT INTO transactions (year_label, transaction_id, date, type, module, category, description, income_amount, expense_amount, payment_method, reference_no, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", tx_2025)

    # =========================================================================
    # SEED 2026 INITIAL ACTIVE RECORDS (Fresh Financial Year)
    # =========================================================================
    print("Seeding 2026 Active Financial Records...")

    vargani_2026 = [
        ('2026', 'JCM-2026-001', 'सुरेश मारुती पाटील', '9890123456', 'फ्लॅट नं १०१, जागृती चौक', 5001.00, 'UPI', '2026-09-01', 'रामचंद्र पाटील', 'Paid', 'वार्षिक वर्गणी'),
        ('2026', 'JCM-2026-002', 'महेश विठ्ठल कुलकर्णी', '9890234567', 'दुकान नं ५, मुख्य बाजार', 11000.00, 'Bank', '2026-09-02', 'प्रकाश कदम', 'Paid', 'व्यापारी देणगी वर्गणी'),
        ('2026', 'JCM-2026-003', 'दीपक रामराव चव्हाण', '9890345678', 'जागृती चौक, गल्ली ३', 2500.00, 'Cash', '2026-09-03', 'सचिन मोरे', 'Paid', 'रोख वर्गणी'),
        ('2026', 'JCM-2026-004', 'नितीन बाबुराव जगताप', '9890456789', 'जागृती चौक, सांगली', 1500.00, 'Cash', '2026-09-04', 'गणेश गायकवाड', 'Paid', 'वर्गणी')
    ]
    cur.executemany("""INSERT INTO vargani (year_label, receipt_no, contributor_name, mobile, address, amount, payment_method, payment_date, collector_name, status, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", vargani_2026)

    mp_donations_2026 = [
        ('2026', 'MPD-2026-001', 'हभप तुकाराम महाराज ट्रस्ट', '9822998877', 10000.00, 'Bank', '2026-09-03', 'महाप्रसाद अन्नदान देणगी')
    ]
    cur.executemany("""INSERT INTO mahaprasad_donations (year_label, receipt_no, donor_name, mobile, amount, payment_method, payment_date, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", mp_donations_2026)

    mp_expenses_2026 = [
        ('2026', 'बासमती तांदूळ ५० किलो', 'कृष्णा किराणा भांडार', 4500.00, 'Cash', '2026-09-04', 'BILL-2026-MP01', 'महाप्रसाद तांदूळ')
    ]
    cur.executemany("""INSERT INTO mahaprasad_expenses (year_label, item_name, vendor, amount, payment_method, expense_date, bill_no, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", mp_expenses_2026)

    expenses_2026 = [
        ('2026', 'Idol', 'श्रींची मूर्ती आगाऊ अनामत रक्कम', 'मूर्तिकार केंद्र', 5000.00, 'Bank', '2026-08-25', 'ADV-01', 'अगाऊ रक्कम'),
        ('2026', 'Permission', 'ध्वनिप्रक्षेपकाची महापालिका व पोलीस परवानगी', 'तहसीलदार कार्यालय', 1200.00, 'Cash', '2026-08-28', 'PERM-99', 'सरकारी फी')
    ]
    cur.executemany("""INSERT INTO expenses (year_label, category, description, vendor, amount, payment_method, expense_date, bill_no, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", expenses_2026)

    dj_2026 = [
        ('2026', 'INCOME', 'DJ-2026-001', 'युवा गणेश मंडळ ग्रुप', 'DJ व मिरवणूक वर्गणी जमा', 5000.00, 'Cash', '2026-09-02', 'युवा वर्गणी')
    ]
    cur.executemany("""INSERT INTO dj_accounts (year_label, type, receipt_or_bill_no, person_or_vendor, description, amount, payment_method, date, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", dj_2026)

    pending_2026 = [
        ('2026', 'संजय पांडुरंग जाधवर', '9890554433', 5000.00, 2000.00, 3000.00, '2026-09-15', 'Partial', 'पहिली हप्ता भरला, बाकी थकीत'),
        ('2026', 'अमोल संभाजी भोसले', '9890665544', 2500.00, 0.00, 2500.00, '2026-09-18', 'Pending', 'संपर्क साधला आहे')
    ]
    cur.executemany("""INSERT INTO pending_vargani (year_label, person_name, mobile, expected_amount, paid_amount, remaining_amount, due_date, status, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", pending_2026)

    tx_2026 = [
        ('2026', 'TX-2026-001', '2026-09-01', 'INCOME', 'VARGANI', 'वर्गणी', 'सुरेश मारुती पाटील वर्गणी जमा', 5001.00, 0.00, 'UPI', 'JCM-2026-001', 'admin'),
        ('2026', 'TX-2026-002', '2026-09-02', 'INCOME', 'VARGANI', 'वर्गणी', 'महेश विठ्ठल कुलकर्णी वर्गणी जमा', 11000.00, 0.00, 'Bank', 'JCM-2026-002', 'admin'),
        ('2026', 'TX-2026-003', '2026-09-03', 'INCOME', 'VARGANI', 'वर्गणी', 'दीपक रामराव चव्हाण वर्गणी जमा', 2500.00, 0.00, 'Cash', 'JCM-2026-003', 'admin'),
        ('2026', 'TX-2026-004', '2026-09-04', 'INCOME', 'VARGANI', 'वर्गणी', 'नितीन बाबुराव जगताप वर्गणी जमा', 1500.00, 0.00, 'Cash', 'JCM-2026-004', 'admin'),
        ('2026', 'TX-2026-005', '2026-09-03', 'INCOME', 'MAHAPRASAD_DONATION', 'महाप्रसाद देणगी', 'हभप तुकाराम महाराज ट्रस्ट देणगी', 10000.00, 0.00, 'Bank', 'MPD-2026-001', 'treasurer'),
        ('2026', 'TX-2026-006', '2026-09-02', 'INCOME', 'DJ_INCOME', 'DJ वर्गणी', 'युवा गणेश मंडळ ग्रुप DJ वर्गणी', 5000.00, 0.00, 'Cash', 'DJ-2026-001', 'treasurer'),
        ('2026', 'TX-2026-007', '2026-09-04', 'EXPENSE', 'MAHAPRASAD_EXPENSE', 'महाप्रसाद खर्च', 'बासमती तांदूळ ५० किलो', 0.00, 4500.00, 'Cash', 'BILL-2026-MP01', 'treasurer'),
        ('2026', 'TX-2026-008', '2026-08-25', 'EXPENSE', 'OTHER_EXPENSE', 'Idol', 'श्रींची मूर्ती आगाऊ अनामत रक्कम', 0.00, 5000.00, 'Bank', 'ADV-01', 'treasurer'),
        ('2026', 'TX-2026-009', '2026-08-28', 'EXPENSE', 'OTHER_EXPENSE', 'Permission', 'ध्वनिप्रक्षेपकाची महापालिका व पोलीस परवानगी', 0.00, 1200.00, 'Cash', 'PERM-99', 'treasurer')
    ]
    cur.executemany("""INSERT INTO transactions (year_label, transaction_id, date, type, module, category, description, income_amount, expense_amount, payment_method, reference_no, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", tx_2026)

    conn.commit()
    conn.close()
    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
