# calvinctools/apphooks.py

class cTools_apphooks:
    """
    A Singleton class to hold application-specific hooks and resources
    for the calvinctools toolkit, such as database sessionmakers.

    This acts as a Service Locator for external dependencies.
    """
    _instance = None
    _app_sessionmaker = None
    _app_db = None
    _appver = ''
    _FormNameToURL_Map = {}
    _ExternalWebPageURL_Map = {}
    _MUSTBEINITIALIZED: set = {
        'app_db',
        # 'app_sessionmaker',
        'FormNameToURL_Map', 
        'ExternalWebPageURL_Map',
        }

    def __new__(cls):
        # Implement the Singleton pattern: always return the same instance
        if cls._instance is None:
            cls._instance = super(cTools_apphooks, cls).__new__(cls)
        return cls._instance

    @classmethod
    def initialize(cls, 
            app_db=None,
            app_sessionmaker=None, 
            FormNameToURL_Map=None,
            ExternalWebPageURL_Map=None,
            appver='',
            **kwargs
            ):  # pylint: disable=unused-argument
        """
        The main method to initialize the singleton with all required hooks.
        This should be called ONCE during application startup before
        any calvinctools module is used.
        """
        instance = cls() # This ensures the instance exists
        if FormNameToURL_Map is None:
            FormNameToURL_Map={}
        if ExternalWebPageURL_Map is None:
            ExternalWebPageURL_Map={}
        if app_db is not None:
            instance.set_app_db(app_db)
        if app_sessionmaker is not None:
            instance.set_app_sessionmaker(app_sessionmaker)
        if FormNameToURL_Map:
            instance.set_FormNameToURL_Map(FormNameToURL_Map)
        if ExternalWebPageURL_Map:
            instance.set_ExternalWebPageURL_Map(ExternalWebPageURL_Map)
        if appver:
            instance.set_appver(appver)
        
        # You can add other app-specific resources here
        # Example: instance._external_config = kwargs.get('config')
        
        return instance
    # initialize
    @classmethod
    def is_initialized(cls):
        """
        Check if all required hooks have been initialized.
        """
        instance = cls()
        return not any(getattr(instance, f'_{attr}', None) is None for attr in cls._MUSTBEINITIALIZED)
    # is_initialized


    def get_app_db(self):
        """
        Retrieve the configured application database sessionmaker.
        """
        if self._app_db is None:
            raise RuntimeError(
                "cTools_apphooks has not been initialized with 'app_sessionmaker'. "
                "Call cTools_apphooks.initialize() first."
            )
        return self._app_db
    # get_app_db
    def set_app_db(self, app_db):
        """
        Set the application database sessionmaker.
        """
        self._app_db = app_db
    # set_app_db

    def get_app_sessionmaker(self):
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
    def set_app_sessionmaker(self, app_sessionmaker):
        """
        Set the application database sessionmaker.
        """
        self._app_sessionmaker = app_sessionmaker
    # set_app_sessionmaker

    def get_appver(self):
        return self._appver
    def set_appver(self, appver):
        self._appver = appver

    def get_FormNameToURL_Map(self):
        if self._app_sessionmaker is None:
            raise RuntimeError(
                "cTools_apphooks has not been initialized with 'FormNameToURL_Map'. "
                "Call cTools_apphooks.initialize() first."
            )
        return self._FormNameToURL_Map
    def set_FormNameToURL_Map(self, FormNameToURL_Map):
        self._FormNameToURL_Map = FormNameToURL_Map

    def get_ExternalWebPageURL_Map(self):
        if self._app_sessionmaker is None:
            raise RuntimeError(
                "cTools_apphooks has not been initialized with 'ExternalWebPageURL_Map'. "
                "Call cTools_apphooks.initialize() first."
            )
        return self._ExternalWebPageURL_Map
    def set_ExternalWebPageURL_Map(self, ExternalWebPageURL_Map):
        self._ExternalWebPageURL_Map = ExternalWebPageURL_Map
    
    # Additional getters/setters can be added as needed

# Convenience function to get the instance
def get_apphooks():
    """
    Global access point to the initialized cTools_apphooks instance.
    """
    return cTools_apphooks()