import os

class Config:

    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY não está definida nas variáveis de ambiente")

    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DB_URL não está definida nas variáveis de ambiente")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = 'static/uploads'

    SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL', 'contato@exemplo.com')
    SUPPORT_PHONE = os.getenv('SUPPORT_PHONE', '+5500000000000')