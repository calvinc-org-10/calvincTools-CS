from flask_wtf import FlaskForm
from wtforms import (
    StringField, SubmitField, Form, FormField, FieldList, IntegerField, HiddenField, BooleanField,
    SelectField,
    )
from wtforms.validators import DataRequired

# from calvincTools.models import menuItems
from . import (MENUCOMMAND, MENUCOMMANDDICTIONARY)



class MenuItemForm(Form):
    id = HiddenField()
    MenuGroup_id = IntegerField()
    MenuID = IntegerField()
    OptionNumber = IntegerField()
    OptionText = StringField()
    Command = SelectField(choices=MENUCOMMANDDICTIONARY.items(), coerce=int)
    Argument = StringField()
    pword = StringField()
    top_line = BooleanField()
    bottom_line = BooleanField()

class MenuGroupForm(Form):
    id = HiddenField()
    GroupName = StringField()
    GroupInfo = StringField()

class MenuEditForm(FlaskForm):
    ### CHANGE ME!! CHANGE ME!!
    menu_group = FormField(MenuGroupForm)
    menu_items = FieldList(FormField(MenuItemForm), min_entries=20, max_entries=20)
    submit = SubmitField('Save Menu')