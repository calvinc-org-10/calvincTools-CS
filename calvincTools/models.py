from typing import Any
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import (
    UniqueConstraint,
    inspect,
    )
from sqlalchemy.orm import (
    declarative_base,
    Mapped, mapped_column,
    )
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.local import LocalProxy

from .mixins import _ModelInitMixin

from .cMenu import MENUCOMMAND
from .dbmenulist import initmenu_menulist

# Module-level db reference - will be set by init_cDatabase
# Using a dictionary to hold the actual db so we can update it
_db_holder = {'db': None}

def get_db():
    """Get the current db instance."""
    return _db_holder['db']

# Create a LocalProxy that will always point to the current db
db = LocalProxy(get_db)

SkeletonModelBase = declarative_base()

# ============================================================================
# MENU SYSTEM MODELS
# ============================================================================

class menuGroups(_ModelInitMixin, SkeletonModelBase):
    """
    Django equivalent: menuGroups
    
    Note: This class will be dynamically converted to a proper db.Model
    by init_cDatabase. Import this class normally in your code.
    """
    __bind_key__ = 'cToolsdb'
    __tablename__ = 'cMenu_menuGroups'
    
    #######################################
    ##  except for __bind_key__ and __tablename__, only method stubs and properties
    ##  necassary for other code to compile are defined here. 
    ##  The actual columns will be added dynamically.
    #######################################
    id: Mapped[int] = mapped_column(primary_key=True)

    def __repr__(self):     # pyright: ignore[reportIncompatibleMethodOverride]
        ...
    
    def __str__(self):     # pyright: ignore[reportIncompatibleMethodOverride]
        ...

    @classmethod
    def createtable(cls, flskapp):      # pylint: disable=unused-argument
        """Create the table and populate with initial data if empty."""
        ...         # pylint: disable=unnecessary-ellipsis

class menuItems(_ModelInitMixin, SkeletonModelBase):
    """
    Django equivalent: menuItems
    
    Note: This class will be dynamically converted to a proper db.Model
    by init_cDatabase. Import this class normally in your code.
    """
    __bind_key__ = 'cToolsdb'
    __tablename__ = 'cMenu_menuItems'
    
    #######################################
    ##  except for __bind_key__ and __tablename__, only method stubs and properties
    ##  necassary for other code to compile are defined here. 
    ##  The actual columns will be added dynamically.
    #######################################
    id: Mapped[int] = mapped_column(primary_key=True)

    def __repr__(self):         # pyright: ignore[reportIncompatibleMethodOverride]
        ...
    
    def __str__(self):      # pyright: ignore[reportIncompatibleMethodOverride]
        ...

    def __init__(self, **kw: Any):      # pylint: disable=unused-argument, super-init-not-called
        """
        Initialize a new menuItems instance. If the menu table doesn't exist, it will be created.
        """
        ...     # pylint: disable=unnecessary-ellipsis


class cParameters(_ModelInitMixin, SkeletonModelBase):
    """
    Django equivalent: cParameters
    
    Note: This class will be dynamically converted to a proper db.Model
    by init_cDatabase. Import this class normally in your code.
    """
    __bind_key__ = 'cToolsdb'
    __tablename__ = 'cMenu_cParameters'
    
    #######################################
    ##  except for __bind_key__ and __tablename__, only method stubs and properties
    ##  necassary for other code to compile are defined here. 
    ##  The actual columns will be added dynamically.
    #######################################
    id: Mapped[int] = mapped_column(primary_key=True)

    def __repr__(self):     # pyright: ignore[reportIncompatibleMethodOverride]
        ...
    
    def __str__(self):      # pyright: ignore[reportIncompatibleMethodOverride]
        ...
    
    @classmethod
    def get_parameter(cls, parm_name: str, default: str = '') -> str:
        """Django equivalent: getcParm"""
        ...
    
    @classmethod
    def set_parameter(cls, parm_name: str, parm_value: str, user_modifiable: bool = True, comments: str = ''):
        """Django equivalent: setcParm"""
        ...


class cGreetings(_ModelInitMixin, SkeletonModelBase):
    """
    Django equivalent: cGreetings
    
    Note: This class will be dynamically converted to a proper db.Model
    by init_cDatabase. Import this class normally in your code.
    """
    __bind_key__ = 'cToolsdb'
    __tablename__ = 'cMenu_cGreetings'
    
    #######################################
    ##  except for __bind_key__ and __tablename__, only method stubs and properties
    ##  necassary for other code to compile are defined here. 
    ##  The actual columns will be added dynamically.
    #######################################
    id: Mapped[int] = mapped_column(primary_key=True)

    def __repr__(self):     # pyright: ignore[reportIncompatibleMethodOverride]
        ...
    
    def __str__(self):          # pyright: ignore[reportIncompatibleMethodOverride]
        ...


# ============================================================================
# USER MODEL
# ============================================================================

class User(UserMixin, SkeletonModelBase):
    """
    User model for authentication. 
    Inherit from UserMixin to get default implementations for: 
    - is_authenticated
    - is_active
    - is_anonymous
    - get_id()
    
    Note: This class will be dynamically converted to a proper db.Model
    by init_cDatabase. Import this class normally in your code.
    """
    __bind_key__ = 'cToolsdb'
    __tablename__ = 'users'
    
    #######################################
    ##  except for __bind_key__ and __tablename__, only method stubs and properties
    ##  necassary for other code to compile are defined here. 
    ##  The actual columns will be added dynamically.
    #######################################
    id: Mapped[int] = mapped_column(primary_key=True)

    def set_password(self, password):
        """Hash and set the user's password."""
        ...

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        ...

    def update_last_login(self):
        """Update the last login timestamp."""
        ...

    def __repr__(self):     # pyright: ignore[reportIncompatibleMethodOverride]
        ...

    def __init__(self, **kw: Any):
        """Initialize a user instance. If the user table doesn't exist, it will be created."""
        ...


# ============================================================================
# INITIALIZATION FUNCTION
# ============================================================================

def init_cDatabase(flskapp, db_instance):
    """
    Initialize the database models with the Flask app and SQLAlchemy instance.
    This function configures the model classes to inherit from db.Model and adds columns.
    
    After calling this function, the model classes (menuGroups, menuItems, cParameters,
    cGreetings, User) will be fully functional SQLAlchemy models that can be imported
    and used anywhere in the application.
    
    Args:
        flskapp: The Flask application instance
        db_instance: The SQLAlchemy instance
        
    Returns:
        tuple: (menuGroups, menuItems, cParameters, cGreetings, User) - The initialized model classes
    """
    # Set the db reference so the LocalProxy works
    _db_holder['db'] = db_instance
    
    # Get reference to current module to update the classes
    import sys
    current_module = sys.modules[__name__]
    
    # Create enhanced model classes that inherit from db.Model
    # These will replace the placeholder classes defined above
    
    class menuGroups(_ModelInitMixin, db_instance.Model):
        """Menu groups model with database columns."""
        __bind_key__ = 'cToolsdb'
        __tablename__ = 'cMenu_menuGroups'
        
        id = db_instance.Column(db_instance.Integer, primary_key=True)
        GroupName = db_instance.Column(db_instance.String(100), unique=True, nullable=False, index=True)
        GroupInfo = db_instance.Column(db_instance.String(250), default='')
        
        # Relationships
        menu_items = db_instance.relationship('menuItems', back_populates='menu_group', lazy='selectin')
        
        def __repr__(self):
            return f'<MenuGroup {self.id} - {self.GroupName}>'
        
        def __str__(self):
            return f'menuGroup {self.GroupName}'

        @classmethod
        def createtable(cls, flskapp):
            """Create the table and populate with initial data if empty."""
            with flskapp.app_context():
                # Create tables if they don't exist
                db_instance.create_all()

                try:
                    # Check if any group exists
                    if not db_instance.session.query(cls).first():
                        # Add starter group
                        starter = cls(GroupName="Group Name", GroupInfo="Group Info")
                        db_instance.session.add(starter)
                        db_instance.session.commit()
                        # Add default menu items for the starter group
                        starter_id = starter.id
                        # Get the menuItems class from module
                        menuItems_cls = getattr(current_module, 'menuItems')
                        # TODO: use dbmenulist initmenu_menulist
                        menu_items = [
                            menuItems_cls(
                                MenuGroup_id=starter_id, MenuID=0, OptionNumber=0, 
                                OptionText='New Menu', 
                                Command=None, Argument='Default', 
                                pword='', top_line=True, bottom_line=True
                                ),
                            menuItems_cls(
                                MenuGroup_id=starter_id, MenuID=0, OptionNumber=11, 
                                OptionText='Edit Menu', 
                                Command=MENUCOMMAND.EditMenu, Argument='', 
                                pword='', top_line=None, bottom_line=None
                                ),
                            menuItems_cls(
                                MenuGroup_id=starter_id, MenuID=0, OptionNumber=19, 
                                OptionText='Change Password', 
                                Command=MENUCOMMAND.ChangePW, Argument='', 
                                pword='', top_line=None, bottom_line=None
                                ),
                            menuItems_cls(
                                MenuGroup_id=starter_id, MenuID=0, OptionNumber=20, 
                                OptionText='Go Away!', 
                                Command=MENUCOMMAND.ExitApplication, Argument='', 
                                pword='', top_line=None, bottom_line=None
                                ),
                            ]
                        db_instance.session.add_all(menu_items)
                        db_instance.session.commit()
                    # endif no group exists
                except IntegrityError:
                    db_instance.session.rollback()
                finally:
                    db_instance.session.close()
                # end try

    class menuItems(_ModelInitMixin, db_instance.Model):
        """Menu items model with database columns."""
        __bind_key__ = 'cToolsdb'
        __tablename__ = 'cMenu_menuItems'
        
        id = db_instance.Column(db_instance.Integer, primary_key=True)
        MenuGroup_id = db_instance.Column(db_instance.Integer, db_instance.ForeignKey('cMenu_menuGroups.id', ondelete='RESTRICT'), nullable=True)
        MenuID = db_instance.Column(db_instance.SmallInteger, nullable=False)
        OptionNumber = db_instance.Column(db_instance.SmallInteger, nullable=False)
        OptionText = db_instance.Column(db_instance.String(250), nullable=False)
        Command = db_instance.Column(db_instance.Integer, nullable=True)
        Argument = db_instance.Column(db_instance.String(250), default='')
        pword = db_instance.Column(db_instance.String(250), default='')
        top_line = db_instance.Column(db_instance.Boolean, nullable=True)
        bottom_line = db_instance.Column(db_instance.Boolean, nullable=True)
        
        # Relationships
        menu_group = db_instance.relationship('menuGroups', back_populates='menu_items', lazy='joined')
        
        # Unique constraint
        __table_args__ = (
            UniqueConstraint('MenuGroup_id', 'MenuID', 'OptionNumber', 
                            name='uq_menu_group_MenuID_OptionNumber'),
        )
        
        def __repr__(self):
            return f'<MenuItem {self.MenuGroup_id},{self.MenuID}/{self.OptionNumber}>'
        
        def __str__(self):
            return f'{self.menu_group}, {self.MenuID}/{self.OptionNumber}, {self.OptionText}'

        def __init__(self, **kw: Any):
            """Initialize a new menuItems instance."""
            inspector = inspect(db_instance.engine)
            if not inspector.has_table(self.__tablename__):
                # If the table does not exist, create it
                db_instance.create_all()
            super().__init__(**kw)

    class cParameters(_ModelInitMixin, db_instance.Model):
        """Parameters model with database columns."""
        __bind_key__ = 'cToolsdb'
        __tablename__ = 'cMenu_cParameters'
        
        parm_name: str = db_instance.Column(db_instance.String(100), primary_key=True)
        parm_value: str = db_instance.Column(db_instance.String(512), default='', nullable=False)
        user_modifiable: bool = db_instance.Column(db_instance.Boolean, default=True, nullable=False)
        comments: str = db_instance.Column(db_instance.String(512), default='', nullable=False)
        
        def __repr__(self):
            return f'<Parameter {self.parm_name}>'
        
        def __str__(self):
            return f'{self.parm_name} ({self.parm_value})'
        
        @classmethod
        def get_parameter(cls, parm_name: str, default: str = '') -> str:
            """Django equivalent: getcParm"""
            param = cls.query.filter_by(parm_name=parm_name).first()
            return param.parm_value if param else default
        
        @classmethod
        def set_parameter(cls, parm_name: str, parm_value: str, user_modifiable: bool = True, comments: str = ''):
            """Django equivalent: setcParm"""
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
                db_instance.session.add(param)
            
            db_instance.session.commit()
            return param

    class cGreetings(_ModelInitMixin, db_instance.Model):
        """Greetings model with database columns."""
        __bind_key__ = 'cToolsdb'
        __tablename__ = 'cMenu_cGreetings'
        
        id = db_instance.Column(db_instance.Integer, primary_key=True)
        greeting = db_instance.Column(db_instance.String(2000), nullable=False)
        
        def __repr__(self):
            return f'<Greeting {self.id}>'
        
        def __str__(self):
            return f'{self.greeting} (ID: {self.id})'

    class User(UserMixin, db_instance.Model):
        """
        User model for authentication with database columns.
        Inherit from UserMixin to get default implementations for:
        - is_authenticated, is_active, is_anonymous, get_id()
        """
        __bind_key__ = 'cToolsdb'
        __tablename__ = 'users'

        id = db_instance.Column(db_instance.Integer, primary_key=True)
        username = db_instance.Column(db_instance.String(80), unique=True, nullable=False, index=True)
        email = db_instance.Column(db_instance.String(120), unique=True, nullable=False, index=True)
        password_hash = db_instance.Column(db_instance.String(255), nullable=False)
        is_active = db_instance.Column(db_instance.Boolean, default=True, nullable=False)
        is_superuser = db_instance.Column(db_instance.Boolean, default=False, nullable=False)
        permissions = db_instance.Column(db_instance.String(1024), nullable=False, default='')
        menuGroup = db_instance.Column(db_instance.Integer, db_instance.ForeignKey(menuGroups.id), nullable=True)
        date_joined = db_instance.Column(db_instance.DateTime, default=datetime.now, nullable=False)
        last_login = db_instance.Column(db_instance.DateTime, nullable=True)

        @property
        def is_active(self):
            return self.is_active
        
        def set_password(self, password):
            """Hash and set the user's password."""
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            """Check if the provided password matches the hash."""
            return check_password_hash(self.password_hash, password)

        def update_last_login(self):
            """Update the last login timestamp."""
            self.last_login = datetime.now()
            db_instance.session.commit()

        def __repr__(self):
            return f'<User {self.username}>'

        def __init__(self, **kw: Any):
            """Initialize a user instance."""
            inspector = inspect(db_instance.engine)
            if not inspector.has_table(self.__tablename__):
                # If the table does not exist, create it
                db_instance.create_all()
            super().__init__(**kw)

    # Update the module-level references so imports work
    setattr(current_module, 'menuGroups', menuGroups)
    setattr(current_module, 'menuItems', menuItems)
    setattr(current_module, 'cParameters', cParameters)
    setattr(current_module, 'cGreetings', cGreetings)
    setattr(current_module, 'User', User)
    
    # Create all tables in the database
    with flskapp.app_context():
        db_instance.create_all(bind_key='cToolsdb')
        # Initialize tables with default data
        menuGroups.createtable(flskapp)
        menuItems()
        cParameters()
        cGreetings()
        User()
    
    return menuGroups, menuItems, cParameters, cGreetings, User
