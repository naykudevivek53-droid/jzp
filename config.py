import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'jagriti-chowk-ganesh-mandal-2026-secret-key-key'
    DATABASE_PATH = os.path.join(BASE_DIR, 'ganesh_mandal_2026.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    BILL_UPLOADS = os.path.join(UPLOAD_FOLDER, 'bills')
    RECEIPT_UPLOADS = os.path.join(UPLOAD_FOLDER, 'receipts')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    
    # Mandal Default Info
    MANDAL_NAME_MR = "जागृती चौक सार्वजनिक गणेश मंडळ"
    MANDAL_NAME_EN = "Jagriti Chowk Sarvajanik Ganesh Mandal"
    FESTIVAL_TITLE_MR = "गणेशोत्सव २०२६ हिशोब व व्यवस्थापन प्रणाली"
    FESTIVAL_TITLE_EN = "Ganeshotsav 2026 Accounting & Management System"
