from flask import Flask, render_template, redirect, url_for, session
from flask_migrate import Migrate

from .database import cTools_db  
from .models import init_cDatabase
from .usr_auth.views import init_login_manager, register_auth_blueprint
from .cMenu.views import menu_bp
from .utils import util_bp
from . import config



# def create_app(config_name='development'):
#     flskapp = Flask(__name__, static_folder='assets', template_folder='templates')
#     flskapp.config.from_object(config.cTools_config[config_name])
    
#     # Initialize extensions
#     cTools_db.init_app(flskapp)
#     init_cDatabase(flskapp)
#     # migrate = Migrate(flskapp, cMenu_db)
#     init_login_manager(flskapp)
    
#     # Register blueprints
#     register_auth_blueprint(flskapp)
#     flskapp.register_blueprint(menu_bp)
#     flskapp.register_blueprint(util_bp)
    
#     # Home route
#     @flskapp.route('/index')    # leave route('/') for caller to set
#     def index():
#         mnugrp = session.get('menu_group', 1)
#         return redirect(url_for('menu.load_menu', menu_group=mnugrp, menu_num=0))
    
#     # Error handlers
#     @flskapp.errorhandler(404)
#     def not_found(error):   # pylint: disable=unused-argument
#         return render_template('errors/404.html'), 404
    
#     @flskapp.errorhandler(403)
#     def forbidden(error):   # pylint: disable=unused-argument
#         return render_template('errors/403.html'), 403
    
#     @flskapp.errorhandler(500)
#     def internal_error(error):   # pylint: disable=unused-argument
#         cTools_db.session.rollback()
#         return render_template('errors/500.html'), 500
    
#     return flskapp


# if __name__ == '__main__':
#     app = create_app()
#     app.run(debug=True)