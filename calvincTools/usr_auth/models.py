import datetime

from flask import render_template, redirect, url_for, flash, request, session
from flask.views import MethodView
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy

from ..database import db
# Assuming you have db instance from Flask-SQLAlchemy

from ..models import MenuGroup

# from your_app import db


# ============================================================================
# USER MODEL
# ============================================================================

class User(UserMixin, db.Model):
    """
    User model for authentication. 
    Inherit from UserMixin to get default implementations for: 
    - is_authenticated
    - is_active
    - is_anonymous
    - get_id()
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False) # type: ignore
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)
    permissions = db.Column(db.String(1024), nullable=False)
    menugroup = db.relationship('MenuGroup', backref='users', lazy='joined')
    date_joined = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.datetime.now()
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'

