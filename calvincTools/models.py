from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
from werkzeug.security import check_password_hash, generate_password_hash

from calvincTools.database import db
from calvincTools.mixins import _ModelInitMixin

# ============================================================================
# MENU SYSTEM MODELS
# ============================================================================

# deprecate?
class MenuCommand(_ModelInitMixin, db.Model):
    """
    Django equivalent: menuCommands
    """
    __tablename__ = 'menu_commands'
    
    command = db.Column(db.Integer, primary_key=True)
    command_text = db.Column(db.String(250), nullable=False)
    
    # Relationships
    menu_items = db.relationship('MenuItem', back_populates='command_obj', lazy='dynamic')
    
    def __repr__(self):
        return f'<MenuCommand {self.command} - {self.command_text}>'
    
    def __str__(self):
        return f'{self.command} - {self.command_text}'


class MenuGroup(_ModelInitMixin, db.Model):
    """
    Django equivalent: menuGroups
    """
    __tablename__ = 'menu_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    group_info = db.Column(db.String(250), default='')
    
    # Relationships
    menu_items = db.relationship('MenuItem', back_populates='menu_group', lazy='selectin')
    
    def __repr__(self):
        return f'<MenuGroup {self.id} - {self.group_name}>'
    
    def __str__(self):
        return f'menuGroup {self.group_name}'


class MenuItem(_ModelInitMixin, db.Model):
    """
    Django equivalent: menuItems
    """
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    menu_group_id = db.Column(db.Integer, db.ForeignKey('menu_groups.id', ondelete='RESTRICT'), nullable=True)
    menu_id = db.Column(db.SmallInteger, nullable=False)
    option_number = db.Column(db.SmallInteger, nullable=False)
    option_text = db.Column(db.String(250), nullable=False)
    command_id = db.Column(db.Integer, db.ForeignKey('menu_commands.command', ondelete='RESTRICT'), nullable=True)
    argument = db.Column(db.String(250), default='')
    pword = db.Column(db.String(250), default='')
    top_line = db.Column(db.Boolean, nullable=True)
    bottom_line = db.Column(db.Boolean, nullable=True)
    
    # Relationships
    menu_group = db.relationship('MenuGroup', back_populates='menu_items', lazy='joined')
    command_obj = db.relationship('MenuCommand', back_populates='menu_items')
    
    # Unique constraint (Django's UniqueConstraint)
    __table_args__ = (
        UniqueConstraint('menu_group_id', 'menu_id', 'option_number', 
                        name='uq_menu_group_menu_id_option_number'),
    )
    
    def __repr__(self):
        return f'<MenuItem {self.menu_group_id},{self.menu_id}/{self.option_number}>'
    
    def __str__(self):
        return f'{self.menu_group}, {self.menu_id}/{self.option_number}, {self.option_text}'


class cParameters(_ModelInitMixin, db.Model):
    """
    Django equivalent: cParameters
    """
    __tablename__ = 'parameters'
    
    parm_name: str = db.Column(db.String(100), primary_key=True)
    parm_value: str = db.Column(db.String(512), default='', nullable=False)
    user_modifiable: bool = db.Column(db.Boolean, default=True, nullable=False)
    comments: str = db.Column(db.String(512), default='', nullable=False)
    
    def __repr__(self):
        return f'<Parameter {self.parm_name}>'
    
    def __str__(self):
        return f'{self.parm_name} ({self.parm_value})'
    
    @classmethod
    def get_parameter(cls, parm_name: str, default: str = '') -> str:
        """
        Django equivalent: getcParm
        """
        param = cls.query.filter_by(parm_name=parm_name).first()
        return param.parm_value if param else default
    
    @classmethod
    def set_parameter(cls, parm_name: str, parm_value: str, user_modifiable: bool = True, comments: str = ''):
        """
        Django equivalent: setcParm
        """
        param = cls.query.filter_by(parm_name=parm_name).first()
        if param:
            param.parm_value = parm_value
        else:
            param = cls(
                parm_name=parm_name,
                parm_value=parm_value,
                user_modifiable=user_modifiable,
                comments=comments
            )
            db.session.add(param)
        
        db.session.commit()
        return param


class Greeting(_ModelInitMixin, db.Model):
    """
    Django equivalent: cGreetings
    """
    __tablename__ = 'greetings'
    
    id = db.Column(db.Integer, primary_key=True)
    greeting = db.Column(db.String(2000), nullable=False)
    
    def __repr__(self):
        return f'<Greeting {self.id}>'
    
    def __str__(self):
        return f'{self.greeting} (ID: {self.id})'


# from your_app import db


# ============================================================================
# USER MODEL
# ============================================================================

class User(UserMixin, db.Model):
    """
    User model for authentication. 
    Inherit from UserMixin to get default implementations for: 
    - is_authenticated
    - is_active
    - is_anonymous
    - get_id()
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False) # type: ignore
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)
    permissions = db.Column(db.String(1024), nullable=False)
    menugroup = db.Column(db.Integer, db.ForeignKey(MenuGroup.id), nullable=True)
    # menugroup = db.relationship('MenuGroup', backref='users', lazy='joined')
    date_joined = db.Column(db.DateTime, default=datetime.now, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.now()
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'

