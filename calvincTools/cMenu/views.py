# pylint: disable=no-member
from flask import (
    Blueprint, 
    current_app,
    url_for, 
    render_template, redirect, 
    request, 
    session,
    flash, 
    )
from flask_login import login_required, current_user

from sqlalchemy import (
    select, union_all, literal, case, cast, Integer, String, Boolean,
    func,
)
from sqlalchemy.orm import aliased

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

    templt = 'menu/cMenu.html'
    cntext = {
        'grpNum': menu_group,
        'menuNum': menu_num,
        'menuName': menu_name,
        'menuContents': menu_html,
        'sysver': "We'll get versioning later",
    }
    
    return render_template(templt, **cntext)
# load_menu

def build_menu_htmlOLD(menu_items, menu_group, menu_num):  # pylint: disable=unused-argument
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
        # endif command type
        
        html = f'<a href="{href}"{onclick}{target} class="btn btn-lg btn-outline-secondary mx-auto">{item.OptionText}</a>'
        menu_list[item.OptionNumber - 1] = html
    # endfor menu_items
    
    # Build grid (2 columns, 10 rows)
    full_html = ""
    for i in range(10):
        full_html += f'<div class="row">'
        full_html += f'<div class="col m-1">{menu_list[i]}</div>'
        full_html += f'<div class="col m-1">{menu_list[i+10]}</div>'
        full_html += f'</div>'
    # endfor rows
    
    return full_html
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
            href = '#'
            onclick = ' onclick="event.preventDefault(); document.getElementById(\'lgoutfm\').submit();"'
            target = ''
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
        endpt = 'forms.browse'
        extra_args['formname'] = command_arg
    elif command_num == MENUCOMMAND.OpenTable:
        endpt = 'forms.show_table'
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
    # need to implement:
    # 21: 'RunCode',
    # 32: 'ConstructSQLStatement',
    # 36: 'LoadExtWebPage',
    # 62: 'ChangeUser',
    # 63: 'ChangeMenuGroup',
    else:
        flash(f"Invalid request for {command_name} ({command_num}) to be performed with argument {command_arg}")
    # endif command_num

    if endpt in current_app.view_functions:
        return redirect(url_for(endpt, **extra_args))
    else:
        flash(f"{command_name} command not implemented yet", "error")
        fallback_url = url_for('menu.load_menu', menu_group=0, menu_num=0)
        return redirect(request.referrer or fallback_url)
    # endif endpoint exists
# handle_command


@menu_bp.route('/editmenu')
@superuser_required
def edit_menu_init():
    """
    Django equivalent: EditMenu_init
    edit_menu_init just finds the first menu group and menu number and redirects to edit_menu for that menu.
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
    
    return redirect(url_for('menu.edit_menu', group_id=menu_grp, menu_num=menu_num))
# edit_menu_init

@menu_bp.route('/edit/<int:group_id>/<int:menu_num>', methods=['GET', 'POST'])
@superuser_required
def edit_menu(group_id, menu_num):
    """
    Django equivalent: EditMenu
    """
    # things go bonkers if these are strings
    group_id = int(group_id)
    menu_num = int(menu_num)

    from ..models import ( db, menuItems, menuGroups, )

    thisMenu = menuItems.query.filter_by(
        MenuGroup_id=group_id, 
        MenuID=menu_num, 
        OptionNumber=0
        ).first()
    if not thisMenu:
        flash(f"Menu {group_id},{menu_num} does not exist", "error")
        return redirect(url_for("menu.edit_menu_init"))
    menuName = thisMenu.OptionText if thisMenu else ""          # type: ignore
    group = thisMenu.menu_group                                 # type: ignore

    # construct the query to get all 20 options with left join to menuItems
    # 1. Define the Recursive CTE (Numbers)
    numbers_cte = select(literal(1).label("n")).cte(name="Numbers", recursive=True)
    numbers_cte = numbers_cte.union_all(
        select(numbers_cte.c.n + 1).where(numbers_cte.c.n < 20)
    )
    # 2. Setup the join and logic
    # We alias the model to make the join clear
    mnuItm = aliased(menuItems)
    stmt = (
        select(
            numbers_cte.c.n.label("OptionNumber"),                                                      # type: ignore
            mnuItm.id,
            # Use coalesce logic similar to the SQL fix provided earlier
            # (many errors suppressed here due to the placeholder vs actual runtime models)
            case((mnuItm.MenuGroup_id != None, mnuItm.MenuGroup_id), else_=group_id).label("MenuGroup_id"),    # type: ignore
            case((mnuItm.MenuID != None, mnuItm.MenuID), else_=menu_num).label("MenuID"),                      # type: ignore
            case((mnuItm.OptionText != None, mnuItm.OptionText), else_="").label("OptionText"),         # type: ignore
            mnuItm.Command,                                                                             # type: ignore
            case((mnuItm.Argument != None, mnuItm.Argument), else_="").label("Argument"),               # type: ignore
            case((mnuItm.pword != None, mnuItm.pword), else_="").label("pword"),                        # type: ignore
            case((mnuItm.top_line != None, mnuItm.top_line), else_=False).label("top_line"),            # type: ignore
            case((mnuItm.bottom_line != None, mnuItm.bottom_line), else_=False).label("bottom_line"),   # type: ignore
        )
        .select_from(numbers_cte)
        .outerjoin(
            mnuItm,
            (numbers_cte.c.n == mnuItm.OptionNumber) & 
            (mnuItm.MenuGroup_id == group_id) & 
            (mnuItm.MenuID == menu_num)
        )
        .order_by(numbers_cte.c.n)
    )
    menu_items_forform = [
        dict(row._mapping) for row in db.session.execute(stmt).fetchall()       # type: ignore      # pylint: disable=protected-access
        ]

    if request.method == "POST":
        form = MenuEditForm()
    else:
        # Initialize form with explicit data so FieldList gets all 20 entries
        menu_group_data = {
            "id": group.id,
            "GroupName": group.GroupName,
            "GroupInfo": group.GroupInfo,
        }
        form = MenuEditForm(
            formdata=None, 
            data={
                "menu_group": menu_group_data,
                "menu_items": menu_items_forform,
                "menu_name": menuName,
            },
        )
    # endif request.method

    changed_data = {}

    if form.validate_on_submit():
        # Update menu group info if changed
        if form.menu_group.GroupName.data != group.GroupName:
            group.GroupName = form.menu_group.GroupName.data
            changed_data['GroupName'] = form.menu_group.GroupName.data
        if form.menu_group.GroupInfo.data != group.GroupInfo:
            group.GroupInfo = form.menu_group.GroupInfo.data
            changed_data['GroupInfo'] = form.menu_group.GroupInfo.data
        if 'GroupName' in changed_data or 'GroupInfo' in changed_data:
            db.session.add(group)

        # has menu name changed? (OptionNumber=0)
        if form.menu_name.data != menuName:
            title_item = menuItems.query.filter_by(
                MenuGroup_id=group_id,
                MenuID=menu_num,
                OptionNumber=0
            ).first()
            if title_item:
                title_item.OptionText = form.menu_name.data     # type: ignore  
                db.session.add(title_item)
            else:
                # This should never happen since the menu must exist to get here, but just in case:
                new_title = menuItems(
                    MenuGroup_id=group_id,
                    MenuID=menu_num,
                    OptionNumber=0,
                    OptionText=form.menu_name.data
                )
                db.session.add(new_title)
            # endif title_item
            changed_data['MenuName'] = form.menu_name.data
            
        # endif menu name changed
        
        db_items = (
            menuItems.query.filter_by(MenuGroup_id=group_id, MenuID=menu_num)
            .filter(menuItems.OptionNumber > 0)                #type: ignore
            .all()
        )
        db_by_option = {item.OptionNumber: item for item in db_items}

        allowed_fields = {
            "MenuGroup_id",
            "MenuID",
            "OptionNumber",
            "OptionText",
            "Command",
            "Argument",
            "pword",
            "top_line",
            "bottom_line",
        }

        for index, entry_form in enumerate(form.menu_items.entries, start=1):
            entry = entry_form.data
            opt_num = entry.get("OptionNumber") or index
            entry["OptionNumber"] = opt_num
            entry["MenuGroup_id"] = group_id
            entry["MenuID"] = menu_num

            db_item = db_by_option.get(opt_num)
            opt_text = (entry.get("OptionText") or "").strip()

            copymoveRequested = entry.get("CopyType", "") or ""
            removalRequested = entry.get("Remove", False) or opt_text == ""
            isNewitem = db_item is None and opt_text != ""
            processRemoval, processCopyMove, processUpdate = False, False, True
            
            changes_made = ""
                        
            if copymoveRequested and removalRequested:
                flash(f"Option {opt_num}: Cannot choose both Remove and Copy/Move. Please fix and resubmit.", "error")
                changes_made += ("<br>" if changes_made else "") + "Error: Remove and Copy/Move both selected. Option not removed nor copied/moved."
                processRemoval, processCopyMove, processUpdate = False, False, True
                # continue
            elif removalRequested:
                processRemoval, processCopyMove, processUpdate = True, False, False
                if isNewitem:
                    flash(f"Option {opt_num}: Cannot remove an option that doesn't exist. Please fix and resubmit.", "error")
                    changes_made += ("<br>" if changes_made else "") + "Error: Remove selected for non-existent option. Option added, not removed."
                    processRemoval, processCopyMove, processUpdate = False, True, True                    
                # continue
            elif copymoveRequested:
                processRemoval, processCopyMove, processUpdate = False, True, True
            # endif copymove vs remove
            
            if isNewitem and processUpdate:
                # New item created if no existing db item and user entered text
                new_item = menuItems(
                    **{key: value for key, value in entry.items() if key in allowed_fields}
                )
                db.session.add(new_item)
                changes_made += ("<br>" if changes_made else "") + "Option added."
            elif removalRequested and processRemoval and db_item is not None:
                # Existing item deleted if user cleared text
                db.session.delete(db_item)
                changes_made += ("<br>" if changes_made else "") + "Option deleted."
            elif db_item is not None and processUpdate:
                # Existing item updated if user changed text or any other field
                for key in allowed_fields:
                    new_val = entry.get(key)
                    if getattr(db_item, key) != new_val:
                        setattr(db_item, key, new_val)
                        changes_made += ("<br>" if changes_made else "") + f"{key} updated."
                # endfor allowed_fields
            # endif db_item vs entry

            # copy/move
            if copymoveRequested and processCopyMove:
                MoveORCopy = entry.get('CopyType')
                CopyTarget = entry.get('CopyTarget', '').split(',')
                targetGroup = None
                if len(CopyTarget)==2:
                    targetGroup = menu_num  # default to same menu if only menu and option number provided
                    try:
                        targetMenu = int(CopyTarget[0])
                    except ValueError:
                        targetMenu = None
                    try:
                        targetOption = int(CopyTarget[1])
                    except ValueError:
                        targetOption = None
                elif len(CopyTarget)==3:
                    try:
                        targetGroup = int(CopyTarget[0])
                    except ValueError:
                        targetGroup = None
                    try:
                        targetMenu = int(CopyTarget[1])
                    except ValueError:
                        targetMenu = None
                    try:
                        targetOption = int(CopyTarget[2])
                    except ValueError:
                        targetOption = None
                else:
                    targetMenu = None
                    targetOption = None
                    pass    # targetGroup is already None
                # endif length of CopyTarget (for parsing the target menu and option)

                if targetGroup is None or targetMenu is None or targetOption is None:
                    changes_made += ("<br>" if changes_made else "") + f"Could not interpret {MoveORCopy} target {entry.get('CopyTarget')}"
                else:
                    if menuItems.query.filter_by(MenuGroup=targetGroup, MenuID=targetMenu, OptionNumber=targetOption).exists():     # type: ignore
                        changes_made += ("<br>" if changes_made else "") + f"Could not {MoveORCopy} to {entry.get('CopyTarget')} - target already exists."
                    else:
                        new_item = menuItems(
                                MenuGroup_id = targetGroup,
                                MenuID = targetMenu,
                                OptionNumber = targetOption,
                                OptionText = entry["OptionText"] or "",
                                Command = entry["Command"],
                                Argument = entry["Argument"]
                            )
                        db.session.add(new_item)
                        if MoveORCopy == 'move' and db_item is not None:   # if move, delete original (but if copy, keep original)
                            db.session.delete(db_item)
                        # endif move (not just copy)

                        changes_made += ("<br>" if changes_made else "") + f"Option {opt_num} {MoveORCopy}d to {entry.get('CopyTarget')}."
                    # endif target exists
                # endif valid target for copy/move
            # endif copy/move requested

            if changes_made:
                changed_data[f'Option{opt_num}'] = changes_made

        # endfor menu_items.entries

        db.session.commit()

        flash(f"changed data: {changed_data}", "info")
        return redirect(url_for("menu.edit_menu", group_id=group_id, menu_num=menu_num))
        ##########################
        # OOPS!! the redirect will cause us to lose the changed_data messages about what changed. 
        # To fix this, we can store the messages in the session before redirecting, 
        # and then pop them in the GET request to display.
        # session['changed_data'] = changed_data
        ##########################
    # endif form.validate_on_submit()

    mnuGoto = {
        'menuGroup':group.GroupName,
        'menuGroup_choices': menuGroups.query.all(),
        'menuID':menu_num,
        'menuID_choices':menuItems.query.filter_by(MenuGroup_id=group_id, OptionNumber=0).all(),
        }

    cntext = {
        'form': form,
        # 'menuGroupName': mnuGroupRec.GroupName,   ## in form
        # 'menuContents':fullMenuHTML,              ## in form
        'menuName':menuName,
        'menuGoto':mnuGoto,
        # 'changed_data': changed_data,
        }
    templt = "menu/edit_menu.html"
    # return render(req, templt, context=cntext)
    return render_template(templt, **cntext)
    
#     return render_template('menu/edit. html',
#                          menu_group=menu_group_obj,
#                          menu_num=menu_num,
#                          menu_items=menu_items,
#                          command_choices=command_choices)

# from sqlalchemy import select

# # Filtered List
# stmt = select(menuItems).filter_by(MenuGroup_id=group_id, OptionNumber=0)
# menuID_choices = db_instance.session.execute(stmt).scalars().all()

# # Single Item
# stmt = select(menuItems).filter_by(MenuGroup_id=group_id, MenuID=menu_id, OptionNumber=0)
# menuName_obj = db_instance.session.execute(stmt).scalar_one_or_none()

# edit_menu

@menu_bp.route('/Gcreate/<int:group_id>/<group_name>/<group_info>')
@superuser_required
def create_group(group_id, group_name, group_info):
    return f"Group {group_id} with name {group_name} and info {group_info} would be created here"

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
        # REPLACE THIS
        # copy from dbmenulist.py - newmenu_menulist depending on whether it's a new menu in an existing group or a new group and menu.
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
    return redirect(url_for('menu.edit_menu', group_id=menu_group, menu_num=menu_num))


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
