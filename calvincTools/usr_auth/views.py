from datetime import datetime
from functools import wraps

from flask import (
    render_template, redirect, url_for, flash, 
    request, session, 
    )
from flask.views import MethodView
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy

# db and models imported in each method so that the initalized versions are used

# Assuming you have db instance from Flask-SQLAlchemy
# from your_app import db

# ============================================================================
# FLASK-LOGIN SETUP
# ============================================================================

def init_login_manager(app):
    """Initialize Flask-Login with the Flask app."""
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # type: ignore # Redirect to login page if not authenticated
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from ..models import User
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
        if current_user.is_authenticated:
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
    from ..models import User, db
    
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
        assert isinstance(remember, bool), "Remember must be a boolean value"
        login_user(user, remember=remember)
        user.update_last_login()
        
        flash(f'Welcome back, {user.username}!', 'success')
        
        # set initial menugroup
        session['menu_group'] = user.menuGroup if user.menuGroup else 1
        
        # Redirect to next page or home
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('index'))
    
    # GET request
    return render_template('auth/login.html')

# flask-login example login view
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     # Here we use a class of some kind to represent and validate our
#     # client-side form data. For example, WTForms is a library that will
#     # handle this for us, and we use a custom LoginForm to validate.
#     form = LoginForm()
#     if form.validate_on_submit():
#         # Login and validate the user.
#         # user should be an instance of your `User` class
#         login_user(user)

#         flask.flash('Logged in successfully.')

#         next = flask.request.args.get('next')
#         # url_has_allowed_host_and_scheme should check if the url is safe
#         # for redirects, meaning it matches the request host.
#         # See Django's url_has_allowed_host_and_scheme for an example.
#         if not url_has_allowed_host_and_scheme(next, request.host):
#             return flask.abort(400)

#         return flask.redirect(next or flask.url_for('index'))
#     return flask.render_template('login.html', form=form)
# from Django http.py
import unicodedata
from urllib.parse import (
    ParseResult, SplitResult, 
    _coerce_args, _splitnetloc, _splitparams, # type: ignore
    scheme_chars, urlencode as original_urlencode, uses_params,
)
def url_has_allowed_host_and_scheme(url, allowed_hosts, require_https=False):
    """
    Return ``True`` if the url uses an allowed host and a safe scheme.

    Always return ``False`` on an empty url.

    If ``require_https`` is ``True``, only 'https' will be considered a valid
    scheme, as opposed to 'http' and 'https' with the default, ``False``.

    Note: "True" doesn't entail that a URL is "safe". It may still be e.g.
    quoted incorrectly. Ensure to also use django.utils.encoding.iri_to_uri()
    on the path component of untrusted URLs.
    """
    if url is not None:
        url = url.strip()
    if not url:
        return False
    if allowed_hosts is None:
        allowed_hosts = set()
    elif isinstance(allowed_hosts, str):
        allowed_hosts = {allowed_hosts}
    # Chrome treats \ completely as / in paths but it could be part of some
    # basic auth credentials so we need to check both URLs.
    return (
        _url_has_allowed_host_and_scheme(url, allowed_hosts, require_https=require_https) and
        _url_has_allowed_host_and_scheme(url.replace('\\', '/'), allowed_hosts, require_https=require_https)
    )


# Copied from urllib.parse.urlparse() but uses fixed urlsplit() function.
def _urlparse(url, scheme='', allow_fragments=True):
    """Parse a URL into 6 components:
    <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
    Return a 6-tuple: (scheme, netloc, path, params, query, fragment).
    Note that we don't break the components up in smaller bits
    (e.g. netloc is a single string) and we don't expand % escapes."""
    url, scheme, _coerce_result = _coerce_args(url, scheme)
    splitresult = _urlsplit(url, scheme, allow_fragments)
    scheme, netloc, url, query, fragment = splitresult
    if scheme in uses_params and ';' in url:
        url, params = _splitparams(url)
    else:
        params = ''
    result = ParseResult(scheme, netloc, url, params, query, fragment)
    return _coerce_result(result)


# Copied from urllib.parse.urlsplit() with
# https://github.com/python/cpython/pull/661 applied.
def _urlsplit(url, scheme='', allow_fragments=True):
    """Parse a URL into 5 components:
    <scheme>://<netloc>/<path>?<query>#<fragment>
    Return a 5-tuple: (scheme, netloc, path, query, fragment).
    Note that we don't break the components up in smaller bits
    (e.g. netloc is a single string) and we don't expand % escapes."""
    url, scheme, _coerce_result = _coerce_args(url, scheme)
    netloc = query = fragment = ''
    i = url.find(':')
    if i > 0:
        for c in url[:i]:
            if c not in scheme_chars:
                break
        else:
            scheme, url = url[:i].lower(), url[i + 1:]

    if url[:2] == '//':
        netloc, url = _splitnetloc(url, 2)
        if (('[' in netloc and ']' not in netloc) or
                (']' in netloc and '[' not in netloc)):
            raise ValueError("Invalid IPv6 URL")
    if allow_fragments and '#' in url:
        url, fragment = url.split('#', 1)
    if '?' in url:
        url, query = url.split('?', 1)
    v = SplitResult(scheme, netloc, url, query, fragment)
    return _coerce_result(v)


def _url_has_allowed_host_and_scheme(url, allowed_hosts, require_https=False):
    # Chrome considers any URL with more than two slashes to be absolute, but
    # urlparse is not so flexible. Treat any url with three slashes as unsafe.
    if url.startswith('///'):
        return False
    try:
        url_info = _urlparse(url)
    except ValueError:  # e.g. invalid IPv6 addresses
        return False
    # Forbid URLs like http:///example.com - with a scheme, but without a hostname.
    # In that URL, example.com is not the hostname but, a path component. However,
    # Chrome will still consider example.com to be the hostname, so we must not
    # allow this syntax.
    if not url_info.netloc and url_info.scheme:
        return False
    # Forbid URLs that start with control characters. Some browsers (like
    # Chrome) ignore quite a few control characters at the start of a
    # URL and might consider the URL as scheme relative.
    if unicodedata.category(url[0])[0] == 'C':
        return False
    scheme = url_info.scheme
    # Consider URLs without a scheme (e.g. //example.com/p) to be http.
    if not url_info.scheme and url_info.netloc:
        scheme = 'http'
    valid_schemes = ['https'] if require_https else ['http', 'https']
    return ((not url_info.netloc or url_info.netloc in allowed_hosts) and
            (not scheme or scheme in valid_schemes))



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
    from ..models import db
    
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
    from ..models import User, db
    
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST': 
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        # confirm_password = request.form.get('confirm_password', '')
        confirm_password = password
        
        # Validate inputs
        if not username or not email or not password or not confirm_password:
            flash('All fields are required.', 'danger')
            return render_template('auth/signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/signup.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('auth/signup.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. ', 'danger')
            return render_template('auth/signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/signup.html')
        
        # Create new user
        new_user = User(username=username, email=email)      # type: ignore
        new_user.menuGroup = 1  # default menu group
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful!  Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    # GET request
    return render_template('auth/signup.html')


@superuser_required
def user_list_view():
    """
    Handle user list management (GET and POST).
    Displays all existing users plus blank forms for new user entries.
    
    GET: Display all users + blank forms
    POST: Save/update all users
    """
    from ..models import User, db
    from .forms import UserListForm
    
    blank_user_count = request.args.get('blank_user_count', 5, type=int)
    
    if request.method == 'GET':
        # Get all existing users
        existing_users = User.query.all()
        
        # Create form with existing users
        form = UserListForm()
        
        # Clear default entry so we can control the list explicitly
        while len(form.users) > 0:
            form.users.pop_entry()
        
        # Populate form with existing users
        for user in existing_users:
            form.users.append_entry(user)
        
        # Add blank users for new entries
        for _ in range(blank_user_count):
            blank_user = User()  # type: ignore
            form.users.append_entry(blank_user)
        
        return render_template(
            'auth/user_list.html',
            form=form,
            blank_user_count=blank_user_count
        )
    
    elif request.method == 'POST':
        form = UserListForm()
        
        if form.validate_on_submit():
            try:
                # Get all user IDs from the request to identify which ones are new/existing
                user_ids_in_form = []
                for i, user_data in enumerate(form.users.data):
                    if hasattr(user_data, 'id') and user_data.id:
                        user_ids_in_form.append(user_data.id)
                
                # Process each user in the form
                for i, user_form in enumerate(form.users.entries):
                    username = user_form.username.data.strip() if user_form.username.data else ''
                    email = user_form.email.data.strip() if user_form.email.data else ''
                    
                    # Skip blank entries (no username and no email)
                    if not username and not email:
                        continue
                    
                    # Check if this is an existing user or new user
                    user = None
                    if hasattr(user_form, 'obj') and user_form.obj and hasattr(user_form.obj, 'id'):
                        user = User.query.get(user_form.obj.id)
                    
                    if user:
                        # Update existing user
                        user.username = username
                        user.email = email      # pyright: ignore[reportAttributeAccessIssue]
                        user.FLDis_active = user_form.FLDis_active.data     # pyright: ignore[reportAttributeAccessIssue]
                        user.is_superuser = user_form.is_superuser.data     # pyright: ignore[reportAttributeAccessIssue]
                        user.permissions = user_form.permissions.data or ''     # pyright: ignore[reportAttributeAccessIssue]
                        
                        # Only update password if provided
                        if user_form.password.data:
                            user.set_password(user_form.password.data)      # pyright: ignore[reportAttributeAccessIssue]
                    else:
                        # Create new user
                        user = User(  # type: ignore
                            username=username,
                            email=email,
                            FLDis_active=user_form.FLDis_active.data,
                            is_superuser=user_form.is_superuser.data,
                            permissions=user_form.permissions.data or '',
                            menuGroup=1  # default menu group
                        )
                        
                        # Set password if provided
                        if user_form.password.data:
                            user.set_password(user_form.password.data)
                        else:
                            # Generate a temporary password for new users
                            user.set_password('TempPassword123!')
                    
                    db.session.add(user)
                
                db.session.commit()
                flash('All users saved successfully!', 'success')
                return redirect(url_for('auth.user_list'))
            
            except Exception as e:
                db.session.rollback()
                flash(f'Error saving users: {str(e)}', 'danger')
                return redirect(url_for('auth.user_list'))
        else:
            flash('Form validation failed. Please check your entries.', 'danger')
            return render_template(
                'auth/user_list.html',
                form=form,
                blank_user_count=blank_user_count
            )


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
    auth_bp.add_url_rule('/users', 'user_list', user_list_view, methods=['GET', 'POST']) # type: ignore
    
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
        from ..models import User, db
        username = request.form.get('susername', '').strip()
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
        
        assert isinstance(remember, bool), "Remember must be a boolean value"
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