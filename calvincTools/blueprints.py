from flask import Blueprint, current_app

ctools_bp = Blueprint(
    'ctools', __name__, 
    static_folder='assets',  # specify static folder for cTools
    static_url_path='/static/ctools',  # specify URL path for cTools static files
    template_folder='templates'
    )

# @ctools_bp.route('/status')
# def status():
#     # Access the calling app's config safely via current_app
#     api_key = current_app.config.get('CTOOLS_API_KEY')
#     return {"status": "ok", "key_used": api_key}

