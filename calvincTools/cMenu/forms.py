from dataclasses import dataclass

from flask_wtf import FlaskForm
from wtforms import (
    StringField, SubmitField, Form, FormField, FieldList, IntegerField, HiddenField, BooleanField,
    SelectField, RadioField,
    )
from wtforms.validators import (DataRequired, Optional, )

# from calvincTools.models import menuItems
from . import (MENUCOMMAND, MENUCOMMANDDICTIONARY)


class MenuItemForm(Form):
    id = HiddenField()
    MenuGroup_id = IntegerField()
    MenuID = IntegerField()
    OptionNumber = IntegerField()
    OptionText = StringField()
    Command = SelectField(choices=MENUCOMMANDDICTIONARY.items(), coerce=int)
    Argument = StringField(default='')
    pword = StringField(default='')
    top_line = BooleanField(default=False)
    bottom_line = BooleanField(default=False)
    CopyType = SelectField(
        choices=[('', '----'), ('copy', 'Copy'), ('move', 'Move'), ],
        validators=[Optional()],
        validate_choice=False,
    )
    CopyTarget = StringField()
    Remove = BooleanField()

class MenuGroupForm(Form):
    id = HiddenField()
    GroupName = StringField()
    GroupInfo = StringField()

class MenuEditForm(FlaskForm):
    ### CHANGE ME??
    menu_group = FormField(MenuGroupForm)
    menu_items = FieldList(FormField(MenuItemForm), min_entries=20, max_entries=20)
    menu_name = StringField('Menu Name', validators=[DataRequired()])
    # submit = SubmitField('Save Menu')