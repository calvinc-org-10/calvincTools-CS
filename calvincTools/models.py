from typing import Any
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import (
    UniqueConstraint,
    inspect,
    )
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from .database import cMenu_db
from .mixins import _ModelInitMixin

from .cMenu import MENUCOMMAND
from .dbmenulist import initmenu_menulist

# ============================================================================
# MENU SYSTEM MODELS
# ============================================================================

# deprecate?
# class MenuCommand(_ModelInitMixin, cMenu_db.Model):
#     """
#     Django equivalent: menuCommands
#     """
#     __tablename__ = 'menu_commands'
    
#     command = cMenu_db.Column(cMenu_db.Integer, primary_key=True)
#     command_text = cMenu_db.Column(cMenu_db.String(250), nullable=False)
    
#     # Relationships
#     menu_items = cMenu_db.relationship('MenuItem', back_populates='command_obj', lazy='dynamic')
    
#     def __repr__(self):
#         return f'<MenuCommand {self.command} - {self.command_text}>'
    
#     def __str__(self):
#         return f'{self.command} - {self.command_text}'

class menuGroups(_ModelInitMixin, cMenu_db.Model):
    """
    Django equivalent: menuGroups
    """
    __tablename__ = 'cMenu_menuGroups'
    
    id = cMenu_db.Column(cMenu_db.Integer, primary_key=True)
    group_name = cMenu_db.Column(cMenu_db.String(100), unique=True, nullable=False, index=True)
    group_info = cMenu_db.Column(cMenu_db.String(250), default='')
    
    # Relationships
    menu_items = cMenu_db.relationship('MenuItem', back_populates='menu_group', lazy='selectin')
    
    def __repr__(self):
        return f'<MenuGroup {self.id} - {self.group_name}>'
    
    def __str__(self):
        return f'menuGroup {self.group_name}'

    @classmethod
    def _createtable(cls, flskapp):
        with flskapp.app_context():
            # Create tables if they don't exist
            cMenu_db.create_all()

            try:
                # Check if any group exists
                if not cMenu_db.session.query(cls).first():
                    # Add starter group
                    starter = cls(group_name="Group Name", group_info="Group Info")
                    cMenu_db.session.add(starter)
                    cMenu_db.session.commit()
                    # Add default menu items for the starter group
                    starter_id = starter.id
                    # TODO: use dbmenulist initmenu_menulist
                    menu_items = [
                        menuItems(
                            menu_group_id=starter_id, menu_id=0, option_number=0, 
                            option_text='New Menu', 
                            command_id=None, argument='Default', 
                            pword='', top_line=True, bottom_line=True
                            ),
                        menuItems(
                            menu_group_id=starter_id, menu_id=0, option_number=11, 
                            option_text='Edit Menu', 
                            command_id=MENUCOMMAND.EditMenu, argument='', 
                            pword='', top_line=None, bottom_line=None
                            ),
                        menuItems(
                            menu_group_id=starter_id, menu_id=0, option_number=19, 
                            option_text='Change Password', 
                            command_id=MENUCOMMAND.ChangePW, argument='', 
                            pword='', top_line=None, bottom_line=None
                            ),
                        menuItems(
                            menu_group_id=starter_id, menu_id=0, option_number=20, 
                            option_text='Go Away!', 
                            command_id=MENUCOMMAND.ExitApplication, argument='', 
                            pword='', top_line=None, bottom_line=None
                            ),
                        ]
                    cMenu_db.session.add_all(menu_items)
                    cMenu_db.session.commit()
                # endif no group exists
            except IntegrityError:
                cMenu_db.session.rollback()
            finally:
                cMenu_db.session.close()
            # end try
        # end with app_context
    # _createtable


class menuItems(_ModelInitMixin, cMenu_db.Model):
    """
    Django equivalent: menuItems
    """
    __tablename__ = 'cMenu_menuItems'
    
    id = cMenu_db.Column(cMenu_db.Integer, primary_key=True)
    menu_group_id = cMenu_db.Column(cMenu_db.Integer, cMenu_db.ForeignKey('cMenu_menuGroups.id', ondelete='RESTRICT'), nullable=True)
    menu_id = cMenu_db.Column(cMenu_db.SmallInteger, nullable=False)
    option_number = cMenu_db.Column(cMenu_db.SmallInteger, nullable=False)
    option_text = cMenu_db.Column(cMenu_db.String(250), nullable=False)
    command_id = cMenu_db.Column(cMenu_db.Integer, cMenu_db.ForeignKey('menu_commands.command', ondelete='RESTRICT'), nullable=True)
    argument = cMenu_db.Column(cMenu_db.String(250), default='')
    pword = cMenu_db.Column(cMenu_db.String(250), default='')
    top_line = cMenu_db.Column(cMenu_db.Boolean, nullable=True)
    bottom_line = cMenu_db.Column(cMenu_db.Boolean, nullable=True)
    
    # Relationships
    menu_group = cMenu_db.relationship('menuGroups', back_populates='menu_items', lazy='joined')
    command_obj = cMenu_db.relationship('MenuCommand', back_populates='menu_items')
    
    # Unique constraint (Django's UniqueConstraint)
    __table_args__ = (
        UniqueConstraint('menu_group_id', 'menu_id', 'option_number', 
                        name='uq_menu_group_menu_id_option_number'),
    )
    
    def __repr__(self):
        return f'<MenuItem {self.menu_group_id},{self.menu_id}/{self.option_number}>'
    
    def __str__(self):
        return f'{self.menu_group}, {self.menu_id}/{self.option_number}, {self.option_text}'

    def __init__(self, **kw: Any):
        """
        Initialize a new menuItems instance. If the menu table doesn't exist, it will be created.
        If the menuGroups table doesn't exist, it will also be created, and a starter group and menu will be added.
        :param kw: Keyword arguments for the menuItems instance.
        """
        inspector = inspect(cMenu_db.engine)
        if not inspector.has_table(self.__tablename__):
            # If the table does not exist, create it
            cMenu_db.create_all()
            # Optionally, you can also create a starter group and menu here
            # menuGroups._createtable()
        #endif not inspector.has_table():
        super().__init__(**kw)
    # __init__

class cParameters(_ModelInitMixin, cMenu_db.Model):
    """
    Django equivalent: cParameters
    """
    __tablename__ = 'cMenu_cParameters'
    
    parm_name: str = cMenu_db.Column(cMenu_db.String(100), primary_key=True)
    parm_value: str = cMenu_db.Column(cMenu_db.String(512), default='', nullable=False)
    user_modifiable: bool = cMenu_db.Column(cMenu_db.Boolean, default=True, nullable=False)
    comments: str = cMenu_db.Column(cMenu_db.String(512), default='', nullable=False)
    
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
            cMenu_db.session.add(param)
        
        cMenu_db.session.commit()
        return param


class cGreetings(_ModelInitMixin, cMenu_db.Model):
    """
    Django equivalent: cGreetings
    """
    __tablename__ = 'cMenu_cGreetings'
    
    id = cMenu_db.Column(cMenu_db.Integer, primary_key=True)
    greeting = cMenu_db.Column(cMenu_db.String(2000), nullable=False)
    
    def __repr__(self):
        return f'<Greeting {self.id}>'
    
    def __str__(self):
        return f'{self.greeting} (ID: {self.id})'


# from your_app import db


# ============================================================================
# USER MODEL
# ============================================================================

class User(UserMixin, cMenu_db.Model):
    """
    User model for authentication. 
    Inherit from UserMixin to get default implementations for: 
    - is_authenticated
    - is_active
    - is_anonymous
    - get_id()
    """
    __tablename__ = 'users'

    id = cMenu_db.Column(cMenu_db.Integer, primary_key=True)
    username = cMenu_db.Column(cMenu_db.String(80), unique=True, nullable=False, index=True)
    email = cMenu_db.Column(cMenu_db.String(120), unique=True, nullable=False, index=True)
    password_hash = cMenu_db.Column(cMenu_db.String(255), nullable=False)
    is_active = cMenu_db.Column(cMenu_db.Boolean, default=True, nullable=False) # type: ignore
    is_superuser = cMenu_db.Column(cMenu_db.Boolean, default=False, nullable=False)
    permissions = cMenu_db.Column(cMenu_db.String(1024), nullable=False)
    menugroup = cMenu_db.Column(cMenu_db.Integer, cMenu_db.ForeignKey(menuGroups.id), nullable=True)
    # menugroup = db.relationship('MenuGroup', backref='users', lazy='joined')
    date_joined = cMenu_db.Column(cMenu_db.DateTime, default=datetime.now, nullable=False)
    last_login = cMenu_db.Column(cMenu_db.DateTime, nullable=True)

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.now()
        cMenu_db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'

    def __init__(self, **kw: Any):
        """
        Initialize a user instance. If the user table doesn't exist, it will be created.
        """
        inspector = inspect(cMenu_db.engine)
        if not inspector.has_table(self.__tablename__):
            # If the table does not exist, create it
            cMenu_db.create_all()
        #endif not inspector.has_table():
        super().__init__(**kw)
    # __init__

def init_cDatabase(flskapp):
    """Create all tables in the database."""
    with flskapp.app_context():
        cMenu_db.create_all()
    # Ensure that the tables are created when the module is imported
    # nope, not when module imported. app context needed first
    menuGroups._createtable(flskapp)
    menuItems() #._createtable()
    cParameters() #._createtable()
    cGreetings() #._createtable()
    User() #._createtable()
# create_all_tables

