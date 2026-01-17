from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user

def superuser_required(f):
    """
    Flask equivalent of Django's @permission_required('SUPERUSER')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You must be logged in to access this page. ', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_superuser:
            flash('You do not have permission to access this page.', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def permission_required(permission):
    """
    Generic permission decorator. 
    Usage: @permission_required('can_edit_menus')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user. is_authenticated:
                flash('You must be logged in. ', 'warning')
                return redirect(url_for('auth. login'))
            
            if not current_user.has_permission(permission):
                flash('You do not have the required permission.', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def user_in_group(group_name):
    """
    Check if user is in a specific group. 
    Usage: @user_in_group('admin')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('You must be logged in.', 'warning')
                return redirect(url_for('auth.login'))
            
            if not current_user.is_in_group(group_name):
                flash(f'You must be in the {group_name} group. ', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator