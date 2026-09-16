import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'jagriti-chowk-ganesh-mandal-2026-secret-key-key'
    
    # Environment
    ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')

    # Database Configuration
    # Supported: MySQL / PostgreSQL / SQLite
    DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('MYSQL_URL')
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = int(os.environ.get('DB_PORT', 3306)) if os.environ.get('DB_PORT') else 3306
    DB_NAME = os.environ.get('DB_NAME')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    
    # Local fallback SQLite database path
    # In production, point this at a persistent disk/volume. Never leave the
    # SQLite file inside an ephemeral deployment checkout.
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or os.path.join(BASE_DIR, 'ganesh_mandal_2026.db')

    # Uploads Configuration
    # In cloud environments with persistent volume mount, set UPLOAD_FOLDER (e.g. /app/uploads or /data/uploads)
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(BASE_DIR, 'uploads')
    BILL_UPLOADS = os.path.join(UPLOAD_FOLDER, 'bills')
    RECEIPT_UPLOADS = os.path.join(UPLOAD_FOLDER, 'receipts')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    
    # Mandal Default Information
    MANDAL_NAME_MR = os.environ.get('MANDAL_NAME_MR', "जागृती चौक गणेशोत्सव मंडळ")
    MANDAL_NAME_EN = os.environ.get('MANDAL_NAME_EN', "Jagriti Chowk Ganeshotsav Mandal")
    FESTIVAL_TITLE_MR = os.environ.get('FESTIVAL_TITLE_MR', "गणेशोत्सव २०२६ हिशोब व व्यवस्थापन प्रणाली")
    FESTIVAL_TITLE_EN = os.environ.get('FESTIVAL_TITLE_EN', "Ganeshotsav 2026 Accounting & Management System")
