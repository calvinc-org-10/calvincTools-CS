"""
calvincTools - A Python package
"""
# Import main modules here as needed
# from .module import function

from flask import Flask, render_template, redirect, url_for, session
# from flask_migrate import Migrate
from sqlalchemy.orm import sessionmaker

from ..usr_auth.views import init_login_manager
from ..blueprints import ctools_bp
from ..usr_auth.routes import register_auth_blueprint
from ..cMenu.routes import register_menu_blueprint
from ..utils.routes import register_util_blueprint

from ..utils.Jinja2Tools import checkTemplate_and_render

from ..CallerContext import CallerContext

class calvincTools(object):
    """
    A Singleton class to hold application-specific hooks and resources
    for the calvinctools toolkit, such as database sessionmakers.

    This acts as a Service Locator for external (and some internal) dependencies.
    """
    cTools_tables = (None, None, None, None, None)   # will be set by init_cDatabase
    
    _instance = None
    _initialized = False  # Track if initialization has occurred
    
    _usr_auth = None            # is the usr_auth module being used, or is there no logging in?
    _main_window_stack = None   # reference to the main window's QStackedWidget, for use in navigation between "main" forms (cMenu, FormLogin) 
    _login_form = None          # reference to the login form, for use in logout functionality (to return to login form after logout)
    _menu_form = None           # reference to the menu form, for use in logout functionality (to reset menu form to default state on logout)
    
    _app_sessionmaker = None
    _appver = ''
    _FormNameToURL_Map = {}
    _ExternalWebPageURL_Map = {}
    _appname='Application'
    _logo=None
    _MUSTBEINITIALIZED: set = {
        'app_db',
        'app_sessionmaker',
        'FormNameToURL_Map', 
        'ExternalWebPageURL_Map',
        }
    
    def __new__(cls, *args, **kwargs):
        # Implement the Singleton pattern: always return the same instance
        if cls._instance is None:
            cls._instance = super(calvincTools, cls).__new__(cls)
            # Initialize QObject parent class
            super(calvincTools, cls._instance).__init__()
        return cls._instance

    def __init__(self, 
        caller_context:CallerContext,
        ):
        """
        Initialize the singleton with all required hooks.
        This only runs once, on first instantiation. Subsequent calls are ignored.
        """
        # Only initialize once - use simple flag to avoid recursion
        if self.__class__._initialized:
            return

        from flask_sqlalchemy import SQLAlchemy
        
        self._caller_context = caller_context
        app = caller_context.flaskapp
        app_db:SQLAlchemy = caller_context.app_db
        app_config = caller_context.config
        cTools_bind_key = caller_context.cTools_bind_key
        cTools_tablenames = caller_context.cTools_tablenames
        cTools_models = caller_context.cTools_models
        
        # 1. configs should be already set by the user
        #    later, we will be procs to add/modify configs
        #    db configs MUST be set before app_db.init_app, but app_db.init_app MUST precede init_cDatabase here

        # Set provided values, or keep class defaults
        if app_db is not None:
            self._app_db = app_db
            self._app_sessionmaker = sessionmaker(bind=app_db.engine)
        self._FormNameToURL_Map = getattr(app_config,'FORMNAME_TO_URL_MAP', {})
        self._ExternalWebPageURL_Map = getattr(app_config,'EXTERNAL_WEBPAGE_URL_MAP', {})
        self._appver = getattr(app_config,'APP_VERSION', '')
        self._appname = getattr(app_config, 'APP_NAME', 'Application')
        self._logo = getattr(app_config, 'APP_LOGO', None)
        
        # Mark as initialized and validate required fields were set
        self.__class__._initialized = True
        
        # Now validate that all required fields are properly initialized
        if not self.__class__.is_properly_initialized():
            # Reset initialization flag so they can try again
            self.__class__._initialized = False
            missing = [attr for attr in self._MUSTBEINITIALIZED 
                      if getattr(self, f'_{attr}', None) is None]
            raise RuntimeError(
                f"calvincTools initialization incomplete. Missing required fields: {missing}. "
                f"Please provide: {', '.join(missing)}"
            )
        # endif not properly initialized
        
        # set other hooks that aren't required but may be used by the app
        self.usr_auth = getattr(app_config, 'USER_AUTHENTICATION_ENABLED', True) # use the setter to ensure it's set to a boolean (defaulting to True if usr_auth is provided but not a bool)
        
        # self.create_main_window_stack()  # create the main window stack and its forms (login, menu) at initialization so they're ready to go when needed
        
        # 2. Register Blueprints
        # This keeps cTools routes separate from the app routes
        app.register_blueprint(
            ctools_bp, 
            url_prefix='/ctools',
            )

        # Initialize extensions
        from ..models import init_cDatabase      # can I move this back to main imports?
        self.cTools_tables = init_cDatabase(app, app_db, cTools_bind_key, cTools_tablenames, cTools_models)
        # migrate = Migrate(app, cMenu_db)
        init_login_manager(app)
        
        # Move this to calling app
        # Create default Calvin user if not exists
        # R E M O V E   I N   P R O D U C T I O N   ! ! !
        # from .app_secrets.create_calvin import create_calvin 
        # create_calvin(app)
        
        # Register blueprints
        register_auth_blueprint(app)
        register_menu_blueprint(app)
        register_util_blueprint(app)
        
        # /index is just a null page
        @app.route('/index')
        def index():
            templt = 'nullpage.html'
            return checkTemplate_and_render(templt)
        
        # Error handlers
        @app.errorhandler(404)
        def not_found(error):   # pylint: disable=unused-argument
            return render_template('errors/404.html'), 404
        
        @app.errorhandler(403)
        def forbidden(error):   # pylint: disable=unused-argument
            return render_template('errors/403.html', error=error), 403
        
        @app.errorhandler(500)
        def internal_error(error):   # pylint: disable=unused-argument
            from ..models import db
            if db is not None:
                db.session.rollback()
            return render_template('errors/500.html', error=error), 500

        # 3. Attach cTools to the app extensions (optional but recommended)
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['ctools'] = self
    # init_app

    @classmethod
    def is_properly_initialized(cls):
        """
        Check if all required hooks have been initialized.
        Returns True only if the instance exists, is marked as initialized,
        and all required fields are set.
        """
        # Check if instance exists and is marked as initialized
        if cls._instance is None or not cls._initialized:
            return False
        
        # Check if all required fields are set (not None)
        return not any(getattr(cls._instance, f'_{attr}', None) is None 
                      for attr in cls._MUSTBEINITIALIZED)
    # is_properly_initialized

    @property
    def app_db(self):
        """
        Retrieve the configured application database sessionmaker.
        """
        if self._app_db is None:
            raise RuntimeError(
                "cTools_apphooks has not been initialized with 'app_db'. "
                "Call cTools_apphooks.initialize() first."
            )
        return self._app_db
    # get_app_sessionmaker
    @app_db.setter
    def app_db(self, app_db):
        """
        Set the application database sessionmaker.
        """
        self._app_db = app_db
        self._app_sessionmaker = sessionmaker(bind=app_db.engine)
    # set_app_sessionmaker

    @property
    def app_sessionmaker(self):
        """
        Retrieve the configured application database sessionmaker.
        """
        if self._app_sessionmaker is None:
            raise RuntimeError(
                "cTools_apphooks has not been initialized with 'app_sessionmaker'. "
                "Call cTools_apphooks.initialize() first."
            )
        return self._app_sessionmaker
    # get_app_sessionmaker
    @app_sessionmaker.setter
    def app_sessionmaker(self, app_sessionmaker):
        """
        Set the application database sessionmaker.
        """
        self._app_sessionmaker = app_sessionmaker
    # set_app_sessionmaker

    @property
    def appver(self):
        return self._appver
    @appver.setter
    def appver(self, appver):
        self._appver = appver

    @property
    def FormNameToURL_Map(self):
        if self._FormNameToURL_Map is None:
            raise RuntimeError(
                "cTools_apphooks has not been initialized with 'FormNameToURL_Map'. "
                "Call cTools_apphooks.initialize() first."
            )
        return self._FormNameToURL_Map
    @FormNameToURL_Map.setter
    def FormNameToURL_Map(self, FormNameToURL_Map):
        self._FormNameToURL_Map = FormNameToURL_Map

    @property
    def ExternalWebPageURL_Map(self):
        if self._ExternalWebPageURL_Map is None:
            raise RuntimeError(
                "cTools_apphooks has not been initialized with 'ExternalWebPageURL_Map'. "
                "Call cTools_apphooks.initialize() first."
            )
        return self._ExternalWebPageURL_Map
    @ExternalWebPageURL_Map.setter
    def ExternalWebPageURL_Map(self, ExternalWebPageURL_Map):
        self._ExternalWebPageURL_Map = ExternalWebPageURL_Map

    @property
    def appname(self):
        return self._appname
    @appname.setter
    def appname(self, appname):
        self._appname = appname

    @property
    def logo(self):
        return self._logo
    @logo.setter
    def logo(self, logo):
        self._logo = logo

    @property
    def usr_auth(self):
        return self._usr_auth
    @usr_auth.setter
    def usr_auth(self, usr_auth):
        self._usr_auth = usr_auth if isinstance(usr_auth, bool) else True  # if usr_auth is provided and is a bool, use it; otherwise default to True (using usr_auth)            

    # def main_window_stack(self):
    #     return self._main_window_stack
    # def login_form(self):
    #     return self._login_form
    # def menu_form(self):
    #     return self._menu_form

    # def create_main_window_stack(self):
    #     self._login_form = url_for('auth.login')
        
    #     mgroup = 1
    #     self._menu_form = url_for('menu.load_menu', menu_group=mgroup, menu_num=0)
        
        
    #     # self._main_window_stack = QStackedWidget()    #this is the standalone version
    #     self._main_window_stack = {}
    #     if self._login_form is not None:
    #         self._main_window_stack['login_form'] = self._login_form
    #     if self._menu_form is not None:
    #         self._main_window_stack['menu_form'] = self._menu_form
    # # create_main_window_stack
    
    # def show_menu_form(self):
    #     MFm = self.menu_form()
    #     # When login is successful, navigate to the menu form
    #     if self._main_window_stack is None or MFm is None:
    #         return  # main window stack or menu form not properly initialized, can't navigate
    #     self._main_window_stack.setCurrentWidget(MFm)
    #     cUsr = current_user()
    #     mGroup = cMenu._DFLT_menuGroup if cUsr is None else cUsr.menuGroup
    #     MFm.loadMenu(mGroup)
    # # show_menu_form
    # def show_login_form(self):
    #     LFm = self.login_form()
    #     if self._main_window_stack is None or LFm is None:
    #         return  # main window stack or menu form not properly initialized, can't navigate
    #     if self.usr_auth:
    #         LFm.reset_fields() # reset login form fields (e.g. clear username/password) when showing login form
    #         self._main_window_stack.setCurrentWidget(LFm)
    #     else:
    #         self.ShutdownRequested.emit()  # emit logout requested signal to trigger any necessary cleanup in the app (e.g. clearing user session data) when showing login form if usr_auth is False (i.e. no login form, so just trigger logout process)
    #         return
    # # show_login_form
    
    # @Slot()
    # def _on_login_successful(self):
    #     self.show_menu_form()
    # # on_login_successful
    
    # def login(self):
    #     # Show the login form or the menu form (whichever is appropriate based on self.usr_auth) when the application starts
    #     LFm = self.login_form()
    #     MFm = self.menu_form()
    #     if self._main_window_stack is None or LFm is None:
    #         return  # main window stack or menu form not properly initialized, can't navigate
    #     if self.usr_auth:
    #         self.show_login_form()
    #     else:
    #         if MFm is None:
    #             return
    #         set_current_user(User_usrauth_not_used)  # set to dummy user since we're not using authentication
    #         self.show_menu_form()

    # def logout(self):
    #     # Emit the LogoutRequested signal to trigger any necessary cleanup in the app (e.g. clearing user session data)
    #     self.LogoutRequested.emit()
    #     # After cleanup is done, emit the Logout signal to indicate logout has been completed
    #     self.show_login_form()      # this will show the login form if usr_auth, else shutdown the app (since there's no login form to show if usr_auth is False, we just trigger the logout process which should lead to app shutdown in that case)
    #     self.Logout.emit()
    # # logout
            
    # implement later (???)
    # cTools_tables = (None, None, None, None, None)   # will be set by init_cDatabase
    # cTools_bind_key=None, 
    # cTools_tablenames=None, 
    # cTools_models=None):
        # from .models import init_cDatabase      # can I move this back to main imports?
        # self.cTools_tables = init_cDatabase(app, app_db, cTools_bind_key, cTools_tablenames, cTools_models)

# calvinCTools
    def end_of_class(self):
        pass


