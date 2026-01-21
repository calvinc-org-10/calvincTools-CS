from flask import Flask, render_template, redirect, url_for
from flask_migrate import Migrate

from .database import db  # , init_cDatabase      # TODO: move this to database.py?
from .usr_auth.views import init_login_manager, register_auth_blueprint
from .views.menu_views import menu_bp
from .views.util_views import util_bp
from . import config

def create_app(config_name='development'):
    flskapp = Flask(__name__, static_folder='assets', template_folder='templates')
    flskapp.config.from_object(config.config[config_name])
    
    # Initialize extensions
    db.init_app(flskapp)
    # init_cDatabase(db)
    migrate = Migrate(flskapp, db)
    init_login_manager(flskapp)
    
    # Register blueprints
    register_auth_blueprint(flskapp)
    flskapp.register_blueprint(menu_bp)
    flskapp.register_blueprint(util_bp)
    
    # Home route
    @flskapp.route('/')
    def index():
        return redirect(url_for('menu.load_menu', menu_group=1, menu_num=0))
    
    # Error handlers
    @flskapp.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @flskapp.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    
    @flskapp.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return flskapp


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)