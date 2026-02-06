from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from sqlalchemy import func

# db and models imported in each method so that the initalized versions are used

from ..decorators import superuser_required
from . import (MENUCOMMAND, MENUCOMMANDDICTIONARY)
from .forms import MenuEditForm

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
        menuGroup_id=MenuGroup_id,
        OptionNumber=0
    ).first()
    
    if not menu_item: 
        return None, f'MenuGroup {MenuGroup_id} has no menu'
    
    # Get minimum MenuID for this group with OptionNumber=0
    result = db.session.query(func.min(menuItems.MenuID)).filter_by(
        menuGroup_id=MenuGroup_id,
        OptyionNumber=0
    ).scalar()
    
    return result, ''


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
    
    # Build menu HTML (you might want to do this in template instead)
    menu_html = build_menu_html(menu_items, menu_group, menu_num)
    
    return render_template('menu/display.html',
                         grpNum=menu_group,
                         menuNum=menu_num,
                         menuName=menu_name,
                         menuContents=menu_html,
                         sysver="We'll get versioning later"
                         )


def build_menu_html(menu_items, menu_group, menu_num):  # pylint: disable=unused-argument
    """
    Helper to build menu HTML. 
    Django equivalent: inline logic in LoadMenu
    """
    # from flask import url_for
    
    # Initialize 20 empty slots
    menu_list = ['<span class="btn btn-lg btn-outline-transparent mx-auto"></span>'] * 20
    
    for item in menu_items:
        if item.OptionNumber == 0:
            continue
        
        # Build HTML for this menu item
        if item.Command == MENUCOMMAND.LoadMenu:
            href = url_for('menu.load_menu', menu_group=menu_group, menu_num=item.Argument)
            target = ''
            onclick = ''
        elif item.Command == MENUCOMMAND.ExitApplication:
            href = '#'
            onclick = ' onclick="event.preventDefault(); document.getElementById(\'lgoutfm\').submit();"'
            target = ''
        else:
            arg = item.Argument if item.Argument else 'no-arg-no'
            href = url_for('menu.handle_command', command_num=item.Command, command_arg=arg)
            target = ' target="_blank"' if item.Command != MENUCOMMAND.ExitApplication else ''
            onclick = ''
        
        html = f'<a href="{href}"{onclick}{target} class="btn btn-lg btn-outline-secondary mx-auto">{item.OptionText}</a>'
        menu_list[item.OptionNumber - 1] = html
    
    # Build grid (2 columns, 10 rows)
    full_html = ""
    for i in range(10):
        full_html += f'<div class="row">'
        full_html += f'<div class="col m-1">{menu_list[i]}</div>'
        full_html += f'<div class="col m-1">{menu_list[i+10]}</div>'
        full_html += f'</div>'
    
    return full_html


@menu_bp.route('/command/<int:command_num>/<command_arg>')
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
        return redirect(url_for('auth.logout'))
    else:
        return f"Command {command_text} ({command_num}) will be performed with argument {command_arg}"


@menu_bp.route('/editmenu')
@superuser_required
def edit_menu_init():
    """
    Django equivalent: EditMenu_init
    """
    # Get first menu group and menu ID
    from ..models import ( db, menuItems, menuGroups, )

    # initial menu group will be the lowest numbered one
    result = db.session.query(func.min(menuItems.MenuGroup_id)).filter_by(
        OptionNumber=0
    ).scalar()
    menu_grp = result if result else 1
    # similarly for menu number
    result = db.session.query(func.min(menuItems.MenuID)).filter_by(
        MenuGroup_id=menu_grp,
        OptionNumber=0
    ).scalar()
    menu_num = result if result else 0
    
    return redirect(url_for('menu.edit_menu', group_id=menu_grp, menu_id=menu_num))


@menu_bp.route('/edit/<int:group_id>/<int:menu_id>', methods=['GET', 'POST'])
@superuser_required
def edit_menu(group_id, menu_id):
    # import the initialized models
    from ..models import (
        db,
        menuItems, menuGroups,
        )
    
    # 1. Fetch group and existing items
    group = menuGroups.query.get_or_404(group_id) # type: ignore
    existing_items = menuItems.query.filter_by(MenuGroup_id=group_id, MenuID=menu_id).all()
    
    # 2. Build the {optionNumber: menuItem} dict as requested
    # We use a dict for quick lookup during POST comparison
    db_items_dict = {item.OptionNumber: item for item in existing_items}
    
    # 3. Create a list of 20 items for the FieldList (1-indexed based on OptionNumber)
    form_init_data = []
    for i in range(1, 21):
        if i in db_items_dict:
            form_init_data.append(db_items_dict[i].__dict__) # Simple way to map model to form
        else:
            # Entry for unused option numbers
            form_init_data.append({'OptionNumber': i, 'id': None, 'MenuGroup_id': group_id, 'MenuID': menu_id})
        #endif 
    #endfor    

    # Initialize form with the group and the list of items
    form = MenuEditForm(obj=group, menu_items=form_init_data)

    if form.validate_on_submit():
        # 4. Handle POST logic: Compare form data to db_items_dict
        for entry in form.menu_items.data:
            opt_num = entry['OptionNumber']
            db_item = db_items_dict.get(opt_num)
            
            # Case A: User entered text for an empty slot -> CREATE
            if not db_item and entry['OptionText']:
                new_item = menuItems(**entry)
                db.session.add(new_item)
                
            # Case B: Slot was occupied but user cleared text -> DELETE
            elif db_item and not entry['OptionText']:
                db.session.delete(db_item)
                
            # Case C: Slot occupied and text changed -> UPDATE
            elif db_item and entry['OptionText'] != db_item.OptionText:
                # Update all relevant fields from the form entry
                for key, value in entry.items():
                    if key != 'id': # Don't overwrite the PK
                        setattr(db_item, key, value)
            # endif db_item vs entry
        # endfor menu_items.data

        db.session.commit()
        # return redirect(url_for('some_success_view'))

    return render_template('menu/edit_menu.html', form=form)
###################### start of first attempt ##########################
# def edit_menu(menu_group, menu_num):
#     """
#     Django equivalent: EditMenu
#     """
#     # things go bonkers if these are strings
#     menu_group = int(menu_group)
#     menu_num = int(menu_num)

#     from ..models import ( db, menuItems, menuGroups, )

#     command_choices = MENUCOMMANDDICTIONARY

#     def commandchoiceHTML(passedcommand):
#         commandchoices_html = ""
#         for ch, chtext in command_choices.items():
#             commandchoices_html += "<option value=" + str(ch)
#             if ch == passedcommand: commandchoices_html += " selected"
#             commandchoices_html += ">" + chtext + "</option>"
#         return commandchoices_html
#     # commandchoiceHTML

#     menu_items = menuItems.query.filter_by(
#         MenuGroup_id=menu_group,
#         MenuID=menu_num
#     ).order_by(menuItems.OptionNumber).all()
#     menu_group_obj = menuGroups.query.get(menu_group)
    
#     if not menu_items:
#         flash(f'Menu {menu_group},{menu_num} does not exist', 'error')
#         return redirect(url_for('menu.edit_menu_init'))
    
#     mnItem_list = [{'OptionText':'',
#                     'Command':'',
#                     'Argument':''}
#             for i in range(20)]
#     changed_data = ''

#     if request.method == 'POST': 
#         # Handle form submission

#         flash('Menu updated successfully', 'success')
#         return redirect(url_for('menu.edit_menu', menu_group=menu_group, menu_num=menu_num))
#     else:   # request.method == 'GET'
#         # GET request - display form
#         pass
#     # endif POST/GET
    
#     return render_template('menu/edit. html',
#                          menu_group=menu_group_obj,
#                          menu_num=menu_num,
#                          menu_items=menu_items,
#                          command_choices=command_choices)
###################### end of first attempt ##########################

@menu_bp.route('/create/<int:menu_group>/<int:menu_num>')
@menu_bp.route('/create/<int:menu_group>/<int:menu_num>/<int:from_group>/<int:from_menu>')
@superuser_required
def create_menu(menu_group, menu_num, from_group=None, from_menu=None):
    """
    Django equivalent:  MenuCreate
    """
    # Check if menu already exists
    from ..models import ( db, menuItems, menuGroups, )

    existing = menuItems.query.filter_by(
        MenuGroup_id=menu_group,
        MenuID=menu_num
    ).first()
    
    if existing:
        flash(f'Menu {menu_group},{menu_num} already exists', 'error')
        return redirect(url_for('menu.edit_menu_init'))
    
    # Get or create menu group
    menu_group_obj = menuGroups.query.get(menu_group)
    if not menu_group_obj: 
        menu_group_obj = menuGroups(id=menu_group, GroupName='New Menu Group')
        db.session. add(menu_group_obj)
        db.session.flush()
    
    if from_menu is not None:
        # Copy from existing menu
        if from_group is None:
            from_group = menu_group
        
        source_items = menuItems.query.filter_by(
            MenuGroup_id=from_group,
            MenuID=from_menu
        ).all()
        
        for item in source_items:
            new_item = menuItems(
                MenuGroup_id=menu_group,
                MenuID=menu_num,
                OptionNumber=item.OptionNumber,
                OptionText=item.OptionText,
                Command=item.Command,
                Argument=item.Argument
            )
            db.session.add(new_item)
    else:
        # Create new menu from scratch
        title_item = menuItems(
            MenuGroup_id=menu_group,
            MenuID=menu_num,
            OptionNumber=0,
            OptionText='New Menu'
        )
        db.session.add(title_item)
        
        exit_item = menuItems(
            MenuGroup_id=menu_group,
            MenuID=menu_num,
            OptionNumber=20,
            OptionText='Return to Main Menu',
            Command=MENUCOMMAND.LoadMenu,
            Argument='0'
        )
        db.session.add(exit_item)
    
    db.session.commit()
    flash('Menu created successfully', 'success')
    return redirect(url_for('menu.edit_menu', menu_group=menu_group, menu_num=menu_num))


@menu_bp.route('/remove/<int:menu_group>/<int:menu_num>')
@superuser_required
def remove_menu(menu_group, menu_num):
    """
    Django equivalent: MenuRemove
    """
    from ..models import ( db, menuItems, menuGroups, )

    menuItems.query.filter_by(
        MenuGroup_id=menu_group,
        MenuID=menu_num
    ).delete()
    
    db.session.commit()
    flash('Menu removed successfully', 'success')
    return redirect(url_for('menu.edit_menu_init'))
