from calvincTools.usr_auth.views import (
    change_password_view, login_view, logout_view, register_view, user_list_view, 
    )


# ============================================================================
# BLUEPRINT REGISTRATION
# ============================================================================

# register_auth_blueprint(app) should be called in your app factory function after initializing the app and db.

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