from datetime import datetime
from functools import wraps

from flask import render_template, redirect, url_for, flash, request, session
from flask.views import MethodView
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy

from ..models import db
# Assuming you have db instance from Flask-SQLAlchemy
# from your_app import db

# ============================================================================
# FLASK-LOGIN SETUP
# ============================================================================

def init_login_manager(app):
    """Initialize Flask-Login with the Flask app."""
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirect to login page if not authenticated
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login."""
        return User.query.get(int(user_id))
    
    return login_manager


# ============================================================================
# CUSTOM DECORATORS
# ============================================================================

def login_required_custom(f):
    """
    Custom decorator to restrict views to authenticated users only.
    This is in addition to Flask-Login's @login_required decorator.
    Use this if you want custom behavior. 
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You must be logged in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def superuser_required(f):
    """
    Decorator to restrict views to superusers only.
    Similar to Django's @permission_required decorator.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated: 
            flash('You must be logged in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.is_superuser:
            flash('You do not have permission to access this page. ', 'danger')
            return redirect(url_for('index'))  # or return a 403 page
        
        return f(*args, **kwargs)
    return decorated_function


def active_user_required(f):
    """
    Decorator to ensure the user account is active.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You must be logged in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.is_active:
            logout_user()
            flash('Your account has been deactivated.  Please contact support.', 'danger')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function


def anonymous_required(f):
    """
    Decorator to restrict views to non-authenticated users only.
    Useful for login/register pages.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user. is_authenticated:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def login_view():
    """
    Handle user login (GET and POST).
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST': 
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not username or not password:
            flash('Please provide both username and password.', 'danger')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid username or password.', 'danger')
            return render_template('auth/login.html')
        
        if not user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'danger')
            return render_template('auth/login.html')
        
        # Log the user in
        login_user(user, remember=remember)
        user.update_last_login()
        
        flash(f'Welcome back, {user.username}!', 'success')
        
        # Redirect to next page or home
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('index'))
    
    # GET request
    return render_template('auth/login.html')


def logout_view():
    """
    Handle user logout.
    """
    if current_user.is_authenticated:
        username = current_user.username
        logout_user()
        flash(f'You have been logged out.  Goodbye, {username}!', 'info')
    
    return redirect(url_for('auth.login'))


def change_password_view():
    """
    Handle password change for authenticated users.
    """
    if not current_user.is_authenticated:
        flash('You must be logged in to change your password.', 'warning')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate inputs
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required.', 'danger')
            return render_template('auth/change_password.html')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return render_template('auth/change_password.html')
        
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long. ', 'danger')
            return render_template('auth/change_password.html')
        
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Your password has been changed successfully.', 'success')
        return redirect(url_for('index'))
    
    # GET request
    return render_template('auth/change_password.html')


def register_view():
    """
    Handle user registration (optional - if you want self-registration).
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST': 
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate inputs
        if not username or not email or not password or not confirm_password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('auth/register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. ', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')
        
        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful!  Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    # GET request
    return render_template('auth/register.html')


# ============================================================================
# BLUEPRINT REGISTRATION
# ============================================================================

def register_auth_blueprint(app):
    """
    Register authentication routes with the Flask app.
    """
    from flask import Blueprint
    
    auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
    
    auth_bp.add_url_rule('/login', 'login', login_view, methods=['GET', 'POST'])
    auth_bp.add_url_rule('/logout', 'logout', logout_view, methods=['GET', 'POST'])
    auth_bp.add_url_rule('/change-password', 'change_password', change_password_view, methods=['GET', 'POST'])
    auth_bp.add_url_rule('/register', 'register', register_view, methods=['GET', 'POST'])
    
    app.register_blueprint(auth_bp)


# ============================================================================
# ALTERNATIVE:  CLASS-BASED VIEWS
# ============================================================================

class LoginView(MethodView):
    """Class-based login view."""
    
    decorators = [anonymous_required]
    
    def get(self):
        return render_template('auth/login.html')
    
    def post(self):
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not username or not password:
            flash('Please provide both username and password.', 'danger')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid username or password.', 'danger')
            return render_template('auth/login.html')
        
        if not user.is_active:
            flash('Your account has been deactivated.', 'danger')
            return render_template('auth/login.html')
        
        login_user(user, remember=remember)
        user.update_last_login()
        
        flash(f'Welcome back, {user.username}!', 'success')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('index'))


class LogoutView(MethodView):
    """Class-based logout view."""
    
    def get(self):
        if current_user.is_authenticated:
            logout_user()
            flash('You have been logged out. ', 'info')
        return redirect(url_for('auth.login'))