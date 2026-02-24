def edit_view():
    SuperMan = True  # Your logic here
    
    # Create a dynamic subform class
    class DynamicItemForm(cParameterItemForm):
        pass

    if not SuperMan:
        # Override the field to be hidden if not SuperMan
        DynamicItemForm.user_modifiable = HiddenField()

    # Create a dynamic main form class using the new subform
    class DynamicEditForm(cParameterEditForm):
        parameters = FieldList(FormField(DynamicItemForm), min_entries=1)

    form = DynamicEditForm()
    # ... rest of your view
