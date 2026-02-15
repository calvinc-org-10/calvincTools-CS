"""
calvincTools - A Python package
"""
# Import main modules here as needed
# from .module import function

from flask import Flask, render_template, redirect, url_for, session
from flask_migrate import Migrate
from .blueprints import ctools_bp
# from calvincTools.config import cTools_config
from .usr_auth.views import init_login_manager, register_auth_blueprint
from .cMenu.views import menu_bp
from .views.util_views import util_bp

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
        app.register_blueprint(menu_bp)
        app.register_blueprint(util_bp)
        
        # Home route
        # Note: We define this route here to ensure it exists, but the caller can override it by defining their own route for '/'
        # in fact, need to make it easier for caller to override this route, since it's likely they will want to customize the home page
        @app.route('/index')    # leave route('/') for caller to set
        def index():
            mnugrp = session.get('menu_group', 1)
            return redirect(url_for('menu.load_menu', menu_group=mnugrp, menu_num=0))
        
        # Error handlers
        @app.errorhandler(404)
        def not_found(error):   # pylint: disable=unused-argument
            return render_template('errors/404.html'), 404
        
        @app.errorhandler(403)
        def forbidden(error):   # pylint: disable=unused-argument
            return render_template('errors/403.html'), 403
        
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

