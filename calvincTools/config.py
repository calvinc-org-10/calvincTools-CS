import os

class CToolsDefaults:
    CTOOLS_API_KEY = "defaultT-keyK"
    CTOOLS_ENABLE_LOGGING = True



class cToolsConfig: 
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-WTF
    WTF_CSRF_ENABLED = True
    
    # Session
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour


class cToolsDevelopmentConfig(cToolsConfig):
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
    #     f'sqlite:///{cToolsConfig.cMenu_dbPath}'
    #     # 'sqlite:///dev_database.db'
    SQLALCHEMY_ECHO = True


class cToolsProductionConfig(cToolsConfig):
    DEBUG = False
    # SQLALCHEMY_DATABASE_URI = os. environ.get('DATABASE_URL') or \
    #     f'sqlite:///{cToolsConfig.cMenu_dbPath}'
    #     # 'sqlite:///prod_database.db'
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True  # HTTPS only


class cToolsTestingConfig(cToolsConfig):
    TESTING = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

from flask import Flask
def cTools_config(app:Flask):
    """Apply default configuration to the Flask app."""
    for key, value in CToolsDefaults.__dict__.items():
        if not key.startswith('__'):
            app.config.setdefault(key, value)
    
    
    root_path = "."
    # root_path = os.path.abspath(os.path.dirname(__file__))
    cMenu_dbPath = f"{root_path}\\cMenudb.sqlite"
    
    # isolate calvincTools db
    app.config.setdefault('SQLALCHEMY_BINDS', {})
    app.config['SQLALCHEMY_BINDS']['cToolsdb'] = f'sqlite:///{cMenu_dbPath}'    
