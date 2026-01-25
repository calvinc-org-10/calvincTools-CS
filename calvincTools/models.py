from typing import Any
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import (
    UniqueConstraint,
    inspect,
    )
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from .database import cTools_db
from .mixins import _ModelInitMixin

from .cMenu import MENUCOMMAND
from .dbmenulist import initmenu_menulist

# ============================================================================
# MENU SYSTEM MODELS
# ============================================================================


class menuGroups(_ModelInitMixin, cTools_db.Model):
    """
    Django equivalent: menuGroups
    """
    __tablename__ = 'cMenu_menuGroups'
    
    id = cTools_db.Column(cTools_db.Integer, primary_key=True)
    GroupName = cTools_db.Column(cTools_db.String(100), unique=True, nullable=False, index=True)
    GroupInfo = cTools_db.Column(cTools_db.String(250), default='')
    
    # Relationships
    menu_items = cTools_db.relationship('menuItems', back_populates='menu_group', lazy='selectin')
    
    def __repr__(self):
        return f'<MenuGroup {self.id} - {self.GroupName}>'
    
    def __str__(self):
        return f'menuGroup {self.GroupName}'

    @classmethod
    def _createtable(cls, flskapp):
        with flskapp.app_context():
            # Create tables if they don't exist
            cTools_db.create_all()

            try:
                # Check if any group exists
                if not cTools_db.session.query(cls).first():
                    # Add starter group
                    starter = cls(GroupName="Group Name", GroupInfo="Group Info")
                    cTools_db.session.add(starter)
                    cTools_db.session.commit()
                    # Add default menu items for the starter group
                    starter_id = starter.id
                    # TODO: use dbmenulist initmenu_menulist
                    menu_items = [
                        menuItems(
                            MenuGroup_id=starter_id, MenuID=0, OptionNumber=0, 
                            OptionText='New Menu', 
                            Command=None, Argument='Default', 
                            pword='', top_line=True, bottom_line=True
                            ),
                        menuItems(
                            MenuGroup_id=starter_id, MenuID=0, OptionNumber=11, 
                            OptionText='Edit Menu', 
                            Command=MENUCOMMAND.EditMenu, Argument='', 
                            pword='', top_line=None, bottom_line=None
                            ),
                        menuItems(
                            MenuGroup_id=starter_id, MenuID=0, OptionNumber=19, 
                            OptionText='Change Password', 
                            Command=MENUCOMMAND.ChangePW, Argument='', 
                            pword='', top_line=None, bottom_line=None
                            ),
                        menuItems(
                            MenuGroup_id=starter_id, MenuID=0, OptionNumber=20, 
                            OptionText='Go Away!', 
                            Command=MENUCOMMAND.ExitApplication, Argument='', 
                            pword='', top_line=None, bottom_line=None
                            ),
                        ]
                    cTools_db.session.add_all(menu_items)
                    cTools_db.session.commit()
                # endif no group exists
            except IntegrityError:
                cTools_db.session.rollback()
            finally:
                cTools_db.session.close()
            # end try
        # end with app_context
    # _createtable


class menuItems(_ModelInitMixin, cTools_db.Model):
    """
    Django equivalent: menuItems
    """
    __tablename__ = 'cMenu_menuItems'
    
    id = cTools_db.Column(cTools_db.Integer, primary_key=True)
    MenuGroup_id = cTools_db.Column(cTools_db.Integer, cTools_db.ForeignKey('cMenu_menuGroups.id', ondelete='RESTRICT'), nullable=True)
    MenuID = cTools_db.Column(cTools_db.SmallInteger, nullable=False)
    OptionNumber = cTools_db.Column(cTools_db.SmallInteger, nullable=False)
    OptionText = cTools_db.Column(cTools_db.String(250), nullable=False)
    Command = cTools_db.Column(cTools_db.Integer, nullable=True)
    Argument = cTools_db.Column(cTools_db.String(250), default='')
    pword = cTools_db.Column(cTools_db.String(250), default='')
    top_line = cTools_db.Column(cTools_db.Boolean, nullable=True)
    bottom_line = cTools_db.Column(cTools_db.Boolean, nullable=True)
    
    # Relationships
    menu_group = cTools_db.relationship('menuGroups', back_populates='menu_items', lazy='joined')
    
    # Unique constraint (Django's UniqueConstraint)
    __table_args__ = (
        UniqueConstraint('MenuGroup_id', 'MenuID', 'OptionNumber', 
                        name='uq_menu_group_MenuID_OptionNumber'),
    )
    
    def __repr__(self):
        return f'<MenuItem {self.MenuGroup_id},{self.MenuID}/{self.OptionNumber}>'
    
    def __str__(self):
        return f'{self.menu_group}, {self.MenuID}/{self.OptionNumber}, {self.OptionText}'

    def __init__(self, **kw: Any):
        """
        Initialize a new menuItems instance. If the menu table doesn't exist, it will be created.
        If the menuGroups table doesn't exist, it will also be created, and a starter group and menu will be added.
        :param kw: Keyword arguments for the menuItems instance.
        """
        inspector = inspect(cTools_db.engine)
        if not inspector.has_table(self.__tablename__):
            # If the table does not exist, create it
            cTools_db.create_all()
            # Optionally, you can also create a starter group and menu here
            # menuGroups._createtable()
        #endif not inspector.has_table():
        super().__init__(**kw)
    # __init__

class cParameters(_ModelInitMixin, cTools_db.Model):
    """
    Django equivalent: cParameters
    """
    __tablename__ = 'cMenu_cParameters'
    
    parm_name: str = cTools_db.Column(cTools_db.String(100), primary_key=True)
    parm_value: str = cTools_db.Column(cTools_db.String(512), default='', nullable=False)
    user_modifiable: bool = cTools_db.Column(cTools_db.Boolean, default=True, nullable=False)
    comments: str = cTools_db.Column(cTools_db.String(512), default='', nullable=False)
    
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
            cTools_db.session.add(param)
        
        cTools_db.session.commit()
        return param


class cGreetings(_ModelInitMixin, cTools_db.Model):
    """
    Django equivalent: cGreetings
    """
    __tablename__ = 'cMenu_cGreetings'
    
    id = cTools_db.Column(cTools_db.Integer, primary_key=True)
    greeting = cTools_db.Column(cTools_db.String(2000), nullable=False)
    
    def __repr__(self):
        return f'<Greeting {self.id}>'
    
    def __str__(self):
        return f'{self.greeting} (ID: {self.id})'


# from your_app import db


# ============================================================================
# USER MODEL
# ============================================================================

class User(UserMixin, cTools_db.Model):
    """
    User model for authentication. 
    Inherit from UserMixin to get default implementations for: 
    - is_authenticated
    - is_active
    - is_anonymous
    - get_id()
    """
    __tablename__ = 'users'

    id = cTools_db.Column(cTools_db.Integer, primary_key=True)
    username = cTools_db.Column(cTools_db.String(80), unique=True, nullable=False, index=True)
    email = cTools_db.Column(cTools_db.String(120), unique=True, nullable=False, index=True)
    password_hash = cTools_db.Column(cTools_db.String(255), nullable=False)
    is_active = cTools_db.Column(cTools_db.Boolean, default=True, nullable=False) # type: ignore
    is_superuser = cTools_db.Column(cTools_db.Boolean, default=False, nullable=False)
    permissions = cTools_db.Column(cTools_db.String(1024), nullable=False, default='')
    menuGroup = cTools_db.Column(cTools_db.Integer, cTools_db.ForeignKey(menuGroups.id), nullable=True)
    # menugroup = db.relationship('MenuGroup', backref='users', lazy='joined')
    date_joined = cTools_db.Column(cTools_db.DateTime, default=datetime.now, nullable=False)
    last_login = cTools_db.Column(cTools_db.DateTime, nullable=True)

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.now()
        cTools_db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'

    def __init__(self, **kw: Any):
        """
        Initialize a user instance. If the user table doesn't exist, it will be created.
        """
        inspector = inspect(cTools_db.engine)
        if not inspector.has_table(self.__tablename__):
            # If the table does not exist, create it
            cTools_db.create_all()
        #endif not inspector.has_table():
        super().__init__(**kw)
    # __init__

def init_cDatabase(flskapp):
    """Create all tables in the database."""
    with flskapp.app_context():
        cTools_db.create_all()
        # Ensure that the tables are created when the module is imported
        # nope, not when module imported. app context needed first
        menuGroups._createtable(flskapp)
        menuItems() #._createtable()
        cParameters() #._createtable()
        cGreetings() #._createtable()
        User() #._createtable()
# create_all_tables

