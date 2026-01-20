import os

class Config: 
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-WTF
    WTF_CSRF_ENABLED = True
    
    # Session
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

    # calvincTools specific
    root_path = "."
    # root_path = os.path.abspath(os.path.dirname(__file__))
    cMenu_dbPath = f"{root_path}\\cMenudb.sqlite"

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        f'sqlite:///{Config.cMenu_dbPath}'
        # 'sqlite:///dev_database.db'
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os. environ.get('DATABASE_URL') or \
        f'sqlite:///{Config.cMenu_dbPath}'
        # 'sqlite:///prod_database.db'
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True  # HTTPS only


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}