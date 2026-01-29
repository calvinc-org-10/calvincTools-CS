from .database import cMenu_dbPath
calvincTools_config = {
    'SQLALCHEMY_BINDS': {'cToolsdb': f'sqlite:///{cMenu_dbPath}'}
}
