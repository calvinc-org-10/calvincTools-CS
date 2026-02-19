from flask import Blueprint

from calvincTools.cMenu.views import (
    load_menu, handle_command, 
    )
from calvincTools.cMenu.editmenu import (
    edit_menu_init, edit_menu,
    create_group, create_menu, remove_menu,
    )
from calvincTools.cMenu.commandhandlers import (
    form_browse, show_table,
    )


def register_menu_blueprint(app):

    from flask import Blueprint

    menu_bp = Blueprint('menu', __name__, url_prefix='/menu')
    
    menu_bp.add_url_rule('/load/<int:menu_group>/<int:menu_num>', 'load_menu', load_menu, methods=['GET'])
    menu_bp.add_url_rule('/command/<int:command_num>/<command_arg>', 'handle_command', handle_command, methods=['GET'])
    menu_bp.add_url_rule('/editmenu', 'edit_menu_init', edit_menu_init, methods=['GET'])
    menu_bp.add_url_rule('/edit/<int:group_id>/<int:menu_num>', 'edit_menu', edit_menu, methods=['POST', 'GET'])
    menu_bp.add_url_rule('/Gcreate/<int:group_id>/<group_name>/<group_info>', 'create_group', create_group, methods=['GET'])
    menu_bp.add_url_rule('/create/<int:menu_group>/<int:menu_num>/<int:from_group>/<int:frosm_menu>', 'create_menu', create_menu, methods=['GET'])
    menu_bp.add_url_rule('/remove/<int:menu_group>/<int:menu_num>', 'remove_menu', remove_menu, methods=['GET'])

    menu_bp.add_url_rule('/formbrowse/<formname>', 'form_browse', form_browse, methods=['GET'])
    menu_bp.add_url_rule('/showtable/<tablename>', 'show_table', show_table, methods=['GET'])

    app.register_blueprint(menu_bp)
    
    