from dataclasses import dataclass

from flask_wtf import FlaskForm
from wtforms import (
    Form, 
    StringField, TextAreaField, 
    IntegerField, HiddenField, BooleanField,
    SelectField, RadioField,
    SubmitField, 
    FormField, FieldList, 
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

class cParameterItemForm(Form):
    parm_name = StringField()
    parm_value = StringField(default='')
    user_modifiable = HiddenField(default='1')
    comments = StringField(default='')

    Remove = BooleanField(default=False)
        
class cParameterEditForm(FlaskForm):
    parameters = FieldList(FormField(cParameterItemForm), min_entries=1)

class cParameterItemForm_SU(Form):
    parm_name = StringField()
    parm_value = StringField(default='')
    user_modifiable = BooleanField(default=True)
    comments = StringField(default='')

    Remove = BooleanField(default=False)
        
class cParameterEditForm_SU(FlaskForm):
    parameters = FieldList(FormField(cParameterItemForm_SU), min_entries=1)

class cGreetingsItemForm(Form):
    pk = HiddenField()      # don't want to clash with the id attribute in Form
    greeting = TextAreaField()

    Remove = BooleanField(default=False)
        
class cGreetingsEditForm(FlaskForm):
    greetings = FieldList(FormField(cGreetingsItemForm), min_entries=1)

