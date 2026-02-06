@app.route('/edit-menu/<int:group_id>/<int:menu_id>', methods=['GET', 'POST'])
def edit_menu(group_id, menu_id):
    # 1. Fetch group and existing items
    group = MenuGroup.query.get_or_404(group_id)
    existing_items = MenuItem.query.filter_by(MenuGroup_id=group_id, MenuID=menu_id).all()
    
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
                new_item = MenuItem(**entry)
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
        return redirect(url_for('some_success_view'))

    return render_template('edit_menu.html', form=form)
