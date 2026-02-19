from calvincTools.utils.misctools import (
    show_routes, show_forms, pretty_show_fns, show_fns,
    )
from calvincTools.cMenu.commandhandlers import (
    run_sql, edit_parameters, greetings,
    )


def register_util_blueprint(app):
    """
    Register authentication routes with the Flask app.
    """
    from flask import Blueprint

    util_bp = Blueprint('utils', __name__, url_prefix='/utils')

    util_bp.add_url_rule('/routes', 'show_routes', show_routes, methods=['GET'])
    util_bp.add_url_rule('/formlist', 'show_forms', show_forms, methods=['GET'])
    # util_bp.add_url_rule('/fns', 'show_fns', show_fns, methods=['GET'])
    # util_bp.add_url_rule('/prettyfns', 'pretty_show_fns', pretty_show_fns, methods=['GET'])

    util_bp.add_url_rule('/sql', 'run_sql', run_sql, methods=['GET', 'POST'])
    util_bp.add_url_rule('/parameters', 'edit_parameters', edit_parameters, methods=['GET', 'POST'])
    util_bp.add_url_rule('/greetings', 'greetings', greetings, methods=['GET', 'POST'])
    
    app.register_blueprint(util_bp)
    
    