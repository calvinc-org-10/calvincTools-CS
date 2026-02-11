from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import select, union_all, literal, case
from sqlalchemy.orm import aliased

from calvincTools.cMenu.forms import MenuEditForm
from calvincTools.cMenu import MENUCOMMAND, MENUCOMMANDDICTIONARY


def edit_menu(group_id, menu_num):
    """
    Proposed update for calvincTools.cMenu.views.edit_menu.

    Key changes:
    - Bind POST data normally (no formdata=None) so validation and updates work.
    - Preserve GET prefill for the 20-entry template.
    - Use model instances for updates/deletes, not dict rows.
    """
    group_id = int(group_id)
    menu_num = int(menu_num)

    from calvincTools.models import db, menuItems, menuGroups

    this_menu = menuItems.query.filter_by(
        MenuGroup_id=group_id,
        MenuID=menu_num,
        OptionNumber=0,
    ).first()
    if not this_menu:
        flash(f"Menu {group_id},{menu_num} does not exist", "error")
        return redirect(url_for("menu.edit_menu_init"))

    menu_name = this_menu.OptionText or ""
    group = this_menu.menu_group

    numbers_cte = select(literal(1).label("n")).cte(name="Numbers", recursive=True)
    numbers_cte = numbers_cte.union_all(
        select(numbers_cte.c.n + 1).where(numbers_cte.c.n < 20)
    )

    mnu_itm = aliased(menuItems)
    stmt = (
        select(
            numbers_cte.c.n.label("OptionNumber"),
            mnu_itm.id,
            case((mnu_itm.MenuGroup_id != None, mnu_itm.MenuGroup_id), else_=group_id).label("MenuGroup_id"),
            case((mnu_itm.MenuID != None, mnu_itm.MenuID), else_=menu_num).label("MenuID"),
            case((mnu_itm.OptionText != None, mnu_itm.OptionText), else_="").label("OptionText"),
            mnu_itm.Command,
            case((mnu_itm.Argument != None, mnu_itm.Argument), else_="").label("Argument"),
            case((mnu_itm.pword != None, mnu_itm.pword), else_="").label("pword"),
            case((mnu_itm.top_line != None, mnu_itm.top_line), else_=False).label("top_line"),
            case((mnu_itm.bottom_line != None, mnu_itm.bottom_line), else_=False).label("bottom_line"),
        )
        .select_from(numbers_cte)
        .outerjoin(
            mnu_itm,
            (numbers_cte.c.n == mnu_itm.OptionNumber)
            & (mnu_itm.MenuGroup_id == group_id)
            & (mnu_itm.MenuID == menu_num),
        )
        .order_by(numbers_cte.c.n)
    )
    menu_items_for_form = [
        dict(row._mapping) for row in db.session.execute(stmt).fetchall()
    ]

    if request.method == "POST":
        form = MenuEditForm()
    else:
        menu_group_data = {
            "id": group.id,
            "GroupName": group.GroupName,
            "GroupInfo": group.GroupInfo,
        }
        form = MenuEditForm(
            formdata=None,
            data={
                "menu_group": menu_group_data,
                "menu_items": menu_items_for_form,
            },
        )

    changed_data = {}
    if form.validate_on_submit():
        group_changed = False
        if form.menu_group.GroupName.data != group.GroupName:
            group.GroupName = form.menu_group.GroupName.data
            group_changed = True
        if form.menu_group.GroupInfo.data != group.GroupInfo:
            group.GroupInfo = form.menu_group.GroupInfo.data
            group_changed = True

        db_items = (
            menuItems.query.filter_by(MenuGroup_id=group_id, MenuID=menu_num)
            .filter(menuItems.OptionNumber > 0)
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

            if db_item is None and opt_text:
                new_item = menuItems(
                    **{key: value for key, value in entry.items() if key in allowed_fields}
                )
                db.session.add(new_item)
            elif db_item is not None and not opt_text:
                db.session.delete(db_item)
            elif db_item is not None:
                for key in allowed_fields:
                    new_val = entry.get(key)
                    if getattr(db_item, key) != new_val:
                        setattr(db_item, key, new_val)

        db.session.commit()
        return redirect(url_for("menu.edit_menu", group_id=group_id, menu_num=menu_num))

    mnu_goto = {
        "menuGroup": group.GroupName,
        "menuGroup_choices": menuGroups.query.all(),
        "menuID": menu_num,
        "menuID_choices": menuItems.query.filter_by(
            MenuGroup_id=group_id, OptionNumber=0
        ).all(),
    }

    cntext = {
        "form": form,
        "menuName": menu_name,
        "menuGoto": mnu_goto,
        "changed_data": changed_data,
    }
    return render_template("menu/edit_menu.html", **cntext)
