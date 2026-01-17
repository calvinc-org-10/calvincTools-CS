from flask import Flask, render_template, redirect, url_for
from flask_migrate import Migrate
from .models import db
from .usr_auth.views import init_login_manager, register_auth_blueprint
from .views.menu_views import menu_bp
from .views.util_views import util_bp
from . import config

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config.config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    init_login_manager(app)
    
    # Register blueprints
    register_auth_blueprint(app)
    app.register_blueprint(menu_bp)
    app.register_blueprint(util_bp)
    
    # Home route
    @app.route('/')
    def index():
        return redirect(url_for('menu.load_menu', menu_group=1, menu_num=0))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)