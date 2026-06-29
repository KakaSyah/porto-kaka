import os
from dotenv import load_dotenv

load_dotenv()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _get_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')


def _get_int(name, default):
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


class Config:
    # Gunakan DB_DRIVER=mysql untuk TiDB/MySQL.
    DB_DRIVER = os.getenv('DB_DRIVER', 'mysql').lower()

    DB_HOST = os.getenv('DB_HOST', '')
    DB_PORT = _get_int('DB_PORT', 4000)
    DB_USER = os.getenv('DB_USER') or os.getenv('DB_USERNAME', '')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME') or os.getenv('DB_DATABASE', '')
    DB_CA_PATH = os.getenv('DB_CA_PATH') or os.getenv('CA_PATH', '')

    MYSQL_CONFIG = {
        'host': DB_HOST,
        'port': DB_PORT,
        'user': DB_USER,
        'password': DB_PASSWORD,
        'database': DB_NAME,
        'ssl_ca': DB_CA_PATH or None
    }

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = _get_bool('FLASK_DEBUG', True)
    SEED_DEMO_DATA = _get_bool('SEED_DEMO_DATA', False)

    PORTFOLIO_USER_ID = _get_int('PORTFOLIO_USER_ID', 0)
    PORTFOLIO_USERNAME = os.getenv('PORTFOLIO_USERNAME', '').strip()

    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', '')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', '')

    RESEND_API_KEY = os.getenv('RESEND_API_KEY', '')
    RESEND_FROM_EMAIL = os.getenv('RESEND_FROM_EMAIL', 'noreply@example.com')
    CONTACT_RECIPIENT_EMAIL = os.getenv('CONTACT_RECIPIENT_EMAIL', os.getenv('PORTFOLIO_CONTACT_EMAIL', 'admin@example.com'))
