
from typing import Any
from datetime import datetime

from sqlalchemy.orm import declarative_base
from flask_login import UserMixin
from sqlalchemy import (
    UniqueConstraint,
    inspect,
    )
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from .mixins import _ModelInitMixin

from .cMenu import MENUCOMMAND
from .dbmenulist import initmenu_menulist

# ============================================================================
# MENU SYSTEM MODELS
# ============================================================================

# This does not need 'db' yet
cToolsdbBase = declarative_base()

class menuGroups(_ModelInitMixin, cToolsdbBase):
    """
    Django equivalent: menuGroups
    """
    __bind_key__ = 'cToolsdb'
    __tablename__ = 'cMenu_menuGroups'
    
    id = Column(Integer, primary_key=True)
    GroupName = Column(String(100), unique=True, nullable=False, index=True)
    GroupInfo = Column(String(250), default='')
    
    # Relationships
    menu_items = relationship('menuItems', back_populates='menu_group', lazy='selectin')
    
    def __repr__(self):
        return f'<MenuGroup {self.id} - {self.GroupName}>'
    
    def __str__(self):
        return f'menuGroup {self.GroupName}'

    @classmethod
    def createtable(cls, flskapp):
        with flskapp.app_context():
            # Create tables if they don't exist
            cToolsdbBase.create_all()

            try:
                # Check if any group exists
                if not cToolsdbBase.session.query(cls).first():
                    # Add starter group
                    starter = cls(GroupName="Group Name", GroupInfo="Group Info")
                    cToolsdbBase.session.add(starter)
                    cToolsdbBase.session.commit()
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
                    cToolsdbBase.session.add_all(menu_items)
                    cToolsdbBase.session.commit()
                # endif no group exists
            except IntegrityError:
                cToolsdbBase.session.rollback()
            finally:
                cToolsdbBase.session.close()
            # end try
        # end with app_context
    # _createtable


class menuItems(_ModelInitMixin, cToolsdbBase): # type: ignore
    """
    Django equivalent: menuItems
    """
    __bind_key__ = 'cToolsdb'
    __tablename__ = 'cMenu_menuItems'
    
    id = Column(Integer, primary_key=True)
    MenuGroup_id = Column(Integer, ForeignKey('cMenu_menuGroups.id', ondelete='RESTRICT'), nullable=True)
    MenuID = Column(SmallInteger, nullable=False)
    OptionNumber = Column(SmallInteger, nullable=False)
    OptionText = Column(String(250), nullable=False)
    Command = Column(Integer, nullable=True)
    Argument = Column(String(250), default='')
    pword = Column(String(250), default='')
    top_line = Column(Boolean, nullable=True)
    bottom_line = Column(Boolean, nullable=True)
    
    # Relationships
    menu_group = relationship('menuGroups', back_populates='menu_items', lazy='joined')
    
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
        inspector = inspect(cToolsdbBase.engine)
        if not inspector.has_table(self.__tablename__):
            # If the table does not exist, create it
            cToolsdbBase.create_all()
            # Optionally, you can also create a starter group and menu here
            # menuGroups._createtable()
        #endif not inspector.has_table():
        super().__init__(**kw)
    # __init__

class cParameters(_ModelInitMixin, cToolsdbBase): # type: ignore
    """
    Django equivalent: cParameters
    """
    __bind_key__ = 'cToolsdb'
    __tablename__ = 'cMenu_cParameters'
    
    parm_name: str = Column(String(100), primary_key=True)
    parm_value: str = Column(String(512), default='', nullable=False)
    user_modifiable: bool = Column(Boolean, default=True, nullable=False)
    comments: str = Column(String(512), default='', nullable=False)
    
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
            cToolsdbBase.session.add(param)
        
        cToolsdbBase.session.commit()
        return param


class cGreetings(_ModelInitMixin, cToolsdbBase): # type: ignore
    """
    Django equivalent: cGreetings
    """
    __bind_key__ = 'cToolsdb'
    __tablename__ = 'cMenu_cGreetings'
    
    id = Column(Integer, primary_key=True)
    greeting = Column(String(2000), nullable=False)
    
    def __repr__(self):
        return f'<Greeting {self.id}>'
    
    def __str__(self):
        return f'{self.greeting} (ID: {self.id})'


# from your_app import db


# ============================================================================
# USER MODEL
# ============================================================================

class User(UserMixin, cToolsdbBase): # type: ignore
    """
    User model for authentication. 
    Inherit from UserMixin to get default implementations for: 
    - is_authenticated
    - is_active
    - is_anonymous
    - get_id()
    """
    __bind_key__ = 'cToolsdb'
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False) # type: ignore
    is_superuser = Column(Boolean, default=False, nullable=False)
    permissions = Column(String(1024), nullable=False, default='')
    menuGroup = Column(Integer, ForeignKey(menuGroups.id), nullable=True)
    # menugroup = db.relationship('MenuGroup', backref='users', lazy='joined')
    date_joined = Column(DateTime, default=datetime.now, nullable=False)
    last_login = Column(DateTime, nullable=True)

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.now()
        cToolsdbBase.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'

    def __init__(self, **kw: Any):
        """
        Initialize a user instance. If the user table doesn't exist, it will be created.
        """
        inspector = inspect(cToolsdbBase.engine)
        if not inspector.has_table(self.__tablename__):
            # If the table does not exist, create it
            cToolsdbBase.create_all()
        #endif not inspector.has_table():
        super().__init__(**kw)
    # __init__

def init_cDatabase(flskapp):
    """Create all tables in the database."""
    with flskapp.app_context():
        cToolsdbBase.create_all(bind_key='cToolsdb')
        # Ensure that the tables are created when the module is imported
        # nope, not when module imported. app context needed first
        menuGroups.createtable(flskapp)
        menuItems() #._createtable()
        cParameters() #._createtable()
        cGreetings() #._createtable()
        User() #._createtable()
# create_all_tables

