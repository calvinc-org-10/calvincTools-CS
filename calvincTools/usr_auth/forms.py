from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional
from wtforms import FieldList, FormField

from calvincTools.models import User

class UserForm(FlaskForm):
    """Form for viewing, editing, and adding users."""
    
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(min=3, max=80, message='Username must be between 3 and 80 characters')
        ],
        render_kw={'class': 'form-control'}
    )
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(message='Invalid email address'),
            Length(max=120)
        ],
        render_kw={'class': 'form-control'}
    )
    
    password = PasswordField(
        'Password',
        validators=[Optional(), Length(min=8, message='Password must be at least 8 characters')],
        render_kw={'class': 'form-control', 'placeholder': 'Leave blank to keep current password'}
    )
    
    FLDis_active = BooleanField(
        'Active',
        default=True,
        render_kw={'class': 'form-check-input'}
    )
    
    is_superuser = BooleanField(
        'Superuser',
        default=False,
        render_kw={'class': 'form-check-input'}
    )
    
    permissions = StringField(
        'Permissions',
        validators=[Optional(), Length(max=1024)],
        render_kw={'class': 'form-control', 'placeholder': 'Comma-separated permissions'}
    )
    
    submit = SubmitField('Save User', render_kw={'class': 'btn btn-primary'})
    
    def validate_username(self, field):
        """Check if username already exists (excluding current user in edit mode)."""
        from calvincTools.models import User

        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('Username already exists.')
    
    def validate_email(self, field):
        """Check if email already exists (excluding current user in edit mode)."""
        from calvincTools.models import User

        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError('Email already registered.')


class UserListForm(FlaskForm):
    """Form for managing multiple users."""
    users = FieldList(FormField(UserForm), min_entries=1)
    # add_user = SubmitField('Add User', render_kw={'class': 'btn btn-secondary'})
    submit = SubmitField('Save All Users', render_kw={'class': 'btn btn-primary'})