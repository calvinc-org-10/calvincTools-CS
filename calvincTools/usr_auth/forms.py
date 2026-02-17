#pylint: disable=no-member
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, IntegerField, BooleanField, 
    DateField,
    SelectField, 
    HiddenField, SubmitField,
    )
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional
from wtforms import FieldList, FormField

# from calvincTools.models import User

class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField(
        'Username',
        validators=[DataRequired(message='Username is required')],
        render_kw={'class': 'form-control'}
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message='Password is required')],
        render_kw={'class': 'form-control'}
    )
    submit = SubmitField('Login', render_kw={'class': 'btn btn-primary'})


class UserForm(FlaskForm):
    """Form for viewing, editing, and adding users."""
    
    pk = HiddenField()  # Hidden field to store user ID for editing existing users
    
    username = StringField(
        'Username',
        validators=[
            # DataRequired(),
            Optional(),
            Length(min=3, max=80, message='Username must be between 3 and 80 characters')
        ],
        render_kw={'class': 'form-control'}
    )
    
    email = StringField(
        'Email',
        validators=[
            # DataRequired(),
            Optional(),
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

    menuGroup = IntegerField(
        'Menu Group',
        validators=[Optional()],
        render_kw={'class': 'form-control'}
    )
    
    date_joined = HiddenField(
        default=datetime.now().strftime('%Y-%m-%d'),
        render_kw={'class': 'form-control'}
    )
    # DateField(
    #     'Date Joined',
    #     format='%Y-%m-%d',
    #     default=datetime.now(),
    #     validators=[Optional()],
    #     render_kw={'class': 'form-control'}
    #     )
    
    last_login = HiddenField(
        default='',
        render_kw={'class': 'form-control'}
    )
    
    submit = SubmitField('Save User', render_kw={'class': 'btn btn-primary'})
    
    def validate_username(self, field):
        """Check if username already exists (excluding current user in edit mode)."""
        from calvincTools.models import User

        record_id_raw = self.pk.data
        record_id = None
        if record_id_raw not in (None, ''):
            try:
                record_id = int(record_id_raw)
            except (TypeError, ValueError):
                record_id = None

        if record_id is not None and not field.data:
            raise ValidationError('Username is required for existing users.')

        if record_id is None and field.data and not self.email.data:
            raise ValidationError('Email is required when username is provided.')

        if not field.data:
            return

        user = User.query.filter_by(username=field.data).first()
        if user and record_id is not None:
            try:
                if int(record_id) == user.id: # type: ignore
                    return
            except (TypeError, ValueError):
                pass

        if user:
            raise ValidationError('Username already exists.')
    
    def validate_email(self, field):
        """Check if email already exists (excluding current user in edit mode)."""
        from calvincTools.models import User

        record_id_raw = self.pk.data
        record_id = None
        if record_id_raw not in (None, ''):
            try:
                record_id = int(record_id_raw)
            except (TypeError, ValueError):
                record_id = None

        if record_id is not None and not field.data:
            raise ValidationError('Email is required for existing users.')

        if record_id is None and field.data and not self.username.data:
            raise ValidationError('Username is required when email is provided.')

        if not field.data:
            return

        user = User.query.filter_by(email=field.data).first()
        if user and record_id is not None:
            try:
                if int(record_id) == user.id: # type: ignore
                    return
            except (TypeError, ValueError):
                pass

        if user:
            raise ValidationError('Email already registered.')


class UserListForm(FlaskForm):
    """Form for managing multiple users."""
    users = FieldList(FormField(UserForm), min_entries=1)
    submit = SubmitField('Save All Users', render_kw={'class': 'btn btn-primary'})