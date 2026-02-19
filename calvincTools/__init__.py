"""
calvincTools - A Python package
"""
# Import main modules here as needed
# from .module import function

from flask import Flask, render_template, redirect, url_for, session
from flask_migrate import Migrate

from .usr_auth.views import init_login_manager
from .blueprints import ctools_bp
from .usr_auth.routes import register_auth_blueprint
from .cMenu.routes import register_menu_blueprint
from .utils.routes import register_util_blueprint

class calvinCTools_init:
    def __init__(self, app=None, app_db=None):
        if app is not None:
            self.init_app(app, app_db)

    def init_app(self, app, app_db):
        # 1. configs should be already set by the user
        #    later, we will be procs to add/modify configs
        #    db configs MUST be set before app_db.init_app, but app_db.init_app MUST precede init_cDatabase here

        # 2. Register Blueprints
        # This keeps cTools routes separate from the app routes
        app.register_blueprint(
            ctools_bp, 
            url_prefix='/ctools',
            )

        # Initialize extensions
        from .models import init_cDatabase      # can I move this back to main imports?
        init_cDatabase(app, app_db)
        # migrate = Migrate(app, cMenu_db)
        init_login_manager(app)
        
        # Create default Calvin user if not exists
        # R E M O V E   I N   P R O D U C T I O N   ! ! !
        # create_calvin(app)
        
        # Register blueprints
        register_auth_blueprint(app)
        register_menu_blueprint(app)
        register_util_blueprint(app)
        
        # Error handlers
        @app.errorhandler(404)
        def not_found(error):   # pylint: disable=unused-argument
            return render_template('errors/404.html'), 404
        
        @app.errorhandler(403)
        def forbidden(error):   # pylint: disable=unused-argument
            return render_template('errors/403.html', error=error), 403
        
        @app.errorhandler(500)
        def internal_error(error):   # pylint: disable=unused-argument
            from .models import db
            if db is not None:
                db.session.rollback()
            return render_template('errors/500.html'), 500

        # 3. Attach cTools to the app extensions (optional but recommended)
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['ctools'] = self
    # init_app
    
# calvinCTools

