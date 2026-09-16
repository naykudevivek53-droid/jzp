import sys
import os
import unittest

# Add parent directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import query_db
from seed_2025_archive import seed_database

class Test2025Archive(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        seed_database()

    def test_2025_main_vargani_total(self):
        res = query_db("SELECT SUM(amount) as total FROM vargani WHERE year_label='2025'", one=True)
        total = float(res['total'] or 0)
        self.assertEqual(total, 89338.00, f"Main Vargani mismatch: expected 89338, got {total}")

    def test_2025_mahaprasad_donation_total(self):
        res = query_db("SELECT SUM(amount) as total FROM mahaprasad_donations WHERE year_label='2025'", one=True)
        total = float(res['total'] or 0)
        self.assertEqual(total, 22861.00, f"Mahaprasad Donation mismatch: expected 22861, got {total}")

    def test_2025_mahaprasad_expense_total(self):
        res = query_db("SELECT SUM(amount) as total FROM mahaprasad_expenses WHERE year_label='2025'", one=True)
        total = float(res['total'] or 0)
        self.assertEqual(total, 20234.00, f"Mahaprasad Expense mismatch: expected 20234, got {total}")

    def test_2025_other_expense_total(self):
        res = query_db("SELECT SUM(amount) as total FROM expenses WHERE year_label='2025'", one=True)
        total = float(res['total'] or 0)
        self.assertEqual(total, 78261.00, f"Other Expense mismatch: expected 78261, got {total}")

    def test_2025_dj_collection_total(self):
        res = query_db("SELECT SUM(amount) as total FROM dj_accounts WHERE year_label='2025' AND type='INCOME'", one=True)
        total = float(res['total'] or 0)
        self.assertEqual(total, 38900.00, f"DJ Collection mismatch: expected 38900, got {total}")

    def test_2025_dj_expense_total(self):
        res = query_db("SELECT SUM(amount) as total FROM dj_accounts WHERE year_label='2025' AND type='EXPENSE'", one=True)
        total = float(res['total'] or 0)
        self.assertEqual(total, 38300.00, f"DJ Expense mismatch: expected 38300, got {total}")

    def test_2025_final_balance(self):
        vargani = float(query_db("SELECT SUM(amount) as total FROM vargani WHERE year_label='2025'", one=True)['total'] or 0)
        mp_donation = float(query_db("SELECT SUM(amount) as total FROM mahaprasad_donations WHERE year_label='2025'", one=True)['total'] or 0)
        dj_income = float(query_db("SELECT SUM(amount) as total FROM dj_accounts WHERE year_label='2025' AND type='INCOME'", one=True)['total'] or 0)
        
        mp_expense = float(query_db("SELECT SUM(amount) as total FROM mahaprasad_expenses WHERE year_label='2025'", one=True)['total'] or 0)
        other_expense = float(query_db("SELECT SUM(amount) as total FROM expenses WHERE year_label='2025'", one=True)['total'] or 0)
        dj_expense = float(query_db("SELECT SUM(amount) as total FROM dj_accounts WHERE year_label='2025' AND type='EXPENSE'", one=True)['total'] or 0)

        total_income = vargani + mp_donation + dj_income
        total_expense = mp_expense + other_expense + dj_expense
        final_balance = total_income - total_expense

        self.assertEqual(total_income, 151099.00, f"Total Income mismatch: got {total_income}")
        self.assertEqual(total_expense, 136795.00, f"Total Expense mismatch: got {total_expense}")
        self.assertEqual(final_balance, 14304.00, f"Final Balance mismatch: expected 14304, got {final_balance}")

if __name__ == '__main__':
    unittest.main()
