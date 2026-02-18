# pylint: disable=no-member
from flask import (
    Blueprint, 
    current_app,
    url_for, 
    render_template, redirect, 
    flash, 
    )
from flask_login import login_required, current_user

from sqlalchemy import (
    union_all, cast, Integer, String, Boolean,
    func,
)


# db and models imported in each method so that the initalized versions are used

from . import (
    MENUCOMMAND, MENUCOMMANDDICTIONARY,
    )

menu_bp = Blueprint('menu', __name__, url_prefix='/menu')


def get_default_menu(MenuGroup_id):
    """
    Django equivalent: DefaultMenu
    """
    from ..models import ( db, menuItems, menuGroups, )
    menu_group = menuGroups.query.get(MenuGroup_id)
    if not menu_group: 
        return None, f'No such MenuGroup as {MenuGroup_id}'
    
    menu_item = menuItems.query.filter_by(
        MenuGroup_id=MenuGroup_id,
        OptionNumber=0
    ).first()
    
    if not menu_item: 
        return None, f'MenuGroup {MenuGroup_id} has no menu'
    
    # Get minimum MenuID for this group with OptionNumber=0
    result = db.session.query(func.min(menuItems.MenuID)).filter_by(
        MenuGroup_id=MenuGroup_id,
        OptionNumber=0
    ).scalar()
    
    return result, ''
# get_default_menu


@menu_bp.route('/load/<int:menu_group>/<int:menu_num>')
@login_required
def load_menu(menu_group, menu_num):
    """
    Django equivalent:  LoadMenu
    Displays a menu to the user. 
    """
    from ..models import ( db, menuItems, menuGroups, )

    # Check if menu exists
    menu_items_query = menuItems.query.filter_by(
        MenuGroup_id=menu_group,
        MenuID=menu_num,
        OptionNumber=0
    )
    
    if not menu_items_query.first():
        # Menu doesn't exist, try default
        default_menu_num, error_msg = get_default_menu(menu_group)
        if default_menu_num is not None:
            flash(f'Menu {menu_num} does not exist', 'warning')
            menu_num = default_menu_num
        else:
            flash(error_msg, 'warning')
            return redirect(url_for('auth.logout'))
    
    # Get all menu items for this menu
    menu_items = menuItems.query.filter_by(
        MenuGroup_id=menu_group,
        MenuID=menu_num
    ).order_by(menuItems.OptionNumber).all()
    
    menu_name = next((item.OptionText for item in menu_items if item.OptionNumber == 0), 'Menu')
    menu_html = build_menu_html(menu_items, menu_group, menu_num)
    sysver = current_app.config.get('APP_VERSION', 'unknown version')

    templt = 'menu/cMenu.html'
    cntext = {
        'grpNum': menu_group,
        'menuNum': menu_num,
        'menuName': menu_name,
        'menuContents': menu_html,
        'sysver': sysver,
        'applogo_url': current_app.config.get('APP_LOGO_URL', None),
    }
    
    return render_template(templt, **cntext)
# load_menu

def build_menu_html(menu_items, menu_group, menu_num):  # pylint: disable=unused-argument
    """
    Helper to build menu HTML. 
    Django equivalent: inline logic in LoadMenu
    """
    # from flask import url_for
    
    # Initialize 20 empty slots
    menu_html = ['<span class="btn btn-lg btn-outline-transparent mx-auto"></span>'] * 20
    
    for item in menu_items:
        if item.OptionNumber == 0:
            continue
        
        # Build HTML for this menu item
        if item.Command == MENUCOMMAND.LoadMenu:
            href = url_for('menu.load_menu', menu_group=menu_group, menu_num=item.Argument)
            target = ''
            onclick = ''
        elif item.Command == MENUCOMMAND.ExitApplication:
            # href = '#'
            # onclick = ' onclick="event.preventDefault(); document.getElementById(\'lgoutfm\').submit();"'
            arg = 'no-arg-no'
            href = url_for('menu.handle_command', command_num=item.Command, command_arg=arg)
            target = ''
            onclick = ''
        else:
            arg = item.Argument if item.Argument else 'no-arg-no'
            href = url_for('menu.handle_command', command_num=item.Command, command_arg=arg)
            target = ' target="_blank"' if item.Command != MENUCOMMAND.ExitApplication else ''
            onclick = ''
        # endif command type
        
        menu_html[item.OptionNumber - 1] = \
            f'<a href="{href}"{onclick}{target} class="btn btn-lg btn-outline-secondary mx-auto">{item.OptionText}</a>'
    # endfor menu_items
    
    return menu_html
# build_menu_html


@menu_bp.route('/command/<int:command_num>/<command_arg>')
@login_required
def handle_command(command_num, command_arg):
    """
    Django equivalent: HandleMenuCommand
    """
    command_name = MENUCOMMANDDICTIONARY.get(command_num, 'UnknownCommand')
    endpt = None
    extra_args = {}

    if command_num == MENUCOMMAND.FormBrowse:
        endpt = 'menu.form_browse'
        extra_args['formname'] = command_arg
    elif command_num == MENUCOMMAND.OpenTable:
        endpt = 'menu.show_table'
        extra_args['tblname'] = command_arg
    elif command_num == MENUCOMMAND.RunSQLStatement:
        endpt = 'utils.run_sql'
    elif command_num == MENUCOMMAND.ChangePW:
        endpt = 'auth.change_password'
    elif command_num == MENUCOMMAND.EditMenu:
        endpt = 'menu.edit_menu_init'
    elif command_num == MENUCOMMAND.EditParameters:
        endpt = 'utils.edit_parameters'
    elif command_num == MENUCOMMAND.EditGreetings:
        endpt = 'utils.edit_greetings'
    elif command_num == MENUCOMMAND.ExitApplication:
        endpt = 'auth.logout'
    elif command_num == MENUCOMMAND.EditUsers:
        endpt = 'auth.user_list'
    elif command_num == MENUCOMMAND.ShowRoutes_URLs:
        endpt = 'utils.show_routes'
    elif command_num == MENUCOMMAND.ShowForms:
        endpt = 'utils.show_forms'
    # need to implement:
    # 21: 'RunCode',
    # 32: 'ConstructSQLStatement',
    # 36: 'LoadExtWebPage',
    # 62: 'ChangeUser',
    # 63: 'ChangeMenuGroup',
    # 110: 'Show Help',
    else:
        flash(f"Invalid request for {command_name} ({command_num}) to be performed with argument {command_arg}")
    # endif command_num

    if endpt in current_app.view_functions:
        return redirect(url_for(endpt, **extra_args))
    else:
        flash(f"{command_name} command not implemented yet", "error")
        notreadyyet_msg = f"{command_name} command not implemented yet. Calvin needs more coffee."
        return render_template("UnderConstruction.html", notreadyyet_msg=notreadyyet_msg)
    # endif endpoint exists
# handle_command

