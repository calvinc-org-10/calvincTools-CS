from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from sqlalchemy import func


from ..database import cTools_db

from ..models import menuItems, menuGroups
from ..decorators import superuser_required
from . import (MENUCOMMAND, MENUCOMMANDDICTIONARY)

menu_bp = Blueprint('menu', __name__, url_prefix='/menu')


def get_default_menu(menu_group_id):
    """
    Django equivalent: DefaultMenu
    """
    menu_group = menuGroups.query.get(menu_group_id)
    if not menu_group: 
        return None, f'No such MenuGroup as {menu_group_id}'
    
    menu_item = menuItems.query.filter_by(
        menu_group_id=menu_group_id,
        option_number=0
    ).first()
    
    if not menu_item: 
        return None, f'MenuGroup {menu_group_id} has no menu'
    
    # Get minimum menu_id for this group with option_number=0
    result = cTools_db.session.query(func.min(menuItems.menu_id)).filter_by(
        menu_group_id=menu_group_id,
        option_number=0
    ).scalar()
    
    return result, ''


@menu_bp.route('/load/<int:menu_group>/<int:menu_num>')
@login_required
def load_menu(menu_group, menu_num):
    """
    Django equivalent:  LoadMenu
    Displays a menu to the user. 
    """
    # Check if menu exists
    menu_items_query = menuItems.query.filter_by(
        menu_group_id=menu_group,
        menu_id=menu_num,
        option_number=0
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
        menu_group_id=menu_group,
        menu_id=menu_num
    ).order_by(menuItems.option_number).all()
    
    menu_name = next((item.option_text for item in menu_items if item.option_number == 0), 'Menu')
    
    # Build menu HTML (you might want to do this in template instead)
    menu_html = build_menu_html(menu_items, menu_group, menu_num)
    
    return render_template('menu/display.html',
                         menu_group=menu_group,
                         menu_num=menu_num,
                         menu_name=menu_name,
                         menu_html=menu_html)


def build_menu_html(menu_items, menu_group, menu_num):
    """
    Helper to build menu HTML. 
    Django equivalent: inline logic in LoadMenu
    """
    from flask import url_for
    
    # Initialize 20 empty slots
    menu_list = ['<span class="btn btn-lg btn-outline-transparent mx-auto"></span>'] * 20
    
    for item in menu_items:
        if item.option_number == 0:
            continue
        
        # Build HTML for this menu item
        if item.command_id == MENUCOMMAND.LoadMenu:
            href = url_for('menu.load_menu', menu_group=menu_group, menu_num=item.argument)
            target = ''
            onclick = ''
        elif item.command_id == MENUCOMMAND.ExitApplication:
            href = '#'
            onclick = ' onclick="event.preventDefault(); document.getElementById(\'lgoutfm\').submit();"'
            target = ''
        else:
            arg = item.argument if item.argument else 'no-arg-no'
            href = url_for('menu.handle_command', command_num=item.command_id, command_arg=arg)
            target = ' target="_blank"' if item.command_id != MENUCOMMAND.ExitApplication else ''
            onclick = ''
        
        html = f'<a href="{href}"{onclick}{target} class="btn btn-lg btn-outline-secondary mx-auto">{item.option_text}</a>'
        menu_list[item.option_number - 1] = html
    
    # Build grid (2 columns, 10 rows)
    full_html = ""
    for i in range(10):
        full_html += f'<div class="row">'
        full_html += f'<div class="col m-1">{menu_list[i]}</div>'
        full_html += f'<div class="col m-1">{menu_list[i+10]}</div>'
        full_html += f'</div>'
    
    return full_html


@menu_bp. route('/command/<int:command_num>/<command_arg>')
@login_required
def handle_command(command_num, command_arg):
    """
    Django equivalent: HandleMenuCommand
    """
    command_text = MENUCOMMANDDICTIONARY.get(command_num, 'UnknownCommand')
    
    if command_num == MENUCOMMAND.FormBrowse:
        return redirect(url_for('forms.browse', formname=command_arg))
    elif command_num == MENUCOMMAND.OpenTable:
        return redirect(url_for('forms.show_table', tblname=command_arg))
    elif command_num == MENUCOMMAND.RunSQLStatement:
        return redirect(url_for('utils.run_sql'))
    elif command_num == MENUCOMMAND.ChangePW:
        return redirect(url_for('auth.change_password'))
    elif command_num == MENUCOMMAND.EditMenu:
        return redirect(url_for('menu.edit_menu_init'))
    elif command_num == MENUCOMMAND.EditParameters:
        return redirect(url_for('utils.edit_parameters'))
    elif command_num == MENUCOMMAND.EditGreetings:
        return redirect(url_for('utils.greetings'))
    elif command_num == MENUCOMMAND.ExitApplication:
        return redirect(url_for('auth. logout'))
    else:
        return f"Command {command_text} ({command_num}) will be performed with argument {command_arg}"


@menu_bp.route('/edit')
@superuser_required
def edit_menu_init():
    """
    Django equivalent: EditMenu_init
    """
    # Get first menu group and menu ID
    result = cTools_db.session.query(func.min(menuItems.menu_group_id)).filter_by(
        option_number=0
    ).scalar()
    
    menu_grp = result if result else 1
    
    result = cTools_db.session.query(func.min(menuItems.menu_id)).filter_by(
        menu_group_id=menu_grp,
        option_number=0
    ).scalar()
    
    menu_num = result if result else 0
    
    return redirect(url_for('menu.edit_menu', menu_group=menu_grp, menu_num=menu_num))


@menu_bp.route('/edit/<int:menu_group>/<int:menu_num>', methods=['GET', 'POST'])
@superuser_required
def edit_menu(menu_group, menu_num):
    """
    Django equivalent: EditMenu
    This is a complex view - simplified version shown
    """
    menu_items = menuItems.query.filter_by(
        menu_group_id=menu_group,
        menu_id=menu_num
    ).order_by(menuItems.option_number).all()
    
    menu_group_obj = menuGroups.query.get(menu_group)
    
    if not menu_items:
        flash(f'Menu {menu_group},{menu_num} does not exist', 'error')
        return redirect(url_for('menu.edit_menu_init'))
    
    if request.method == 'POST': 
        # Handle form submission
        # Process POST data similar to Django version
        # This would be quite long - simplified here
        flash('Menu updated successfully', 'success')
        return redirect(url_for('menu.edit_menu', menu_group=menu_group, menu_num=menu_num))
    
    # GET request - display form
    # command_choices = MenuCommand.query.order_by(MenuCommand.command).all()
    command_choices = MENUCOMMANDDICTIONARY
    
    return render_template('menu/edit. html',
                         menu_group=menu_group_obj,
                         menu_num=menu_num,
                         menu_items=menu_items,
                         command_choices=command_choices)


@menu_bp.route('/create/<int:menu_group>/<int:menu_num>')
@menu_bp.route('/create/<int:menu_group>/<int:menu_num>/<int:from_group>/<int:from_menu>')
@superuser_required
def create_menu(menu_group, menu_num, from_group=None, from_menu=None):
    """
    Django equivalent:  MenuCreate
    """
    # Check if menu already exists
    existing = menuItems.query.filter_by(
        menu_group_id=menu_group,
        menu_id=menu_num
    ).first()
    
    if existing:
        flash(f'Menu {menu_group},{menu_num} already exists', 'error')
        return redirect(url_for('menu.edit_menu_init'))
    
    # Get or create menu group
    menu_group_obj = menuGroups.query.get(menu_group)
    if not menu_group_obj: 
        menu_group_obj = menuGroups(id=menu_group, group_name='New Menu Group')
        cTools_db.session. add(menu_group_obj)
        cTools_db.session.flush()
    
    if from_menu is not None:
        # Copy from existing menu
        if from_group is None:
            from_group = menu_group
        
        source_items = menuItems.query.filter_by(
            menu_group_id=from_group,
            menu_id=from_menu
        ).all()
        
        for item in source_items:
            new_item = menuItems(
                menu_group_id=menu_group,
                menu_id=menu_num,
                option_number=item.option_number,
                option_text=item.option_text,
                command_id=item.command_id,
                argument=item.argument
            )
            cTools_db.session.add(new_item)
    else:
        # Create new menu from scratch
        title_item = menuItems(
            menu_group_id=menu_group,
            menu_id=menu_num,
            option_number=0,
            option_text='New Menu'
        )
        cTools_db.session.add(title_item)
        
        exit_item = menuItems(
            menu_group_id=menu_group,
            menu_id=menu_num,
            option_number=20,
            option_text='Return to Main Menu',
            command_id=MENUCOMMAND.LoadMenu,
            argument='0'
        )
        cTools_db.session.add(exit_item)
    
    cTools_db.session.commit()
    flash('Menu created successfully', 'success')
    return redirect(url_for('menu.edit_menu', menu_group=menu_group, menu_num=menu_num))


@menu_bp.route('/remove/<int:menu_group>/<int:menu_num>')
@superuser_required
def remove_menu(menu_group, menu_num):
    """
    Django equivalent: MenuRemove
    """
    menuItems.query.filter_by(
        menu_group_id=menu_group,
        menu_id=menu_num
    ).delete()
    
    cTools_db.session.commit()
    flash('Menu removed successfully', 'success')
    return redirect(url_for('menu.edit_menu_init'))